---
name: ux-redesign
description: UI/UX and web-design method for making an interactive page or artifact simple, clear and user-friendly — a first-time-visitor audit, then a redesign of the information architecture (few views, one entry point, essentials before optional extras, related content together), progressive disclosure (short version first, "Go deeper" for detail), plain language for non-technical readers, and interaction affordances (clickable cards, prev/next, back-to-top, click-outside close). Use when a page feels confusing, cluttered, "everything dumped in", hard to navigate, not striking, or not friendly for first-time or non-technical users; when the user asks to "simplify", "redesign", "make it user friendly", "review it as a first-time visitor", or "act as a UI/UX / web designer". Runs inside web-artifact-workflow (PLAN → DESIGN → CONTENT) and finishes with its audit.
argument-hint: '<page.html or artifact url> [--review-only]'
disable-model-invocation: false
---

# UX Redesign

## Purpose

Turn a page that holds the right content but overwhelms people into one a first-time visitor understands in seconds. It was learned redesigning an explainer hub that had 9 equal tabs, a 14-section wall of text, duplicated material and essentials mixed with extras (the owner called it "a protein soup with everything dumped in"). The redesign cut it to 4 views, put one thesis on the first screen, showed the short version first and hid detail behind "Go deeper". It lost nothing.

This skill is the **design method**. `web-artifact-workflow` is the **quality gate** (audit, accessibility, launch). Use both: this skill for steps 1–3 of that workflow, then its audit script and launch checklist. The built-in `artifact-design` guidance still sets the page contract (tokens, both themes, fonts, CDN rules), and `RESEARCH_PROTOCOL.md` still governs every fact.

**Never drop content to simplify.** Move it, layer it, or merge duplicates. Every verified sentence, figure, viewer and tool keeps working. Old links redirect.

## Step 1 · First-time-visitor audit (before touching code)

Open the live page at desktop and phone width as someone who has never seen it. Answer in writing:

1. **What is this, in one sentence?** Can a visitor say it after 5 seconds on the first screen?
2. **Where do I start?** Is there one obvious first action, or many equal ones?
3. **What do I need vs. what is optional?** Is the order by importance?
4. **Where is X?** Pick three things a user would look for. Is each in exactly one obvious place?
5. **What can I click?** Does everything that looks clickable work, and does everything clickable look clickable?
6. **Could a non-technical person follow it?** Count the undefined terms on the first screen.

Symptoms that mean "redesign, don't polish":

| Symptom | Seen as |
|---|---|
| More than ~5 top-level tabs of equal weight | "Too many doors" |
| First screen asks the visitor to read or choose before showing the point | No thesis |
| One view holds more than ~6 sections at the same level | A wall |
| The same material in two or more places | Duplication, so people can't tell which one is canonical |
| Optional extras listed before or mixed with essentials | Wrong order |
| An explanation and its picture in different places | Split content |
| Case-specific numbers in a general explainer | Distracts general readers and leaks private detail |
| Cards, boxes or figures that look interactive but aren't | Broken affordance |

Write the verdict as 3–5 bullets in the reply before redesigning. If the user already gave feedback, quote it and map each point to a fix.

## Step 2 · Information architecture

- **4–5 top views at most**, each with one job. A pattern that worked: **Home** (what it is, why, ways in) · **How it works** (understanding) · **Build/Use** (doing) · **Library** (everything to view or download).
- **Home = thesis + one primary call to action.** The headline states the single idea. A secondary action and a "short on time?" link are fine; five persona cards are not.
- **Ways in by intent and time, not by persona.** For example "Get the idea · 10 min", "Understand it · 30 min", "Build your own · 2–3 h", each with 3 concrete steps.
- **Essentials before optional extras, everywhere:** chapter order, guide lists, tables. Label them "Essential" and "Optional", and keep stable IDs (guide numbers) even when the display order changes.
- **Co-locate:** an explanation, its figure and its example sit together. Ask "if I read this paragraph, is the picture right here?"
- **One canonical place per item.** Merge duplicates; link to the canonical place instead of repeating.
- **Keep old links working** with an alias map from every old hash to its new place (see `references/patterns.md`).
- Number things only when they are a real sequence (setup steps, chapters read in order). Don't number a set of equal cards.

## Step 3 · Progressive disclosure

Every section has three layers:
1. **The short version:** 2–3 sentences in plain words, visible.
2. **One key visual or interactive**, visible: the picture that carries the idea.
3. **"Go deeper"**, collapsed: tables, extra figures, file names, edge cases.

Links that point into collapsed detail must open it. A section with nothing worth hiding doesn't need a "Go deeper".

## Step 4 · First screen

- **The hero states the thesis and shows the most characteristic thing in the subject's world**, as real content, not decoration. Good examples: a real audit trail (sentence → note → page → original PDF); the system's own core diagram at full width.
- Size the hero to its content, not to the viewport. A wide diagram gets the full width (a two-row hero: headline and actions, then the visual). Never squeeze a detailed diagram into half the width.
- If the user dislikes a hero, swap it quickly. The content of the rejected version usually still belongs somewhere else on the page.

## Step 5 · Plain language for first-time and non-technical readers

- Define a term where it first appears ("Obsidian, a free note-taking app"), and keep a glossary with a pointer to it.
- Stat tiles only when the numbers are the point. In a general explainer, replace case-specific counts with general statements ("One idea per note", "Untouched originals").
- Add a two-minute primer where a skill is assumed (for example "Never used the Terminal?": how to open it, paste a command, replace placeholders, why nothing shows when typing a password).
- Mark "What's new" sections as being for existing users.
- Analogies help non-technical readers, and an interactive analogy helps more (for example a six-step office story). Label it as an analogy.
- Follow the writing rules of `artifact-design`: active voice, short sentences, a control says exactly what happens.

## Step 6 · Interaction affordances

Whatever looks interactive must be interactive, from both mouse and keyboard:
- story or step cards are `<button>`s that jump to their step;
- image and slide viewers have Prev/Next, a position counter, arrow keys, and close on Esc or a click outside;
- a "↑ Top" button appears after about 500 px of scrolling;
- anchor jumps land below the sticky header (measure the header; don't guess);
- alternatives (for example three prompts) are tabs with arrow-key support, not three stacked walls of text;
- Copy buttons copy the content only, every time, including a second click;
- search once there are more than about 5 sections, covering chapters, guides, prompts, terms and files.

Working code for each is in `references/patterns.md`.

## Step 7 · Phone width (about 390 px)

- The top nav moves to its own full-width row, and all tabs fit without hidden scrolling.
- Wide tables and diagrams scroll inside their own container, which takes focus (`tabindex="0"`, `role="region"`, `aria-label`), plus a "swipe sideways" hint.
- Tap targets: 24 px minimum, 44 px for primary buttons.

## Step 8 · Visual design

- Reuse the project's existing tokens, and colours that already mean something (for example the colours your diagrams already use for each concept), before inventing new ones.
- One display face, one body face, one mono face for labels and file names; a clear type scale.
- Put the boldness in one place (the hero). Keep everything else quiet: plain cards, generous spacing, few borders.
- A dark hero in a light page: scope dark token values to `.hero`, so components inside it (diagrams, cards) render dark in both themes.
- Avoid the generic AI looks listed in `artifact-design`.

## Step 9 · Build so nothing verified is retyped

- Keep the new layout in a **template** and assemble the page with a **builder** that carries the verified content data, interactives and viewers over from the previous version (for example `_build/<page>_redesign/template.html` plus `build_page.py`).
- Back up the previous published version before replacing it.
- Patch reused code in the builder with exact-match replacements that assert they matched once.

## Step 10 · Verify, publish, record

1. Syntax-check the script (`node -e "new Function(...)"`).
2. Run `web-artifact-workflow/scripts/audit_page.js` on every view at 1280 px light and 390 px dark, and fix every violation. Typical ones after a redesign: an unfocusable scroll region, small brand or text links, heading order.
3. Run `scripts/link_check.js` (this skill): every internal link lands its target below the sticky header and opens enclosing `<details>`.
4. Write one feature test per new interaction (click a story card, Prev/Next, back-to-top, prompt tabs, Copy twice) with Playwright, and save it in the project's `_build/` tests folder.
5. Look once at the hero and one detail view at both widths, fix what shows, then publish.
6. Record the decision (what changed and why, in the user's words) in `DECISIONS.md`, add the launch checklist to `PROJECT-STATE.md`, and log the change.

## Report to the user

Start with the first-time-visitor verdict (3–5 bullets), then the new structure as a small table (view → what it does), how each piece of user feedback was handled, what was kept, and the checks run (audit before → after, tests). Mention old links still working. List open items with the exact action each needs.
