#!/usr/bin/env python3
"""
Process source PDFs through OCR pipeline.

Safe execution: atomic writes, temporary files, no overwrites unless --force.
"""

import argparse
import hashlib
import shutil
import subprocess
import sys
import tempfile
import yaml
from datetime import datetime
from pathlib import Path


def load_config(vault_root: Path) -> dict:
    """Load source pipeline configuration."""
    config_path = vault_root / "00-System" / "Config" / "source-pipeline.yml"

    if not config_path.exists():
        print(f"ERROR: Config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def check_dependencies() -> dict:
    """
    Check for required system dependencies.

    Returns dict with:
    - available: list of available tools
    - missing: list of missing tools
    - all_present: bool
    """
    tools = ['pdftotext', 'pdfinfo', 'ocrmypdf', 'tesseract']
    available = []
    missing = []

    for tool in tools:
        try:
            result = subprocess.run(
                ['which', tool],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                available.append(tool)
            else:
                missing.append(tool)
        except:
            missing.append(tool)

    return {
        'available': available,
        'missing': missing,
        'all_present': len(missing) == 0
    }


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


def perform_ocr(pdf_path: Path, lang: str, output_path: Path, force: bool = False) -> dict:
    """
    Perform OCR on PDF using OCRmyPDF.

    Args:
        pdf_path: Input PDF
        lang: Language code(s), e.g., 'tur', 'eng', 'tur+ara'
        output_path: Output OCR'd PDF path
        force: Overwrite existing output

    Returns:
        dict with status, output_path, error
    """
    result = {
        "status": "failed",
        "output_path": None,
        "error": None
    }

    # Check if output exists
    if output_path.exists() and not force:
        result["status"] = "skipped"
        result["output_path"] = str(output_path)
        result["error"] = "Output exists (use --force to overwrite)"
        return result

    try:
        # Create temporary output file
        with tempfile.NamedTemporaryFile(
            dir=output_path.parent,
            suffix='.pdf',
            delete=False
        ) as tmp:
            tmp_path = Path(tmp.name)

        # Run OCRmyPDF
        cmd = [
            'ocrmypdf',
            '--language', lang,
            '--skip-text',  # Skip pages that already have text
            '--rotate-pages',
            '--deskew',
            '--clean',
            str(pdf_path),
            str(tmp_path)
        ]

        ocr_result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=1800  # 30 minute timeout
        )

        if ocr_result.returncode == 0:
            # Atomic rename
            tmp_path.replace(output_path)
            result["status"] = "success"
            result["output_path"] = str(output_path)
        else:
            # Clean up temporary file
            if tmp_path.exists():
                tmp_path.unlink()
            result["error"] = f"ocrmypdf failed: {ocr_result.stderr}"

    except subprocess.TimeoutExpired:
        if tmp_path.exists():
            tmp_path.unlink()
        result["error"] = "OCR timeout (>30 minutes)"
    except Exception as e:
        if 'tmp_path' in locals() and tmp_path.exists():
            tmp_path.unlink()
        result["error"] = str(e)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Process source PDFs through OCR pipeline"
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="PDF file to process"
    )
    parser.add_argument(
        "--lang",
        type=str,
        help="Language code(s) for OCR: tur, eng, ara, or combinations like tur+ara"
    )
    parser.add_argument(
        "--vault-root",
        type=Path,
        help="Vault root directory (auto-detected if not specified)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing output files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without processing"
    )
    parser.add_argument(
        "--doctor",
        action="store_true",
        help="Check system dependencies and exit"
    )

    args = parser.parse_args()

    # Auto-detect vault root
    if not args.vault_root:
        script_dir = Path(__file__).parent
        args.vault_root = script_dir.parent.parent
        if not (args.vault_root / "CLAUDE.md").exists():
            print("WARNING: Could not auto-detect vault root", file=sys.stderr)
            if args.file:
                args.vault_root = args.file.parent
            else:
                args.vault_root = Path.cwd()

    # Doctor mode
    if args.doctor:
        print("Checking system dependencies...\n")
        deps = check_dependencies()

        if deps['available']:
            print("Available tools:")
            for tool in deps['available']:
                print(f"  ✓ {tool}")

        if deps['missing']:
            print("\nMissing tools:")
            for tool in deps['missing']:
                print(f"  ✗ {tool}")
            print("\nInstallation hints:")
            print("  macOS: brew install poppler tesseract ocrmypdf")
            print("  Ubuntu/Debian: apt install poppler-utils tesseract-ocr ocrmypdf")
            print("\nFor language support:")
            print("  macOS: brew install tesseract-lang")
            print("  Ubuntu/Debian: apt install tesseract-ocr-tur tesseract-ocr-ara")
            sys.exit(1)
        else:
            print("\n✓ All dependencies available")
            sys.exit(0)

    # Require file for processing
    if not args.file:
        print("ERROR: --file required (or use --doctor to check dependencies)", file=sys.stderr)
        sys.exit(1)

    # Validate input
    if not args.file.exists():
        print(f"ERROR: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    if not args.file.suffix.lower() == ".pdf":
        print(f"ERROR: Not a PDF file: {args.file}", file=sys.stderr)
        sys.exit(1)

    # Load config
    config = load_config(args.vault_root)

    # Detect text layer and language
    print(f"Inspecting: {args.file.name}")
    text_layer = detect_text_layer(args.file)

    if text_layer["error"]:
        print(f"ERROR: {text_layer['error']}", file=sys.stderr)
        sys.exit(1)

    has_text = text_layer["has_good_text"]
    lang_detect = detect_language(text_layer["sample_text"])

    print(f"  Text layer: {'Good' if has_text else 'Poor/None'}")
    print(f"  Character count (first 3 pages): {text_layer['char_count']}")
    print(f"  Language inference: {lang_detect['language_inference'] or 'Unknown'}")
    print(f"  Confidence: {lang_detect['language_confidence']}")

    # Validate language parameter if provided
    VALID_LANGUAGES = {
        'tur', 'eng', 'ara',
        'tur+ara', 'eng+ara', 'tur+eng',
        'tur+eng+ara'
    }

    if args.lang and args.lang not in VALID_LANGUAGES:
        print(f"\nERROR: Invalid language code: {args.lang}", file=sys.stderr)
        print("Valid language codes:", file=sys.stderr)
        print("  Single: tur, eng, ara", file=sys.stderr)
        print("  Combined: tur+ara, eng+ara, tur+eng, tur+eng+ara", file=sys.stderr)
        sys.exit(1)

    # Determine processing path
    needs_ocr = not has_text

    if needs_ocr and not args.lang:
        print("\nERROR: OCR required but no language specified", file=sys.stderr)
        print(f"Suggested language: {lang_detect['language_inference'] or 'tur|eng|ara'}", file=sys.stderr)
        print("Specify language with: --lang <code>", file=sys.stderr)
        sys.exit(1)

    if lang_detect['confirmation_required'] and not args.lang:
        print("\nWARNING: Language detection uncertain", file=sys.stderr)
        print(f"Inference: {lang_detect['language_inference'] or 'Unknown'}", file=sys.stderr)
        print("Recommend specifying explicit --lang parameter", file=sys.stderr)
        if needs_ocr:
            sys.exit(1)

    # Prepare output paths
    stem = args.file.stem
    ocr_dir = args.vault_root / config['folder_structure']['ocr']
    text_dir = args.vault_root / config['folder_structure']['text']

    ocr_dir.mkdir(parents=True, exist_ok=True)
    text_dir.mkdir(parents=True, exist_ok=True)

    ocr_pdf_path = ocr_dir / f"{stem}{config['file_naming']['ocr_suffix']}.pdf"
    text_final_path = text_dir / f"{stem}{config['file_naming']['text_suffix']}.txt"

    # Legacy TXT representation decision logic
    legacy_txt_path = text_dir / f"{stem}.txt"
    legacy_exists = legacy_txt_path.exists()
    canonical_exists = text_final_path.exists()

    # Case D: Both representations exist - representation conflict
    if legacy_exists and canonical_exists:
        print(f"\nERROR: TXT representation conflict detected", file=sys.stderr)
        print(f"  Legacy representation: {legacy_txt_path.relative_to(args.vault_root)}", file=sys.stderr)
        print(f"  Canonical representation: {text_final_path.relative_to(args.vault_root)}", file=sys.stderr)
        print(f"\nCannot silently choose between representations.", file=sys.stderr)
        print(f"Explicit user resolution required:", file=sys.stderr)
        print(f"  1. Migrate legacy → canonical: Manually delete {legacy_txt_path.name}, rerun pipeline", file=sys.stderr)
        print(f"  2. Preserve legacy only: Manually delete {text_final_path.name}", file=sys.stderr)
        print(f"  3. Archive legacy: Rename {legacy_txt_path.name} to {stem}__archived.txt, rerun pipeline", file=sys.stderr)
        sys.exit(1)

    # Case B: Only legacy representation exists - legacy-compatible mode
    use_legacy_mode = legacy_exists and not canonical_exists
    if use_legacy_mode:
        print(f"\nLegacy TXT representation detected: {legacy_txt_path.relative_to(args.vault_root)}")
        print(f"  Operating in legacy-compatible mode")
        print(f"  Legacy file will remain the active text representation")
        print(f"  Canonical migration requires explicit user decision")
        print(f"  Validation and ingestion workflows will use legacy TXT")
        print(f"\nSkipping text extraction (legacy representation takes precedence)")
        # Override text_final_path to point to legacy for validation step
        text_final_path = legacy_txt_path

    if args.dry_run:
        print("\nDRY RUN: Would perform the following operations:")
        if needs_ocr:
            print(f"  1. OCR: {args.file.name} → {ocr_pdf_path.relative_to(args.vault_root)}")
            print(f"     Language: {args.lang}")
            print(f"  2. Extract text with page markers: {ocr_pdf_path.name} → {text_final_path.relative_to(args.vault_root)}")
        else:
            print(f"  1. Extract text with page markers: {args.file.name} → {text_final_path.relative_to(args.vault_root)}")
        print(f"  2. Quality validation: {text_final_path.name}")
        sys.exit(0)

    # Execute processing
    print("\nProcessing:")

    # Step 1: OCR if needed
    source_pdf = args.file
    if needs_ocr:
        print(f"\n[1/3] Running OCR (language: {args.lang})...")
        ocr_result = perform_ocr(args.file, args.lang, ocr_pdf_path, force=args.force)

        if ocr_result["status"] == "skipped":
            print(f"  Skipped: {ocr_result['error']}")
            source_pdf = ocr_pdf_path
        elif ocr_result["status"] == "success":
            print(f"  ✓ Created: {ocr_pdf_path.relative_to(args.vault_root)}")
            source_pdf = ocr_pdf_path
        else:
            print(f"  ✗ Failed: {ocr_result['error']}", file=sys.stderr)
            sys.exit(1)
    else:
        print("\n[1/3] OCR not required (native text layer detected)")

    # Step 2: Extract text and add page markers preserving physical PDF page correspondence
    print(f"\n[2/3] Extracting text and adding page markers...")

    # Skip extraction if in legacy mode
    if use_legacy_mode:
        print(f"  Skipped: Using legacy TXT representation")
    # Check if final output already exists
    elif text_final_path.exists() and not args.force:
        print(f"  Skipped: Output exists (use --force to overwrite)")
    else:
        try:
            # Get PDF page count using pdfinfo
            pdfinfo_result = subprocess.run(
                ['pdfinfo', str(source_pdf)],
                capture_output=True,
                text=True,
                timeout=10
            )

            total_pages = 0
            for line in pdfinfo_result.stdout.split('\n'):
                if line.startswith('Pages:'):
                    total_pages = int(line.split(':')[1].strip())
                    break

            if total_pages == 0:
                print(f"  ✗ Failed: Could not determine PDF page count", file=sys.stderr)
                sys.exit(1)

            # Extract text page-by-page to preserve empty page correspondence
            output_lines = []
            pages_with_text = 0
            pages_without_text = 0

            for page_num in range(1, total_pages + 1):
                # Extract single page
                page_result = subprocess.run(
                    ['pdftotext', '-layout', '-f', str(page_num), '-l', str(page_num), str(source_pdf), '-'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if page_result.returncode != 0:
                    print(f"  ✗ Failed: Could not extract page {page_num}", file=sys.stderr)
                    sys.exit(1)

                page_text = page_result.stdout.strip()

                # Add page marker
                output_lines.append(f"\n\n--- PDF PAGE {page_num} ---\n\n")

                if page_text:
                    output_lines.append(page_text)
                    pages_with_text += 1
                else:
                    output_lines.append("[NO EXTRACTED TEXT]")
                    pages_without_text += 1

            output_text = "".join(output_lines)

            # Write to final output atomically
            with tempfile.NamedTemporaryFile(
                mode='w',
                encoding='utf-8',
                dir=text_dir,
                delete=False,
                suffix='.tmp'
            ) as tmp_final:
                tmp_final.write(output_text)
                tmp_final_path = Path(tmp_final.name)

            # Atomic rename to final path
            tmp_final_path.replace(text_final_path)

            print(f"  ✓ Created: {text_final_path.relative_to(args.vault_root)}")
            print(f"  Physical PDF pages: {total_pages}")
            print(f"  Pages with text: {pages_with_text}")
            print(f"  Pages without text: {pages_without_text}")

        except Exception as e:
            # Clean up temporary files on error
            if 'tmp_final_path' in locals() and tmp_final_path.exists():
                tmp_final_path.unlink()
            print(f"  ✗ Failed: {e}", file=sys.stderr)
            sys.exit(1)

    # Step 3: Quality validation
    print(f"\n[3/3] Quality validation...")
    validate_script = args.vault_root / "00-System" / "Scripts" / "validate-text.py"

    if validate_script.exists():
        try:
            validate_result = subprocess.run(
                [
                    sys.executable,
                    str(validate_script),
                    '--file', str(text_final_path),
                    '--vault-root', str(args.vault_root)
                ],
                capture_output=True,
                text=True,
                timeout=60
            )

            if validate_result.returncode == 0:
                print("  ✓ Quality validation completed")
                print(validate_result.stdout)
            else:
                print(f"  ⚠ Validation warnings:", file=sys.stderr)
                print(validate_result.stderr, file=sys.stderr)
        except Exception as e:
            print(f"  ⚠ Validation failed: {e}", file=sys.stderr)
    else:
        print("  ⚠ Validation script not found, skipping")

    print("\n✓ Processing complete")
    print(f"\nNext steps:")
    print(f"  1. Review quality report: 01-Library/Reports/{stem}__quality.md")
    print(f"  2. Read text output: {text_final_path.relative_to(args.vault_root)}")
    print(f"  3. If quality is acceptable, proceed with source ingestion")


if __name__ == "__main__":
    main()
