---
name: citation-verification
description: Verification principles and workflow for checking that a citation, quotation, or cited claim is real and accurately represented before it enters a wiki page, project note, or deliverable. Use when adding a citation, checking "is this quote/reference real", or reviewing sourcing before a Write Gate.
tags: [Research, Citation, Reference, Evidence]
version: 0.1.0
disable-model-invocation: false
---

# Citation Verification

Reference guide for verifying citations, quotations, and cited claims. Adapted for this vault from the `claude-scholar` project's citation-verification skill; the underlying integrity rules already exist in `RESEARCH_PROTOCOL.md` — this skill supplies the mechanical verification workflow that supports them.

**Core Principle**: Verify every non-obvious citation, quotation, or attributed claim before writing it into a page, rather than trusting recall. This applies to primary-source page/footnote references from `/01-Library/Text/`, and to secondary-literature citations (journal articles, reports, books) added during `ingest` or `save`.

## Core Problems

1. **Fabricated citations or quotes** — citing a source, page number, or wording that does not exist. This is the single highest-risk failure mode for AI-assisted writing; treat any citation generated purely from memory as unverified until checked.
2. **Mismatched attribution** — wrong author, year, page number, or edition.
3. **Misrepresented claims** — the source exists, but does not actually say what is being attributed to it.
4. **Silently dropped uncertainty** — a hedged or contested claim in the source gets restated as settled fact.

## Verification Priority Order

For secondary literature (modern academic/policy sources):
1. DOI / publisher landing page
2. CrossRef metadata
3. arXiv ID / landing page (preprints)
4. Semantic Scholar
5. Verified Zotero metadata (via this vault's `/zotero-sources` skill)
6. WebSearch / Google Scholar — for discovery only, never as the final authority

For primary sources already in `/01-Library/Text/`:
1. The extracted text file itself, at the exact page marker
2. The OCR/quality report in `/01-Library/Reports/` if OCR fidelity is in question
3. Do not rely on general model knowledge of the source's contents — always re-check the actual extracted text

## Verification Steps

1. **Locate the source.** Find the DOI, arXiv ID, publisher page, verified Zotero item, or the exact page-marked passage in `/01-Library/Text/`.
2. **Confirm bibliographic details.** Title, author(s), year, venue/publisher, page or footnote number must match — do not round or approximate a page number.
3. **Confirm the claim, not just the source.** Re-read the actual passage. Search for the specific claim or quotation; do not assume it appears just because the source is topically relevant.
4. **Match quotations exactly.** A direct quotation must be character-for-character traceable to the source (adjusting only for a stated translation, which must be labeled as such per `CLAUDE.md` Language Rules).
5. **Record what you could not verify.** If a citation cannot be confirmed, mark it `[CITATION NEEDED]` or `[UNVERIFIED]` inline, state this explicitly to the user, and do not silently drop it or silently treat it as confirmed.

## Common Failure Patterns to Watch For

- A page number that "sounds right" but was never actually checked against the text.
- A claim attributed to a source's general argument when the source only mentions it in passing, or hedges it.
- A quotation lightly paraphrased and then presented with quotation marks.
- Citing a secondary source's summary of a primary source as if it were the primary source itself.
- Treating an abstract-only or paywalled source as if its full findings were confirmed.

## Failure Handling

- Never fabricate a DOI, page number, or quotation to fill a gap.
- If verification fails after a reasonable search, say so plainly and mark the citation as unverified rather than proceeding as if it passed.
- Distinguish "source not found" from "source found but claim not confirmed" — these require different follow-up.

## Relationship to This Vault's Workflows

- This skill governs the verification *mechanics*; `RESEARCH_PROTOCOL.md` remains the highest authority on when a claim may be used as evidence.
- Applies during `ingest` (Section 3, Extract Knowledge), `save`, and any `lint wiki` pass checking for "incomplete or unclear citations" / "unverifiable quotations".
- Use alongside the `/zotero-sources` skill for locating canonical bibliographic metadata already in this library.
