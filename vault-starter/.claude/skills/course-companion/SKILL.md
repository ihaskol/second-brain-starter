---
name: course-companion
description: Add a course-specific chatbot ("course companion") to a course hub or course page. It answers only from approved course materials (syllabus, calendar, page-cited reading findings, slide text, study guides, glossary, FAQ) with a citation on every answer. It has two tiers (keyword answers for everyone, plus AI Explain/Coach/Practise modes for students signed in to Claude), guardrails (never writes graded work, quotes deadlines verbatim, refers personal matters to the instructor), an anonymous instructor queue, and an optional logo. Use when the user asks for a course chatbot, course assistant, AI tutor, FAQ bot, "chatbot based on the syllabus/readings", or to feed course materials or study guides into a chatbot.
argument-hint: '<course page or hub> [--logo image] [--owner-only]'
disable-model-invocation: false
---

# Course Companion

## Purpose

Give students a chatbot that answers from the course's own verified materials, shows where each answer comes from, and coaches instead of doing their work. Rules: `00-System/COURSE-COMPANION-STANDARD.md` (read it first). It was first built as a layer on a real course hub (2026-10); that course's code and data are not part of this starter pack, so build the layer below from the standard.

## Before building

1. Read the course project's `PROJECT-STATE.md` and `DECISIONS.md`. Who may see the chatbot, and from when? Is there a sensitivity, such as an AI complaint?
2. Load the `artifact-capabilities` skill. The chatbot uses `sample` (AI tier), `db` (queue) and `user` (owner check).
3. **If the course already has a page the instructor likes, add the chatbot as a layer. Never redesign the page.**

## Steps

1. **Knowledge pack.** Build it from verified materials only:
   ```bash
   python3 00-System/Scripts/build_companion_kp.py \
     --decks "<project>/Presentations/Week-*_v2.pptx" \
     --guide "<project>/Exams/<student study guide>.md" \
     --weekmap '{"04":"w03"}' --out "<project>/suite/data/companion-kp.json"
   ```
   - The page itself also builds items from the hub's data: calendar, readings with findings, glossary, corrections, FAQ, methods, synthesis prompts.
   - **Exclude** answer keys, exam items, speaker notes and licensed full texts (standard §4).
2. **Layer.** Write three files in the project's `_build/layer/`:
   - `layer.css` (panel styles);
   - `layer.html` (button and panel; `<div role="dialog">`);
   - `layer.js` (knowledge index, IDF matching, guards, Tier 1, Tier 2 `sample` calls, queue, owner switch).

   Keep the course constants at the top of `layer.js`: `COURSE` (contact, office hours), `RULES` (system prompt with the course name), `KP` (syllabus and policy items), `SUGGEST` (example questions).
3. **Apply it to the page** with anchored insertions that fail loudly if the page changes. Use a small build script that inserts the layer at named anchors and stops if an anchor is missing.
   - Keep the page's original source in `_build/source/`.
   - `--no-companion` gives the owner-only build.
4. **Logo (optional).** Make a cropped round avatar (about 192 px) and a banner (about 900 px wide) with PIL into `assets/`. The images load only when the panel is enabled. Flag any university mascot or brand for a brand check.
5. **Test** (scripts in the project's `_build/`):
   - `test_companion_answers.js`: about 10 questions covering deadline, definition, reading finding, study, "write my…", off-topic and personal;
   - `test_companion.js`: axe with the panel open, at 1280 light and 390 dark;
   - the `web-artifact-workflow` audit on every view;
   - a student-view check (no owner-only items, no private links).
6. **Publish** the page with `files` for `data/*.json` and `assets/*`, plus `capabilities: {db:{}, user:{}, sample:{}}`.
   - Then probe the db: write a queue doc, read it back, delete it.
   - The page's existing PDFs and files are kept on update.
7. **Record:**
   - the decision (who sees it, from when) in `DECISIONS.md`;
   - the artifact table and session log in `PROJECT-STATE.md`;
   - a `log.md` line.

## Known pitfalls

- `sample` spends the **viewer's** Claude usage. Signed-out students get Tier 1 only, so Tier 1 must be good.
- Keyword matching quotes notes; it can't write new explanations. Show a close second match ("Also relevant"). Weight rare terms (IDF). Boost the first author when the question names one. Boost glossary items only for definitional questions that already match.
- A db rule can't be write-only; anonymous queue rows are readable by Contributors (standard §5).
- Private links, such as a private sample page, must not be shown to students. Gate them on the owner check.
- After any change to the decks or guides, rebuild the knowledge pack and republish with the data file.
