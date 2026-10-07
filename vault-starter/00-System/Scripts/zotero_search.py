#!/usr/bin/env python3
"""
Zotero Library Search
Second Brain - Academic Source Management

Search Zotero library by title, creator, year, DOI, tag, collection, or citation key.

Usage:
    python3 zotero_search.py "search query" [--vault-root PATH] [--limit N]

Examples:
    python3 zotero_search.py "state capacity"
    python3 zotero_search.py "Bernard Lewis" --limit 20
    python3 zotero_search.py "democracy" --vault-root /path/to/vault

Exit codes:
    0 - Search completed successfully
    1 - Search failed or no results
    2 - Configuration error
"""

import sys
import os
import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional
import hashlib

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


def search_items(base_url: str, query: str, timeout: int, limit: int) -> List[Dict]:
    """Search Zotero items using local API"""
    # Use /users/0/items endpoint with q parameter
    search_url = f"{base_url}/users/0/items"

    params = {
        'q': query,
        'limit': limit,
        'include': 'data',
    }

    try:
        response = requests.get(search_url, params=params, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Search failed: {e}", file=sys.stderr)
        return []


def get_item_attachments(base_url: str, item_key: str, timeout: int) -> List[Dict]:
    """Get child attachments for an item"""
    attachments_url = f"{base_url}/users/0/items/{item_key}/children"

    params = {
        'itemType': 'attachment',
    }

    try:
        response = requests.get(attachments_url, params=params, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return []


def check_duplicate_status(vault_root: Path, item_data: Dict, attachments: List[Dict]) -> Dict:
    """Check if item or its attachments already exist in Second Brain"""
    status = {
        'is_duplicate': False,
        'duplicate_type': None,
        'duplicate_location': None,
        'pdf_count': 0,
        'has_local_pdf': False,
    }

    # Count PDF attachments
    pdf_attachments = [a for a in attachments if a['data'].get('contentType') == 'application/pdf']
    status['pdf_count'] = len(pdf_attachments)

    # Check if any PDF is available locally
    for att in pdf_attachments:
        if 'path' in att['data'] or att['data'].get('linkMode') in ['linked_file', 'imported_file']:
            status['has_local_pdf'] = True
            break

    # Check for existing provenance manifests (indicates previous import)
    reports_dir = vault_root / "01-Library/Reports"
    if reports_dir.exists():
        item_key = item_data['key']

        for report_file in reports_dir.glob("*__zotero.md"):
            try:
                content = report_file.read_text(encoding='utf-8')
                if f"zotero_item_key: {item_key}" in content:
                    status['is_duplicate'] = True
                    status['duplicate_type'] = 'zotero_item_key'
                    status['duplicate_location'] = str(report_file)
                    return status
            except Exception:
                continue

    # Check DOI
    doi = item_data.get('DOI')
    if doi:
        # Simple check: search for DOI in existing reports
        for report_file in reports_dir.glob("*__*.md"):
            try:
                content = report_file.read_text(encoding='utf-8')
                if f"doi: {doi}" in content.lower() or doi.lower() in content.lower():
                    status['is_duplicate'] = True
                    status['duplicate_type'] = 'doi'
                    status['duplicate_location'] = str(report_file)
                    return status
            except Exception:
                continue

    return status


def format_creators(creators: List[Dict]) -> str:
    """Format creator list for display"""
    if not creators:
        return "Unknown"

    formatted = []
    for creator in creators[:3]:  # Show first 3
        if 'lastName' in creator:
            formatted.append(creator['lastName'])
        elif 'name' in creator:
            formatted.append(creator['name'])

    if len(creators) > 3:
        formatted.append("et al.")

    return ", ".join(formatted)


def print_result(item: Dict, attachments: List[Dict], duplicate_status: Dict, index: int):
    """Print a single search result"""
    data = item['data']

    print(f"\n{'='*80}")
    print(f"[{index}] {data.get('title', 'Untitled')}")
    print(f"{'='*80}")

    # Creators
    creators = data.get('creators', [])
    print(f"Creators: {format_creators(creators)}")

    # Year
    date = data.get('date', '')
    if date:
        year = date[:4] if len(date) >= 4 else date
        print(f"Year: {year}")

    # Item type
    item_type = data.get('itemType', 'unknown')
    print(f"Type: {item_type}")

    # DOI/ISBN
    doi = data.get('DOI')
    isbn = data.get('ISBN')
    if doi:
        print(f"DOI: {doi}")
    if isbn:
        print(f"ISBN: {isbn}")

    # Publication
    pub = data.get('publicationTitle') or data.get('publisher')
    if pub:
        print(f"Publication: {pub}")

    # Collections
    collections = data.get('collections', [])
    if collections:
        print(f"Collections: {len(collections)} collection(s)")

    # Tags
    tags = data.get('tags', [])
    if tags:
        tag_names = [t.get('tag', '') for t in tags[:5]]
        print(f"Tags: {', '.join(tag_names)}")
        if len(tags) > 5:
            print(f"      (+{len(tags) - 5} more)")

    # Attachments
    print(f"PDF Attachments: {duplicate_status['pdf_count']}")
    if duplicate_status['has_local_pdf']:
        print(f"Local PDF: ✓ Available")
    else:
        print(f"Local PDF: ✗ Not available (requires Zotero sync)")

    # Duplicate status
    if duplicate_status['is_duplicate']:
        print(f"\n⚠️  DUPLICATE DETECTED")
        print(f"    Type: {duplicate_status['duplicate_type']}")
        print(f"    Location: {duplicate_status['duplicate_location']}")
    else:
        print(f"\n✓ Not a duplicate (safe to import)")

    # Item key (for import)
    print(f"\nItem Key: {data['key']}")
    print(f"Import command: /zotero-sources import --item {data['key']}")


def main():
    parser = argparse.ArgumentParser(
        description="Search Zotero library for academic sources"
    )
    parser.add_argument(
        'query',
        help="Search query (title, creator, DOI, etc.)"
    )
    parser.add_argument(
        '--vault-root',
        type=Path,
        help="Path to Second Brain vault root (default: current directory)"
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=50,
        help="Maximum number of results (default: 50)"
    )

    args = parser.parse_args()
    vault_root = args.vault_root or Path.cwd()

    # Load config
    try:
        config = load_config(vault_root)
    except Exception as e:
        print(f"ERROR: Failed to load config: {e}", file=sys.stderr)
        return 2

    base_url = config['local_api']['base_url']
    timeout = config['local_api']['timeout_seconds']

    # Search
    print(f"Searching Zotero library for: '{args.query}'")
    print(f"Limit: {args.limit} results\n")

    items = search_items(base_url, args.query, timeout, args.limit)

    if not items:
        print("No results found.")
        return 1

    print(f"Found {len(items)} result(s)")

    # Display results
    for idx, item in enumerate(items, 1):
        # Get attachments
        attachments = get_item_attachments(base_url, item['data']['key'], timeout)

        # Check duplicate status
        duplicate_status = check_duplicate_status(vault_root, item['data'], attachments)

        # Print result
        print_result(item, attachments, duplicate_status, idx)

    # Summary
    print(f"\n{'='*80}")
    print(f"Total results: {len(items)}")

    duplicates = sum(
        1 for item in items
        if check_duplicate_status(
            vault_root,
            item['data'],
            get_item_attachments(base_url, item['data']['key'], timeout)
        )['is_duplicate']
    )

    if duplicates > 0:
        print(f"Duplicates: {duplicates} (already in Second Brain)")
        print(f"New sources: {len(items) - duplicates}")

    print(f"\nUse '/zotero-sources import --item <KEY>' to import a specific item")

    return 0


if __name__ == "__main__":
    sys.exit(main())
