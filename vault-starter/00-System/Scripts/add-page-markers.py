#!/usr/bin/env python3
"""
Add PDF page markers to plain text files.

Inserts '--- PDF PAGE N ---' markers at form-feed characters.
Safe execution: temporary files, atomic writes, no in-place editing.
"""

import argparse
import sys
import tempfile
from pathlib import Path


def add_page_markers(input_path: Path, output_path: Path, force: bool = False, dry_run: bool = False) -> dict:
    """
    Add page markers to text file.

    Returns:
        dict with status, page_count, output_path, error
    """
    result = {
        "status": "failed",
        "page_count": 0,
        "output_path": None,
        "error": None
    }

    # Check if output exists
    if output_path.exists() and not force and not dry_run:
        result["status"] = "skipped"
        result["output_path"] = str(output_path)
        result["error"] = "Output exists (use --force to overwrite)"
        return result

    try:
        # Read input
        text = input_path.read_text(encoding="utf-8", errors="replace")

        # Split on form-feed characters
        pages = text.split("\f")

        # Build output with markers
        output_lines = []
        page_num = 1

        for page in pages:
            if page.strip():  # Skip empty pages
                output_lines.append(f"\n\n--- PDF PAGE {page_num} ---\n\n")
                output_lines.append(page.strip())
                page_num += 1

        output_text = "".join(output_lines)
        result["page_count"] = page_num - 1

        if dry_run:
            result["status"] = "dry-run"
            result["output_path"] = str(output_path)
            return result

        # Atomic write using temporary file
        with tempfile.NamedTemporaryFile(
            mode='w',
            encoding='utf-8',
            dir=output_path.parent,
            delete=False,
            suffix='.tmp'
        ) as tmp:
            tmp.write(output_text)
            tmp_path = Path(tmp.name)

        # Atomic rename
        tmp_path.replace(output_path)

        result["status"] = "success"
        result["output_path"] = str(output_path)

    except Exception as e:
        if 'tmp_path' in locals() and tmp_path.exists():
            tmp_path.unlink()
        result["error"] = str(e)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Add PDF page markers to plain text files"
    )
    parser.add_argument(
        "--file",
        type=Path,
        required=True,
        help="Input text file path"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file path (required unless --dry-run)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing output file"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without writing files"
    )

    args = parser.parse_args()

    # Validate input exists
    if not args.file.exists():
        print(f"ERROR: Input file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    # Require output path unless dry-run
    if not args.dry_run and not args.output:
        print("ERROR: --output required unless --dry-run is specified", file=sys.stderr)
        sys.exit(1)

    # Reject output == input
    if args.output and args.output.resolve() == args.file.resolve():
        print("ERROR: Output path cannot be the same as input path", file=sys.stderr)
        sys.exit(1)

    # Set output path for dry-run display
    if args.dry_run and not args.output:
        args.output = args.file.parent / f"{args.file.stem}__with-markers.txt"

    # Process
    result = add_page_markers(args.file, args.output, force=args.force, dry_run=args.dry_run)

    if result["status"] == "dry-run":
        print(f"DRY RUN: Would add page markers to {args.file}")
        print(f"  Detected pages: {result['page_count']}")
        print(f"  Would write to: {result['output_path']}")
        sys.exit(0)

    if result["status"] == "skipped":
        print(f"SKIPPED: {result['error']}", file=sys.stderr)
        sys.exit(2)

    if result["status"] == "success":
        print(f"SUCCESS: Added {result['page_count']} page markers")
        print(f"  Output: {result['output_path']}")
        sys.exit(0)

    print(f"FAILED: {result['error']}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
