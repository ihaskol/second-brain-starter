#!/usr/bin/env python3
"""
Merge chunk text files back into complete source files.

For each chunked PDF (e.g., 04-0087), finds all chunk text files
(04-0087_chunk01__text.txt, 04-0087_chunk02__text.txt, etc.) and
concatenates them into a single file (04-0087__text.txt).
"""

import os
import re
from pathlib import Path
from collections import defaultdict

def main():
    vault_root = Path(__file__).resolve().parents[2]  # vault root
    text_dir = vault_root / "01-Library/Text"

    print("Merging chunk files into complete source texts...")
    print()

    # Find all chunk files and group by base name
    chunk_pattern = re.compile(r'^(.+)_chunk\d+_p\d+-\d+__text\.txt$')
    chunks_by_base = defaultdict(list)

    for file_path in text_dir.glob("*_chunk*__text.txt"):
        match = chunk_pattern.match(file_path.name)
        if match:
            base_name = match.group(1)
            chunks_by_base[base_name].append(file_path)

    # Merge each group
    for base_name, chunk_files in sorted(chunks_by_base.items()):
        # Sort chunks by chunk number
        chunk_files.sort(key=lambda p: int(re.search(r'_chunk(\d+)_', p.name).group(1)))

        output_file = text_dir / f"{base_name}__text.txt"

        print(f"  Merging {len(chunk_files)} chunks for: {base_name}")

        # Concatenate all chunks
        with open(output_file, 'w', encoding='utf-8') as outf:
            for chunk_file in chunk_files:
                with open(chunk_file, 'r', encoding='utf-8') as inf:
                    outf.write(inf.read())

        # Report results
        lines = sum(1 for _ in open(output_file, 'r', encoding='utf-8'))
        size_mb = output_file.stat().st_size / (1024 * 1024)
        print(f"    ✓ Created: {output_file.name} ({lines:,} lines, {size_mb:.2f} MB)")

    print()
    print(f"✓ Chunk merging complete! ({len(chunks_by_base)} sources merged)")
    print(f"  Combined files are in: {text_dir}")

if __name__ == '__main__':
    main()
