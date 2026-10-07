# Zotero Integration for Second Brain

## Overview

This directory contains Zotero integration resources for the Second Brain vault. The integration provides read-only access to your Zotero library, enabling you to search, browse, and selectively import academic sources with full bibliographic provenance preservation.

## Quick Start

### 1. Ensure Zotero Local API is Enabled

1. Open Zotero desktop application
2. Go to **Edit → Preferences** (or **Zotero → Preferences** on Mac)
3. Navigate to **Advanced → General**
4. Check: **"Allow other applications on this computer to communicate with Zotero"**
5. Restart Zotero if needed

### 2. Run Health Check

```bash
/zotero-sources doctor
```

This will verify:
- Zotero API connectivity
- Vault structure
- Required scripts
- Python dependencies

### 3. Browse Your Library

List all collections:
```bash
/zotero-sources collections
```

Search for sources:
```bash
/zotero-sources search "democracy Islam"
/zotero-sources search "Bernard Lewis"
```

### 4. Import a Source

```bash
/zotero-sources import --item <ITEM_KEY>
```

The item key is shown in search results.

### 5. Process Imported PDF

After import, the PDF will be in `05-Inbox/`. Process it:

```bash
/process-sources 05-Inbox
```

This will run the standard source pipeline (intake → OCR if needed → quality validation).

### 6. Ingest Into Wiki

Once validated, create neutral wiki notes:

```bash
ingest this
```

## Integration Architecture

### Data Flow

```
Zotero Library (Local API)
    ↓
Search/Browse
    ↓
Select Item
    ↓
Duplicate Check (SHA-256, DOI, ISBN, Item Key)
    ↓
Copy PDF to 05-Inbox/
    ↓
Create Provenance Manifest (01-Library/Reports/)
    ↓
Hand Off to /process-sources
    ↓
Intake → OCR → Quality Validation
    ↓
Neutral Wiki Ingestion (02-Wiki/)
    ↓
Optional Project Mapping (03-Projects/)
```

### File Locations

- **Configuration:** `00-System/Config/zotero-integration.yml`
- **Scripts:** `00-System/Scripts/zotero_*.py`
- **Skill Definition:** `.claude/skills/zotero-sources/SKILL.md`
- **Provenance Manifests:** `01-Library/Reports/*__zotero.md`
- **Imported PDFs:** `05-Inbox/` → `01-Library/Originals/`

### Provenance Preservation

Each imported source receives a Zotero provenance manifest in `01-Library/Reports/`:

**Filename:** `FILENAME__zotero.md`

**Contains:**
- Zotero library ID, item key, attachment key
- Collections, tags, citation key
- Title, creators, date, publisher
- DOI, ISBN, URL
- SHA-256 hash
- Import timestamp

This ensures full traceability from Zotero → Second Brain → Wiki → Projects.

## Commands

### `/zotero-sources doctor`

**Health check to verify Zotero connectivity.**

Checks:
- Vault structure
- Zotero local API reachable
- Collections/items readable
- 05-Inbox writable
- /process-sources skill present
- Pipeline scripts compile
- No credentials in Git

**Usage:**
```bash
/zotero-sources doctor
```

### `/zotero-sources search <query>`

**Search Zotero library by title, creator, DOI, tag, etc.**

**Usage:**
```bash
/zotero-sources search "state capacity"
/zotero-sources search "Bernard Lewis"
```

**Output:**
- Item key (for import)
- Title, creators, year
- DOI, ISBN, publication
- Collections, tags
- PDF attachment count
- Duplicate status

### `/zotero-sources collections`

**List all Zotero collections with item counts.**

**Usage:**
```bash
/zotero-sources collections
```

**Output:**
- Collection name
- Item count
- Subcollection count
- Project mapping status

### `/zotero-sources import --item <key>`

**Import a specific Zotero item.**

**Usage:**
```bash
/zotero-sources import --item ABCD1234
```

**Workflow:**
1. Retrieve metadata
2. Identify PDF attachments
3. Check duplicates
4. Copy PDF to 05-Inbox/
5. Create provenance manifest
6. Report readiness for /process-sources

**Safety:**
- Will NOT overwrite existing sources
- Will NOT import duplicates
- Will NOT modify Zotero data

### `/zotero-sources import --collection <name>`

**Import items from a collection (future enhancement).**

**Usage:**
```bash
/zotero-sources import --collection "Peace and War" --limit 10
```

**Status:** Not yet fully implemented in Phase 1.

## Configuration

### `00-System/Config/zotero-integration.yml`

Key settings:

```yaml
integration_mode: local-api

local_api:
  base_url: "http://localhost:23119/api"
  api_version: 3
  library_id: YOUR_ZOTERO_LIBRARY_ID  # run 00-System/Scripts/zotero_doctor.py to detect it

project_mappings:
  collections:
    "My Collection": "My-Project"
```

### Project Mappings

**Optional** mapping from Zotero collections/tags to Second Brain projects.

**Important:** Mappings are applied AFTER neutral wiki ingestion to preserve source-bounded separation.

**Order:**
1. Import from Zotero
2. Process through pipeline (intake → OCR → quality)
3. Create neutral wiki notes (02-Wiki/)
4. **THEN** apply project mapping (03-Projects/)

This prevents contaminating neutral wiki pages with project-specific interpretation.

## Duplicate Detection

Before importing, the system checks:

1. **SHA-256 hash** - Identical file already in `01-Library/Originals`
2. **Zotero item key** - Already imported from Zotero
3. **Zotero attachment key** - Specific PDF already imported
4. **DOI** - Same scholarly work (warns if different hash)
5. **ISBN** - Same book (warns if different file)
6. **Normalized title + creator + year** - Fuzzy match

**Behavior:**
- **Same hash in Originals** → REJECT (no duplicate storage)
- **Same DOI but different hash** → WARN (possible edition/version conflict)
- **Same title but different DOI** → ALLOW (not assumed duplicate)

## Safety Guarantees

This integration will **NEVER**:

- Write to Zotero (create, edit, delete items/collections/tags)
- Modify Zotero attachments (rename, move, delete)
- Access Zotero SQLite database directly
- Store API keys in Git-tracked files
- Import entire library automatically
- Overwrite existing Second Brain originals
- Create project interpretation in neutral wiki

**Read-only by design.**

## Workflow Example

```bash
# 1. Health check
/zotero-sources doctor

# 2. Search for topic
/zotero-sources search "Hudaybiya treaty"

# Output shows:
# [1] The Life of Muhammad - Ibn Ishaq
#     Item Key: ABCD1234
#     PDF Attachments: 1
#     ✓ Not a duplicate

# 3. Import item
/zotero-sources import --item ABCD1234

# 4. Process imported PDF
/process-sources 05-Inbox

# 5. Review quality report
cat 01-Library/Reports/Ibn Ishaq - 1997__quality.md

# 6. If quality_status: passed, ingest
ingest this

# 7. Verify wiki page created
cat 02-Wiki/ibn-ishaq-1997-life-of-muhammad.md

# 8. Check provenance preserved
cat 01-Library/Reports/Ibn Ishaq - 1997__zotero.md
```

## Integration with CLAUDE.md Workflows

- **`inspect raw`** - Works on Zotero-imported PDFs in `05-Inbox/`
- **`approved, ingest`** - Processes Zotero sources through standard pipeline
- **`query vault`** - Can query imported Zotero sources
- **`lint wiki`** - Checks Zotero-imported pages for integrity

## Current Limitations (Phase 1)

1. **File copy not fully implemented** - Manual copy required for now
2. **Collection import incomplete** - Use `--item` for individual imports
3. **Better BibTeX not integrated** - Local API only
4. **Group libraries not supported** - User library only
5. **Attachment path resolution** - Requires additional Zotero API work

These will be addressed in future phases.

## Troubleshooting

### "Local API is not enabled"

**Solution:**
1. Open Zotero → Preferences → Advanced
2. Enable "Allow other applications to communicate"
3. Restart Zotero

### "Cannot connect to Zotero local API"

**Check:**
- Is Zotero desktop running?
- Is the local API enabled?
- Try: `curl "http://localhost:23119/api/"`

### "No PDF attachments found"

**Causes:**
- Item has no PDF attached in Zotero
- PDF not synced locally (cloud-only storage)

**Solution:**
- Attach PDF in Zotero
- Or sync PDFs locally if using Zotero Storage

### "Duplicate detected"

**Explanation:**
The source (or a version of it) already exists in Second Brain.

**Options:**
- Skip import (use existing version)
- Review existing source to confirm it's the same
- If different edition/version, manually review before importing

## Support and Documentation

- **Skill definition:** `.claude/skills/zotero-sources/SKILL.md`
- **Configuration:** `00-System/Config/zotero-integration.yml`
- **Technical handoff:** `ZOTERO-INTEGRATION-HANDOFF.md`
- **Source pipeline:** `00-System/Source-Pipeline.md`
- **Research protocol:** `RESEARCH_PROTOCOL.md`
- **Vault workflows:** `CLAUDE.md`

## Future Enhancements (Phase 2+)

- Better BibTeX CSL JSON fallback
- Full file path resolution and automatic copy
- Collection batch import
- Group library support
- Enhanced citation key handling
- Zotero note import
- Annotation import
- Bidirectional sync (wiki → Zotero tags/notes)

## Status

**Current Phase:** Phase 1 - Read-only local API integration

**Working:**
- Health checks (`doctor`)
- Library search (`search`)
- Collection browsing (`collections`)
- Duplicate detection
- Provenance manifest creation

**In Progress:**
- File copy automation (`import`)
- Collection batch import

**Planned:**
- Better BibTeX integration
- Group libraries
- Advanced features

---

**Last Updated:** 2026-07-19

**Integration Mode:** local-api (read-only)

**Vault:** Second Brain - Academic Research Knowledge Base
