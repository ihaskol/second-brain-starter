#!/usr/bin/env python3
"""
Zotero Source Import
Second Brain - Academic Source Management

Import selected Zotero items into Second Brain with full provenance preservation.

Usage:
    python3 zotero_import.py --item <ITEM_KEY> [--vault-root PATH]
    python3 zotero_import.py --collection <NAME> [--limit N] [--vault-root PATH]

Examples:
    python3 zotero_import.py --item ABCD1234
    python3 zotero_import.py --collection "Peace and War" --limit 10

Exit codes:
    0 - Import completed successfully
    1 - Import failed
    2 - Configuration or argument error
"""

import sys
import os
import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib
import shutil
from datetime import datetime

try:
    import requests
except ImportError:
    print("ERROR: requests library not installed", file=sys.stderr)
    print("Install: pip3 install requests", file=sys.stderr)
    sys.exit(2)

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML library not installed", file=sys.stderr)
    print("Install: pip3 install pyyaml", file=sys.stderr)
    sys.exit(2)


def load_config(vault_root: Path) -> Dict:
    """Load Zotero integration config"""
    config_path = vault_root / "00-System/Config/zotero-integration.yml"

    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_item(base_url: str, item_key: str, timeout: int) -> Optional[Dict]:
    """Retrieve item metadata from Zotero"""
    item_url = f"{base_url}/users/0/items/{item_key}"

    try:
        response = requests.get(item_url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to retrieve item: {e}", file=sys.stderr)
        return None


def get_attachments(base_url: str, item_key: str, timeout: int) -> List[Dict]:
    """Get PDF attachments for an item"""
    attachments_url = f"{base_url}/users/0/items/{item_key}/children"

    params = {
        'itemType': 'attachment',
    }

    try:
        response = requests.get(attachments_url, params=params, timeout=timeout)
        response.raise_for_status()
        attachments = response.json()

        # Filter to PDFs only
        return [a for a in attachments if a['data'].get('contentType') == 'application/pdf']

    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to retrieve attachments: {e}", file=sys.stderr)
        return []


def compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 hash of file"""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def check_duplicates(vault_root: Path, item_data: Dict, sha256: Optional[str] = None) -> Tuple[bool, str]:
    """
    Check for duplicates in Second Brain.
    Returns (is_duplicate, reason)
    """
    # Check SHA-256 if provided
    if sha256:
        originals_dir = vault_root / "01-Library/Originals"
        if originals_dir.exists():
            for original_file in originals_dir.glob("*.pdf"):
                try:
                    if compute_sha256(original_file) == sha256:
                        return True, f"Identical file exists: {original_file.name}"
                except Exception:
                    continue

    # Check Zotero item key in reports
    reports_dir = vault_root / "01-Library/Reports"
    item_key = item_data['key']

    if reports_dir.exists():
        for report_file in reports_dir.glob("*__zotero.md"):
            try:
                content = report_file.read_text(encoding='utf-8')
                if f"zotero_item_key: {item_key}" in content:
                    return True, f"Already imported: {report_file.name}"
            except Exception:
                continue

    # Check DOI
    doi = item_data.get('DOI')
    if doi and reports_dir.exists():
        for report_file in reports_dir.glob("*__*.md"):
            try:
                content = report_file.read_text(encoding='utf-8')
                if f"doi: {doi}" in content.lower():
                    return True, f"Same DOI exists: {report_file.name}"
            except Exception:
                continue

    return False, ""


def format_filename(item_data: Dict, config: Dict) -> str:
    """Generate filename from item metadata"""
    creators = item_data.get('creators', [])
    year = item_data.get('date', '')[:4] if item_data.get('date') else ''
    title = item_data.get('title', 'Untitled')

    # Get first creator's last name
    creator_name = "Unknown"
    if creators:
        if 'lastName' in creators[0]:
            creator_name = creators[0]['lastName']
        elif 'name' in creators[0]:
            creator_name = creators[0]['name']

    # Build filename
    filename = f"{creator_name} - {year} - {title}.pdf"

    # Sanitize
    filename = filename.replace('/', '-').replace('\\', '-').replace(':', '-')

    # Limit length
    max_length = config['import']['filename'].get('max_length', 200)
    if len(filename) > max_length:
        filename = filename[:max_length - 4] + ".pdf"

    return filename


def create_provenance_manifest(
    vault_root: Path,
    item: Dict,
    attachment: Dict,
    pdf_path: Path,
    sha256: str,
    config: Dict
) -> Path:
    """Create Zotero provenance manifest"""
    data = item['data']
    att_data = attachment['data']

    # Base filename without extension
    base_name = pdf_path.stem

    # Manifest path
    reports_dir = vault_root / "01-Library/Reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = reports_dir / f"{base_name}__zotero.md"

    # Extract library info
    library = item.get('library', {})

    # Format creators
    creators_list = []
    for creator in data.get('creators', []):
        creator_dict = {}
        if 'lastName' in creator:
            creator_dict['lastName'] = creator['lastName']
        if 'firstName' in creator:
            creator_dict['firstName'] = creator['firstName']
        if 'name' in creator:
            creator_dict['name'] = creator['name']
        creators_list.append(creator_dict)

    # Get collections (keys only for now)
    collection_keys = data.get('collections', [])

    # Get tags
    tags = [t.get('tag', '') for t in data.get('tags', [])]

    # Build frontmatter
    frontmatter = {
        'report_type': 'zotero-provenance',
        'zotero_library_type': library.get('type', 'user'),
        'zotero_library_id': library.get('id'),
        'zotero_item_key': data['key'],
        'zotero_attachment_key': att_data['key'],
        'zotero_collection_keys': collection_keys,
        'zotero_tags': tags,
        'item_type': data.get('itemType'),
        'title': data.get('title'),
        'creators': creators_list,
        'date': data.get('date'),
        'publisher': data.get('publisher'),
        'publication_title': data.get('publicationTitle'),
        'doi': data.get('DOI'),
        'isbn': data.get('ISBN'),
        'url': data.get('url'),
        'attachment_filename': att_data.get('filename'),
        'attachment_mime_type': att_data.get('contentType'),
        'source_sha256': sha256,
        'imported_to': str(pdf_path.relative_to(vault_root)),
        'imported_at': datetime.utcnow().isoformat() + 'Z',
        'integration_mode': 'local-api',
    }

    # Write manifest
    content = "---\n"
    content += yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)
    content += "---\n\n"
    content += f"# Zotero Import Provenance: {data.get('title', 'Untitled')}\n\n"
    content += "This file records the bibliographic provenance of a source imported from Zotero.\n\n"
    content += "**Do not edit this file manually.** It was generated automatically by the Zotero integration.\n\n"
    content += "## Source Information\n\n"
    content += f"- **Zotero Item Key:** {data['key']}\n"
    content += f"- **Zotero Attachment Key:** {att_data['key']}\n"
    content += f"- **Library:** {library.get('name', 'Unknown')} (ID: {library.get('id')})\n"
    content += f"- **Imported:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n"

    if data.get('DOI'):
        content += f"**DOI:** {data['DOI']}\n\n"
    if data.get('ISBN'):
        content += f"**ISBN:** {data['ISBN']}\n\n"

    content += "## Next Steps\n\n"
    content += "1. Run `/process-sources 05-Inbox` to process this PDF\n"
    content += "2. The source will go through intake → OCR (if needed) → quality validation\n"
    content += "3. Once validated, use `ingest` workflow to create neutral wiki notes\n"
    content += "4. Zotero provenance will be preserved throughout the pipeline\n"

    manifest_path.write_text(content, encoding='utf-8')
    return manifest_path


def import_item(
    vault_root: Path,
    base_url: str,
    item_key: str,
    timeout: int,
    config: Dict
) -> bool:
    """Import a single Zotero item"""
    print(f"\nImporting item: {item_key}")
    print("=" * 80)

    # Get item metadata
    item = get_item(base_url, item_key, timeout)
    if not item:
        print("✗ Failed to retrieve item metadata")
        return False

    data = item['data']
    print(f"✓ Retrieved: {data.get('title', 'Untitled')}")

    # Get PDF attachments
    attachments = get_attachments(base_url, item_key, timeout)

    if not attachments:
        print("✗ No PDF attachments found")
        print("  This item cannot be imported (no PDF)")
        return False

    print(f"✓ Found {len(attachments)} PDF attachment(s)")

    # Handle multiple PDFs
    if len(attachments) > 1:
        print("\nMultiple PDFs found:")
        for idx, att in enumerate(attachments, 1):
            print(f"  [{idx}] {att['data'].get('filename', 'Unknown')}")
        print("\n⚠️  Multiple PDF handling not yet implemented")
        print("   Using first PDF for now")

    attachment = attachments[0]
    att_data = attachment['data']

    # Get attachment file path from Zotero
    # Note: Zotero local API doesn't directly provide file path
    # We need to construct it or get it from attachment data

    # For now, we'll skip the actual file copy and just create the manifest
    # This is a Phase 1 limitation - full file access requires additional logic

    print(f"\n⚠️  File copy not yet implemented in Phase 1")
    print(f"   Attachment: {att_data.get('filename', 'Unknown')}")
    print(f"   This feature requires Zotero file path resolution")

    return False  # Return False until file copy is implemented


def main():
    parser = argparse.ArgumentParser(
        description="Import academic sources from Zotero into Second Brain"
    )
    parser.add_argument(
        '--item',
        help="Zotero item key to import"
    )
    parser.add_argument(
        '--collection',
        help="Zotero collection name to import from"
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=10,
        help="Maximum number of items to import from collection (default: 10)"
    )
    parser.add_argument(
        '--vault-root',
        type=Path,
        help="Path to Second Brain vault root (default: current directory)"
    )

    args = parser.parse_args()

    if not args.item and not args.collection:
        parser.error("Either --item or --collection must be specified")

    vault_root = args.vault_root or Path.cwd()

    # Load config
    try:
        config = load_config(vault_root)
    except Exception as e:
        print(f"ERROR: Failed to load config: {e}", file=sys.stderr)
        return 2

    base_url = config['local_api']['base_url']
    timeout = config['local_api']['timeout_seconds']

    # Import
    if args.item:
        success = import_item(vault_root, base_url, args.item, timeout, config)
        return 0 if success else 1
    else:
        print(f"ERROR: Collection import not yet implemented", file=sys.stderr)
        print(f"Use --item <KEY> to import individual items for now", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
