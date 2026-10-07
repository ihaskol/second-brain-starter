# Source Processing Pipeline

## Purpose

This document defines the vault-level source processing pipeline for converting PDF sources into searchable, quality-validated text suitable for research ingestion.

The pipeline is vault-level infrastructure, reusable by all current and future projects.

For research-integrity rules (citations, quotations, evidence standards), see `RESEARCH_PROTOCOL.md`.

For ingestion workflow (creating wiki notes from validated sources), see `CLAUDE.md`.

---

## Seven-Stage Source Lifecycle

Sources move through seven stages from acquisition to project use:

**Stage 0: Acquisition**
- Location: `05-Inbox/` (temporary staging)
- Status: Unvalidated, unprocessed
- Action: Manual download/transfer to vault

**Stage 1: Intake Review**
- Location: `05-Inbox/` or `01-Library/Originals/`
- Tool: `inspect-pdf.py`
- Output: Intake report (`01-Library/Reports/*__intake.md`)
- Decision: ACCEPT / REQUEST BETTER COPY / HOLD FOR MANUAL REVIEW

**Stage 2: Format Preparation**
- Location: `01-Library/Originals/` (immutable storage)
- Tool: `process-source.py`
- Output: OCR PDF (`01-Library/OCR/*__ocr.pdf`) if needed
- Output: Text with page markers (`01-Library/Text/*__text.txt`)

**Stage 3: Quality Review**
- Location: `01-Library/Text/`
- Tool: `validate-text.py`
- Output: Quality report (`01-Library/Reports/*__quality.md`)
- Status: `quality_status: passed | usable-with-review | failed`

**Stage 4: Neutral Ingestion**
- Location: `02-Wiki/` (atomic knowledge pages)
- Tool: `ingest` workflow (defined in `CLAUDE.md`)
- Status: `research_status: inspected | partially-ingested | fully-ingested`

**Stage 5: Verification**
- Location: `02-Wiki/` and `01-Library/Text/`
- Tool: Manual verification against original source
- Status: `research_status: verified` (on wiki page)
- Status: `status: reviewed` (on wiki page frontmatter)

**Stage 6: Project Use**
- Location: `03-Projects/*/` (project-specific usage)
- Constraint: Project-specific verification requirements apply
- Example: Chapter 4 requires NotebookLM quotation verification

---

## File Naming Conventions

### Source PDFs

Original PDFs use standard academic citation format:

```
Author - Year - Title.pdf
```

Example: `Lewis - 1996 - The Middle East.pdf`

### Generated Files

Pipeline-generated files use suffixes to indicate processing stage:

**OCR Output:**
```
Author - Year - Title__ocr.pdf
```
Location: `01-Library/OCR/`

**Canonical Text Output (with page markers):**
```
Author - Year - Title__text.txt
```
Location: `01-Library/Text/`

**Intake Report:**
```
Author - Year - Title__intake.md
```
Location: `01-Library/Reports/`

**Quality Report:**
```
Author - Year - Title__quality.md
```
Location: `01-Library/Reports/`

**Completion Manifest:**
```
Author - Year - Title__completion.md
```
Location: `01-Library/Processed/` (created when source fully ingested)

### Legacy Compatibility

Existing files without suffixes remain unchanged. The pipeline does not rename or move legacy files.

Examples of legacy files:
- `01-Library/Processed/Lewis - 1996 - The Middle East.pdf`
- `01-Library/Text/khel-1980-siyar.txt`

New files created from legacy sources will use the standard naming convention.

**Legacy TXT Representation Handling:**

The pipeline implements four-case decision logic for text representations:

**Case A: Neither file exists**
- Generates `source__text.txt` as canonical pipeline output

**Case B: Only `source.txt` exists (Legacy Mode)**
- Treats as legacy-compatible representation
- Never overwrites, renames, deletes, or duplicates legacy file
- Does not automatically create `source__text.txt`
- Reports that legacy TXT remains the active representation
- Validation and ingestion workflows use the legacy TXT
- Canonical migration requires separate explicit user decision

**Case C: Only `source__text.txt` exists**
- Treats as canonical representation
- Skips or replaces according to `--force` rules (standard pipeline behavior)

**Case D: Both `source.txt` and `source__text.txt` exist (Conflict)**
- Reports TXT representation conflict
- Does not silently choose either representation
- Does not modify either file
- Requires explicit user resolution:
  1. Migrate legacy → canonical: Delete `source.txt`, rerun pipeline
  2. Preserve legacy only: Delete `source__text.txt`
  3. Archive legacy: Rename `source.txt` to `source__archived.txt`, rerun pipeline

---

## Status Taxonomy

Three independent status fields track source progression:

### 1. technical_status

Indicates whether text extraction succeeded:

- `native-text`: Extracted from original PDF text layer
- `ocr-completed`: Generated via OCR pipeline
- `extraction-failed`: Text extraction encountered errors

Location: Quality report frontmatter

Does NOT imply: verified, reliable, ready for citation

### 2. quality_status

Indicates whether text meets technical quality thresholds:

- `passed`: Meets all quality thresholds (character density, low mojibake, page correspondence)
- `usable-with-review`: Meets minimum thresholds, manual review recommended
- `failed`: Does not meet quality thresholds

Location: Quality report frontmatter

Does NOT imply: inspected, verified, ready for research use

### 3. research_status

Indicates manual verification status:

- `not-inspected`: Text has not been manually inspected
- `inspected`: Source has been read and assessed
- `partially-ingested`: Some content converted to wiki notes
- `fully-ingested`: All relevant content extracted to wiki notes
- `verified`: Claims and quotations checked against original source

Location: Quality report frontmatter (initial), wiki page frontmatter (final)

Required before: direct quotation in manuscript, treating as verified evidence, citation in published work

---

## Script Reference

All scripts located in `00-System/Scripts/`

Python dependencies in `00-System/requirements.txt`

Configuration in `00-System/Config/source-pipeline.yml`

### Python Runtime

**Supported Runtime:** Python 3.11+

**Current Environment:** Python 3.8.18

**Current Environment Conformity:** Incomplete

Python 3.8 compatibility is best-effort only, not the supported baseline. The pipeline is designed for Python 3.11+ but includes compatibility code for Python 3.8 where `Path.is_relative_to()` is unavailable.

Python 3.8 compatibility code:
- `inspect-pdf.py` uses try/except ValueError instead of `Path.is_relative_to()` (requires Python 3.9+)

External dependencies (must be installed separately):
- pdftotext (from poppler-utils)
- pdfinfo (from poppler-utils)
- ocrmypdf
- tesseract with language packs: eng, tur, ara

### inspect-pdf.py

**Purpose:** Inspect PDF for text layer quality and language detection

**Usage:**
```bash
python3 00-System/Scripts/inspect-pdf.py \
  --file "path/to/source.pdf" \
  [--vault-root "/path/to/vault"] \
  [--dry-run]
```

**Output:**
- Intake report: `01-Library/Reports/*__intake.md`
- Console summary: text layer assessment, language inference, recommendation

**Recommendation codes:**
- `ACCEPT` - Ready for native text extraction
- `ACCEPT (OCR REQUIRED)` - Scanned document, OCR needed
- `HOLD FOR MANUAL REVIEW` - Good text layer but language uncertain
- `REQUEST BETTER COPY` - Text extraction failed

**Safe execution:**
- Read-only operations
- No file modification
- No automatic file movement

### process-source.py

**Purpose:** Process source PDFs through OCR pipeline

**Usage:**
```bash
# Check dependencies
python3 00-System/Scripts/process-source.py --doctor

# Process with native text extraction
python3 00-System/Scripts/process-source.py \
  --file "01-Library/Originals/Author - Year - Title.pdf"

# Process with OCR
python3 00-System/Scripts/process-source.py \
  --file "01-Library/Originals/Author - Year - Title.pdf" \
  --lang tur

# Multilingual OCR
python3 00-System/Scripts/process-source.py \
  --file "01-Library/Originals/Author - Year - Title.pdf" \
  --lang tur+ara

# Dry run
python3 00-System/Scripts/process-source.py \
  --file "01-Library/Originals/Author - Year - Title.pdf" \
  --lang eng \
  --dry-run
```

**Language codes:**
- `tur` - Turkish
- `eng` - English
- `ara` - Arabic
- `tur+ara` - Turkish and Arabic (multilingual)
- `tur+eng+ara` - All three languages

**Output:**
- OCR PDF (if needed): `01-Library/OCR/*__ocr.pdf`
- Text with page markers: `01-Library/Text/*__text.txt`
- Quality report: `01-Library/Reports/*__quality.md`

**Safe execution:**
- Atomic writes using temporary files
- Skip existing outputs unless `--force`
- No in-place editing
- No automatic file movement
- Originals remain in `01-Library/Originals/` permanently

### validate-text.py

**Purpose:** Validate text quality and generate quality report

**Usage:**
```bash
python3 00-System/Scripts/validate-text.py \
  --file "01-Library/Text/Author - Year - Title__text.txt" \
  [--vault-root "/path/to/vault"]
```

**Output:**
- Quality report: `01-Library/Reports/*__quality.md`
- Console summary: quality status, page count, issues

**Quality checks:**
- Character density (minimum 50 chars/page)
- Replacement character count (maximum 50)
- Mojibake patterns (Turkish encoding issues: Ã§, Ä±, ÅŸ, Ã¼, Ã¶, etc.)
- Page count correspondence (PDF pages vs text markers)

**Safe execution:**
- Read-only operations
- No file modification

### add-page-markers.py

**Purpose:** Add PDF page markers to plain text files (standalone utility)

**Usage:**
```bash
python3 00-System/Scripts/add-page-markers.py \
  --file "input.txt" \
  --output "output.txt" \
  [--force] \
  [--dry-run]
```

**Output:**
- Text with `--- PDF PAGE N ---` markers at each form-feed character

**Note:** This script is primarily used as a standalone utility. The main `process-source.py` pipeline integrates page marker addition automatically.

**Safe execution:**
- Requires explicit `--output` path
- Rejects `input == output`
- Skips existing output unless `--force`
- Atomic writes using temporary files
- No in-place editing

---

## Standard Workflow

### For PDFs with Native Text Layer

```bash
# 1. Inspect
python3 00-System/Scripts/inspect-pdf.py \
  --file "05-Inbox/New-Source.pdf"

# If recommendation is ACCEPT:

# 2. Move to Originals (manual)
mv "05-Inbox/New-Source.pdf" "01-Library/Originals/Author - Year - Title.pdf"

# 3. Process (native text extraction)
python3 00-System/Scripts/process-source.py \
  --file "01-Library/Originals/Author - Year - Title.pdf"

# 4. Review quality report
cat "01-Library/Reports/Author - Year - Title__quality.md"

# If quality_status is passed:

# 5. Proceed to ingestion
# Use the ingest workflow (00-System/VAULT-WORKFLOWS.md)
```

### For Scanned PDFs (OCR Required)

```bash
# 1. Inspect
python3 00-System/Scripts/inspect-pdf.py \
  --file "05-Inbox/Scanned-Source.pdf"

# If recommendation includes suggested language:

# 2. Move to Originals (manual)
mv "05-Inbox/Scanned-Source.pdf" "01-Library/Originals/Author - Year - Title.pdf"

# 3. Process with OCR
python3 00-System/Scripts/process-source.py \
  --file "01-Library/Originals/Author - Year - Title.pdf" \
  --lang tur

# 4. Review quality report
cat "01-Library/Reports/Author - Year - Title__quality.md"

# If quality_status is passed or usable-with-review:

# 5. Manual review (if needed)
# Read sample pages in 01-Library/Text/Author - Year - Title__text.txt

# 6. Proceed to ingestion or re-process with different settings
```

---

## Troubleshooting

### Missing Dependencies

Run doctor command:
```bash
python3 00-System/Scripts/process-source.py --doctor
```

Install missing tools:

**macOS:**
```bash
brew install poppler tesseract ocrmypdf tesseract-lang
```

**Ubuntu/Debian:**
```bash
apt install poppler-utils tesseract-ocr ocrmypdf
apt install tesseract-ocr-tur tesseract-ocr-ara
```

### Language Detection Uncertain

If `inspect-pdf.py` reports low confidence:

1. Read sample text in intake report
2. Determine language manually
3. Specify explicit `--lang` parameter to `process-source.py`

### OCR Quality Poor

If quality report shows `quality_status: failed`:

1. Check mojibake patterns and encoding issues
2. Try re-processing with different language combination
3. Try alternative OCR settings (edit `process-source.py` OCRmyPDF parameters)
4. Request better source copy if available

### Page Count Mismatch

If PDF pages ≠ text pages:

1. Check if PDF contains blank pages (not extracted)
2. Check if multi-column layout caused page detection issues
3. Manually verify sample pages
4. Document mismatch in quality report or source page

### File Already Exists

Scripts skip existing outputs by default. To re-process:

```bash
python3 00-System/Scripts/process-source.py \
  --file "01-Library/Originals/Author - Year - Title.pdf" \
  --force
```

Use `--force` with caution. It will overwrite existing files.

---

## Integration with Vault Workflows

### Relation to CLAUDE.md

`00-System/VAULT-WORKFLOWS.md` (indexed from `CLAUDE.md`) defines the `ingest` workflow for creating wiki notes from validated sources.

Source Pipeline prepares sources for ingestion. `ingest` operates on `01-Library/Text/*.txt` files.

**Division of responsibility:**
- Source Pipeline: Stage 0-3 (Acquisition → Quality Review)
- `ingest` workflow: Stage 4-5 (Neutral Ingestion → Verification)

### Relation to RESEARCH_PROTOCOL.md

`RESEARCH_PROTOCOL.md` is the highest authority for research integrity.

Source Pipeline enforces technical quality. Research Protocol enforces evidential standards.

**Key principles from Research Protocol:**
- Never fabricate citations or quotations
- Never invent missing metadata
- Separate source-reported content from interpretation
- Preserve uncertainty and limitations
- Require verification before treating claims as evidence

Quality status `passed` does NOT override Research Protocol verification requirements.

### Relation to Project-Specific Rules

Projects may add stricter requirements beyond vault-level rules.

Example: a book project may require NotebookLM quotation verification for one chapter (defined in `03-Projects/<Project>/00-System/CLAUDE-<Chapter>.md`)

**Authority hierarchy:**
1. `RESEARCH_PROTOCOL.md` (research integrity - highest authority)
2. Project-specific rules (e.g., `CLAUDE-Chapter4.md`)
3. `CLAUDE.md` and `00-System/VAULT-WORKFLOWS.md` (vault-level workflows)
4. `Source-Pipeline.md` (technical processing)

---

## Version Control

### Tracked Files

Version the following in Git:

- All scripts (`00-System/Scripts/*.py`)
- Configuration (`00-System/Config/source-pipeline.yml`)
- Dependencies (`00-System/requirements.txt`)
- Documentation (`00-System/Source-Pipeline.md`)
- Intake reports (`01-Library/Reports/*__intake.md`)
- Quality reports (`01-Library/Reports/*__quality.md`)
- Final text files (`01-Library/Text/*.txt`) - user decides whether to stage

### Ignored Files

Do NOT version the following (add to `.gitignore`):

- OCR PDFs (`01-Library/OCR/*__ocr.pdf`)
- Temporary files (`00-System/.source-pipeline-tmp/`, `*.partial`, `*.tmp`)
- Python caches (`**/__pycache__/`, `*.pyc`)

Rationale: OCR PDFs are regenerable intermediates. Reports are provenance records and should be versioned.

---

## Operational Tracking

For tracking in-progress sources (currently processing, paused, blocked), see:

`01-Library/Sources-In-Progress.md`

That file contains:
- Currently Processing list
- Paused/Blocked list with reasons
- Completion status for large multi-section sources

When a source is fully ingested and verified, remove it from Sources-In-Progress and record completion in:
- Source page in `02-Wiki/`
- `log.md` entry
- Optional completion manifest in `01-Library/Processed/`
