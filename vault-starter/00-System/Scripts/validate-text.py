#!/usr/bin/env python3
"""
Validate text quality and generate quality report.

Safe execution: read-only text analysis, no file modification.
"""

import argparse
import hashlib
import re
import subprocess
import sys
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


def compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 hash of file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            sha256.update(block)
    return sha256.hexdigest()


def get_pdf_page_count(pdf_path: Path) -> int:
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


def validate_text_quality(text_path: Path, config: dict) -> dict:
    """
    Validate text quality.

    Returns dict with:
    - page_count: int
    - pages_with_text: int
    - pages_without_text: int
    - empty_pages: list of int
    - total_chars: int
    - avg_chars_per_page: float
    - replacement_char_count: int
    - mojibake_detected: bool
    - mojibake_patterns: list
    - quality_status: 'passed' | 'usable-with-review' | 'failed'
    - issues: list of strings
    """
    result = {
        "page_count": 0,
        "pages_with_text": 0,
        "pages_without_text": 0,
        "empty_pages": [],
        "total_chars": 0,
        "avg_chars_per_page": 0.0,
        "replacement_char_count": 0,
        "mojibake_detected": False,
        "mojibake_patterns": [],
        "quality_status": "failed",
        "issues": []
    }

    try:
        text = text_path.read_text(encoding='utf-8', errors='replace')

        # Count pages (markers) and identify empty pages
        page_markers = re.findall(r'--- PDF PAGE (\d+) ---', text)
        result["page_count"] = len(page_markers)

        # Split text by page markers to analyze each page
        pages = re.split(r'\n\n--- PDF PAGE \d+ ---\n\n', text)
        # First element is text before first marker (usually empty)
        pages = pages[1:] if len(pages) > 1 else pages

        for i, page_text in enumerate(pages, start=1):
            page_content = page_text.strip()
            if page_content == "[NO EXTRACTED TEXT]" or not page_content:
                result["pages_without_text"] += 1
                result["empty_pages"].append(i)
            else:
                result["pages_with_text"] += 1

        # Character statistics
        result["total_chars"] = len(text)
        if result["page_count"] > 0:
            result["avg_chars_per_page"] = result["total_chars"] / result["page_count"]

        # Replacement character detection
        result["replacement_char_count"] = text.count('\ufffd')

        # Mojibake detection
        mojibake_patterns = config['quality_thresholds']['mojibake_patterns']
        found_patterns = []

        for pattern in mojibake_patterns:
            if pattern in text:
                found_patterns.append(pattern)

        if found_patterns:
            result["mojibake_detected"] = True
            result["mojibake_patterns"] = found_patterns

        # Quality assessment
        min_chars = config['quality_thresholds']['min_chars_per_page']
        max_replacement = config['quality_thresholds']['max_replacement_chars']

        if result["page_count"] == 0:
            result["issues"].append("No page markers found")
            result["quality_status"] = "failed"
        elif result["avg_chars_per_page"] < min_chars:
            result["issues"].append(f"Low character density ({result['avg_chars_per_page']:.0f} chars/page, threshold: {min_chars})")
            result["quality_status"] = "failed"
        elif result["replacement_char_count"] > max_replacement:
            result["issues"].append(f"High replacement character count ({result['replacement_char_count']}, threshold: {max_replacement})")
            result["quality_status"] = "usable-with-review"
        elif result["mojibake_detected"]:
            result["issues"].append(f"Mojibake detected: {', '.join(result['mojibake_patterns'][:3])}")
            result["quality_status"] = "usable-with-review"
        else:
            result["quality_status"] = "passed"

    except Exception as e:
        result["issues"].append(f"Validation error: {str(e)}")
        result["quality_status"] = "failed"

    return result


def check_page_correspondence(text_path: Path, pdf_path: Path) -> dict:
    """
    Check if text page count matches PDF page count.

    Returns dict with:
    - pdf_pages: int
    - text_pages: int
    - match: bool
    - issue: str or None
    """
    result = {
        "pdf_pages": 0,
        "text_pages": 0,
        "match": False,
        "issue": None
    }

    try:
        # Get PDF page count
        if pdf_path.exists():
            result["pdf_pages"] = get_pdf_page_count(pdf_path)
        else:
            result["issue"] = "PDF file not found"
            return result

        # Get text page count
        text = text_path.read_text(encoding='utf-8', errors='replace')
        page_markers = re.findall(r'--- PDF PAGE (\d+) ---', text)
        result["text_pages"] = len(page_markers)

        # Check match
        if result["pdf_pages"] == result["text_pages"]:
            result["match"] = True
        else:
            result["issue"] = f"Page count mismatch (PDF: {result['pdf_pages']}, Text: {result['text_pages']})"

    except Exception as e:
        result["issue"] = f"Correspondence check error: {str(e)}"

    return result


def generate_quality_report(
    text_path: Path,
    pdf_path: Path,
    vault_root: Path,
    config: dict
) -> str:
    """Generate quality report markdown."""

    # Compute hashes
    text_hash = compute_sha256(text_path)
    pdf_hash = compute_sha256(pdf_path) if pdf_path.exists() else "N/A"

    # Validate quality
    quality = validate_text_quality(text_path, config)

    # Check page correspondence
    correspondence = check_page_correspondence(text_path, pdf_path)

    # Determine technical_status
    if pdf_path.name.endswith(config['file_naming']['ocr_suffix'] + '.pdf'):
        technical_status = "ocr-completed"
    elif quality["quality_status"] != "failed":
        technical_status = "native-text"
    else:
        technical_status = "extraction-failed"

    # Determine overall recommendation
    if quality["quality_status"] == "passed" and correspondence["match"]:
        recommendation = "ACCEPT - Suitable for inspection and controlled ingestion"
    elif quality["quality_status"] == "usable-with-review":
        recommendation = "ACCEPT WITH CAUTION - Manual review recommended"
    else:
        recommendation = "REVIEW REQUIRED - Quality issues detected"

    report = f"""---
source_file: "{pdf_path.name if pdf_path.exists() else 'Unknown'}"
text_file: "{text_path.name}"
source_hash_sha256: "{pdf_hash}"
text_hash_sha256: "{text_hash}"
created: "{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
report_type: "quality"
technical_status: "{technical_status}"
quality_status: "{quality["quality_status"]}"
research_status: "not-inspected"
---

# Quality Report: {text_path.stem}

## File Information

- **Text File:** {text_path.name}
- **Text Size:** {text_path.stat().st_size / 1024:.1f} KB
- **Text SHA-256:** `{text_hash}`
- **Source PDF:** {pdf_path.name if pdf_path.exists() else 'Unknown'}
- **Source SHA-256:** `{pdf_hash}`

## Text Statistics

- **Page Count:** {quality["page_count"]}
- **Pages with Text:** {quality["pages_with_text"]}
- **Pages without Text:** {quality["pages_without_text"]}
- **Total Characters:** {quality["total_chars"]:,}
- **Average Characters/Page:** {quality["avg_chars_per_page"]:.0f}
- **Replacement Characters (�):** {quality["replacement_char_count"]}

## Page Correspondence

- **PDF Pages:** {correspondence["pdf_pages"]}
- **Text Pages:** {correspondence["text_pages"]}
- **Match:** {"Yes" if correspondence["match"] else "No"}
"""

    if correspondence["issue"]:
        report += f"- **Issue:** {correspondence['issue']}\n"

    # Add empty pages section if any
    if quality["empty_pages"]:
        report += f"\n## Empty Pages\n\n"
        report += f"The following pages had no extracted text:\n\n"
        # Show first 20 empty pages, then summarize
        if len(quality["empty_pages"]) <= 20:
            report += f"Pages: {', '.join(map(str, quality['empty_pages']))}\n"
        else:
            first_20 = ', '.join(map(str, quality["empty_pages"][:20]))
            report += f"Pages: {first_20}, ... ({len(quality['empty_pages'])} total)\n"
        report += "\n"

    report += f"""
## Quality Assessment

- **Technical Status:** `{technical_status}`
  - `native-text`: Extracted from original PDF text layer
  - `ocr-completed`: Generated via OCR pipeline
  - `extraction-failed`: Text extraction encountered errors

- **Quality Status:** `{quality["quality_status"]}`
  - `passed`: Meets all quality thresholds
  - `usable-with-review`: Meets minimum thresholds, manual review recommended
  - `failed`: Does not meet quality thresholds

- **Research Status:** `not-inspected`
  - Text has not been manually inspected for research use
  - Quality status only indicates technical suitability
  - Verification required before using as evidence

"""

    if quality["issues"]:
        report += "## Quality Issues\n\n"
        for issue in quality["issues"]:
            report += f"- {issue}\n"
        report += "\n"

    if quality["mojibake_detected"]:
        report += f"""## Encoding Issues

Mojibake patterns detected: {', '.join(quality["mojibake_patterns"][:5])}

"""

    report += f"""## Recommendation

**{recommendation}**

## Status Taxonomy

This report provides three independent status fields:

1. **technical_status**: Whether text was extracted successfully
   - Does NOT imply: verified, reliable, ready for citation

2. **quality_status**: Whether text meets technical quality thresholds
   - Does NOT imply: inspected, verified, ready for research use

3. **research_status**: Manual verification status
   - Currently: `not-inspected`
   - Verification required before: direct quotation, manuscript citation, treating as verified evidence

## Next Steps

"""

    if quality["quality_status"] == "passed":
        report += """1. Text extraction successful and meets quality thresholds
2. Proceed to manual inspection (Stage 4)
3. Use `ingest` workflow to create neutral wiki notes
4. Mark research_status after verification
"""
    elif quality["quality_status"] == "usable-with-review":
        report += """1. Review quality issues manually
2. Check sample pages for accuracy
3. Decide whether to: accept with caution, re-OCR with different settings, or request better source
4. Document any known quality limitations
"""
    else:
        report += """1. Review extraction failures
2. Consider: re-OCR with different language settings, different OCR tool, or request better source copy
3. Do not proceed to ingestion until quality issues resolved
"""

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Validate text quality and generate quality report"
    )
    parser.add_argument(
        "--file",
        type=Path,
        required=True,
        help="Text file to validate"
    )
    parser.add_argument(
        "--vault-root",
        type=Path,
        help="Vault root directory (auto-detected if not specified)"
    )

    args = parser.parse_args()

    # Validate input exists
    if not args.file.exists():
        print(f"ERROR: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    # Auto-detect vault root
    if not args.vault_root:
        script_dir = Path(__file__).parent
        args.vault_root = script_dir.parent.parent
        if not (args.vault_root / "CLAUDE.md").exists():
            print("WARNING: Could not auto-detect vault root", file=sys.stderr)
            args.vault_root = args.file.parent

    # Load config
    config = load_config(args.vault_root)

    # Find corresponding PDF
    stem = args.file.stem
    ocr_suffix = config['file_naming']['ocr_suffix']
    text_suffix = config['file_naming']['text_suffix']

    # Remove text suffix if present
    if stem.endswith(text_suffix):
        stem = stem[:-len(text_suffix)]

    # Look for PDF (check both OCR and Originals)
    ocr_dir = args.vault_root / config['folder_structure']['ocr']
    originals_dir = args.vault_root / config['folder_structure']['originals']

    pdf_path = ocr_dir / f"{stem}{ocr_suffix}.pdf"
    if not pdf_path.exists():
        pdf_path = originals_dir / f"{stem}.pdf"

    if not pdf_path.exists():
        print(f"WARNING: Corresponding PDF not found for {args.file.name}", file=sys.stderr)
        pdf_path = Path("unknown.pdf")  # Placeholder for report

    # Generate report
    report_content = generate_quality_report(args.file, pdf_path, args.vault_root, config)

    # Write report
    reports_dir = args.vault_root / config['folder_structure']['reports']
    reports_dir.mkdir(parents=True, exist_ok=True)

    quality_suffix = config['file_naming']['quality_suffix']
    report_path = reports_dir / f"{stem}{quality_suffix}.md"

    report_path.write_text(report_content, encoding='utf-8')

    print(f"Quality report created: {report_path.relative_to(args.vault_root)}")

    # Load and display summary
    quality = validate_text_quality(args.file, config)
    print()
    print("Summary:")
    print(f"  Quality status: {quality['quality_status']}")
    print(f"  Page count: {quality['page_count']}")
    print(f"  Avg chars/page: {quality['avg_chars_per_page']:.0f}")

    if quality["issues"]:
        print(f"  Issues: {len(quality['issues'])}")
        for issue in quality["issues"]:
            print(f"    - {issue}")

    sys.exit(0)


if __name__ == "__main__":
    main()
