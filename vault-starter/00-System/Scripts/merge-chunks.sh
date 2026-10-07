#!/bin/bash
# Merge chunk text files back into complete source files

VAULT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TEXT_DIR="$VAULT_ROOT/01-Library/Text"

echo "Merging chunk files into complete source texts..."

# Function to merge chunks for a given base name
merge_chunks() {
    local base_name="$1"
    local output_file="$TEXT_DIR/${base_name}__text.txt"
    local temp_file="/tmp/merge_${base_name}.txt"
    
    # Find all chunks for this base, sorted by chunk number
    chunks=$(find "$TEXT_DIR" -name "${base_name}_chunk*__text.txt" | sort -V)
    
    if [ -z "$chunks" ]; then
        return
    fi
    
    chunk_count=$(echo "$chunks" | wc -l | tr -d ' ')
    echo "  Merging $chunk_count chunks for: $base_name"
    
    # Clear temp file
    > "$temp_file"
    
    # Concatenate all chunks
    for chunk_file in $chunks; do
        cat "$chunk_file" >> "$temp_file"
    done
    
    # Move to final location
    mv "$temp_file" "$output_file"
    
    # Count lines
    lines=$(wc -l < "$output_file" | tr -d ' ')
    size=$(ls -lh "$output_file" | awk '{print $5}')
    echo "    ✓ Created: $output_file ($lines lines, $size)"
}

# Process each PDF that has chunks
for base in "02-0085" "03-0086" "04-0087" "05-0088" "06-0089" "09-0092" "10-0093" "11-0094" "إمتاع الأسماع-المقريزي - ت محمود شاكر"; do
    merge_chunks "$base"
done

echo ""
echo "✓ Chunk merging complete!"
echo "  Combined files are in: $TEXT_DIR"
