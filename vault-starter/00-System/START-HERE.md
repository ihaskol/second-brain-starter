# Second Brain — Start Here

## Purpose

This is the vault-level routing page. Use it to identify the smallest relevant context before opening detailed notes or source files.

It does not replace:

- `RESEARCH_PROTOCOL.md` for research integrity,
- `AGENTS.md` or `CLAUDE.md` for tool-specific operating rules,
- project-specific instructions for project work,
- `00-System/Source-Pipeline.md` for source-processing mechanics.

For memory, context, workflow-graph, freshness, and write rules, follow `00-System/ENGINEERING-CONTRACT.md`.

---

## Authority Order

`RESEARCH_PROTOCOL.md` governs truthfulness, evidence, citation, verification, and other research-integrity questions. No project, workflow, or tool rule may weaken it.

For goals, scope, format, and other non-integrity questions, use this order:

1. The user's current explicit instruction
2. The relevant project-specific system files
3. `00-System/ENGINEERING-CONTRACT.md`
4. `AGENTS.md` or `CLAUDE.md`
5. Supplementary workflow documentation

Project rules may be stricter than vault-level rules, but they may not weaken research-integrity requirements.

---

## Bootstrap Sequence

For every non-trivial task:

1. Classify the task as vault-level, source-processing, or project-specific.
2. Read this router and the relevant portion of `00-System/ENGINEERING-CONTRACT.md`.
3. For research work, read the relevant portion of `RESEARCH_PROTOCOL.md`.
4. For project work, load the project's current-state source listed below.
5. Search `index.md` or the relevant hub for candidate notes.
6. Load only the notes and source passages required for the task.

Do not begin by recursively reading the entire vault.

### Initial Context Budget

- Bootstrap with no more than three system/state documents when possible.
- Target approximately 6,000 tokens or less for initial context.
- Retrieve wiki notes in batches of no more than five.
- Reserve at least 25% of the available context for verification, synthesis, and the final answer.
- Expand context only when the current evidence packet identifies a specific gap.

`index.md` is a catalog, not a default context bundle. Search it or read only the relevant section.

---

## Task Router

### Vault Query or Synthesis

Read:

1. `00-System/ENGINEERING-CONTRACT.md`
2. `RESEARCH_PROTOCOL.md`
3. The relevant section of `index.md`
4. Up to five candidate wiki notes
5. Original source passages only when verification is required

Default behavior: answer without saving unless the user explicitly requests a write.

### Source Inspection or Ingestion

Read:

1. `00-System/Source-Pipeline.md`
2. `RESEARCH_PROTOCOL.md`
3. `01-Library/Sources-In-Progress.md`
4. The relevant source, intake report, and quality report

Use the approval gates defined in the existing ingest workflow. Never overwrite an original source.

### Wiki Maintenance or Lint

Read:

1. `00-System/ENGINEERING-CONTRACT.md`
2. `00-System/MAINTENANCE.md`
3. `00-System/LINK-REGISTRY.md` when link health is in scope
4. The LINT workflow in `00-System/VAULT-WORKFLOWS.md`
5. `index.md`
6. Only the pages identified by the lint scope

Lint is read-only by default. Do not merge, delete, rename, or rewrite pages without approval.

---

## Project Router

The vault can hold several project areas. Each project has one canonical `PROJECT-STATE.md` and one append-only `DECISIONS.md`. Add one entry per project below; keep each entry short.

### <Project Name> (example — replace)

Canonical current-state source:

- `03-Projects/<Project Name>/PROJECT-STATE.md`

Then read `DECISIONS.md` and `PROJECT-GRAPH.md` in the same folder. One or two sentences: current status, scope, what to load next, and any project-specific rules (e.g. source-bounded, citation style).

---

## Shared Build Tools (`00-System/Scripts/`)

Deliverable standards for every project (English only, Times New Roman, visuals everywhere) and reusable builders:

- `md-to-docx.sh` — Markdown → Word (Times New Roman, TOC); `_reference-times-new-roman.docx` is its style template
- `deck_kit.py` — `python-pptx` toolkit (`Deck`, `.bullets()`, `.chart()`, `pipeline_diagram()`) — Times New Roman enforced; audience presets
- `forecast_bakeoff.py` — `bakeoff(series, horizon, n_origins)`: seasonal-naive / ETS / ARIMA / Theta / Croston / ensemble through one rolling-origin backtest, returns the winner + forecast
- Full-featured decks: use the registered **`presentation-builder`** skill (`.claude/skills/presentation-builder/`)
- Tool pitfalls learned the hard way (Keynote, Pages, pandoc, web fetches, artifacts): `00-System/LESSONS-LEARNED.md`
- A page that feels confusing, cluttered or unfriendly (simplify, redesign, first-time-visitor review, UI/UX): use the **`ux-redesign`** skill (`.claude/skills/ux-redesign/`), then finish with `web-artifact-workflow`
- Any interactive page or artifact (audit, polish, launch): follow the **`web-artifact-workflow`** skill (`.claude/skills/web-artifact-workflow/`), including its accessibility audit script
- Whole-course interactive student page (course map, week pages with slides, workshops, exam prep): use the **`course-hub-builder`** skill (`.claude/skills/course-hub-builder/`)
- In-class group workshops: follow `00-System/WORKSHOP-DESIGN-STANDARD.md` (interactive HTML + Word + Excel from one config; team codes; class comparison; `#instructor` keys)

---

## Retrieval Stop Conditions

Stop loading context when all of the following are true:

- the task and output format are clear,
- the relevant project state is known,
- each material claim has a traceable source or an explicit uncertainty label,
- contradictions and missing evidence are visible,
- additional files are unlikely to change the conclusion.

If these conditions are not met, identify the exact missing evidence before loading more context.

---

## Write Gate

Before writing anything to the vault, confirm:

1. The user requested or clearly authorized a write.
2. The destination matches the memory type.
3. An equivalent note or state record does not already exist.
4. Provenance, verification state, and freshness are preserved.
5. The change is recorded in the appropriate index, log, project state, or decision record.

For the full write policy, follow `00-System/ENGINEERING-CONTRACT.md`.
