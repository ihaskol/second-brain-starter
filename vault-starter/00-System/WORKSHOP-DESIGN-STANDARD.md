---
title: Workshop Design Standard
created: 2026-10-06
updated: 2026-10-06
status: active
scope: vault-wide (any project that builds in-class group workshops)
---

# Workshop Design Standard

This is the general logic for in-class group workshops built in this vault. It comes from a redistricting simulator built for a university politics course (2026-10-04/05), which the user singled out as the model, and from its generalisation to all the other workshops in that course on 2026-10-06. It sits under `RESEARCH_PROTOCOL.md`: every fact, figure, and quotation in a workshop follows the same evidence rules as any other deliverable.

## 1. What a workshop is for

A workshop makes students **do** the method from the week's readings (measure, code, aggregate, design, audit), not just discuss it. Each workshop has:

- **one skill** taken from the readings (for example, "two coders, then agreement");
- **one artifact** the team produces and submits (a code, a memo, a redesigned form);
- **one comparison moment** where teams see each other's answers side by side and the class discusses why they differ.

## 2. The three-format rule

Every workshop ships in three formats with the same content:

| Format | File | Use |
|---|---|---|
| Interactive (primary) | `<Wn>-Interactive-Workshop.html` (offline single file) + a published artifact link | Teams work on one laptop; autosave; built-in timer; submission code |
| Word | `<Wn>-Student-Worksheet.docx` + `<Wn>-Instructor-Guide.docx` | Paper backup; accessibility; printing |
| Excel | `<Wn>-Workshop.xlsx` | Calculations that should be visible as formulas (agreement and κ, weighted aggregates, simulators, severity totals) |

The paper and spreadsheet versions are generated from the same configuration as the interactive one, so they cannot drift apart.

## 3. Structure of the interactive version

1. **Header:** team name, members, and an agenda timer (choose a step → Start; "Big" puts a full-screen countdown on the projector).
2. **Tabs follow the class agenda**, one tab per part (typical: brief → individual work → team work → reveal → write-up). Each tab opens with a one-line instruction saying what to do and how long it takes.
3. **Predict before reveal.** Wherever there is a "right answer" (real findings, subgroup data), students commit to a prediction first; the reveal needs two clicks so it can't happen by accident.
4. **Evidence chips.** When students build a grid or matrix, each cell asks which source card supports it (A–G), so claims stay tied to readings.
5. **Self-check after commitment.** Model answers appear only after the team has answered an item.
6. **Submit tab:** a checklist of what is complete, plus a **team code** (compressed text of all answers). Teams paste it into a Canvas text-entry assignment. File downloads are not relied on, because artifact pages block them.
7. **Class comparison tab:** the instructor pastes all team codes and gets block-by-block aggregation (vote counts, averages, all text answers) to project for the debrief.
8. **Instructor keys** are shown only when the address ends with `#instructor`. There is no visible button, so students don't stumble on keys.
9. **Robustness:** works offline; no external libraries; autosave in browser storage, wrapped so it never breaks the page; light and dark themes; usable at phone width; keyboard-accessible.

## 4. Content rules

- **Real data or labelled fiction.** Every number is either traced to a source with a page number (shown in the footer and the instructor guide) or marked **fictional** on screen. Mixed designs are allowed and encouraged (real population shares, fictional vote results) as long as the label says which is which.
- **Answer keys cite pages.** A key that states a finding gives the page.
- **No current events beyond what was verified** at build time; date-sensitive facts (for example, regulatory deadlines) carry the date they were checked.
- **Times New Roman** in Word and Excel outputs; English deliverables.

## 5. Timing pattern (75-minute session)

| Phase | Minutes | Purpose |
|---|---|---|
| Brief / warm-up | 5–10 | One concrete hook; state the skill |
| Individual work | 10–20 | Independent judgement before group pressure (essential for coding and rating tasks) |
| Team work | 20–30 | Compare, resolve, build the artifact |
| Reveal / pressure test | 10–15 | Real findings or random events challenge the artifact |
| Debrief with class comparison | 10–15 | Projected comparison; "why do teams differ?" |

## 6. Instructor guide contents (per workshop)

At a glance (goal, link, offline file, keys, group size) → before class (share link, Canvas text-entry assignment, print backups) → minute-by-minute plan → tab-by-tab description → answer keys and model answers → debrief prompts → assessment (participation + 5-point rubric) → troubleshooting → accessibility → sources and data.

## 7. Build and quality gates

Reference implementation (not included in this pack):
- `engine.html` (shared page; the config is injected);
- `lib.py` (build);
- `w*.py` (one config per week);
- `gen_docs.py` (Word/Excel generator);
- `tests/` (Playwright smoke tests).

Before handing over a workshop:

1. A smoke test runs every tab with no console errors.
2. The team code round-trips through Class comparison.
3. Keys appear with `#instructor` and not without.
4. There is no horizontal overflow at 390 px.
5. Every number is checked against its source, or labelled fictional.
6. Word and Excel are regenerated from the final config, and Excel formulas are checked against the interactive result.
7. The accessibility audit passes with no violations: `.claude/skills/web-artifact-workflow/scripts/audit_page.js` (axe-core, both widths and themes, tap targets).
8. A launch checklist (share the link, test as a non-owner, post on Canvas) goes into the project's `PROJECT-STATE.md`; see the `web-artifact-workflow` skill.

## 8. Sharing

Published artifacts start **private**. The instructor shares each link from the page's Share menu before class. The offline HTML is always uploaded to Canvas as a backup.
