# Second Brain — Files to Share

A shareable copy of the Second Brain setup: the system files (the "engine") plus the setup guides. It contains **no research content and no credentials**.

Prepared by Isa Haskologlu, PhD. Packaged 2026-10-06; the pipeline-tools guide added the same day; guides renumbered in setup order on 2026-10-13.

**License:** © 2026 Isa Haskologlu, PhD. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (full text in `LICENSE.txt`). You may share and adapt everything here for any purpose, as long as you give credit, link to the license and say what you changed. Suggested credit: *"Based on The Second Brain by Isa Haskologlu, PhD, CC BY 4.0."* Citation details: `CITATION.cff`, or the "How to cite this" box on the hub page.

---

## What is in this folder

### `guides/` — read these first

| File | What it is |
|---|---|
| `Integration-Setup-Guides.pdf` / `.docx` | Step-by-step setup for every integration (Claude Code, Zotero, NotebookLM, Jev, …), plus Guide 3: the PDF, OCR and Word/PDF tools the scripts need |
| `integration-quick-reference.pdf` / `.png` | One-page cheat sheet of the same steps |
| `Second-Brain-Guide.pdf` / `.docx` | How the system works and why (pipeline, memory, verification) |
| `second-brain-infographic.pdf` / `.png` | One-page visual overview |
| `Installing_Jev_for_Claude_Code_Audited.docx` | Installing the optional Jev decision aid in Claude Code |
| `Installing_Jev_in_VS_Code_English_Guide.docx` | The same for VS Code |
| `PROMPTS.md` | Copy-and-paste prompts to start, resume and end a project, plus the short commands (`inspect raw`, `query vault: …`, `lint wiki`, …) |

### `vault-starter/` — copy this as your new vault

```
vault-starter/
├── CLAUDE.md                 # Short operating manual Claude Code reads every session (178 lines)
├── AGENTS.md                 # Same manual for Codex/other agents
├── RESEARCH_PROTOCOL.md      # Research-integrity rules (highest authority)
├── index.md, log.md          # EMPTY starters — catalog and activity log
├── .gitignore                # Already ignores the Zotero key file
├── 00-System/
│   ├── START-HERE.md         # Task + project router (project list is a blank template)
│   ├── VAULT-WORKFLOWS.md    # Detailed workflows (ingest, query, lint, …), read when a command needs them
│   ├── LESSONS-LEARNED.md    # Tool pitfalls learned the hard way
│   ├── ENGINEERING-CONTRACT.md (incl. session handoff), MAINTENANCE.md, Source-Pipeline.md,
│   │   WORKSHOP-DESIGN-STANDARD.md,
│   │   SECOND_BRAIN_WORKFLOW.md, LINK-REGISTRY.md (blank template)
│   ├── requirements.txt
│   ├── Scripts/              # Source pipeline, Zotero, lint and output tools
│   ├── Config/               # source-pipeline.yml, zotero-integration.yml
│   └── Zotero/README.md
├── .claude/skills/           # citation-verification, course-hub-builder, explainer-video, presentation-builder,
│                             # process-sources, research-ideation, ux-redesign, web-artifact-workflow, zotero-sources
├── .agents/skills/           # Codex copies of process-sources, zotero-sources
├── 04-Templates/             # Sablon-*.md note templates (Turkish names) + two English templates
│                             # (software project kickoff, user interview)
└── 01-Library/ 02-Wiki/ 03-Projects/ 05-Inbox/ 06-Archive/   # empty folders
```

**Scripts included:** `inspect-pdf.py`, `process-source.py`, `validate-text.py`, `add-page-markers.py` (source pipeline); `split-pdf.py`, `split-pdf-qpdf.sh`, `queue-chunks.py`, `merge-chunks.py/.sh` (large books); `zotero_doctor.py`, `zotero_search.py`, `zotero_import.py` (Zotero); `lint-vault.py`, `test-vault-system.py` (health checks); `md-to-docx.sh`, `_reference-times-new-roman.docx`, `fix-docx-fonts.py`, `deck_kit.py`, `forecast_bakeoff.py` (outputs).

---

## Quick start

**Which guides you need:** everyone does Guides 0–2 (Claude Code, Obsidian, Git). Do Guide 3 before your first PDF. Guides 9–10 are for Zotero users. The rest are optional. You need a paid Claude plan; Jev also needs a TypeSafe account.

1. Copy `vault-starter/` to where you want your vault, rename it (e.g. `Second Brain`), and open it in Obsidian. The folders already exist, so skip the folder-creation step in Guide 1.
2. Follow Guide 0 in `guides/Integration-Setup-Guides.pdf` to install Claude Code.
3. Follow **Guide 3** to install the pipeline tools: Homebrew, poppler, OCRmyPDF/Tesseract (plus language packs), qpdf, Python with the packages in `00-System/requirements.txt` (in a `.venv` inside the vault, already git-ignored), and pandoc. It ends with `process-source.py --doctor`, which must report "All dependencies available".
4. Run `git init` in the vault (Guide 2). `.gitignore` already covers the Zotero key file and `.venv/`.
5. **Zotero (optional, Guides 9–10):** open `00-System/Config/zotero-integration.yml` and replace `YOUR_ZOTERO_LIBRARY_ID` with your own ID (`.venv/bin/python 00-System/Scripts/zotero_doctor.py` detects it). Replace the example `"My Collection": "My-Project"` mappings with your own, or delete them. To write notes back to Zotero, create your own API key and save it as `00-System/Config/.zotero-web-api-key`; Guide 10 shows how to enter it at a hidden prompt. Never paste it into a chat or a command line.
6. Add any other guides you want (Claude in Chrome, NotebookLM, Jev, …).
7. Start Claude Code in the vault, put a PDF in `01-Library/Originals/`, and say `inspect raw`.
8. Start your first project with the "Start a new project" prompt in `guides/PROMPTS.md`.

---

## Not included (on purpose)

- **Credentials:** the Zotero Web API key, the Jev/TypeSafe key (`~/.config/typesafe/key`) and `.claude/settings.local.json`. Make your own.
- **Personal research:** all wiki pages, sources, reports, project folders, and the real `index.md` / `log.md`.
- **Personal identifiers:** the Zotero library ID, the original vault's absolute paths and the original project names were replaced with placeholders. Scripts now find the vault root on their own.
- The old `CLAUDE-SECOND-BRAIN-USAGE-GUIDE` files and their PNGs were left out. They described an older folder layout and one specific project; `guides/` replaces them.

## Notes

- `ux-redesign` is a UI/UX method for making an interactive page simple and user-friendly: a first-time-visitor audit, few views, essentials first, short version first with "Go deeper", plain language, clickable affordances. It includes tested code patterns and `scripts/link_check.js` (needs Node.js and `playwright-core`). Use it together with `web-artifact-workflow`.
- `course-hub-builder` builds one interactive page for a whole course. Its template (`assets/course-hub-template.html`) is a neutral example, a fictional course ("EX 101 · Evidence and Public Policy"), built from a real course hub with every course-specific value replaced by a [bracketed] placeholder. Fill each placeholder from your own verified materials.
- `explainer-video` makes narrated, captioned explainer videos drawn in code: a 16:9 whiteboard, a 9:16 colored-pencil short, or an interactive in-page player. It needs Python with `kokoro-onnx` (local text-to-speech; download the model files from the kokoro-onnx releases), `ffmpeg`, Node.js with `playwright-core`, and a music track whose licence you have checked (CC0 recommended; none is bundled). Fonts and the drawing library are bundled with their licences.

- `AGENTS.md` is the same manual as `CLAUDE.md` for Codex and other agents. If you edit one, mirror the change in the other.
- The system files were re-synced on 2026-10-06 after the vault's restructure: a short `CLAUDE.md` with the detailed workflows in `VAULT-WORKFLOWS.md`, session handoff (each project keeps a short `PROJECT-STATE.md`; see `ENGINEERING-CONTRACT.md` §2) and `LESSONS-LEARNED.md`. Project names and personal examples were replaced with placeholders.
- The worked examples in `Second-Brain-Guide` (a terrorism data analysis and a hypothetical investment review) are illustrations only. Their data and notes are not included.
- The templates in `04-Templates/` have Turkish filenames (*Sablon* = template, *Kaynak Notu* = source note, *Karar* = decision, *İddia–Kanıt* = claim–evidence).
