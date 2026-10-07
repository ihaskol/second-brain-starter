# Vault Workflows

The detailed operating procedures of this vault. They were moved verbatim from `CLAUDE.md` on 2026-10-06 so that the file loaded every session stays short. `CLAUDE.md` names the section to read for each command or task. **Read the relevant section before carrying out that workflow.** `RESEARCH_PROTOCOL.md` still governs research integrity.

The full pre-restructure `CLAUDE.md` is archived at `06-Archive/CLAUDE-full-before-2026-10-06-restructure.md`.

---

## Vault Structure

**Source Processing:**
- `/01-Library/Originals/` - Original source PDFs (immutable storage)
- `/01-Library/OCR/` - OCR'd PDFs (regenerable intermediates)
- `/01-Library/Text/` - Extracted text files with page markers
- `/01-Library/Reports/` - Intake and quality reports (provenance records)
- `/01-Library/Processed/` - Completion manifests for fully ingested sources
- `/01-Library/Placeholders/` - Metadata-only records for citation-referenced sources
- `/01-Library/Sources-In-Progress.md` - Live tracking of active source processing
- `/05-Inbox/` - Temporary staging for new sources (pre-intake)

**Knowledge Base:**
- `/02-Wiki/` - Atomic knowledge pages
- `index.md` - Catalog of all wiki pages
- `log.md` - Chronological record of vault activity

**System Documentation:**
- `CLAUDE.md` - Vault workflows, organization, formatting
- `RESEARCH_PROTOCOL.md` - Research integrity and evidence standards (highest authority)
- `/00-System/Source-Pipeline.md` - Source processing technical documentation
- `/00-System/SECOND_BRAIN_WORKFLOW.md` - Supplementary procedural notes
- `/00-System/Scripts/` - Python automation scripts
- `/00-System/Config/` - Pipeline configuration

**Projects:**
- `/03-Projects/` - Project-specific work with independent system files

**Templates:**
- `/04-Templates/` - Reusable templates

**Archive:**
- `/06-Archive/` - Deprecated or superseded materials

**Legacy Compatibility:**

Existing files from pre-pipeline processing (e.g., `Lewis - 1996 - The Middle East.pdf` in Processed/, `khel-1980-siyar.txt` without page markers) remain unchanged. The pipeline does not rename or relocate legacy files.

**Safety Rules:**

Do not delete or overwrite original source files unless explicitly instructed.

Do not place generated wiki pages inside `/01-Library/`.

Original PDFs remain in `/01-Library/Originals/` permanently; they are never moved to Processed/.

**Legacy TXT Representation:**

The pipeline handles four cases for text representations:

- **Neither exists:** Creates canonical `source__text.txt`
- **Only `source.txt` exists (Legacy Mode):** Preserves legacy file, skips text extraction, uses legacy for validation/ingestion. Migration requires explicit user decision.
- **Only `source__text.txt` exists:** Standard pipeline behavior (skip or overwrite with `--force`)
- **Both exist (Conflict):** Exits with error. User must resolve: migrate legacy→canonical (delete `source.txt`), preserve legacy only (delete `source__text.txt`), or archive legacy (rename `source.txt`)

See `00-System/Source-Pipeline.md` for complete legacy decision logic.

---

## Source Acquisition and Quality Control

Before ingesting a source, it must pass through the source processing pipeline.

For complete pipeline documentation, see `00-System/Source-Pipeline.md`.

**Seven-Stage Source Lifecycle:**

- **Stage 0**: Acquisition (manual download to `05-Inbox/`)
- **Stage 1**: Intake Review (inspect text layer and language)
- **Stage 2**: Format Preparation (OCR if needed, text extraction, page markers)
- **Stage 3**: Quality Review (mojibake detection, page correspondence)
- **Stage 4**: Neutral Ingestion (create wiki notes - this file's `ingest` workflow)
- **Stage 5**: Verification (manual checking against original source)
- **Stage 6**: Project Use (project-specific application with additional constraints)

**Quality Gates:**

A source must have `quality_status: passed` or `usable-with-review` before proceeding to ingestion.

Quality status indicates technical suitability for text extraction. It does NOT indicate:
- Research verification complete
- Ready for manuscript citation
- Reliable as verified evidence

Verification (Stage 5) is required before using claims or quotations as evidence.

**Pipeline Scripts:**

Located in `00-System/Scripts/`:
- `inspect-pdf.py` - Intake review (text layer, language detection)
- `process-source.py` - OCR and text extraction
- `validate-text.py` - Quality validation
- `add-page-markers.py` - Page marker insertion

**Standard Workflow:**

```bash
# 1. Inspect new source
python3 00-System/Scripts/inspect-pdf.py --file "05-Inbox/new-source.pdf"

# 2. If ACCEPT recommendation, move to Originals (manual)
mv "05-Inbox/new-source.pdf" "01-Library/Originals/Author - Year - Title.pdf"

# 3. Process (native text or OCR)
python3 00-System/Scripts/process-source.py \
  --file "01-Library/Originals/Author - Year - Title.pdf" \
  [--lang tur|eng|ara]

# 4. Review quality report
cat "01-Library/Reports/Author - Year - Title__quality.md"

# 5. If quality_status: passed, proceed to ingest workflow (below)
```

**Integration with Ingest Workflow:**

The `ingest` workflow (defined in this file) operates on validated text files from `01-Library/Text/`.

Source Pipeline prepares sources (Stages 0-3). `ingest` creates wiki notes (Stage 4).

---

## INGEST Workflow

When I say `ingest this`, `ingest the raw folder`, or give an equivalent instruction:

### 1. Inspect the source

- Identify all unprocessed files in `/01-Library/Originals`.
- Read each source as completely as the available format allows.
- Identify the source type.
- Extract available bibliographic metadata.
- Do not invent missing metadata.
- Follow `RESEARCH_PROTOCOL.md`.

### 2. Check existing notes

Before creating a page:

- Search `/02-Wiki` for the same or a closely related concept.
- Check page titles, aliases, tags, and related notes.
- Update an existing page when the new source adds evidence to the same idea.
- Create a new page only when the concept is meaningfully distinct.
- Do not create near-duplicate pages.

### 3. Extract knowledge

For each source:

- Identify important claims, definitions, methods, findings, arguments, limitations, and open questions.
- Separate source-reported content from interpretation.
- Create atomic pages with one primary idea per page.
- Preserve qualifications, limitations, and scope conditions.
- Do not generalize beyond what the source supports.
- Do not infer unreported findings.
- For every **academic secondary source** (journal article, book chapter, working paper, research/policy report — not a primary historical/religious text), add a `## Research Design Profile` section: research question, main argument, theory, hypotheses, theory-building-or-testing, independent variable, dependent variable, control variables, methodology, data, findings, abstract, conclusion. Template and rules (including how to mark a field `Not applicable` honestly, and quoting the abstract/conclusion verbatim) are in `.claude/skills/research-ideation/references/research-contract.md`. Cross-check every field against the actual source text — this is a `citation-verification` checkpoint, not boilerplate.
- When the source came from Zotero and a write-enabled Zotero API key is configured (`00-System/Config/.zotero-web-api-key`, gitignored), push a condensed version of the Research Design Profile as a Zotero child note on the source's item, mirroring what's in the wiki page.

### 4. Link knowledge

For each new or updated page:

- Search `/02-Wiki` for genuinely related pages.
- Add meaningful `[[wikilinks]]`.
- Add reciprocal links when useful.
- Explain non-obvious relationships.
- If a concept connects to three or more substantial pages, flag it as a possible hub.
- Suggest a hub page when several notes form a clear topic cluster.

### 5. Update the vault

After processing:

- Add new pages to `index.md`.
- Update index entries for substantially revised pages.
- Append an entry to `log.md`.
- Update `/01-Library/Sources-In-Progress.md` with completion status.
- Optionally create completion manifest in `/01-Library/Processed/`.
- Do not move or rename original sources (they remain in `/01-Library/Originals/`).
- Report which files were processed, skipped, or failed.

---

## QUERY Workflow

When I ask a question about the vault:

- Search relevant pages in `/02-Wiki` before answering.
- Identify which notes and sources support the answer.
- Cite supporting wiki pages using `[[wikilinks]]`.
- Cite original sources when source information is available.
- Separate source-reported facts, synthesis, interpretation, hypothesis, recommendation, and uncertainty.
- Surface disagreements between sources.
- Do not hide contradictory evidence.
- Do not present general model knowledge as vault-derived knowledge.
- If external knowledge is used, label it explicitly.
- State clearly when the vault does not contain enough evidence.
- Do not save the answer as a page unless I explicitly ask you to save it.

---

## SAVE Workflow

When I ask you to save an answer:

- Check whether an equivalent page already exists.
- Update the existing page when appropriate.
- Otherwise create a new atomic page.
- Preserve the distinction between evidence and interpretation.
- Add citations and source attribution.
- Add related notes.
- Update `index.md`.
- Append the change to `log.md`.

---

## LINT Workflow

When I say `lint the wiki`, find and report:

- unsupported factual claims,
- incomplete or unclear citations,
- unverifiable quotations,
- contradictory pages,
- outdated or superseded claims,
- duplicate or near-duplicate pages,
- orphan pages,
- broken wikilinks,
- pages missing required metadata,
- pages containing too many unrelated ideas,
- conclusions that overstate the available evidence,
- weakly supported claims,
- unresolved knowledge gaps.

Organize the report under:

- Critical integrity issues
- Citation issues
- Contradictions
- Outdated claims
- Duplicate pages
- Orphan pages
- Broken links
- Structural issues
- Knowledge gaps
- Recommended actions

Do not delete, merge, or rewrite pages automatically during linting.

Report each item under "Contradictions" as a Contradiction Matrix row (claim, supporting source(s), opposing/qualifying source(s), nature of disagreement, possible explanation, resolution status) — see `.claude/skills/research-ideation/references/research-contract.md`. Do not collapse a contradiction into a vague "sources disagree" note.

---

## Weekly Review Workflow

When I ask for a weekly review:

- Review everything created or substantially updated during the requested period.
- Identify the most important ideas.
- Identify new connections between old and new pages.
- Identify emerging hub topics.
- Identify unresolved contradictions.
- Identify weakly supported conclusions.
- Identify missing evidence.
- Suggest valuable next questions or sources.
- Cite the relevant wiki pages.


In source-bounded mode, do not introduce any named external source, scholar, work, event, example, or technical concept that is absent from the vault.
---

## YAML Frontmatter

Every page in `/02-Wiki` must begin with this YAML structure:

    ---
    title:
    created:
    updated:
    language:
    tags: []
    aliases: []
    page_type:
    status: needs-verification
    sources: []
    ---

Rules:

- Use dates in `YYYY-MM-DD` format.
- Use `tr`, `en`, or another suitable language code.
- Do not invent metadata.
- Use `needs-verification` when a page has not been manually checked.
- Use `reviewed` only after claims and citations have been checked against the source.

**Status Distinction:**

`status` is page-level verification (this individual page has been checked).

For source-level `research_status` (not-inspected, inspected, partially-ingested, fully-ingested, verified), see `RESEARCH_PROTOCOL.md` and `00-System/Source-Pipeline.md`.

---

## Standard Page Structure

Use this structure when appropriate:

    ---
    title:
    created:
    updated:
    language:
    tags: []
    aliases: []
    page_type:
    status: needs-verification
    sources: []
    ---

    # Title

    ## Summary

    A concise summary of the primary idea.

    ## Content

    A clear explanation of the concept, claim, method, finding, or argument.

    Important factual claims must include inline citations.

    ## Evidence

    Describe the evidence supporting the claim.

    Include only information actually available in the source, such as study design, data source, sample, method, reported result, and limitations.

    ## Interpretation

    Clearly label synthesis or interpretation that is not directly reported by the source.

    Omit this section when there is no interpretation.

    ## Uncertainty and Limitations

    State what remains uncertain, what the source does not establish, and what evidence is missing.

    ## Conflicting Evidence

    Describe meaningful disagreements when they exist.

    Omit this section when no conflict is known.

    ## Related Notes

    - [[related-page]]

    ## Sources

    Provide complete source information to the extent available.

    Do not invent missing citation fields.

Do not add empty sections merely to satisfy the template.

---

## Linking Rules

- Use `[[wikilinks]]` for internal links.
- Link concepts at their first meaningful mention.
- Avoid excessive linking.
- Prefer meaningful relationships over link quantity.
- Add reciprocal links when they improve navigation.
- Explain non-obvious relationships.
- Consider splitting a page when it contains multiple independent ideas.
- Do not split a page solely because it exceeds a word count.

---

## Index Rules

`index.md` should contain:

- an alphabetical page catalog,
- hub pages,
- pages needing verification,
- contested pages,
- recently created or updated pages.

Use this format:

    - [[page-name]] — one-sentence description

---

## Log Rules

Append new entries to `log.md`.

Do not overwrite previous entries.

Use this format:

    ## YYYY-MM-DD

    ### Operation
    Ingest / Saved query / Lint / Review / Manual update

    ### Sources processed
    - Source name

    ### Pages created
    - [[page-name]]

    ### Pages updated
    - [[page-name]]

    ### Issues
    - Missing metadata
    - Conflicting evidence
    - Incomplete source
    - None

---

## Final Check Before Writing

Before creating or updating a page, verify:

- Does an equivalent page already exist?
- Is the page focused on one primary idea?
- Is every important factual claim supported?
- Are source content and interpretation separated?
- Are quotations exact and traceable?
- Are citations real and copied accurately?
- Is uncertainty stated honestly?
- Are conflicting sources preserved?
- Are wikilinks meaningful?
- Is original source attribution retained?
- Have all rules in `RESEARCH_PROTOCOL.md` been followed?

## Short Command Interface

Use the following short commands as aliases for the full workflows defined in this file and in `RESEARCH_PROTOCOL.md`.

### `inspect raw`

When I say `inspect raw`:

- Find all unprocessed files in `/01-Library/Originals`.
- Operate in strict source-bounded mode.
- Do not use external knowledge.
- Do not create, modify, move, or delete files.
- Read each source as completely as possible.
- Report:
  - files found,
  - readability,
  - available bibliographic metadata,
  - proposed source pages,
  - proposed atomic pages,
  - main claims,
  - available citations,
  - missing metadata,
  - incomplete access,
  - uncertainty,
  - possible connections to existing wiki pages.
- Wait for approval before writing files.

### `approved, ingest`

When I say `approved, ingest`:

- Proceed with the most recently proposed ingest plan.
- Follow `CLAUDE.md` and `RESEARCH_PROTOCOL.md`.
- Remain in strict source-bounded mode.
- Do not use external knowledge.
- Do not invent metadata.
- Clearly separate source-reported claims, author interpretation, normative claims, Claude synthesis, and uncertainty.
- Use exact page numbers and footnote numbers when available.
- Mark new pages as `status: needs-verification`.
- Update `index.md` and `log.md`.
- Update `/01-Library/Sources-In-Progress.md` with completion status.
- Optionally create completion manifest in `/01-Library/Processed/`.
- Original sources remain in `/01-Library/Originals/` permanently.
- Report every file created, modified, or moved.

### `query vault: [question]`

When I say `query vault: [question]`:

- Search the existing vault before answering.
- Use only vault content unless external research is explicitly authorized.
- Cite relevant wiki pages and original sources.
- Separate source-reported findings from Claude synthesis.
- State uncertainty and evidence gaps.
- Do not save the answer unless explicitly requested.

### `lint wiki`

When I say `lint wiki`:

- Run the complete lint workflow.
- Operate in strict source-bounded mode.
- Do not introduce external names, works, events, examples, or technical concepts.
- Do not modify files.
- Return a prioritized report.

### `weekly review`

When I say `weekly review`:

- Review material added or substantially updated during the last seven days.
- Use only information explicitly contained in the vault.
- Suggest generic source types only.
- Do not name external scholars, books, databases, events, or examples.
- Do not modify files.

### Large source workflow

When a source is a book or exceeds approximately 100 pages:

- Do not ingest the entire source in one operation.
- Inspect the table of contents and propose a chapter-level plan.
- Process only one chapter or bounded section at a time.
- Keep the source files in `/01-Library/Originals` until every approved section has been processed.
- Maintain one book-level source page across all phases.
- Do not create duplicate source pages for individual chunks.
- Record completed and pending sections on the book-level source page and in `log.md`.
- Move the source to `/01-Library/Processed` only after the full book has been completed and linted.

