---
name: presentation-builder
description: Turn source material (documents, data, research, notes) into a polished, editable PowerPoint deck. Adapts structure, tone, and design to the stated or inferred audience — executive/business, academic/teaching, general-public, technical, or sales/pitch.
argument-hint: '<source files or topic> [--slides N] [--audience executive|academic|general|technical|sales] [--cover]'
disable-model-invocation: false
---

# Presentation Builder

## Purpose

Transform source material — reports, research, data, notes, transcripts, or a topic the user describes directly — into a polished, **editable `.pptx` file**. Not an outline, not a written recommendation for what slides *could* look like: an actual PowerPoint file the user can open, edit, and present.

Every deck follows the same underlying discipline:

**Story → Evidence → Insight → Action → Design**

But *how* that discipline is expressed — vocabulary, title style, visual density, citation handling, color and type choices — depends on who the deck is for. Determining the audience is not optional framing; it changes concrete decisions throughout the build. See **Audience Adaptation** below before writing any slide.

---

## Step 0 — Determine the Audience

Before planning slides, decide (from the user's explicit statement, or inferred from the source material and its evident purpose) which audience mode applies. If genuinely ambiguous and it would change the deck significantly, ask — don't silently guess for a client-facing or graded deliverable.

| Mode | Typical context | What changes |
|---|---|---|
| **Executive / Business** | Leadership readout, strategy deck, client presentation | Conclusion-led titles, minimal text, KPI cards, business-implication framing, restrained corporate palette |
| **Academic / Teaching** | Lecture slides, course material, conference talk | Concept-first titles allowed (not every slide needs a "finding"), citations and sources preserved precisely, room for definitions and theory, discussion-prompt slides are normal |
| **General / Public** | Community talk, informational session, non-specialist audience | Plain language, minimal jargon, more explanatory scaffolding per slide, larger type, fewer numbers per slide |
| **Technical** | Engineering review, architecture walkthrough, research methods audience | Precise terminology kept intact, methodology and limitations get real slide space, diagrams over prose |
| **Sales / Pitch** | Investor pitch, product pitch, proposal | Problem→solution arc, benefit-forward language, strong single CTA at the end, visually bolder |

Record the chosen mode once at the start (in your own working notes, not necessarily on a slide) and apply it consistently — don't drift between a business tone and an academic tone mid-deck.

**Cross-cutting rule regardless of mode:** never invent facts, figures, quotations, or sources that are not in the material provided. If asked for an academic or research-facing deck, treat citation accuracy with the same rigor as the source documents — a wrong journal name or fabricated co-author is a real error, not a formatting nitpick.

---

## Required Output

Every invocation must produce an actual `.pptx` file.

**Where to save it:**
1. If the user names a location, use it.
2. Otherwise, if the working project has an obvious presentations location (e.g. a `Presentations/` folder already in use), save there.
3. Otherwise, save alongside the source material, or in the current working directory if there is no clear source location.
4. If truly ambiguous and this is a one-off request, ask rather than guessing a folder structure the user didn't ask for.

**Filename:** `<topic-in-kebab-case>_<YYYYMMDD>.pptx` (add `_HHMM` if multiple decks might be built same day). Do not overwrite an existing file unless asked — append `_v2`, `_v3`, etc.

At completion, report the exact final path, slide count, and confirm speaker notes and QA were completed (see **Final Report** at the end).

---

## Source-Document Operating Mode

The user may point you at one or more: PDFs, Word docs, Markdown, plain text, existing PowerPoint/Excel/CSV, notebooks, SQL output, or already-written analysis — or may simply describe a topic and ask you to work from your own knowledge or a conversation's findings.

When invoked:

1. Read all source material first, completely.
2. Identify the strongest conclusions, evidence, and implications for the chosen audience.
3. Determine the best storyline for the **exact slide count requested**.
4. Do not invent facts, metrics, conclusions, or sources absent from the material.
5. Preserve important terminology, definitions, caveats, and exact quantitative values.
6. Compress and synthesize — do not paste source text onto slides.
7. Prefer a diagram over dense prose whenever the content is a process, comparison, hierarchy, sequence, or framework.
8. Add speaker notes to every substantive slide (see **Speaker Notes**).

If the requested slide count is too small for everything, prioritize **main conclusion → strongest evidence → meaning → action**, and push lower-priority detail into speaker notes rather than crowding the slide.

---

## Slide Count Discipline

**Do not add a cover slide unless explicitly requested.** Assume the user may already have a title slide, a branded shell, or is inserting these into an existing deck.

- "Create 3 slides from X" → exactly 3 substantive content slides.
- "Create 5 slides from Y" → exactly 5 substantive content slides.
- A cover, if requested, counts toward the total unless the user says otherwise.

Create a cover only on explicit request ("include a cover slide," "build a complete deck," "start with a title slide"). When included, keep it minimal: title, optional subtitle, optional presenter/date — no analytical content.

---

## Storytelling Principles

### 1. Start with the question, not the slide

Before building anything, answer for yourself:
- Who is this for (see Step 0), and what should they walk away knowing or deciding?
- What is the single strongest conclusion, in one sentence?

Then build: **Conclusion → Supporting arguments → Evidence → Implications → Action** (or, in academic mode, **Concept → Explanation → Evidence → Significance → Open questions** — the shape adapts, the discipline doesn't).

### 2. Build an argument tree before coding slides

```
Main conclusion / thesis
├── Point 1 → Evidence
├── Point 2 → Evidence
├── Point 3 → Evidence
└── Implication / Action / Discussion prompt
```

The deck must make sense if someone reads *only* the slide titles in order.

### 3. Titles carry the message (mode-dependent)

**Executive/Business/Sales:** titles state the conclusion, not the topic.
- Weak: "Campaign Performance" → Strong: "CTV drove the strongest incremental reach while social expanded engagement"

**Academic/Technical:** a clear concept or claim title is still stronger than a bare label, but a well-scoped topic title is legitimate when the slide's job is to define or introduce something.
- Acceptable: "Linked Fate: Definition and Measurement"
- Stronger where the source supports it: "Linked fate predicts little on its own — group consciousness does the work"

**General/Public:** titles should read like something you'd say out loud to a friend, not like a report header.

### 4. One primary message per slide

Before finishing a slide, complete internally: *"The audience should leave this slide understanding that ___."* If that sentence needs "and," split the slide.

### 5. Match the visual to the information

| Relationship | Visual |
|---|---|
| Category comparison | Bar chart |
| Time trend | Line chart |
| Contribution / bridge | Waterfall |
| Relationship between variables | Scatter plot |
| Precise values | Table |
| Headline metrics | KPI cards |
| Progression / conversion | Funnel |
| Sequential process | Process flow / chain diagram |
| Chronology | Timeline |
| Levels / org structure | Hierarchy |
| Two-dimensional comparison | 2×2 matrix or axis map |
| Process, methodology, architecture | Blueprint diagram |
| Change over time (single subject) | Before/After |
| Overlapping category membership | Venn diagram |

Never choose a visual because it looks good — choose it because it proves the slide's one claim.

### 6. Charts are evidence, not decoration

- Cut unnecessary gridlines, series, legends, borders, decorative effects.
- Emphasize the finding that matters (neutral color for context, accent color for the point).
- Add a one-line interpretation near the chart — don't leave the audience to derive it.
- Never describe correlation as causation. Never overstate what the data shows.

### 7. Layout creates hierarchy before decoration does

Standard reading order top to bottom: **Title → Evidence/visual → Interpretation → Source note.** Keep margins, grid, and spacing consistent slide to slide. Consistent footer/slide-number treatment reads as competence even before anyone reads the content.

### 8. Business/practical interpretation (executive, sales, technical modes)

For every significant finding, answer **What? → So what? → Now what?** — don't stop at describing the data. (In academic mode, "now what" often becomes "what remains uncertain" or "what would the next study need to establish" — adapt the third question to the audience rather than forcing an action item onto a research finding that doesn't have one.)

---

## Presentation Structure by Length

**2 slides:** Slide 1 — core idea/framework. Slide 2 — evidence/implication/action.

**3 slides:** Slide 1 — core framework or main claim. Slide 2 — how it works / evidence. Slide 3 — so-what / application.

**4–6 slides:** Main insight/context → framework/methodology → key evidence → (comparison/additional evidence) → implications → recommendation or next steps. Reorder freely if the material supports a stronger sequence.

**Larger decks (7+):** Executive/opening summary → context/objective → 2–4 key-finding slides → supporting analysis → implications → recommendations/next steps → methodology → appendix. Use section-divider slides for navigation once the deck is long enough to need them.

**Executive summary, when used**, contains only: **What we found** (2–4 top findings) → **Why it matters** → **What we recommend/what follows.** Don't reproduce the whole deck here.

---

## Speaker Notes — Required

Every substantive slide needs embedded speaker notes, saved inside the `.pptx` itself (visible in Presenter View / Notes Page), not a separate notes document.

Notes should sound spoken, not repeat the slide's visible text. Cover, briefly: what the slide is about → the key message → what evidence to point at → why it matters → a transition line to the next slide. Target roughly 30–60 seconds of spoken content per slide unless told otherwise. Academic-mode notes may run longer where a concept needs unpacking; sales-mode notes should be tighter and more energetic.

Example (business mode):
> "This slide shows where we see the clearest opportunity to extend reach beyond the existing audience. CTV stands out because the target audience has both strong viewing behavior and enough addressable scale. Social stays important for engagement, but CTV is the stronger reach play. So we'd prioritize CTV for reach and lean on social for engagement."

Example (academic mode):
> "Linked fate is the idea that your own outcomes are tied to your group's outcomes. Gay, Hochschild, and White's 2016 study is important here because it found linked fate expressed at similar levels across White, Black, Hispanic, and Asian respondents — so it isn't the distinctively Black phenomenon it's sometimes assumed to be. That matters because it means linked fate alone is a weak predictor of political behavior — group consciousness, which adds an awareness of power and a belief that action is needed, is doing more of the actual work."

Implementation: with `python-pptx`, populate `slide.notes_slide.notes_text_frame`. After building, verify programmatically that every substantive slide has non-empty notes.

---

## Visual Design System

Use the audience mode to select a palette and type system — don't default to one look for every deck. If the user supplies brand colors, a template, or (for an academic deck) an institution's colors, use those instead of anything below.

**Canvas:** 16:9 widescreen, 13.333 × 7.5 in, unless the user needs 4:3 or a specific size.

**Default palettes** (use as a starting point, not a mandate):

| Mode | Primary | Accent | Neutral | Background |
|---|---|---|---|---|
| Executive/Business | Deep navy | Teal/cyan | Light gray | White / very light blue-gray |
| Academic/Teaching | Institution color if known, else deep navy | Gold or a warm secondary | Warm gray | Off-white or white |
| General/Public | A single approachable accent (avoid corporate navy-only starkness) | Complementary warm tone | Mid gray | White |
| Technical | Navy or dark slate | One clear semantic accent | Cool gray | White or very light gray |
| Sales/Pitch | Bolder saturated primary | High-contrast accent | Dark or light per brand | Depends on brand energy |

Semantic colors, used consistently regardless of mode: green = positive/opportunity, red = risk/decline, amber = caution, gray = neutral/context.

**Typography:** **for this vault the standing requirement is Times New Roman on every deck, in every mode, with zero exceptions — Calibri must never appear** (user instruction 2026-09-05, re-affirmed and hardened 2026-09-22 after Calibri was found vault-wide; see the memory note `output-language-and-formatting`). Setting the run font per-shape is necessary but **not sufficient** — python-pptx's default theme has Calibri baked into `<a:majorFont>`/`<a:minorFont>`, so any text that skips an explicit override (an unstyled placeholder, an empty-run paragraph, a shape added outside the helper) silently renders in Calibri regardless of the per-run convention. This is exactly what happened, undetected, across every deck in the vault. `deck_kit.Deck.save()` now patches the theme XML directly as the real fix (`_patch_theme_font()`, called automatically on every save) — `_tnr()` remains available for explicit per-run control but don't rely on it alone. If building a deck any other way (raw python-pptx, a different template, editing someone else's `.pptx`), **always verify the theme's `<a:latin typeface>` too**, not just the runs you touched — check with `python3 -c "import zipfile,re; z=zipfile.ZipFile('deck.pptx'); print(re.findall(r'typeface=\"([^\"]+)\"', z.read('ppt/theme/theme1.xml').decode()))"` before calling a deck done. `deck_kit.Deck` / `pipeline_diagram()` are ready-made building blocks (Times New Roman, action-title slide helpers, a data-pipeline diagram). Approximate scale: title 28–34pt, slide title 22–26pt, body 13–17pt (≥30pt for a student/10-20-30 deck), chart labels 10–13pt, source/footer 8–10pt. Also standing: **English output even when the request is in Turkish**; a methodology / pipeline diagram in any methodological deck; a references slide near the end for academic/student decks.

**Speaker notes → Keynote import failure:** if a deck has any speaker notes (`slide.notes_slide`), python-pptx's save leaves `ppt/presentation.xml` missing the required `<p:notesMasterIdLst>` element even though the notesMaster part, its relationship, and its Content_Types override all exist — PowerPoint and Google Slides silently tolerate this, but Apple Keynote's importer rejects the whole file with "The file format is invalid." Root cause confirmed 2026-09-22 via isolated repro and fixed across 50 affected decks vault-wide. `deck_kit.Deck.save()` now patches this automatically (`_patch_notes_master_decl()`, called after `_patch_theme_font()`). If building/editing a deck with notes any other way (raw python-pptx, editing someone else's `.pptx`), check with `python3 -c "import zipfile; z=zipfile.ZipFile('deck.pptx'); print('notesMasterIdLst' in z.read('ppt/presentation.xml').decode())"` before calling it done — `False` means Keynote will refuse to open it even though PowerPoint/Google Slides open it fine.

---

## Building Visuals Without an Image-Generation Tool

Assume no image-generation model is available. Build every visual programmatically as editable shapes — this produces cleaner, more consistent, more truly-editable results than sourcing or generating raster images, and it's the approach proven across native-PowerPoint-diagram work in this vault (chain diagrams, axis maps, packing/cracking grids, Venn diagrams, bar charts — all built from primitive shapes, not images).

**Implementation, in priority order:**
1. `python-pptx` — the default; broadly available and sufficient for shapes, text, tables, connectors, and native charts.
2. `PptxGenJS` (Node) — use instead if the environment has it and the user's workflow is JS-based.
3. Any other supported presentation-generation library already present in the environment.

Check what's actually available before starting rather than assuming.

**Reusable native-shape building blocks** (build once per deck, reuse across slides):
- `add_title(slide, text, subtitle)` — title + optional subtitle textbox
- `add_box(...)` — rounded rectangle with centered text, for concept/step cards
- `add_arrow(...)` — connector with a manually-added triangle tail marker (older `python-pptx` connector objects don't expose arrowheads directly — construct the `<a:tailEnd>` XML element and append it to the line)
- `add_chain(...)` — a left-to-right sequence of boxes joined by arrows, for processes and pathways
- `add_venn3(...)` — three overlapping ovals with transparency, for intersecting-category concepts
- `add_grid(...)` — a colored cell grid, for spatial/proportional comparisons
- `add_bars(...)` — a simple labeled bar chart built from rectangles, for when a native chart object is overkill
- `add_axis_map(...)` — a two-axis position map with plotted points, for framework/positioning diagrams

Build these as small reusable functions at the start of the generation script rather than one-off shape code per slide — it keeps the deck visually consistent and makes later edits (recoloring, resizing) a one-line change instead of a rewrite.

**Icons:** minimal, modern, consistent line icons — either a real SVG icon set if one is available in the environment, programmatically-constructed simple SVGs (arrow, target, check, magnifying glass, funnel, database), or native-PowerPoint-shape icons (target = circle + inner circle + arrow; process = rounded rectangles + arrows; database = stacked ovals/cylinders; decision = diamond + connectors). Never use random emoji as primary icons in executive, technical, or sales-mode decks — academic/teaching decks may use a light touch of emoji only if the user's own material does (e.g., a discussion-prompt slide), and only sparingly.

**Blueprint-style process/framework visuals:** when content describes a process, workflow, methodology, or system, consider a numbered-stage blueprint: light background, primary-color header band, numbered circles, short stage titles, 1–3 bullets per stage, directional arrows, consistent icon per stage. This is a strong default for methodology and process slides across every audience mode.

---

## Data Integrity

Before finalizing: verify every number, percentage, unit, date, label, and calculation against the source. Confirm charts and narrative agree, executive-summary numbers match detail slides, and speaker notes don't contradict what's on the slide. Never state a source that wasn't actually provided — if none was given, either omit the source line or use an accurate placeholder like "Source: user-provided material," never a fabricated citation.

For academic/research-facing decks specifically: treat this with the same rigor the vault's research protocol requires elsewhere — verify author names, years, and venue details against the actual source rather than trusting a remembered or previously-written citation, and flag anything unverifiable rather than silently asserting it.

---

## Build Workflow

1. **Inspect inputs** — read every source file, note, or dataset provided; don't skip material because it's inconvenient to parse.
2. **Determine the story** — audience (Step 0), objective, main conclusion, supporting arguments, strongest evidence.
3. **Outline the slides** — before writing any generation code, draft (in your own working notes) each slide's title, key message, evidence, visual choice, and speaker-note intent. Confirm this matches the exact requested slide count.
4. **Select layouts** — vary layout by slide purpose (summary, evidence, comparison, process/blueprint, matrix, timeline, recommendation, section divider) rather than repeating one template for every slide.
5. **Build the actual `.pptx`** — text and, where practical, charts stay editable; diagrams are vector shapes, not screenshots or flattened images.
6. **Add icons/diagrams** — reinforce comprehension, not decoration; keep icon size and stroke weight consistent across the deck.
7. **Add speaker notes** to every substantive slide.
8. **Story QA** — read only the titles in order; confirm the conclusion is obvious and every slide advances the argument.
9. **Data QA** — recheck every number, date, unit, label, and source against the material.
10. **Visual QA** — check for text overflow, overlap, misalignment, inconsistent icons/colors, cramped or overly sparse slides; render/screenshot the deck if the environment allows it, and actually look at it before calling the work done.
11. **Slide-count QA** — confirm the exact requested count, with no silently-added cover, appendix, or methodology slide.
12. **Speaker-notes QA** — confirm every substantive slide has notes, correctly matched, non-contradictory, and conversational.
13. **Save and report** (see below).

---

## Final Report

On completion, state plainly:

- **File:** exact filename
- **Location:** full path
- **Slides:** count (confirm it matches the request)
- **Audience mode used:** which of the modes above was applied, and why if it was inferred rather than stated
- **Speaker notes:** included / not applicable
- **QA:** completed, with any caveats (e.g., "visual QA done via rendered screenshot" vs. "could not render in this environment, recommend a quick open-and-look before presenting")

---

## Final Standard

The result should read like it was built by someone who does this professionally in the target domain — a strategy team's deck for executives, a professor's slides for a lecture hall, a clear public talk for a general audience — never like raw AI output, a document pasted into slide shapes, an unrelated pile of charts, or a generic template with no point of view.

**Story → Evidence → Insight → Action → Design** — in that priority order. A beautiful deck with a weak story is not a successful deck. A successful deck lets the audience understand, within a few minutes: what this is about, why it matters, and what — if anything — should happen next.
