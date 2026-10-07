# Research Contract

Use this contract to carry research state across a research session or a project's lifetime: what question is being studied, what evidence currently exists, what claim that evidence actually allows, what uncertainty remains, and what should happen next.

In this vault, `Knowledge` below maps to `/02-Wiki` (or a project's own synthesis notes), and `Writing` maps to a project's manuscript/deliverable files under `/03-Projects/`.

## Research Question Card

Use this card when a vague idea becomes a research direction, e.g. at the start of a new project or a new line of inquiry within one.

```md
## Research Question Card

Question:
Type: exploratory | confirmatory | applied
Hypothesis:
Why it matters:
Current evidence:
Missing evidence:
What would support it:
What would falsify it:
Minimal next action:
Decision: explore | read more | run experiment | stop
```

## Evidence Record

Use this record for a source-reported finding, a project note, or an analysis artifact that may later support a claim.

```md
## Evidence Record

Evidence ID:
Source:
Source type: full source | secondary literature | primary excerpt | project note | abstract-only | unverified
Supports:
Contradicts:
Method / provenance:
Limitation:
Project relevance:
Claim strength: speculative | observed | supported | strong
```

Evidence ID format:
- Use `ER-YYYYMMDD-shortslug-NN`, e.g. `ER-20260919-state-capacity-01`.
- Keep IDs unique within the project or research thread.
- Use stable, human-readable slugs — not `E1`, `source-a`, or similar.
- Reuse the same Evidence ID when the same evidence is referenced downstream; create a new one only for a distinct source or analysis result.

## Evidence Matrix

Use this when comparing several sources side by side on the same question — e.g. surveying what multiple secondary sources say about one event, or checking how a claim is treated across several primary-source passages. Each row should have (or reference) its own Evidence Record; the matrix is a comparison view, not a replacement for the individual records.

| Evidence ID | Source | Claim / finding | Method or basis | Limitation | Claim strength |
|---|---|---|---|---|---|
| ER-... | | | | | |

- One row per source, not per claim — a source that speaks to several claims gets one row per claim it supports.
- Fill "Claim strength" using the Strength Rules below; don't leave it blank to avoid a judgment call.
- Use this matrix to notice patterns (e.g. every row above `observed` relies on the same secondary source restating one primary passage) before writing a synthesis paragraph.

## Contradiction Matrix

Use this when two or more sources disagree, rather than silently picking the more convenient one. This is the concrete format behind `CLAUDE.md`'s "Preserve disagreements between sources" and the `lint wiki` Contradictions category.

| Claim | Supporting source(s) | Opposing / qualifying source(s) | Nature of disagreement | Possible explanation | Resolution status |
|---|---|---|---|---|---|
| | | | factual / interpretive / chronological / translation | | unresolved / one source stronger / partially reconciled |

- "Nature of disagreement" matters: a translation discrepancy, a chronological conflict, and a genuine interpretive dispute call for different handling — don't collapse them into one vague "sources disagree" note.
- "Possible explanation" is a hypothesis, not a resolution — e.g. differing source traditions, one author writing centuries later, a copyist variant. Record it as a hypothesis, not a settled account, unless it is itself sourced.
- Default "Resolution status" to `unresolved` unless there is a specific, named reason to prefer one source (e.g. closer to the event, better manuscript tradition, corroborated elsewhere) — "one source stronger" still requires naming that reason.
- A wiki page's "Conflicting Evidence" section should reflect a Contradiction Matrix row, not paraphrase around it.

## Research Design Profile

Required for every **academic secondary source** ingested into this vault (journal article, book chapter, working paper, research/policy report) — see `CLAUDE.md`'s INGEST Workflow. Not required, and not forced, on primary historical/religious source pages (Quran verses, Hadith, Sira excerpts) where the schema does not apply. Add this as a `## Research Design Profile` section in the source's wiki page, and (when a write-enabled Zotero connection is configured) push a condensed version as a Zotero child note on the source's item.

```md
## Research Design Profile

Research question:
Main argument:
Theory:
Hypotheses:
Theory-building or theory-testing:
Independent variable:
Dependent variable:
Control variables:
Methodology:
Data:
Findings:
Abstract:
Conclusion:
```

Rules:
- "Research question" comes first and is distinct from "Main argument": the question is what the source set out to answer (often stated explicitly in the introduction, e.g. "What explains X?" or "Why do some Y but not others?"); the main argument is the answer it gives. State the question in the source's own terms where possible, not just a restatement of the title.
- Every field must be cross-checked against the actual source text (read the relevant sections — abstract, methods, results, conclusion — don't infer from the title or from memory). This is a `citation-verification` checkpoint, not a formality.
- Use `Not applicable` **with a one-clause reason** for any field that doesn't fit the source — most qualitative literature reviews, doctrinal/policy essays, and opinion pieces have no IV/DV/control variables/dataset, and forcing an answer would fabricate structure the source doesn't have. Do not leave a field blank instead of writing `Not applicable`.
- "Abstract" and "Conclusion" are quoted **verbatim** with a page reference when the source has them. When a source has no formal abstract or no section titled "Conclusion" (common in edited-volume chapters, doctoral monographs, and short opinion pieces), say so explicitly rather than fabricating one or silently substituting a paraphrase.
- "Theory-building or theory-testing" is a judgment call — state which, briefly, in the same line (e.g. "theory-testing — derives and tests three hypotheses from an existing theory" vs. "theory-building — proposes a new causal mechanism").
- This profile supplements, and does not replace, the vault's existing per-source page structure (Bibliographic Information, Scope/Argument, Findings, Limitations, Related Notes, Sources) — it is one additional section, not a rewrite of the page.

## Claim Candidate

Use this when synthesis or interpretation suggests wording that may later enter a wiki page, project manuscript, or deliverable.

```md
## Claim Candidate

Claim:
Source evidence:
Allowed wording:
Forbidden stronger wording:
Uncertainty:
Next check:
Decision: keep | weaken | revise | discard
```

## Source Trust Levels

- `full source` / `primary excerpt`: can support `observed`, `supported`, or `strong` claims when the passage, page marker, and any translation are named per `RESEARCH_PROTOCOL.md`.
- `secondary literature`: can support project claims when the argument, method, and limitations of the citing work are named — run it through `citation-verification` first.
- `project note`: can support hypotheses and plans, but not source-backed claims unless it links to a separate Evidence Record.
- `abstract-only` / `unverified`: supports discovery and a `To-Read` / `needs-verification` note only. Do not use it to support a wiki page's Content section or a manuscript claim until it is replaced by a verified source.

## Claim Promotion Gate

Before a claim moves from a working note into a wiki page's Content section, a project manuscript, or any polished deliverable, check:

1. The claim has at least one Evidence Record ID.
2. The source type is strong enough for the intended claim (see Source Trust Levels).
3. The claim strength has not been silently upgraded from what the source supports.
4. Allowed wording and forbidden stronger wording are both recorded.
5. Contradictory or missing evidence is preserved, not hidden — per `CLAUDE.md`'s Core Principles.

If any item fails, keep the claim as a hypothesis, an open question, or a `needs-verification` note instead of polishing it into a durable conclusion.

## Strength Rules

- `speculative`: a plausible idea, weak or indirect evidence only.
- `observed`: seen in a source or note, but not yet enough for a durable conclusion.
- `supported`: backed by explicit evidence — a verified passage, citation, or documented finding.
- `strong`: backed by multiple independent evidence anchors, or a source's central, well-supported finding.

Do not promote a claim to a stronger level without naming the evidence that justifies the upgrade.
