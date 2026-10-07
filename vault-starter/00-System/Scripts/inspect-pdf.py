#!/usr/bin/env python3
"""
Inspect PDF for text layer quality and language detection.

Safe execution: read-only operations, no file modification.
"""

import argparse
import hashlib
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 hash of file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            sha256.update(block)
    return sha256.hexdigest()


def detect_text_layer(pdf_path: Path) -> dict:
    """
    Test if PDF has usable text layer.

    Returns dict with:
    - has_good_text: bool
    - char_count: int
    - sample_text: str
    - error: str or None
    """
    try:
        result = subprocess.run(
            ["pdftotext", "-l", "3", str(pdf_path), "-"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return {
                "has_good_text": False,
                "char_count": 0,
                "sample_text": "",
                "error": f"pdftotext failed: {result.stderr}"
            }

        text = result.stdout
        char_count = len(text.strip())
        has_good_text = char_count > 200  # 3-page threshold

        return {
            "has_good_text": has_good_text,
            "char_count": char_count,
            "sample_text": text[:500],
            "error": None
        }

    except subprocess.TimeoutExpired:
        return {
            "has_good_text": False,
            "char_count": 0,
            "sample_text": "",
            "error": "pdftotext timeout"
        }
    except Exception as e:
        return {
            "has_good_text": False,
            "char_count": 0,
            "sample_text": "",
            "error": str(e)
        }


def detect_language(sample_text: str) -> dict:
    """
    Infer language from sample text.

    Returns dict with:
    - language_inference: str or None
    - language_confidence: 'high' | 'medium' | 'low'
    - confirmation_required: bool
    """
    if not sample_text or len(sample_text.strip()) < 50:
        return {
            "language_inference": None,
            "language_confidence": "low",
            "confirmation_required": True
        }

    # English stopwords for language disambiguation
    ENGLISH_STOPWORDS = {
        'the', 'of', 'and', 'to', 'in', 'a', 'is', 'that', 'for', 'it',
        'with', 'as', 'was', 'on', 'by', 'be', 'this', 'which', 'or',
        'from', 'at', 'an', 'are', 'not', 'his', 'but', 'had', 'has'
    }

    # Tokenize and count English stopwords
    tokens = sample_text.lower().split()
    english_stopword_count = sum(1 for token in tokens if token in ENGLISH_STOPWORDS)
    english_stopword_ratio = english_stopword_count / len(tokens) if tokens else 0

    # Character-based heuristics
    has_turkish_chars = any(c in sample_text for c in "çğıöşüÇĞİÖŞÜ")
    has_arabic_chars = any("\u0600" <= c <= "\u06FF" for c in sample_text)
    has_latin_chars = any(c.isalpha() and ord(c) < 256 for c in sample_text)

    # Count Turkish character density
    turkish_char_count = sum(1 for c in sample_text if c in "çğıöşüÇĞİÖŞÜ")
    turkish_char_ratio = turkish_char_count / len(sample_text) if sample_text else 0

    # Strong English signal: high stopword ratio (> 8%)
    strong_english = english_stopword_ratio > 0.08

    # Weak Turkish signal: isolated Turkish-looking characters (< 0.5% density)
    # This catches diacritics and transliterations in English text
    weak_turkish = has_turkish_chars and turkish_char_ratio < 0.005

    # Multilingual detection
    scripts = []

    if has_arabic_chars:
        scripts.append("ara")

    # Only classify as Turkish if:
    # - Turkish characters present AND
    # - NOT weak Turkish signal (diacritics/transliterations) AND
    # - NOT strong English signal
    if has_turkish_chars and not weak_turkish and not strong_english:
        scripts.append("tur")
    # Otherwise, if Latin characters and strong English signal, classify as English
    elif has_latin_chars and strong_english:
        scripts.append("eng")
    # Fallback: Latin chars without strong evidence
    elif has_latin_chars:
        scripts.append("eng")

    # Handle conflicting signals: Turkish chars + strong English
    if has_turkish_chars and strong_english:
        # Likely English with transliterated names/diacritics
        return {
            "language_inference": "eng",
            "language_confidence": "medium",
            "confirmation_required": True
        }

    if len(scripts) > 1:
        # Mixed scripts - require confirmation
        return {
            "language_inference": "+".join(scripts),
            "language_confidence": "medium",
            "confirmation_required": True
        }

    if len(scripts) == 1:
        # High confidence only for Arabic script or strong Turkish (not weak)
        if scripts[0] == "ara":
            confidence = "high"
        elif scripts[0] == "tur" and not weak_turkish:
            confidence = "high"
        elif scripts[0] == "eng" and strong_english:
            confidence = "high"
        else:
            confidence = "medium"

        return {
            "language_inference": scripts[0],
            "language_confidence": confidence,
            "confirmation_required": confidence != "high"
        }

    return {
        "language_inference": None,
        "language_confidence": "low",
        "confirmation_required": True
    }


def get_page_count(pdf_path: Path) -> int:
    """Get PDF page count using pdfinfo."""
    try:
        result = subprocess.run(
            ["pdfinfo", str(pdf_path)],
            capture_output=True,
            text=True,
            timeout=10
        )

        for line in result.stdout.split("\n"):
            if line.startswith("Pages:"):
                return int(line.split(":")[1].strip())

        return 0

    except:
        return 0


def generate_intake_report(pdf_path: Path, vault_root: Path, dry_run: bool = False) -> str:
    """Generate intake report markdown."""
    sha256 = compute_sha256(pdf_path)
    text_layer = detect_text_layer(pdf_path)
    lang_detect = detect_language(text_layer["sample_text"])
    page_count = get_page_count(pdf_path)

    # Python 3.8-compatible relative path check
    try:
        rel_path = pdf_path.relative_to(vault_root)
    except ValueError:
        rel_path = pdf_path

    report = f"""---
source_file: "{pdf_path.name}"
source_hash_sha256: "{sha256}"
source_path: "{rel_path}"
created: "{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
report_type: "intake"
---

# Intake Report: {pdf_path.stem}

## File Information

- **Filename:** {pdf_path.name}
- **Size:** {pdf_path.stat().st_size / 1024:.1f} KB
- **SHA-256:** `{sha256}`
- **Page Count:** {page_count}

## Text Layer Assessment

- **Has Usable Text:** {"Yes" if text_layer["has_good_text"] else "No"}
- **Character Count (first 3 pages):** {text_layer["char_count"]}
- **Assessment:** {"Native text extraction suitable" if text_layer["has_good_text"] else "OCR required"}
"""

    if text_layer["error"]:
        report += f"\n**Error:** {text_layer['error']}\n"

    report += f"""
## Language Detection

- **Inference:** {lang_detect["language_inference"] or "Unknown"}
- **Confidence:** {lang_detect["language_confidence"]}
- **Manual Confirmation Required:** {"Yes" if lang_detect["confirmation_required"] else "No"}

"""

    if lang_detect["confirmation_required"]:
        report += """**Action Required:** Supply explicit --lang parameter when processing.

"""

    report += f"""## Sample Text

```
{text_layer["sample_text"][:300].strip()}...
```

## Recommendation

"""

    if text_layer["has_good_text"] and not lang_detect["confirmation_required"]:
        report += "**ACCEPT** - Ready for native text extraction.\n"
    elif text_layer["has_good_text"]:
        report += "**HOLD FOR MANUAL REVIEW** - Good text layer but language uncertain.\n"
    elif not text_layer["error"]:
        report += "**ACCEPT (OCR REQUIRED)** - Scanned document, OCR needed.\n"
    else:
        report += "**REQUEST BETTER COPY** - Text extraction failed.\n"

    report += f"""
## Next Steps

"""

    if text_layer["has_good_text"]:
        report += f"""1. Move or copy to `01-Library/Originals/`
2. Run: `python3 00-System/Scripts/process-source.py --file "01-Library/Originals/{pdf_path.name}"`
"""
    else:
        lang_hint = lang_detect["language_inference"] or "[tur|eng|ara]"
        report += f"""1. Move or copy to `01-Library/Originals/`
2. Run: `python3 00-System/Scripts/process-source.py --file "01-Library/Originals/{pdf_path.name}" --lang {lang_hint}`
"""

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Inspect PDF text layer and detect language"
    )
    parser.add_argument(
        "--file",
        type=Path,
        required=True,
        help="PDF file to inspect"
    )
    parser.add_argument(
        "--vault-root",
        type=Path,
        help="Vault root directory (auto-detected if not specified)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Display report without writing file"
    )

    args = parser.parse_args()

    # Validate input
    if not args.file.exists():
        print(f"ERROR: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    if not args.file.suffix.lower() == ".pdf":
        print(f"ERROR: Not a PDF file: {args.file}", file=sys.stderr)
        sys.exit(1)

    # Auto-detect vault root
    if not args.vault_root:
        script_dir = Path(__file__).parent
        args.vault_root = script_dir.parent.parent
        if not (args.vault_root / "CLAUDE.md").exists():
            print("WARNING: Could not auto-detect vault root", file=sys.stderr)
            args.vault_root = args.file.parent

    # Generate report
    report_content = generate_intake_report(args.file, args.vault_root, args.dry_run)

    if args.dry_run:
        print("=" * 60)
        print("DRY RUN: Intake Report")
        print("=" * 60)
        print(report_content)
        sys.exit(0)

    # Write report
    reports_dir = args.vault_root / "01-Library" / "Reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    report_path = reports_dir / f"{args.file.stem}__intake.md"

    report_path.write_text(report_content, encoding="utf-8")

    print(f"Intake report created: {report_path.relative_to(args.vault_root)}")
    print()
    print("Summary:")
    text_layer = detect_text_layer(args.file)
    lang_detect = detect_language(text_layer["sample_text"])
    print(f"  Text layer: {'Good' if text_layer['has_good_text'] else 'Poor/None'}")
    print(f"  Language: {lang_detect['language_inference'] or 'Unknown'} ({lang_detect['language_confidence']} confidence)")
    print(f"  Confirmation required: {'Yes' if lang_detect['confirmation_required'] else 'No'}")

    sys.exit(0)


if __name__ == "__main__":
    main()
