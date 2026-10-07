#!/bin/bash
# Split large PDFs into smaller chunks using qpdf
#
# Usage:
#   ./split-pdf-qpdf.sh "path/to/file.pdf" [chunk_size] [output_dir]
#
# Arguments:
#   file.pdf     - Input PDF file
#   chunk_size   - Pages per chunk (default: 100)
#   output_dir   - Output directory (default: input_dir/filename_chunks)

set -e

if [ $# -lt 1 ]; then
    echo "Usage: $0 <input.pdf> [chunk_size] [output_dir]"
    exit 1
fi

INPUT_PDF="$1"
CHUNK_SIZE="${2:-100}"
BASENAME=$(basename "$INPUT_PDF" .pdf)
INPUT_DIR=$(dirname "$INPUT_PDF")
OUTPUT_DIR="${3:-$INPUT_DIR/${BASENAME}_chunks}"

# Check if input file exists
if [ ! -f "$INPUT_PDF" ]; then
    echo "✗ Error: File not found: $INPUT_PDF"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Get total number of pages
TOTAL_PAGES=$(qpdf --show-npages "$INPUT_PDF")

echo "Splitting: $BASENAME.pdf"
echo "  Total pages: $TOTAL_PAGES"
echo "  Chunk size: $CHUNK_SIZE pages"
echo "  Output directory: $OUTPUT_DIR"
echo ""

# Calculate number of chunks
NUM_CHUNKS=$(( ($TOTAL_PAGES + $CHUNK_SIZE - 1) / $CHUNK_SIZE ))

# Split into chunks
for ((i=0; i<$NUM_CHUNKS; i++)); do
    START_PAGE=$(( $i * $CHUNK_SIZE + 1 ))
    END_PAGE=$(( ($i + 1) * $CHUNK_SIZE ))

    if [ $END_PAGE -gt $TOTAL_PAGES ]; then
        END_PAGE=$TOTAL_PAGES
    fi

    CHUNK_NUM=$(printf "%02d" $(($i + 1)))
    OUTPUT_FILE="${OUTPUT_DIR}/${BASENAME}_chunk${CHUNK_NUM}_p$(printf '%04d' $START_PAGE)-$(printf '%04d' $END_PAGE).pdf"

    qpdf "$INPUT_PDF" --pages . $START_PAGE-$END_PAGE -- "$OUTPUT_FILE"

    ACTUAL_PAGES=$(( $END_PAGE - $START_PAGE + 1 ))
    echo "  ✓ Created chunk $(($i + 1))/$NUM_CHUNKS: $(basename "$OUTPUT_FILE") ($ACTUAL_PAGES pages)"
done

echo ""
echo "✓ Successfully split into $NUM_CHUNKS chunks"
echo "  Output directory: $OUTPUT_DIR"
