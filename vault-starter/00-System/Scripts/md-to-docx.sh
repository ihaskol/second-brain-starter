#!/bin/bash
# md-to-docx.sh — convert Markdown deliverables to Word (.docx) with the vault's
# standard styling: Times New Roman, table of contents, English.
#
# Standards enforced (see memory: output-language-and-formatting):
#   - Times New Roman on all styles (via _reference-times-new-roman.docx)
#   - -V lang=en
#   - --toc --toc-depth=2
#
# Usage:
#   00-System/Scripts/md-to-docx.sh file1.md [file2.md ...]        # one .docx per file
#   00-System/Scripts/md-to-docx.sh --combined out.docx a.md b.md  # one combined .docx
#   00-System/Scripts/md-to-docx.sh --dir path/to/folder           # every *.md in the folder
#
# Requires: pandoc.
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REF="$SCRIPT_DIR/_reference-times-new-roman.docx"
COMMON=(--from=gfm --to=docx --reference-doc="$REF" --toc --toc-depth=2 -V lang=en)

if [ "$1" = "--combined" ]; then
  shift; OUT="$1"; shift
  pandoc "$@" -o "$OUT" "${COMMON[@]}" --metadata title="$(basename "${OUT%.docx}")"
  echo "built $OUT"
  exit 0
fi

if [ "$1" = "--dir" ]; then
  cd "$2"
  for f in *.md; do
    [ -f "$f" ] || continue
    pandoc "$f" -o "${f%.md}.docx" "${COMMON[@]}" --metadata title="${f%.md}"
    echo "built ${f%.md}.docx"
  done
  exit 0
fi

for f in "$@"; do
  [ -f "$f" ] || { echo "skip (not found): $f"; continue; }
  pandoc "$f" -o "${f%.md}.docx" "${COMMON[@]}" --metadata title="$(basename "${f%.md}")"
  echo "built ${f%.md}.docx"
done
