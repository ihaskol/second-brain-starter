# Second Brain Operating Manual

## Purpose

This vault is a research-oriented second brain.

Its purpose is to:

- ingest source material,
- convert sources into structured atomic notes,
- preserve source attribution,
- connect new knowledge with existing knowledge,
- support reliable research and synthesis,
- identify contradictions, uncertainty, and missing evidence,
- maintain a coherent knowledge base over time.

For all rules concerning truthfulness, evidence, citations, quotations, uncertainty, synthetic data, and hallucination prevention, always follow `RESEARCH_PROTOCOL.md`.

If this file conflicts with `RESEARCH_PROTOCOL.md` on a research-integrity issue, follow `RESEARCH_PROTOCOL.md`.

---

## Bootstrap and Scoped Context

For every non-trivial task:

1. Read `00-System/START-HERE.md` and use its task and project router.
2. Follow `00-System/ENGINEERING-CONTRACT.md` for memory writes, context budgets, freshness, workflow graphs, link classification, and maintenance.
3. For research work, apply `RESEARCH_PROTOCOL.md` and load only the relevant project state, index section, notes, and source passages.
4. Do not recursively read the vault; bootstrap with no more than three system/state documents when possible and retrieve wiki notes in batches of no more than five.
5. Do not write until the engineering contract's Write Gate is satisfied.
6. For graph-shaped work, use only real data or decision dependencies, isolate per-node context, and run fresh-context verification before synthesis.

`00-System/START-HERE.md` and `00-System/ENGINEERING-CONTRACT.md` are the single sources of truth for these engineering rules. Do not duplicate their full contents here.

---

## Session Handoff (every session)

The model remembers nothing between sessions; the files do. For project work:

1. **Start:** read the project's `PROJECT-STATE.md` first. It is short: current state, open items, last decision, "Tried and rejected — don't retry", and the last five session-log entries. Don't repeat a rejected approach unless the user asks.
2. **End:** if the session changed project files, update the current state, open items, and last decision. Add one session-log entry (done · decided and why · open · tried and rejected) and record any failed approach.
3. **Keep it short:** about 150 lines. Move older detail verbatim to `PROJECT-HISTORY.md`.
4. **Nothing important stays in scratch folders.** Copy scripts, verified-facts lists, OCR output and backups into the project's `_build/` before the session ends.

Full rule: `00-System/ENGINEERING-CONTRACT.md` §2, "Session Handoff and Resumability". Tool pitfalls already learned the hard way: `00-System/LESSONS-LEARNED.md`. Read the relevant section before using Keynote, Pages, pandoc, web fetches or artifact publishing.

---

## Project Routing

This vault supports both neutral knowledge base maintenance and project-specific work.

**Vault-Level Work (Neutral Knowledge Base)**

Routes source processing, wiki maintenance, and knowledge organization through:
- `CLAUDE.md` (this file)
- `RESEARCH_PROTOCOL.md`
- `00-System/Source-Pipeline.md`

Use for: source acquisition and quality control, `ingest`, `query vault`, `lint wiki`, `weekly review`, and all wiki page creation/maintenance.

**Project-Specific Work**

Individual projects may have additional constraints beyond vault-level rules.

Projects are located in `03-Projects/` with their own system documentation.

When working on project-specific tasks, consult the project's system files for additional requirements.

**Authority Hierarchy:**

`RESEARCH_PROTOCOL.md` is the highest authority for research integrity in all contexts.

Project-specific rules may add stricter verification requirements but cannot override research integrity principles.

**Critical Boundaries:**

- Neutral wiki notes must never be rewritten to conform to a project thesis.
- Project drafts and interpretations are not independent research evidence.
- Wiki pages may inform project arguments, but projects may apply stricter verification and additional frameworks.

**When Ambiguous:**

If the requested target system (vault-level vs project-specific) is unclear, ask for clarification before proceeding.

---

## Vault Structure (summary)

- `01-Library/`: sources. `Originals/` (immutable PDFs), `OCR/`, `Text/`, `Reports/`, `Processed/`, `Placeholders/`, `Sources-In-Progress.md`
- `02-Wiki/`: atomic knowledge pages · `index.md`: catalog · `log.md`: chronological activity
- `03-Projects/`: project work with its own state, decisions and history files
- `00-System/`: system documentation, scripts, config · `04-Templates/` · `05-Inbox/` (staging) · `06-Archive/`
- `.claude/skills/`: registered skills

Safety: never delete or overwrite original source files unless explicitly instructed. Never place wiki pages inside `01-Library/`. Originals stay in `Originals/` permanently. Details, including legacy TXT handling: `00-System/VAULT-WORKFLOWS.md` § Vault Structure.

---

## Workflows: read the section before acting

All detailed workflows are in `00-System/VAULT-WORKFLOWS.md`. When a command or task below comes up, read that section first, then follow it exactly.

| Command / task | Section in `00-System/VAULT-WORKFLOWS.md` |
|---|---|
| Source intake, OCR, quality gates (Stages 0–3) | Source Acquisition and Quality Control (+ `00-System/Source-Pipeline.md`) |
| `ingest this`, `inspect raw`, `approved, ingest` | INGEST Workflow; Short Command Interface |
| A question about the vault, `query vault: …` | QUERY Workflow |
| "save this answer" | SAVE Workflow |
| `lint wiki` | LINT Workflow |
| `weekly review` | Weekly Review Workflow |
| A book or a source over about 100 pages | Short Command Interface → Large source workflow |
| Creating or editing any `02-Wiki/` page | YAML Frontmatter; Standard Page Structure; Linking Rules; Final Check Before Writing |
| Updating `index.md` / `log.md` | Index Rules; Log Rules |

Skills for specialised work are listed in `00-System/START-HERE.md` (Shared Build Tools): `presentation-builder`, `course-hub-builder`, `web-artifact-workflow`, `ux-redesign`, `research-ideation`, `citation-verification`, `zotero-sources`, `process-sources`.

---

## Core Principles

- Prefer accuracy over completeness.
- Prefer explicit uncertainty over unsupported confidence.
- Keep one primary idea per page.
- Preserve source attribution.
- Preserve disagreements between sources.
- Never treat generated text as evidence.
- Never treat a summary as a replacement for the original source.
- Prefer updating an existing page over creating a duplicate.
- Do not make destructive changes without explicit permission.

---

## Filename Rules

- Use English filenames.
- Use lowercase kebab-case.
- Use descriptive concept names.
- Avoid generic filenames.
- Avoid unnecessary dates.
- Avoid special characters that may cause filesystem problems.

Examples:

- `transformer-attention-mechanism.md`
- `retrieval-augmented-generation.md`
- `limitations-of-self-reported-data.md`

The visible page title may be in Turkish or English.

---

## Language Rules

- Use English filenames.
- Write page content in Turkish or English according to my instruction.
- Preserve technical terminology.
- Preserve the original language of direct quotations.
- Clearly label translated quotations.
- Do not present a translation as the original wording.

---

## Change-Safety Rules

Before making many changes:

- Briefly explain the planned changes.
- Identify which files will be created or modified.
- Do not delete files without explicit permission.
- Do not overwrite original source material.
- Do not silently alter citation details.
- Report incomplete or failed operations.
- Ask before performing a destructive merge, split, or restructuring operation.

---
