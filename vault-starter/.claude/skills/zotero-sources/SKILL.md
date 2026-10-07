---
name: zotero-sources
description: Search, browse, and import academic sources from Zotero library with full provenance preservation
argument-hint: 'doctor | search <query> | collections | import --item <key> | import --collection <name> [--limit N]'
disable-model-invocation: false
---

# Zotero Sources Integration

## Purpose

This skill provides read-only access to your Zotero library, enabling you to:

- Search your entire Zotero collection
- Browse collections and items
- Import selected sources into Second Brain with full bibliographic provenance
- Automatically detect duplicates before import
- Hand off imported PDFs to the existing `/process-sources` workflow

## Commands

### `doctor`

Health check to verify Zotero connectivity and Second Brain readiness.

**Usage:**
```
/zotero-sources doctor
```

**Checks:**
- Vault root detected
- Zotero local API reachable (http://localhost:23119/api)
- API version 3 response
- Collections/items readable
- 05-Inbox writable
- /process-sources skill present
- Pipeline scripts compile
- No credentials stored in tracked files

### `search <query>`

Search your Zotero library by title, creator, year, DOI, tag, or collection.

**Usage:**
```
/zotero-sources search "state capacity"
/zotero-sources search "Bernard Lewis"
/zotero-sources search "democracy Islam"
```

**Output includes:**
- Item key
- Title
- Creators
- Year
- Item type
- DOI/ISBN (when available)
- Collections
- Tags
- Number of PDF attachments
- Attachment availability
- Second Brain duplicate status

**Does NOT automatically import** - search is read-only.

### `collections`

List all Zotero collections with item counts.

**Usage:**
```
/zotero-sources collections
```

**Output includes:**
- Collection name
- Item count
- Subcollection count
- Collection key
- Project mapping status (if configured)

### `import --item <key>`

Import a specific Zotero item by its item key.

**Usage:**
```
/zotero-sources import --item ABCD1234
```

**Workflow:**
1. Retrieve item metadata from Zotero
2. Identify PDF attachments
3. Handle zero, one, or multiple PDFs (requires selection if multiple)
4. Check for duplicates (SHA-256, DOI, ISBN, item key)
5. Copy selected PDF to 05-Inbox/
6. Create Zotero provenance manifest in 01-Library/Reports/
7. Report readiness for /process-sources

**Safety:**
- Will NOT overwrite existing originals
- Will NOT import if duplicate detected (unless --force flag added later)
- Will NOT modify Zotero data
- Verifies SHA-256 before and after copying

### `import --collection <name> [--limit N]`

Import items from a Zotero collection.

**Usage:**
```
/zotero-sources import --collection "Peace and War"
/zotero-sources import --collection "Peace and War" --limit 10
```

**Workflow:**
1. List all items in collection
2. For each item (up to limit):
   - Check duplicate status
   - Present import plan
3. Request confirmation before proceeding
4. Import approved items sequentially
5. Create provenance manifests
6. Report readiness for /process-sources

**Safety:**
- Requires explicit confirmation before batch import
- Skips items without PDF attachments (reports them)
- Skips duplicates (reports them)
- Never imports entire library by default

## Architecture

### Integration Mode

**Phase 1 (Current):** Local API only
- Read-only access via http://localhost:23119/api
- Requires Zotero desktop running
- No API keys needed
- No remote sync required

**Phase 2 (Future):** Optional Better BibTeX fallback
- Auto-export CSL JSON support
- Enhanced citation key support

### Data Flow

```
Zotero Item
→ Resolve metadata via Local API
→ Resolve child PDF attachment
→ Verify attachment local availability
→ Compute SHA-256
→ Check Second Brain duplicates (Originals, Inbox, Wiki)
→ Create Zotero provenance manifest (01-Library/Reports/)
→ Copy selected PDF to 05-Inbox/
→ Hand off to /process-sources
→ Neutral wiki ingestion (02-Wiki/)
→ Optional project mapping (03-Projects/)
```

### Provenance Preservation

Each imported source receives a Zotero provenance manifest:

**Location:** `01-Library/Reports/FILENAME__zotero.md`

**Contains:**
- Zotero library ID, item key, attachment key
- Collection keys and names
- Tags
- Citation key (if available)
- Item type (journalArticle, book, etc.)
- Title, creators, date, publisher
- DOI, ISBN, URL
- Attachment filename and MIME type
- Source SHA-256
- Import timestamp
- Integration mode (local-api)

### Duplicate Detection

Before importing, checks:

1. SHA-256 hash (identical file already in Originals)
2. Zotero item key (already imported from Zotero)
3. Zotero attachment key (specific PDF already imported)
4. DOI (same scholarly work, possibly different edition)
5. ISBN (same book, possibly different file)
6. Normalized title + creator + year

**Behavior:**
- Same hash in Originals → REJECT (no duplicate)
- Same DOI but different hash → WARN (possible edition/version conflict)
- Same title but different DOI/ISBN → ALLOW (not assumed duplicate)

### Project Mapping

**Optional** mapping from Zotero collections/tags to 03-Projects/ directories.

Configured in `00-System/Config/zotero-integration.yml`:

```yaml
project_mappings:
  collections:
    "My Collection": "My-Project"
  tags:
    "project:my-project": "My-Project"
```

**Execution order:**
1. Import from Zotero
2. Neutral processing and wiki ingestion (02-Wiki/)
3. THEN apply project mapping (03-Projects/)

**Prevents:**
- Contaminating neutral wiki with project-specific interpretation
- Rewriting source-bounded notes to match project thesis

## Safety Guarantees

This skill will NEVER:

- Write to Zotero (create, edit, delete items/collections/tags)
- Modify Zotero attachments (rename, move, delete)
- Access Zotero SQLite database directly
- Store API keys in Git-tracked files
- Import entire library automatically (requires explicit selection)
- Overwrite existing Second Brain originals
- Modify /process-sources behavior
- Create project interpretation in neutral wiki

## Configuration

See: `00-System/Config/zotero-integration.yml`

## Scripts

- `00-System/Scripts/zotero_doctor.py` - Health check
- `00-System/Scripts/zotero_search.py` - Search library
- `00-System/Scripts/zotero_import.py` - Import orchestration

## Dependencies

- Zotero desktop application (running)
- Local API enabled in Zotero preferences
- Python 3.11+ with requests library
- Existing /process-sources skill
- Existing source pipeline scripts

## Workflow Example

```bash
# 1. Health check
/zotero-sources doctor

# 2. Browse collections
/zotero-sources collections

# 3. Search for specific topic
/zotero-sources search "peace treaty"

# 4. Import specific item
/zotero-sources import --item ABCD1234

# 5. Process imported PDF
/process-sources 05-Inbox

# 6. Verify imported source reached neutral wiki
cat index.md
```

## Integration with CLAUDE.md Workflows

- `inspect raw` - Works on 05-Inbox/ after Zotero import
- `approved, ingest` - Processes Zotero-imported sources
- `query vault` - Can query imported Zotero sources
- `lint wiki` - Checks Zotero-imported pages

## Handoff Documentation

See: `ZOTERO-INTEGRATION-HANDOFF.md` for complete technical specification.

See: `00-System/Zotero/README.md` for user-facing documentation.

## Status

**Phase 1 (Current):** Read-only local API integration
- Commands: doctor, search, collections, import
- Provenance: Full metadata preservation
- Safety: Read-only, explicit selection, duplicate detection
- Handoff: /process-sources workflow

**Phase 2 (Future):** Enhanced features
- Better BibTeX CSL JSON fallback
- Group library support
- Enhanced citation key handling
- Batch import optimizations
