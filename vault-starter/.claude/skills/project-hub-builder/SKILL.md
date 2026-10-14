---
name: project-hub-builder
description: Build one interactive page that explains and supports a project, tool or method for outside readers. It has four views (Home with "start where you are" paths, How it works with short answers and "Go deeper", Build with step-by-step guides that end in a check and copyable prompts, and Library with video, slides, documents, figures and what's new), plus search, a sharp in-page PDF viewer, a seekable video and light/dark themes. Use when the user asks for a hub, landing page, explainer site, portal, "one page with everything about X", or a page to share a project or method with colleagues, but not for a course; for a course use course-hub-builder.
argument-hint: '<project folder> [--audience …] [--no-video]'
disable-model-invocation: false
---

# Project Hub Builder

## Purpose

Turn a project's verified materials into one page that a first-time visitor understands in minutes and that an expert can still dig into: the problem, how it works, how to build or use it, and every deck, document, figure and video in one place. The pattern comes from a real hub that explains an AI research system. `assets/project-hub-template.html` is that hub with all its content replaced by `[bracketed]` placeholders.

Use `course-hub-builder` instead when the page serves a course: weeks, readings, exams, assignments.

## Governing rules

- Run **`web-artifact-workflow`** around the build: PLAN → DESIGN → CONTENT → MOTION → BUILD → AUDIT → LAUNCH. Its "Media and files on the artifact host" section applies to video, audio, captions and the PDF viewer. Its `audit_page.js` is the accessibility gate before every publish.
- Use **`ux-redesign`** for structure: the first-time-visitor audit, few views, the short answer first with "Go deeper", plain words, controls that look clickable.
- Everything on the page comes from verified project material (`RESEARCH_PROTOCOL.md`). Benefits that weren't measured are called **design goals**, not results. Invented examples are labelled. No testimonials, user counts or SEO.
- Don't publish private details: personal paths, keys, account IDs, names of other people's projects. Scan before publishing and before sharing.

## Structure (keep it)

| View | Holds | Notes |
|---|---|---|
| **Home** `#start` | Title and one-sentence promise; **Why it exists** (without it → what goes wrong → what this does); the video (optional); **Start where you are** (3 paths with a time estimate, e.g. "Get the idea · 10 minutes"); the latest 3 changes | One primary action per view |
| **How it works** `#how` | Chapters (`#how-<id>`), each with a 2–3 sentence answer first, figures, then **Go deeper**. A **What it can't do** chapter and a glossary | The honest-limits chapter is required |
| **Build** `#build` | **Before you start** (safety rules: never paste keys into a chat…); guides in setup order, each step with **where to type** (Terminal / inside the AI tool / browser / app), a copyable command and a **Check** line; a progress bar saved in this browser; copyable **prompts** | Essential guides first, optional ones marked |
| **Library** `#library` | Video; slides and documents in the in-page PDF viewer; a figures gallery with a lightbox; **What's new** | The subnav lists every section |

Plus a header **search** (chapters, glossary, guides, prompts, decks, documents, figures; arrow keys and Esc work), a light/dark/system theme setting, a footer (credit and licence, the date facts were last checked, how to cite this), and `ALIAS` entries so old links keep working after a redesign.

## Build steps

1. **Gather (bounded):** read the project state, the verified content (spine or report), the deck PDFs, the figures and the video files. Make a list of claims, each with its source.
2. **Plan:** fill the CONTENT block in a copy of the template: `SITE`, `WHY`, `WAYS`, `CHAPTERS`, `GLOSSARY`, `SAFETY`, `GUIDES`, `PROMPTS`, `VIDEO`, `DECKS`, `DOCS`, `FIGS`, `NEW`. Leave nothing in brackets.
   - For a large hub, keep the data in its own file and join it to the template with a small build script, so later edits touch only the data.
3. **Media:** PDFs go in `pdfs/`, figures in `img/`, video and poster in `media/` (540p or 720p H.264, a few MB). Captions are WebVTT text inside `VIDEO.vtt`, because the host doesn't serve `.vtt`. For a narrated explainer, use the **`explainer-video`** skill.
4. **Test:** serve the folder, then run `scripts/smoke_test.js` and `web-artifact-workflow/scripts/audit_page.js` on every view at 1280 px (light) and 390 px (dark). Fix every failure, then look once at the screenshots.
5. **Publish** with the Artifact tool. Publish `pdfs/*`, `img/*` and `media/*` as supporting `files`. To replace a supporting file published in an earlier session, read it first. The artifact stays private until the owner shares it.
6. **Record:** in `PROJECT-STATE.md`, note the link, the version, what changed and the test results. Log design decisions in `DECISIONS.md` and add an entry to `What's new`.

## Technical notes (from the reference build)

- **Video:** fetched once as a Blob, so it can seek; one Blob URL serves every view that shows it. Use a poster frame with content.
- **PDF viewer:** PDF.js 3.11.174, rendered at `max(2, dpr × 1.5)` with a Full screen button. Links that point straight to the page's own files fail inside the artifact frame, so show files in the page.
- **State:** checkmarks and theme go in `localStorage` (wrapped in try/catch); the footer says so. Never use storage for anything shared.
- **Copy buttons:** use `navigator.clipboard` with a select-the-text fallback ("Press Ctrl/⌘+C").
- **Single source for repeated text:** when a prompt or guide also appears in a Markdown or Word handout, generate the handout from the hub's data, never the other way round. Make the generator stop at the end of the array it reads.
- **Taking the page offline:** a copied page loses `pdfs/` and `media/`. Share the link or a zip of the whole folder.
