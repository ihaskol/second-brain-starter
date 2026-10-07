#!/usr/bin/env python3
"""
Queue all unprocessed chunk files for OCR.
"""

import os
import subprocess
from pathlib import Path

vault_root = Path(__file__).resolve().parents[2]  # vault root
originals_dir = vault_root / "01-Library/Originals"
text_dir = vault_root / "01-Library/Text"

# Find all chunk directories
chunk_dirs = sorted([d for d in originals_dir.glob("*_chunks") if d.is_dir()])

print(f"Found {len(chunk_dirs)} chunk directories\n")

queued_count = 0

for chunk_dir in chunk_dirs:
    source_name = chunk_dir.name.replace("_chunks", "")
    chunks = sorted(chunk_dir.glob("*.pdf"))

    print(f"Processing {source_name}: {len(chunks)} chunks")

    for chunk_pdf in chunks:
        chunk_base = chunk_pdf.stem
        text_file = text_dir / f"{chunk_base}__text.txt"

        if not text_file.exists():
            # Queue this chunk for OCR
            log_file = f"/tmp/ocr_{chunk_base}.log"
            cmd = [
                "python3",
                str(vault_root / "00-System/Scripts/process-source.py"),
                "--file", str(chunk_pdf),
                "--vault-root", str(vault_root),
                "--lang", "ara"
            ]

            with open(log_file, 'w') as log:
                subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, cwd=str(vault_root))

            queued_count += 1
            print(f"  ✓ Queued: {chunk_base}")
        else:
            print(f"  - Skip (exists): {chunk_base}")

    print()

print(f"\n✓ Queued {queued_count} chunks for OCR processing")
