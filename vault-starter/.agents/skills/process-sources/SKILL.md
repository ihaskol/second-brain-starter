---
name: process-sources
description: Sequentially process one or more academic PDF sources through intake, extraction or OCR, quality review, neutral ingestion, and optional Git commits.
argument-hint: '[PDF paths... | directory] [--recursive] [--commit]'
disable-model-invocation: true
---

# Sequential Source Processing

Work from the project root:

${CLAUDE_PROJECT_DIR}

The invocation arguments are:

$ARGUMENTS

## 1. Interpret the input

Accept these invocation modes:

### No path supplied

Process every PDF located directly inside:

05-Inbox/

Sort files alphabetically by filename.

### One directory supplied

Process every PDF directly inside that directory.

Do not search subdirectories unless `--recursive` is present.

### One or more PDF paths supplied

Process the exact PDF paths in the order supplied by the user.

Quoted paths containing spaces must be treated as single paths.

### Optional flags

- `--recursive`: include PDFs in subdirectories
- `--commit`: create controlled Git commits after each successful source

Remove flags from the source-path list before processing.

Reject and report:

- missing paths,
- non-PDF files,
- duplicate paths,
- empty directories,
- paths outside the vault,
- files already queued more than once.

Do not process PDFs in parallel.

## 2. Read the governing files once

Before processing the queue, read:

- AGENTS.md
- RESEARCH_PROTOCOL.md
- 00-System/SECOND_BRAIN_WORKFLOW.md
- 00-System/Source-Pipeline.md

For project-specific ingestion, also read that project's governing files under:

- 03-Projects/<Project>/00-System/

Run:

git status --short

If unrelated uncommitted changes could be overwritten or confused with this
batch, report them before processing. Do not discard them.

## 3. Build the processing queue

Create an ordered queue containing:

- queue number,
- source filename,
- current location,
- SHA-256 hash,
- detected existing derivatives,
- initial status: PENDING.

Show the queue before beginning.

Process only one source at a time.

## 4. Handle each PDF sequentially

For each source, perform the following complete workflow.

### A. Intake location

If the source is inside `05-Inbox/`:

1. Verify that it is a readable PDF.
2. Compute its SHA-256 hash.
3. Check whether a file with the same name already exists in:
   `01-Library/Originals/`.
4. If no conflict exists, move the PDF to:
   `01-Library/Originals/`.
5. Verify that the hash is unchanged after the move.
6. Do not overwrite an existing original.
7. If a filename or hash conflict exists, mark the source BLOCKED and continue
   to the next source.

Once inside `01-Library/Originals/`, the PDF is immutable.

### B. Inspect existing state

Check for corresponding files in:

- 01-Library/Originals/
- 01-Library/OCR/
- 01-Library/Text/
- 01-Library/Reports/
- 02-Wiki/
- 03-Projects/

Identify:

- original PDF,
- OCR derivative,
- canonical TXT,
- legacy TXT,
- intake report,
- quality report,
- existing source note,
- existing atomic wiki notes,
- project mappings.

Do not duplicate existing work.

### C. Inspect the PDF

Run:

python3 00-System/Scripts/inspect-pdf.py \
  --file "<original PDF path>" \
  --vault-root . \
  --dry-run

Determine:

- physical PDF page count,
- text-layer condition,
- likely language,
- confidence,
- OCR requirement,
- recommended route.

If safe, create or refresh the intake report.

### D. Run processing dry-run

Run:

python3 00-System/Scripts/process-source.py \
  --file "<original PDF path>" \
  --vault-root . \
  [--lang APPROVED_LANGUAGE] \
  --dry-run

Use only these OCR-language values:

- tur
- eng
- ara
- tur+ara
- eng+ara
- tur+eng
- tur+eng+ara

Do not silently select an OCR language from low- or medium-confidence
inference.

### E. Process the source

If the dry-run is safe:

1. Run the actual processing command.
2. Preserve the original PDF unchanged.
3. Generate the appropriate derivatives:
   - searchable OCR PDF when needed,
   - canonical TXT or approved legacy representation,
   - intake report,
   - quality report.
4. Preserve one page marker for every physical PDF page.
5. Mark pages without extracted text explicitly.
6. Do not overwrite legacy TXT files automatically.

### F. Review quality

Verify:

- original PDF hash is unchanged,
- physical PDF page count equals TXT page-marker count,
- pages without text are identified,
- encoding is valid UTF-8,
- language inference is plausible,
- OCR output is readable,
- no mojibake is present,
- no unsafe legacy/canonical conflict exists,
- no temporary or partial files remain,
- quality status is justified.

### G. Safe automatic repair

When a technical check fails:

1. Diagnose the cause.
2. Fix it automatically only when the fix is:
   - safe,
   - reversible,
   - non-destructive,
   - limited to generated derivatives or pipeline code,
   - incapable of modifying original PDFs or verified notes.
3. Re-run the failed test.
4. Allow a maximum of two automatic repair attempts per source.

Safe repairs may include:

- regenerating a derivative,
- rebuilding page markers,
- recreating a quality report,
- cleaning temporary files,
- correcting a deterministic pipeline defect and running regression tests.

Do not invent or reconstruct missing scholarly content.

### H. Blocking conditions

Mark the current source BLOCKED when resolution requires:

- scholarly judgment,
- manual verification against the source,
- ambiguous OCR-language selection,
- destructive action,
- a choice between conflicting source representations,
- uncertain correction of words or quotations,
- modification of verified wiki notes,
- unsupported reconstruction of missing content.

A blocked source must not stop the entire batch.

Record the reason and continue with the next source.

### I. Neutral wiki ingestion

When all technical and quality checks pass:

1. Search `02-Wiki/` for existing source and concept notes.
2. Create or update one neutral source note.
3. Create only necessary atomic wiki notes.
4. Preserve physical PDF page references.
5. Separate:
   - direct quotation,
   - neutral paraphrase,
   - researcher inference,
   - project interpretation.
6. Keep project interpretation out of `02-Wiki/`.
7. Do not modify the manuscript.
8. Update `index.md`, `log.md`, and
   `01-Library/Sources-In-Progress.md` only when required by the workflow.

### J. Optional Git commits

If `--commit` is absent:

- do not stage or commit files,
- include all resulting changes in the final report.

If `--commit` is present:

1. Never use `git add .`.
2. Commit pipeline code fixes separately from source content.
3. For each successfully processed source, use separate thematic commits:

   - source derivatives:
     `Process <short source name> and record quality reports`

   - neutral wiki ingestion:
     `Ingest <short source name> as neutral source notes`

4. Run before every commit:

   git diff --cached --check
   git diff --cached --stat
   git status --short

5. Never commit unrelated files.

## 5. Per-source result

After each PDF, record:

- queue number,
- source name,
- final original path,
- processing route,
- language or OCR language,
- generated files,
- physical page count,
- page-marker count,
- pages without text,
- technical_status,
- quality_status,
- research_status,
- wiki notes created or updated,
- Git commits, if any,
- final result:
  - COMPLETED
  - COMPLETED WITH REVIEW
  - BLOCKED
  - FAILED

Then continue to the next PDF.

## 6. Final batch report

Return one concise table containing:

- queue number,
- filename,
- route,
- technical status,
- quality status,
- ingestion result,
- Git commit hash, if applicable,
- unresolved issue.

Also report:

- total PDFs discovered,
- completed count,
- blocked count,
- failed count,
- generated files,
- modified files,
- remaining files in `05-Inbox/`,
- final `git status --short`.

Do not process any PDF that was not part of the resolved input queue.
