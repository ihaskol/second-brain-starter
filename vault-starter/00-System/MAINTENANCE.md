# Second Brain Maintenance Rhythm

## Purpose

This is the canonical maintenance checklist for the vault's system layer. It keeps routing, state, freshness, and the knowledge graph usable without reorganizing subject-matter notes by default.

Maintenance begins with observation. A report is not permission to delete, merge, rename, archive, or broadly rewrite notes.

---

## Safety Rules

1. Keep a recent recoverable backup before a broad maintenance session.
2. Run read-only checks before proposing edits.
3. Separate definite structural errors from judgment calls.
4. Correct an exact mechanical error only when the intended target is unambiguous.
5. Ask for approval before deletion, merge, rename, archive, bulk metadata changes, or interpretive restructuring.
6. Preserve original sources, citations, historical handoffs, decision history, and supersession trails.
7. Record material maintenance in `log.md`; record consequential project choices in the relevant `DECISIONS.md`.

---

## Weekly Check — Operational Health

Run once per active week and after a substantial ingestion or restructuring session.

1. Run the read-only health check:

   ```bash
   python3 00-System/Scripts/lint-vault.py
   ```

2. Review critical issues first. Do not conceal a failure by weakening the check.
3. Review, but do not automatically repair:
   - changes in index coverage,
   - new planned or broken links,
   - dynamic notes past `review_after`,
   - project states past `review_after`,
   - title or alias collisions,
   - exact duplicates and zero-incoming pages.
4. Open each active project's `PROJECT-STATE.md` and confirm its current phase, next action, blockers, pending decisions, and canonical artifacts.
5. Reconcile `01-Library/Sources-In-Progress.md`: every active or paused source should have one honest status and one next action.
6. Save a reviewed health snapshot to `00-System/VAULT-HEALTH.md` only when it adds useful operational history.

### Weekly Completion Gate

- The health check ran without changing the vault.
- Every critical issue is resolved or explicitly reported as blocked.
- Overdue dynamic claims are not presented as current without re-verification.
- Each active project and source has a clear next action.
- Any approved repair is logged.

---

## Monthly Check — Graph and Memory Quality

Run once per active month or before a major synthesis.

1. Compare the current graph with `00-System/LINK-REGISTRY.md`.
2. Review exact duplicates and likely near-duplicates. Propose keep/merge/supersede actions; do not execute them without approval.
3. Review pages with no meaningful incoming wiki links. Decide whether they are valid leaf notes, need a useful relationship, or belong in a project hub.
4. Review high-frequency concepts as possible hubs. Add a hub only when it improves retrieval for multiple existing notes.
5. Sample `needs-verification` pages by current project value; verify against original sources rather than changing status in bulk.
6. Review unresolved contradictions, incomplete citations, stale source locators, and superseded records.
7. Check whether aliases and filenames still provide stable retrieval after any approved rename.
8. Confirm that `index.md` remains a catalog rather than a context dump.

### Monthly Completion Gate

- No unapproved destructive or broad changes occurred.
- Proposed merges, renames, and archives are listed separately for user approval.
- Link-registry changes reflect actual classifications, not a goal of zero missing links.
- Verification status still means what `RESEARCH_PROTOCOL.md` says it means.

---

## Milestone or Quarterly Check — System Integrity

Run at a major project milestone or roughly quarterly during active use.

1. Confirm that a recoverable vault backup exists.
2. Compare the bootstrap blocks in `AGENTS.md` and `CLAUDE.md` and keep their shared operating contract aligned.
3. Review `00-System/START-HERE.md`, `00-System/ENGINEERING-CONTRACT.md`, and this file for contradictions or obsolete routes.
4. Confirm that every project has exactly one canonical `PROJECT-STATE.md` and an append-only `DECISIONS.md`.
5. Review canonical deliverables and unresolved intermediate exports; do not promote or delete either by filename alone.
6. Review large binary files and source derivatives for storage and version-control policy. Never remove an original source as a cleanup shortcut.
7. Run the acceptance suite:

   ```bash
   python3 00-System/Scripts/test-vault-system.py
   ```

8. Record the milestone result, exceptions, and approved changes in `log.md`.

---

## Priority Order

When time is limited, work in this order:

1. Research-integrity or source-traceability failures
2. Missing or conflicting canonical project state
3. Overdue dynamic facts used in current work
4. Index or registry drift that breaks retrieval
5. Broken links with known intended targets
6. Verification backlog relevant to an active project
7. Optional graph enrichment and cosmetic cleanup

---

## Maintenance Output Contract

A maintenance report should state:

- date and scope,
- checks run,
- critical failures,
- non-critical review queues,
- exact files changed,
- items intentionally left unchanged,
- approvals still required,
- next maintenance trigger.

Never describe a warning queue as completed work. Never treat a passing structural check as proof that every research claim is true.
