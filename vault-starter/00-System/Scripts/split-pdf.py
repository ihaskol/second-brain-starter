#!/usr/bin/env python3
"""
Split large PDFs into smaller chunks for OCR processing.

Usage:
    python3 split-pdf.py --file "path/to/large.pdf" --chunk-size 100 --output-dir "path/to/chunks"
"""

import argparse
import sys
from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter

def split_pdf(input_path, chunk_size=100, output_dir=None):
    """Split a PDF into smaller chunks."""
    input_path = Path(input_path)

    if not input_path.exists():
        print(f"✗ Error: File not found: {input_path}")
        return False

    # Default output directory: same location as input, with "_chunks" suffix
    if output_dir is None:
        output_dir = input_path.parent / f"{input_path.stem}_chunks"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        reader = PdfReader(str(input_path))
        total_pages = len(reader.pages)

        print(f"Splitting: {input_path.name}")
        print(f"  Total pages: {total_pages}")
        print(f"  Chunk size: {chunk_size} pages")
        print(f"  Output directory: {output_dir}")
        print()

        num_chunks = (total_pages + chunk_size - 1) // chunk_size  # Ceiling division

        for chunk_num in range(num_chunks):
            start_page = chunk_num * chunk_size
            end_page = min(start_page + chunk_size, total_pages)

            # Create output filename with chunk info
            chunk_filename = f"{input_path.stem}_chunk{chunk_num+1:02d}_p{start_page+1:04d}-{end_page:04d}.pdf"
            chunk_path = output_dir / chunk_filename

            # Create writer for this chunk
            writer = PdfWriter()

            # Add pages to this chunk
            for page_num in range(start_page, end_page):
                writer.add_page(reader.pages[page_num])

            # Write chunk to file
            with open(chunk_path, 'wb') as output_file:
                writer.write(output_file)

            print(f"  ✓ Created chunk {chunk_num+1}/{num_chunks}: {chunk_filename} ({end_page - start_page} pages)")

        print()
        print(f"✓ Successfully split into {num_chunks} chunks")
        print(f"  Output directory: {output_dir}")
        return True

    except Exception as e:
        print(f"✗ Error splitting PDF: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Split large PDFs into smaller chunks for OCR')
    parser.add_argument('--file', required=True, help='Path to PDF file to split')
    parser.add_argument('--chunk-size', type=int, default=100, help='Pages per chunk (default: 100)')
    parser.add_argument('--output-dir', help='Output directory for chunks (default: input_dir/filename_chunks)')

    args = parser.parse_args()

    success = split_pdf(args.file, chunk_size=args.chunk_size, output_dir=args.output_dir)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
