---
name: web-artifact-workflow
description: Quality workflow for any interactive web page or published artifact built in this vault (course hubs, workshop pages, study pages, dashboards, simulators, explainers) — PLAN → DESIGN → CONTENT → MOTION → BUILD → AUDIT → LAUNCH, adapted from a 7-role website workflow, with an automated accessibility/layout audit script and a launch checklist. Use whenever building, revising, auditing or launching an HTML page or artifact; also when the user asks to "audit", "polish", "make production-ready" or "launch" a page.
argument-hint: '<page.html or artifact url> [--audit-only] [--routes a,b,c]'
disable-model-invocation: false
---

# Web Artifact Workflow

## Purpose

A seven-step pass that every interactive page in this vault goes through before and after publishing. It adapts a common "website team" prompt set (architect, UI/UX designer, landing-page writer, motion designer, full-stack developer, auditor, launch) to **private, evidence-first tools for students and colleagues**. Steps that only make sense for marketing sites are adapted or skipped on purpose (see the table).

Use it together with:
- the built-in `artifact-design` guidance (page contract, theming, layout) and `dataviz` (any chart);
- `ux-redesign` when the page needs simplifying or restructuring, not just polishing (first-time-visitor audit, information architecture, progressive disclosure, affordances); it runs inside steps 1–3 below;
- the domain builder, if there is one: `course-hub-builder` (whole-course pages), `00-System/WORKSHOP-DESIGN-STANDARD.md` (in-class workshops), `presentation-builder` (decks; not web pages).

`RESEARCH_PROTOCOL.md` still governs every fact on the page.

## The seven steps, adapted

| Step | Role | Do | Skip or adapt |
|---|---|---|---|
| 1. PLAN | Website architect | Sitemap (sections and hash routes), the **main user journey**, the one action that matters most (for students: open this week, do the workshop, review). Decide the release policy and what is real vs. labelled fiction. | "Conversion funnel" means getting people to do the learning task, not buy something. |
| 2. DESIGN | UI/UX designer | Reuse the existing family look in the project (tokens, fonts) before inventing one. Type scale, spacing, components, visual hierarchy; both themes; phone width. | Don't restyle a page that already matches its siblings just to look "premium". |
| 3. CONTENT | Landing-page writer | Clear headline and **one primary call to action** per view; a short "N things to do" list; an **FAQ built only from governing documents** (syllabus, policies); plain words. | **Never** add testimonials, social proof, user counts, urgency tricks or invented quotes. That would be fabrication under `RESEARCH_PROTOCOL.md`. |
| 4. MOTION | Motion designer | At most: a short view fade-in (≤ 200 ms, starting from a visible state), hover lift on cards, clear focus rings. All of it off under `prefers-reduced-motion` and a page "Reduce motion" setting. | No scroll-triggered reveals, parallax, autoplay or content hidden at `opacity:0`. |
| 5. BUILD | Full-stack developer | Single responsive file (or file + supporting files); data in one block at the top of the script; keyboard support (Enter/Space on custom controls, arrow keys in maps/lists, Esc closes popups); search when the page has more than ~5 sections; `localStorage` wrapped in try/catch for per-viewer conveniences only. | No frameworks unless they do substantial work; no external calls beyond the artifact CDN allowlist. |
| 6. AUDIT | Website auditor | Run `scripts/audit_page.js` (below), then fix **every** violation; check screenshots once. Check performance: page weight; heavy libraries (PDF.js etc.) loaded only on first use. | **SEO is not applicable** to private artifacts. Don't add meta keywords, sitemaps or indexing tags. |
| 7. LAUNCH | Final polish | Write a **launch checklist** into the project's `PROJECT-STATE.md`; republish to the same URL; record changes in `DECISIONS.md` and `log.md`. | "Deployment" = publishing an artifact plus sharing. Sharing is the owner's action; never claim it's done unless the publish result says so. |

## Media and files on the artifact host (learned 2026-10-13)

- Published media have **no byte-range support**. Fetch video and audio once as a Blob and play it from an object URL, or seeking won't work.
- **Not served:** `.vtt` and `.m4a`. Embed captions as a Blob `<track>`, and use `.mp3`, `.ogg` or `.wav` for audio. The publish error lists the served types.
- Give every video a **poster** that shows content.
- A page copied alone to another computer loses its `media/` and `pdfs/` folders. Share the link, or embed small media as `data:` URIs when the page must travel as one file.
- Details and code patterns: the `course-hub-builder` skill, section "Video, audio and captions".

## Step 6 in detail: the audit

```bash
# serve the page folder
python3 -m http.server 8765 &            # from the folder holding the page and its files
# run the audit (Playwright-core path needed once per machine)
PLAYWRIGHT_CORE=/path/to/node_modules/playwright-core \
  node .claude/skills/web-artifact-workflow/scripts/audit_page.js \
  http://localhost:8765/page.html home,map,weeks,w06,exam ./shots
```

The script checks every route at **1280 px light** and **390 px dark**:
- axe-core WCAG 2 A/AA + best-practice violations (axe is downloaded once from cdnjs and cached next to the script);
- console and page errors (favicon 404s ignored);
- horizontal overflow;
- tap targets under 24 px. Links inside sentences are counted separately, because WCAG 2.5.8 exempts them.

It exits 1 if there are violations, errors or overflow, so it can gate a publish.

**Fixes that came up in practice (a course hub):**
- `html-has-lang`: the publish skeleton has no `lang`, so set `document.documentElement.lang="en"` at the top of the script.
- `color-contrast` on tinted chips: add a darker `--x-text` token for text on `--x-soft` backgrounds, defined in both themes.
- `nested-interactive`: an SVG holding focusable nodes must be `role="group"` with an `aria-label`, not `role="img"`.
- `heading-order`: card titles under an `h1` become `<h2 class="h3">` (style by class, structure by level).
- Small targets: give progress-bar links a 24 px hit area with the visible bar drawn by a pseudo-element; standalone small links get `display:inline-block; padding-block:4px`; checkboxes ≥ 1.5 rem.

Then look once at the screenshots (map/diagram, one detail view, every chart type, phone width), fix what shows, and stop. No loops.

## Step 7 in detail: launch checklist template

Copy into `PROJECT-STATE.md` and tick items off as they happen:

```markdown
### <Page name> launch checklist
- [ ] Share the page from its Share menu: <artifact url>
- [ ] Share every artifact it links to (list them), or the links fail for viewers
- [ ] Open it as a non-owner (or ask one user) and test one of each link type and one file
- [ ] Fill remaining gaps: missing files, unknown dates/facts (list them)
- [ ] Post the link where users look (Canvas page / announcement / email)
- [ ] After first use: collect feedback (`04-Templates/template-user-interview.md`, feedback variant)
```

## Report to the user

State what each step changed, what was deliberately skipped and why, the audit result (before → after), and the open launch items with the exact action each needs.
