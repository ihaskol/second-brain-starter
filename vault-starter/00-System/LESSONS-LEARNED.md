---
title: Lessons Learned (operations)
created: 2026-10-06
updated: 2026-10-06
status: active
scope: vault-wide
---

# Lessons Learned

Hard-won operational lessons from building in this vault. Each one cost at least one failed attempt. Read the section for the tool you are about to use. Project-specific dead ends live in each project's `PROJECT-STATE.md` under "Tried and rejected". Add a line here when a lesson applies beyond one project, with the date and where it happened.

## Keynote, Pages, PowerPoint files

- **Never touch documents the user has open.** Check first: `osascript -e 'tell application "Keynote" to get {name, modified} of every document'`. An export script once closed two user-edited decks without saving, and the edits were lost (2026-10-06).
- **Keynote export:**
  - Copy decks to a folder **inside the vault** (Keynote's sandbox can't read `/private/tmp`) and open them with `open -a Keynote <file>`.
  - Export only the document opened by name, then close only that one: `.claude/skills/course-hub-builder/scripts/export_pdf_keynote.applescript`.
  - Wrap each call in a watchdog: `perl -e 'alarm 90; exec @ARGV' osascript …`.
  - If two attempts time out, a dialog is blocking Keynote. Stop and tell the user (2026-10-04, 2026-10-06).
- **Keynote saving a `.pptx`** can delete the original filename and create `_2.pptx`. Check `git status` after Keynote touches a file (2026-09-21).
- **Pages:** don't round-trip a `.pages` file while Pages has unsaved copies open. Ask first (2026-08-30).
- **Calibri theme bug:** setting fonts per run isn't enough. The deck or document theme (`ppt/theme/themeN.xml`, `word/theme/theme1.xml`) defaults to Calibri. `deck_kit.save()` patches decks; `00-System/Scripts/fix-docx-fonts.py` patches Word files (2026-09-22).
- **Keynote import bug:** decks with no `notesMasterIdLst` lose their notes in Keynote. `deck_kit.save()` adds it (2026-09-22).
- **No LibreOffice on the original machine.** For a first-page thumbnail of a `.docx`, use `qlmanage -t -s 1200 -o out file.docx`.

## Pandoc and Word

- **Check output before replacing originals.** A guessed output flag once overwrote two `.docx` files with HTML. Run `file new.docx` first (2026-08-30).
- `md-to-docx.sh` replaces the YAML `title:` with the filename. For documents with a real title, call pandoc directly (2026-09).

## Python, shell and macOS

- macOS sometimes blocks Python started from a working directory in Documents, or denies directory listing mid-session. Run from the session scratchpad, but **copy every script and result back into the project before the session ends**. Scratch folders are deleted (2026-10-05, 2026-10-06).
- Headless browser tests: `npm i playwright-core` in the scratchpad works with the cached Chromium in `~/Library/Caches/ms-playwright/`. No browser download is needed.

## Web pages and artifacts

- **Artifact pages block downloads, `print()`, `mailto:` and cross-origin workers.** Submit work with copyable codes, show email addresses as selectable text, and load PDF.js's worker as a `<script>` before `pdf.min.js` (2026-10-05, 2026-10-06).
- **Local test servers garble characters** unless the page has `<meta charset="utf-8">` (2026-10-06).
- **Run the accessibility audit before publishing:** `.claude/skills/web-artifact-workflow/scripts/audit_page.js`. A page that passed smoke tests still had 4 violations: `lang`, contrast, nested interactive, heading order (2026-10-06).
- **Charts:** validate the palette for light and dark with the `dataviz` script. Draw bars proportionally: the bar sits in a wrapper track and the value label in its own column (2026-10-06).

## Sources, facts and the web

- **Verify slide facts against full texts with page numbers, not abstracts or older slides.** Early course decks had many invented or misattributed numbers. A numeric cross-check script that matches every number on a deck to a source text fixed this (2026-10-04/05).
- **Earlier notes can be wrong too.** A logged correction ("this figure is not in the source") was itself wrong; the figure was on a later page. Re-check before repeating a correction (2026-10-05).
- **Syndicated news copies can misstate details,** for example which court decided a case. Check the original outlet (2026-10-05).
- **X/Twitter posts** return HTTP 402 to direct fetches. The public mirror `https://api.fxtwitter.com/<user>/status/<id>` returns the text, including X "articles" (2026-10-06).
- **Some publishers block scripted downloads** (Springer). Read the open-access version in the browser (2026-10-05).
- **Never combine counts across conflict datasets** (ACLED, GRID, UCDP define "an event" differently), and check redistribution terms before sharing raw data. GRID and ACLED restrict it (a conflict-data project, 2026-09).

## Jev (TypeSafe decision model)

- **Never evidence.** Jev outputs choose what to check, route or prioritise. They never appear as a reason, citation or verification status in any vault page or deliverable (`RESEARCH_PROTOCOL.md`; audited Jev deck, 2026-09-29).
- **Use it for repeated decisions over known options:** triage, routing, ranking, flagging. Use the LLM for writing and code for anything computable (counts, dates, test results, file checks).
- **Build the state in code:** short, factual fields only. Irrelevant context lowers accuracy.
- **Keep thresholds in code**, scaled to the cost of being wrong. Read the full probability spread, not just the winning label. Low confidence means a person or a stronger model decides.
- **Shadow mode first:** run it beside current practice, log agreement, and set thresholds from that log before Jev decides anything. Pin the model version and keep the questions with the results.
- **Privacy:** no student data, personal data or unpublished manuscripts go to the API without approval. Prefer filenames and metadata over full text.
- **The key** is entered only at a hidden `read -s` prompt in Terminal, never in chat or a command (2026-09-29).

## Sessions and project state

- **Write the handoff:** at the end of each session, update the project's short current state and add a session-log entry, including what was tried and rejected. See `ENGINEERING-CONTRACT.md` §2 (2026-10-06).
- **Keep `PROJECT-STATE.md` short** (about 150 lines). A 102 KB state file couldn't be read in one pass. Move old detail verbatim to `PROJECT-HISTORY.md` (2026-10-06).
