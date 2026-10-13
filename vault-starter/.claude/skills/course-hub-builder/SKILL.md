---
name: course-hub-builder
description: Build one interactive, student-facing page for a whole course — course mind map with thematic threads, week pages (readings with verified findings, key-figure charts, verified news, in-page PDF slide viewer, workshop links, practice questions, missed-class path), exam prep, methods toolbox, assignments and support — designed for different learner types. Use when the user asks for a course hub, course page, course portal, "everything for the course in one page", or a whole-course interactive page for students.
argument-hint: '<project folder> [--release all|past-only] [--no-news]'
disable-model-invocation: false
---

# Course Hub Builder

## Purpose

Turn a course project's existing, verified materials into **one interactive page** that students use all semester: a course map, a page per class, slides they can read in the browser, workshop links, exam prep and support. The page *links and organizes* what already exists. It adds study tools, but no new unverified facts.

The template, `assets/course-hub-template.html`, is a neutral example: a fictional course ("EX 101 · Evidence and Public Policy") built from a real course hub, with every course-specific value replaced by a [bracketed] placeholder. Start from that template and replace the data block, the dates and the placeholders; don't redesign from scratch. Placeholders are not content: fill each one from your own verified materials.

## Governing rules (read first)

- `RESEARCH_PROTOCOL.md` governs every finding, number, quote and news item. `00-System/ENGINEERING-CONTRACT.md` governs writes. Follow the project's own `PROJECT-STATE.md` and `DECISIONS.md`.
- Apply your own deliverable standards (language, fonts, visuals).
- **Verified content only.** Every reading finding, chart number, practice question, "common mistake" and news item must come from a source already verified in the project, such as page-verified decks, a verification log, or the syllabus. Cite pages where the source does. If something isn't verified, leave it out; never fill a gap from memory.
- **News:** use news items already verified in the project (e.g. the decks' "In the news" slides). Show outlet and date. Add a URL only if the verified source records one. New web news requires web research plus `citation-verification` first, and the user's go-ahead.

## Inputs to gather (bounded retrieval)

1. `PROJECT-STATE.md`, `PROJECT-GRAPH.md`, recent `DECISIONS.md` entries: calendar changes, artifact links, open errors.
2. The current syllabus: schedule, readings, learning goals, grading, policies, resources.
3. The verified per-reading content. Extract text from the latest decks with `python-pptx`, saved to the scratchpad and read in parts. Use the research-design profile, results tables, practice questions, corrections logs and "In the news" slides.
4. Workshop configs and links (e.g. `Workshop-Documents/_build/links.json`, `cfg/*.json`).
5. The student PDFs that exist, and those still missing.

## Questions to ask before building (only if unresolved)

Use AskUserQuestion, at most three questions, with a recommended option first:
- **Calendar conflicts:** an exam moved onto a class day, or an undocumented session. Never guess dates; unknown sessions show "Session details on Canvas".
- **Release policy:** show all weeks, marking future ones "upcoming · may change" (recommended), or lock future weeks.
- **Missing PDFs:** export now or show "coming soon".

## Page design (keep this structure)

Single HTML file with a hash router. Tabs: **Start · Course map · Weeks · Workshops · Exam prep · Methods toolbox · Assignments · Support**, plus `#<weekid>` deep links. All course content sits in one data block at the top of the script (LINKS, PDF_READY, MODULES, THREADS, WEEKS, GLOSSARY, MISTAKES, DESIGN_Q, SYNTH, METHODS, PERSONAS, FIG, NEWS). Later edits touch only that block.

- **Start:** next class (computed from today's date), countdowns to real deadlines, semester progress bar, learner paths, the 4 most recent news items, the class-session rhythm, and the course's big ideas.
- **Learner paths:** planner, big picture, close reader, hands-on, exam-focused, missed a class, English as an additional language, quiet in class. Each is 2–4 links into the hub.
- **Course map:** SVG mind map (center → modules → sessions, in fixed columns, never overlapping) plus thread toggles that outline the weeks building each idea. Take threads from the syllabus's own framing, and label them "interpretive guide, not an exam key". Add a timeline list below as the accessible alternative.
- **Week page:**
  - big question
  - a content note where topics are heavy
  - readings: role chip, design chip, citation, one verified finding
  - **key-figure chart**
  - **In the news** (finding + "Connect" line)
  - "Check yourself" questions (labelled practice, not exam items)
  - a missed-class path
  - slides: in-page PDF.js viewer, "Open PDF" fallback, "PDF coming soon" when missing
  - workshop card, learning goal, threads, "I've reviewed this week" checkbox
- **Exam prep:**
  - link to any existing exam study page
  - flashcards and a searchable glossary
  - reading → design matching quiz
  - right-or-wrong items from the corrections logs (for students who studied old slides)
  - cross-week synthesis prompts with an outline box
  - 14-day plan from a chosen exam date
- **Methods toolbox:** design → strongest claim → what to watch → course readings; a six-step article-reading template; careful-wording table.
- **Assignments:** weighted what-if calculator (states that it is an estimate, Canvas governs), due dates, late policy, fieldwork guide, project-option chooser, the syllabus's AI-use statement.
- **Support:** instructor contact (address as selectable text plus a copy button; no mailto), attendance, alternate participation, discussion norms, wellbeing, accessibility, and academic resources, all from the syllabus.
- **Display settings:** theme (system/light/dark), text size, wider spacing, reduce motion.

## Technical rules (learned in the first real build)

- Artifact page contract: tokens on `:root` with both dark blocks; body background from a token; 16px gutter; no horizontal scroll at 390px; `<meta charset="utf-8">` at the top (local test servers otherwise garble the characters).
- **Privacy:** progress, outlines, calculator entries and settings go in `localStorage` only, wrapped in try/catch. Say so on the page. Collect nothing.
- **PDF viewer:** lazy-load PDF.js 3.11.174 from cdnjs. Load `pdf.worker.min.js` as a `<script>` **before** `pdf.min.js`, so it runs as a main-thread fake worker; cross-origin workers are blocked. Then `getDocument("pdfs/<file>")`. Publish PDFs as supporting `files` under `pdfs/`.
- **Charts:** load the `dataviz` skill first. Use thin horizontal bars with direct value labels, a legend when there are 2 or more series, a source line, and text in ink tokens. Run `validate_palette.js` for light **and** dark. The values that passed in the first build are light `#00806a,#a8720a,#2f62b0` and dark `#2fa88d,#b88a28,#5f8fd6`. Bars must be proportional: put the bar inside a wrapper track and the value label in its own grid column. Never subtract a fixed width from the bar.
- **Links** to workshops and other artifacts open in a new tab; they stay private until the owner shares them. Say so on the page and in the report.

## Slide PDFs (Keynote export, safely)

- **Never touch documents the user has open.** First check them: `osascript -e 'tell application "Keynote" to get {name, modified} of every document'`. Unsaved open documents mean the user is working, so leave them alone.
- Copy each saved `.pptx` to a temp folder **inside the vault**, with a unique name. Keynote's sandbox can't open copies in `/private/tmp`, and the AppleScript hangs.
- Open each copy with `open -a Keynote <file>`, then run `scripts/export_pdf_keynote.applescript <docName> <out.pdf>`. It waits for that exact document, exports slides only, and closes **only that document** without saving. Wrap each call in a watchdog (`perl -e 'alarm 90; exec @ARGV' osascript …`).
- If it times out twice, stop. Keynote is blocked by a dialog: tell the user, show "PDF coming soon", and continue. After a later export, add the files to `PDF_READY` and the publish set, republish, and delete the temp folder.

## QA (one pass, then publish)

1. Serve the folder (`python3 -m http.server 8765`) and run `node scripts/qa_hub.js <shots-dir> <page.html>`. Set `PLAYWRIGHT_CORE` to a local `playwright-core` path, and edit the script's `routes` and week IDs for the course. It checks every route at 1280 px light and 390 px dark for console errors and horizontal overflow, clicks the exam subtabs, a thread and the slide viewer, and saves screenshots.
2. Look at the map, one week page, and every chart type once. Fix what shows, then publish. No loops.

## Publish and record

- Publish with the Artifact tool (`icon: "map"`), with `root` set to the site folder and `files` mapping `pdfs/*`. It is private until shared.
- Save the page to `03-Projects/<Project>/Course-Hub/`.
- Update `PROJECT-STATE.md` (link, sections, sources, calendar choices, missing PDFs, QA) and `DECISIONS.md` (design choices and reasons). Append to the vault `log.md`.
- **Report to the user:** link and privacy; what each section contains; learner types covered; additions they didn't ask for; QA result; and open items with the exact action needed (sharing links, missing PDFs, unknown dates).
