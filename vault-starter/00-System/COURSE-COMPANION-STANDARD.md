# Course Companion Standard (course chatbots)

Rules for any course-specific chatbot built in this vault. First built for a real course hub in October 2026. How-to: the `course-companion` skill (`.claude/skills/course-companion/`).

`RESEARCH_PROTOCOL.md` governs every fact the chatbot shows.

## 1. What it is

- A side panel on a course page: an artifact, usually the course hub.
- It answers **only from approved course materials** and shows the source of every answer.
- It is a **tutor with guardrails, not an answer engine.** Evidence:
  - an unrestricted chatbot raised practice scores but lowered later exam scores without AI by 17% (Bastani et al., 2025, *PNAS*);
  - a purpose-built tutor outperformed active learning (Kestin et al., 2025, *Scientific Reports*).
  - Check both papers yourself before citing them to students (`RESEARCH_PROTOCOL.md`).

## 2. Two tiers (required)

| Tier | Who | How it answers |
|---|---|---|
| **1 · Course answers** | everyone; no account needed | Matches the question to knowledge-pack items in the page (keyword + IDF scoring) and quotes the best item, plus a close second as "Also relevant". No AI runs. |
| **2 · AI modes** (Explain · Coach · Practise) | viewers signed in to Claude | In-page `sample` calls, which spend the **viewer's own** Claude usage and ask consent on first use. The page retrieves the items first and passes them in the prompt; the answer must cite item ids, or it is replaced by "not in the course materials". |

Tier 2 is optional; Tier 1 must always work. Never make a student depend on having an AI account.

## 3. Guardrails (each one is testable)

1. **Cites its source.** Every answer shows citation chips (e.g., "Week 9 lecture, slide 6").
2. **Says when it doesn't know:** "I can't find this in the course materials", plus **Send to instructor**.
3. **Deadlines and policies are quoted verbatim** from the course data, never generated. In AI modes, a strong syllabus or policy match goes to Tier 1.
4. **Course rules are labelled separately from university rules.** University rules carry "Pending university policy check".
5. **Never writes graded work.** A request like "write/draft/do my memo/report/reflection/exam…" gets a fixed refusal plus coaching.
6. **Personal matters** (grades, extensions, accommodations, emergencies) are referred to the instructor's office hours and email.
7. **"This looks wrong"** on every answer feeds the instructor's queue.
8. **Coach mode** asks one question at a time (claim → evidence → alternative → what would change your mind); a hint only after two stuck turns.
9. **Practice feedback** is for ungraded answers only: one strength, one criterion to improve (rubric words), one question. No score and no rewrite.

## 4. What goes into the knowledge pack

| Include | Exclude (always) |
|---|---|
| Syllabus fields, calendar, grading, policies | Answer keys, exam items, QTI files |
| Page-verified reading findings with page numbers | **Full texts of licensed readings**: copyright on a shared page, and many university libraries forbid uploading licensed resources to AI tools |
| Lecture and article-analysis slide text (no speaker notes) | Speaker notes, instructor-only guides |
| Student study guides, glossary, FAQ, corrections logs | Student work or any personal data |
| Methods toolbox, synthesis or practice prompts | Unverified notes, AI-generated summaries |
| Open Access full texts **only after a licence check** | |

Build the file with `00-System/Scripts/build_companion_kp.py`. Publish it next to the page as `data/<name>-kp.json`; the page fetches it and falls back to the built-in items.

## 5. Privacy and data

- Only **anonymous** queue items are stored (unanswered questions; answers marked wrong): no name, no ID.
- The platform rule "write implies read" (a db rule can't be write-only) means Contributors can read anonymous queue rows. Decide this per course: accept it, or use per-person `{self}` paths.
- Signed-out viewers can't write to the db. Show the office-hours fallback instead of failing.
- The panel reminds students not to type personal or health information.

## 6. Accessibility and UI

- The panel is `<div role="dialog">`, not `<aside role="dialog">` (axe aria-allowed-role). It needs an Esc close, a labelled input and a visible focus ring.
- **Audit with the panel open** as well as closed (e.g. a `_build/test_companion.js` axe script).
- A logo or mascot is optional. Load its images only when the panel is enabled. University mascots or marks need a brand check before wide sharing.

## 7. Release checklist

- [ ] Knowledge pack rebuilt from current verified materials; exclusions respected
- [ ] Answer test (`_build/test_companion_answers.js`) on at least 10 questions:
  - deadline → verbatim syllabus;
  - definition → glossary;
  - reading finding → slide or finding with page;
  - study question → guide;
  - "write my …" → refusal;
  - off-topic → not found;
  - personal → referral.
- [ ] axe 0 violations with the panel open (desktop light and phone dark)
- [ ] Student view tested (owner-only switches off; no private links shown to students)
- [ ] Instructor told how to read the queue (about 10 min a week) and how to switch the chatbot off (rebuild with `--no-companion`)
- [ ] Decision recorded in the project's `DECISIONS.md` (who sees it, from when)
