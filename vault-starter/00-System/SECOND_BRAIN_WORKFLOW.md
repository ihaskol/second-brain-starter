# Second Brain Workflow — Claude Code + Obsidian

**Documentation Note:**

This file is extended documentation. Root `CLAUDE.md` governs operational rules. `RESEARCH_PROTOCOL.md` governs research integrity. A project's own `03-Projects/<Project>/00-System/` files govern that project's work. In case of conflict, the governing files take precedence.

---

## Purpose

This workflow is designed to transform sources into a secure, traceable, and reusable knowledge base using Claude Code within an Obsidian vault.

The system's core cycle:

```text
RAW SOURCE
→ INSPECT
→ APPROVE
→ INGEST
→ QUERY
→ LINT
→ REVIEW
→ ADD NEW SOURCES
```

Core principle:

> Not just storing sources, but transforming them into atomic, linked, and auditable wiki pages.

---

# 1. System Structure

Vault root:

```text
<path to your vault>/Second Brain
```

Basic structure:

```text
Second Brain/
├── CLAUDE.md
├── RESEARCH_PROTOCOL.md
├── index.md
├── log.md
├── 00-System/
│   ├── Scripts/
│   ├── Config/
│   ├── Source-Pipeline.md
│   └── SECOND_BRAIN_WORKFLOW.md
├── 01-Library/
│   ├── Originals/
│   ├── OCR/
│   ├── Text/
│   ├── Reports/
│   ├── Processed/
│   ├── Placeholders/
│   └── Sources-In-Progress.md
├── 02-Wiki/
├── 03-Projects/
├── 04-Templates/
├── 05-Inbox/
└── 06-Archive/
```

## File and Folder Roles

### `CLAUDE.md`

Defines workflows:

- ingest
- query
- lint
- weekly review
- short commands
- large source workflow

### `RESEARCH_PROTOCOL.md`

Defines research integrity:

- source-bounded mode
- citation accuracy
- attribution
- uncertainty
- hallucination prevention
- external knowledge prohibition
- source-reported claim vs Claude synthesis distinction

### `/01-Library/Originals`

Unprocessed original sources:

- PDF
- TXT
- MD
- DOCX

### `/01-Library/Processed`

Completion manifests for fully processed sources.

A source is marked complete only after all planned sections are finished and linted.

**Note:** Original PDFs remain in `/01-Library/Originals/` permanently. They are never moved to Processed/.

### `/01-Library/Placeholders`

Placeholder files containing only citation metadata without actual source text.

These are not ingested.

### `/02-Wiki`

Atomic knowledge pages created by Claude.

### `index.md`

Catalog of all wiki pages.

### `log.md`

Chronological record of all ingest, correction, and lint operations.

---

# 2. Core Research Rules

## Strict Source-Bounded Mode

Claude uses only information explicitly found within the vault.

Claude must not:

- add names, books, events, dates, or concepts from outside the vault
- identify unknown persons by inference
- generate bibliographic metadata not in the source
- add examples from model memory
- fabricate missing page numbers
- write as if a primary source cited by a secondary source was directly read

## Mandatory Distinctions

Each page should separate these categories as much as possible:

- Source-reported claim
- Author interpretation
- Normative claim
- Claude synthesis
- Uncertainty and limitations
- Evidence not provided

## Status Rules

New pages should default to:

```yaml
status: needs-verification
```

A page should only be changed to `status: reviewed` after claims and citations have been directly checked against the source.

For the distinction between page-level `status: reviewed` and source-level `research_status: verified`, see `RESEARCH_PROTOCOL.md`.

---

# 3. Short Commands

Short commands defined in `CLAUDE.md`:

## `inspect raw`

Function:

- finds unprocessed sources in `/01-Library/Originals`
- checks readability
- extracts metadata
- proposes page plan
- reports claim and citation structure
- does not write files
- waits for approval

## `approved, ingest`

Function:

- implements the most recently approved ingest plan
- creates wiki pages
- updates index and log files
- updates `/01-Library/Sources-In-Progress.md` with completion status

Safe usage:

```text
approved, ingest only [exact filename]
```

If multiple sources are in `/01-Library/Originals`, the filename must be specified.

## `query vault: [question]`

Function:

- uses only vault content
- cites relevant wiki pages and sources
- shows agreement, tension, contradiction, and uncertainty
- does not create new pages unless requested by user

## `lint wiki`

Function:

Detects:

- contradiction
- broken link
- orphan page
- duplicate
- missing metadata
- unsupported claim
- citation error
- external knowledge leakage
- attribution problem

Does not modify files by default.

## `weekly review`

Function:

- summarizes additions from the last 7 days
- extracts the most important ideas
- shows new connections
- identifies emerging hub topics
- suggests knowledge gaps
- should only suggest generic source types

---

# 4. Normal Source Workflow

This workflow is used for short articles, reports, and manageable-length documents.

## Step 1 — Place source in `/01-Library/Originals`

Example:

```text
/01-Library/Originals/article.pdf
```

## Step 2 — Inspect

Claude Code:

```text
inspect raw
```

or safer:

```text
Inspect only this source:

01-Library/Originals/[exact filename]

Do not inspect other files.
Do not ingest yet.
Follow CLAUDE.md and RESEARCH_PROTOCOL.md.
```

## Step 3 — Review inspection report

Checklist:

- is the file fully readable?
- is the author name correct?
- are title, year, journal/publisher correct?
- is source type correctly identified?
- how many source pages and atomic pages were proposed?
- are the claims genuinely distinct?
- has external knowledge leaked in?
- are page numbers or footnotes present?
- is missing metadata explicitly noted?

## Step 4 — Approve

```text
approved, ingest only [exact filename]
```

## Step 5 — Post-ingest verification

Expected outcomes:

- source page created
- atomic pages created
- all new pages marked `needs-verification`
- index updated
- log updated
- Sources-In-Progress.md updated
- no files deleted
- report provided

---

# 5. Large Source Workflow

Used for 100+ page books or files that exceed Claude Code's PDF reader limit.

**New Source Processing:**

For a new PDF source, it must first go through the Source Pipeline:
- Intake review (text layer, language detection)
- Format preparation (OCR if needed)
- Quality validation

For detailed procedures, see: `00-System/Source-Pipeline.md`

**Sources already in TXT format** can use this workflow directly.

## Core Rule

Do not ingest an entire large book in one operation.

Instead:

```text
Source page
→ Preface/Introduction
→ Chapter 1
→ Chapter 2
→ ...
→ Final synthesis
→ Final lint
→ Mark complete in Sources-In-Progress.md
```

## Step 1 — Convert PDF to TXT

Terminal:

```bash
pdftotext -layout \
"/full/path/source.pdf" \
"/full/path/source.txt"
```

## Step 2 — Add page markers

Use the pipeline script:

```bash
python3 00-System/Scripts/add-page-markers.py \
  --file "/full/path/source__text.txt" \
  --output "/full/path/source.txt"
```

Or manual method:

```bash
python3 - <<'PY'
from pathlib import Path

path = Path("/full/path/source.txt")
text = path.read_text(encoding="utf-8", errors="replace")
pages = text.split("\f")

output = []
for i, page in enumerate(pages, start=1):
    if page.strip():
        output.append(f"\n\n--- PDF PAGE {i} ---\n\n{page.strip()}")

path.write_text("".join(output), encoding="utf-8")
print(f"Marked {len([p for p in pages if p.strip()])} PDF pages.")
PY
```

## Step 3 — Use TXT as source representation

Claude Code:

```text
Inspect only this source representation:

01-Library/Originals/[source].txt

Treat the matching PDF and TXT as two representations of the same source.

Use the TXT for text analysis.
Do not attempt to read the full PDF.
Do not ingest yet.
```

## Step 4 — Create chapter-level plan

Claude should report:

- total detected page markers
- bibliographic metadata
- table of contents
- printed page numbers
- PDF marker ranges
- recommended chapter boundaries
- extraction problems
- pagination uncertainty

## Step 5 — Phase-by-phase ingest

Example:

```text
Approve Phase 1 only.
```

Phase 1:

- book-level source page
- Preface
- Introduction
- 3–5 strong atomic pages

Later:

```text
inspect Friedmann Chapter 1 only
approved, ingest Friedmann Chapter 1 only
```

## Large Source File Management Rule

PDF and TXT remain in:

```text
/01-Library/Originals
```

After all sections are completed:

```text
finalize [source]
```

creates a completion manifest in `/01-Library/Processed/`, but the original files remain in Originals/.

---

# 6. PDF Reader Error Workflow

If Claude Code gives this error:

```text
PDF too large. Please double press esc...
```

## Actions

### 1. Clear the session

```text
/clear
```

or close and reopen Claude Code.

### 2. If file still won't read, convert to TXT

```bash
pdftotext -layout source.pdf source.txt
```

### 3. Read the TXT

```text
Use the TXT for analysis.
Do not try to read the full PDF.
```

### 4. Pagination rule

- TXT page marker = PDF image page
- printed book page may differ
- if printed page is clearly visible, cite it
- if not visible, use `PDF PAGE N`
- never invent page numbers

---

# 7. Query Workflow

Run a meaningful query every 3–5 sources.

Example:

```text
query vault: Compare Author A's account with Author B's account.
```

Query response should make these distinctions:

- Author A claims
- Author B claims
- Direct agreement
- Partial support
- Tension
- Contradiction
- No support
- Claude synthesis
- Uncertainty

## Important

When two secondary sources support each other, this should be called:

```text
cross-source corroboration
```

This is not:

```text
independent verification
```

---

# 8. Lint Workflow

## When to run

- every 3–5 sources
- after large ingest
- after major correction
- before weekly review

## First lint should only generate a report

```text
lint wiki
```

## Items checked in lint report

- unsupported factual claims
- incomplete citations
- unverifiable quotations
- external knowledge leakage
- author attribution
- Claude synthesis labeling
- contradictions
- outdated claims
- duplicate pages
- orphan pages
- broken links
- YAML metadata
- overstatement
- indirect citations
- knowledge gaps

## Correction workflow

First:

```text
Prepare a correction plan.
Do not edit files yet.
```

Then only apply required corrections.

Then again:

```text
lint wiki
```

## Clean lint criteria

- critical issues: 0
- external knowledge violations: 0
- broken links: 0
- orphan pages: 0
- metadata issues: 0
- all pages remain appropriately marked

---

# 9. Weekly Review Workflow

Every week:

```text
weekly review
```

Review should include these sections:

1. Three most important ideas
2. New connections
3. Emerging hub topics
4. Contradictions and uncertainty
5. Weakest-supported claims
6. Pages requiring corroboration
7. Knowledge gaps
8. Generic source types to add
9. Research questions for next week

## Source-bounded review rule

Weekly review:

- must not suggest named external scholars
- must not suggest named books
- must not suggest named databases
- must not add named events
- should only suggest generic source types

Correct:

```text
Add comparative empirical research on taxation and representation.
```

Incorrect:

```text
Read [specific scholar/book not in vault].
```

---

# 10. Source Tracking

**Completed and ongoing source information is no longer maintained here.**

For current source status, see:

**`01-Library/Sources-In-Progress.md`**

This file contains:
- Currently Processing (active source operations)
- Paused (paused sources)
- Blocked (blocked sources)
- Recently Completed (temporary operational handoff)

---

# 11. Current Status

**This section is no longer managed here.**

For current source status and where we left off:

**`01-Library/Sources-In-Progress.md`**

For partially ingested or paused sources, refer to the relevant source entry.

---

# 12. Working with Multi-Section Sources

For large sources (e.g., books):

1. Start with Source Pipeline (if new PDF)
2. Ingest one section at a time
3. After each section, update `01-Library/Sources-In-Progress.md`
4. When all sections are complete:
   - Final lint
   - Remove from Sources-In-Progress.md
   - Add completion record to source page
   - Optional: create completion manifest in `/01-Library/Processed/`
5. Original PDF remains in `/01-Library/Originals/` (never moved)

---

# 13. Daily Most Efficient Routine

## When a new short source arrives

```text
1. source → /05-Inbox
2. python3 00-System/Scripts/inspect-pdf.py --file "05-Inbox/[filename]"
3. if ACCEPT → mv to /01-Library/Originals
4. python3 00-System/Scripts/process-source.py --file "01-Library/Originals/[filename]"
5. check quality report → 01-Library/Reports/
6. if quality_status: passed → ingest workflow
7. update 01-Library/Sources-In-Progress.md
```

## When a large book arrives

```text
1. Source Pipeline (inspect, OCR if needed, validate)
2. inspect structure
3. create book source page
4. add to 01-Library/Sources-In-Progress.md
5. process one chapter at a time
6. after each section, update Sources-In-Progress.md
7. final lint
8. remove from Sources-In-Progress.md, add completion record
```

## Every few sources

```text
query vault: [question]
```

## Weekly

```text
lint wiki
weekly review
review 01-Library/Sources-In-Progress.md
```

---

# 14. Handoff Instructions for Another LLM

An LLM reading this file should:

1. First read the `CLAUDE.md` file.
2. Then read the `RESEARCH_PROTOCOL.md` file.
3. Check the `index.md` and `log.md` files.
4. Compare `/01-Library/Originals` and `/01-Library/Processed` folders.
5. Check the "Current Status" section in this workflow.
6. Verify completion status before moving a source file.
7. If a source page exists, do not create a duplicate.
8. Do not exit source-bounded mode.
9. In uncertain situations, do not write files; first request inspection report and approval.
10. When implementing the most recently approved plan, do not expand scope.

---

# 15. Governing Principle

> The vault is not a storage folder.
> It is a maintained, source-bounded, auditable knowledge system.

Success criterion is not the increase in note count, but the preservation of:

- source fidelity
- traceable citations
- clear attribution
- uncertainty visibility
- meaningful links
- no hallucinated knowledge
- reproducible workflow
