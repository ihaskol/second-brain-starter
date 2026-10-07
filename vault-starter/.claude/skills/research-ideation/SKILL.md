---
name: research-ideation
description: Use when starting a new research direction, a new project, or a new chapter/section within one — turning a vague interest into a research question, identifying gaps, choosing a method, and tracking evidence and claim strength as work proceeds. Trigger on "brainstorm research ideas", "5W1H", "research gap", "define research question", "research plan", "what's missing in the evidence".
version: 0.1.0
disable-model-invocation: false
---

# Research Ideation

Supports moving from a vague idea to a traceable research direction: a research question, the evidence for and against it, what would falsify it, and the minimal next action — adapted for this vault's project-based research work (`03-Projects/`) and neutral wiki maintenance (`02-Wiki/`).

## 1. Idea Brainstorming (5W1H)

Use these six questions to pressure-test a research direction before committing time to it:

- **What** — What specific question, claim, or phenomenon is being studied? What is out of scope?
- **Why** — Why does it matter? To whom (this project, the broader vault, an external audience)?
- **Who** — Whose account, perspective, or data does the evidence come from? Whose is missing?
- **When** — What time period or scope does the question cover?
- **Where** — What domain, geography, or context does it apply to — and where does it stop applying?
- **How** — What method or evidence would actually answer this (close reading of a primary source, comparison across secondary sources, quantitative analysis, etc.)?

If an answer is thin (e.g. "why" is vague, or "how" has no realistic evidence path), that is a signal to narrow the question before proceeding, not to write around the gap.

## 2. Gap Analysis

When surveying what the vault or a project already covers, check for gaps of these kinds:

- **Evidentiary gap** — the question is discussed but no primary source or reliable secondary source has actually been checked.
- **Methodological gap** — existing notes rely on one lens (e.g. one author's framework) with no comparison or contestation.
- **Coverage gap** — a period, actor, or angle relevant to the question has no note at all.
- **Interpretive gap** — sources exist but disagree, and the disagreement has not been surfaced (see `CLAUDE.md`'s "Preserve disagreements between sources").
- **Currency gap** — a claim rests on outdated material superseded by more recent or more direct evidence.

Before creating a new page or extending a project, search `/02-Wiki` and the relevant project folder first — a gap that's actually already covered should update an existing note, not spawn a duplicate.

## 3. Research Question Formulation

Turn a gap into a specific question using a Research Question Card (see `references/research-contract.md`). A workable question:

- names what would count as support and what would count as falsification,
- is scoped to something answerable from sources this vault can actually access or acquire,
- states the minimal next action (e.g. "check pages 40–52 of X for the claim", not "read more").

## 4. Evidence Tracking

As sources are checked, log them as Evidence Records (`references/research-contract.md`) rather than folding conclusions directly into prose. This keeps claim strength (`speculative` / `observed` / `supported` / `strong`) explicit and auditable, and is what `lint wiki` checks against when flagging "weakly supported claims" or "conclusions that overstate the available evidence."

Two comparison formats build on the Evidence Record, both in `references/research-contract.md`:
- **Evidence Matrix** — a table for comparing several sources on the same question side by side, useful before writing a synthesis paragraph.
- **Contradiction Matrix** — a table for recording *how* sources disagree (factual / interpretive / chronological / translation) rather than silently favoring one. Use this whenever `CLAUDE.md`'s "Preserve disagreements between sources" applies, and to back a wiki page's Conflicting Evidence section or a `lint wiki` Contradictions finding.

Run any citation or quotation through the `citation-verification` skill before it is recorded as evidence.

## 5. Method Selection

For each candidate method (close textual reading, cross-source comparison, quantitative/coded analysis, etc.), weigh:

- What it can and cannot establish for this question.
- What sources it requires, and whether this vault already has them (`/01-Library`) or they need acquisition (Source Acquisition pipeline in `CLAUDE.md`).
- The realistic time cost against the value of the answer.

## 6. Research Planning

For anything spanning more than a session, sketch:

- Milestones (e.g. "source acquired and quality-passed" → "ingested" → "synthesized" → "written up").
- What could block progress (source access, translation, OCR quality) and the fallback if it does.
- The explicit stopping point for "good enough evidence" versus open-ended reading.

## Where This Fits

```
Vague interest → 5W1H brainstorm → Gap analysis (check 02-Wiki / project first)
    → Research Question Card → Evidence Records as sources are checked
    → Claim Promotion Gate before writing conclusions into a page or manuscript
```

This complements, and does not replace, `RESEARCH_PROTOCOL.md` (governs what may count as evidence) and each project's own system files under `03-Projects/*/00-System/` (govern that project's additional constraints). When the two conflict, `RESEARCH_PROTOCOL.md` and the project's own rules win.

## Reference

- `references/research-contract.md` — Research Question Card, Evidence Record, Evidence Matrix, Contradiction Matrix, Claim Candidate templates, source trust levels, and the Claim Promotion Gate.
