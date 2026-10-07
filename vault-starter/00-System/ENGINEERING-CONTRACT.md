# Second Brain Engineering Contract

## Purpose

This contract defines how the vault handles memory, context, workflow graphs, knowledge-graph links, freshness, and operational state.

It supplements the existing research and source-processing rules. It does not replace `RESEARCH_PROTOCOL.md`, project-specific constraints, or the source pipeline.

The goal is to keep the vault reliable across tools, models, agents, and long-running projects without loading or rewriting more material than a task requires.

---

## 1. Authority and Anchors

### Authority Order

Use the authority order defined in `00-System/START-HERE.md`.

For research-integrity questions, `RESEARCH_PROTOCOL.md` remains the highest vault authority.

### Immutable or Approval-Gated Anchors

An anchor is an input that downstream workflow nodes may use but may not silently reinterpret or modify.

Default anchors are:

- the user's current explicit instruction,
- the approved task scope,
- `RESEARCH_PROTOCOL.md`,
- original source files,
- exact quotations and source locators,
- the canonical project-state record,
- explicit user decisions and accepted deliverables.

If anchors conflict, stop and surface the conflict. Do not resolve a material conflict by assumption.

---

## 2. Memory Types and Write Policy

Store information according to its function, not merely according to the tool that produced it.

| Memory type | Canonical location | Write trigger | Retrieval rule | Retention |
|---|---|---|---|---|
| Evidence and durable knowledge | `02-Wiki/` | Reusable, source-supported knowledge has been identified | Retrieve through `index.md`, hubs, tags, titles, aliases, and meaningful links | Keep; supersede explicitly when necessary |
| Source provenance | `01-Library/Originals/`, `Text/`, `Reports/`, source pages | A source enters or advances through the pipeline | Retrieve by source identifier and processing status | Preserve original and provenance records |
| Project state | Project `PROJECT-STATE.md` when available (short current-state record; see §2 Session Handoff) | Objective, phase, canonical artifact, blocker, next action, or rejected approach changes; end of every working session | Load once at project-task bootstrap | Keep current and short; move superseded detail verbatim to `PROJECT-HISTORY.md` |
| Decisions | Project `DECISIONS.md` when available | A consequential choice is accepted, rejected, or reversed | Retrieve only decisions relevant to the current task | Append-only; corrections create a new entry |
| Workflow and system rules | `00-System/`, `AGENTS.md`, `CLAUDE.md` | A reusable operating rule changes | Load only the relevant section | Version and review deliberately |
| Session handoff | The "Session log" and "Tried and rejected" sections of `PROJECT-STATE.md` (older entries in `PROJECT-HISTORY.md`); legacy standalone handoff files | End of every working session that changed project files | Read with the current state at bootstrap | Last five session entries stay in the state file; older entries move to history |
| Project history | Project `PROJECT-HISTORY.md` | Detail is superseded or the state file exceeds its size limit | Search only when the current state points to it or a past detail is needed | Append-only; moved verbatim, never rewritten |
| Activity history | `log.md` | A material ingest, correction, verification, or maintenance operation completes | Search by date, operation, source, or page | Append-only |
| User/self preferences | A future explicit preference record | The user explicitly provides a stable cross-project preference | Load only when relevant | Never infer sensitive or unstable preferences |
| Ephemeral working context | Not persisted by default | Temporary reasoning, scratch work, or discarded alternatives | Do not retrieve as memory | Discard after the task unless the user requests preservation |

### Write Gate

Before writing:

1. Confirm that the user requested or clearly authorized a write.
2. Identify the memory type and canonical destination.
3. Search for an equivalent page, state record, or decision.
4. Prefer updating the canonical record over creating a duplicate.
5. Preserve source attribution, verification status, uncertainty, and freshness.
6. Record the change in the appropriate index, log, state, or decision record.

Do not save:

- private chain-of-thought or hidden reasoning,
- speculative content as durable knowledge,
- a chat summary as a substitute for source evidence,
- transient tool output with no future operational value,
- a new page solely because a task produced text.

### Session Handoff and Resumability

The model starts every session with no memory. Anything that must still be true next session lives in a file that is read at the start: the project's `PROJECT-STATE.md`.

**Shape of `PROJECT-STATE.md`** (template: `04-Templates/Sablon-Proje-Durumu.md`). Keep it short, with a target of about 150 lines or 15 KB. Sections, in this order:

1. Current state: status and phase, as of a date.
2. Canonical artifacts: current files only.
3. Status by workstream.
4. Open items, each with an owner (user or Claude) and the exact action needed.
5. Last decision and why: one paragraph.
6. Tried and rejected — don't retry: approaches that failed, and why.
7. Session log: the last five sessions, newest first.
8. Pointers: `DECISIONS.md`, `PROJECT-GRAPH.md`, `PROJECT-HISTORY.md`.

**At the end of every session that changed project files:**

1. Update the current state, open items, and last decision.
2. Add one session-log entry of at most 8 lines: *done · decided (and why) · still open · tried and rejected*.
3. Add any failed approach to "Tried and rejected", with its reason, so the next session does not repeat it.
4. If the file exceeds the size target, move the oldest detail **verbatim** to `PROJECT-HISTORY.md`, newest block at the top. Never delete it.

**Durable working files.** Session scratch folders are temporary, and the system deletes them. Before a session ends, copy anything that would be needed to rerun, verify, or restore work into the project. Examples: scripts, verified-facts lists, OCR output, backups of originals, page sources. Put them in the project's `_build/` folder or the relevant subfolder. Never record a scratch path as the canonical location of anything.

**Compaction.** When context must be compressed, keep constraints, decisions with their reasons, rejected approaches, and the final state of each artifact. Drop used search results, intermediate drafts, and empty tool calls. Test: after compaction, the agent can still say why it did not take the other path.

**Brief first.** If a task fails because a competent person could not do it from the same brief, fix the brief (task, constraints, current artifact). Do not load more context.

### Update, Split, Merge, and Supersede

- Update when new evidence concerns the same primary idea.
- Split when a page contains independently reusable ideas with different evidence bases.
- Merge only after a read-only duplicate review and explicit approval.
- Never delete an old page merely because a new page is better.
- Use `superseded` or an explicit `superseded_by` reference when a record is replaced.
- Preserve redirects or aliases when renaming would otherwise break retrieval.

---

## 3. Provenance, Verification, and Evidence Strength

The existing `sources`, inline citations, evidence sections, processing reports, and verification statuses are the primary provenance system.

Do not add a page-wide confidence score merely to create an appearance of precision.

When evidence strength is useful, use the labels and explanations in `RESEARCH_PROTOCOL.md`:

- Strong
- Moderate
- Limited
- Contested
- Insufficient

Apply the label to a claim or conclusion and explain the basis. Do not use an unexplained numeric confidence value.

The following distinctions must remain visible:

- original source versus derived text,
- directly inspected source versus secondary citation,
- source-reported claim versus interpretation or synthesis,
- page-level verification versus source-level processing status,
- current evidence versus superseded or stale evidence.

---

## 4. Freshness Policy

Freshness is claim-dependent. `updated` records file activity; it does not prove that a claim remains current.

### Freshness Classes

Use these fields only when useful:

```yaml
freshness_class: durable | periodic | dynamic
valid_as_of: YYYY-MM-DD
review_after: YYYY-MM-DD
```

Definitions:

- `durable`: historical, conceptual, or source-interpretive knowledge that normally changes only when better evidence appears.
- `periodic`: syllabi, project plans, institutional descriptions, or recurring processes that should be reviewed at defined milestones.
- `dynamic`: law, policy, officeholders, organizational status, current statistics, active technology, or other time-sensitive claims.

Do not mass-add freshness fields to every existing page. Add them when a page is created, materially updated, or reviewed and freshness is relevant.

### Freshness Behavior

- When `review_after` has passed, label the page or claim as needing freshness review before presenting it as current.
- Preserve historically correct statements with their original `valid_as_of` date.
- Add newer evidence rather than silently rewriting historical context.
- If a current answer depends on dynamic information, verify it against an appropriate current source.
- Mark superseded claims explicitly; do not erase the earlier record.

### Source Priority

Source priority depends on the claim:

1. The exact original source inspected sufficiently for the claim
2. Current primary or authoritative documentation for operative facts, while retaining bias and limitation analysis
3. Relevant high-quality research for causal, comparative, or interpretive claims
4. A reviewed vault page with traceable sources
5. A `needs-verification` vault page
6. A project summary, handoff, or activity log
7. General model knowledge, explicitly labeled and used only when authorized

Newer is not automatically better; authority is not the same as neutrality; a summary is not a source replacement.

---

## 5. Index-First and Scoped Context

### Retrieval Sequence

1. Read `00-System/START-HERE.md`.
2. Classify the task and select the relevant project state or system workflow.
3. Search the relevant portion of `index.md` or a project hub.
4. Load candidate notes in small batches.
5. Follow meaningful links only when they answer a specific evidence gap.
6. Load original source passages for verification, quotation, or unresolved conflict.

Do not recursively load every linked note.

### Context Budget

- Bootstrap: no more than three system/state documents when possible.
- Initial target: approximately 6,000 tokens or less.
- Retrieval batch: no more than five wiki notes.
- Reserve: at least 25% of available context for verification, synthesis, and output.
- Large sources: plan and process in bounded sections with stable page or line anchors.
- Expansion: identify the missing question before loading the next batch.

If a tool or model has a smaller limit, reduce these budgets proportionally.

### Compression

Compress working context into an evidence packet before synthesis.

A minimal evidence packet contains:

```text
claim
claim_type
source
locator
support_or_conflict
verification_status
freshness_or_valid_as_of
uncertainty
```

Compression rules:

- Preserve exact source locators and material qualifications.
- Keep contradictions rather than averaging them away.
- Label interpretation and synthesis explicitly.
- Never convert an uncertain claim into a definite statement to save space.
- Never treat a compressed packet as a replacement for the original when exact verification is required.

### Per-Node Context

Each workflow node receives only:

- its task and output contract,
- the relevant anchors,
- the smallest necessary source or note set,
- upstream artifacts that are true dependencies.

Do not pass an entire worker's chat history or hidden reasoning to another node.

---

## 6. Workflow Graph Contract

### Standard Research Graph

```text
Scope and plan
      ↓
Independent evidence nodes (fan-out)
      ↓
Evidence-complete barrier
      ↓
Fresh-context verification
      ↓
Reduce and synthesize
      ↓
Schema and quality validation
      ↓
Approved write-back and state update
```

This graph is a default pattern, not a requirement to use multiple agents for every task. Use a simple linear workflow when the task is small or genuinely sequential.

### Node Contract

Every material node must define:

| Field | Requirement |
|---|---|
| `node_id` | Stable short identifier |
| `purpose` | One bounded responsibility |
| `inputs` | Exact sources, notes, anchors, or upstream artifacts |
| `output_schema` | Required structure of the result |
| `dependencies` | Only real data or decision dependencies |
| `parallel_safe` | Whether it can run independently |
| `completion_gate` | Observable condition for success |
| `failure_behavior` | Retry, partial result, stop, or escalation |

One node should not research, verify, synthesize, and write the final record unless the task is trivial.

### Real Edges and Fake-Edge Removal

Create an edge only when the downstream node requires:

- data produced by the upstream node,
- a decision made by the upstream node,
- completion of a shared safety or quality gate.

Do not create an edge merely because:

- tasks share a topic,
- tasks were listed in sequence,
- one worker could read another worker's commentary,
- a previous workflow happened to run serially.

If two nodes can complete from the same anchors without consuming each other's output, they should be eligible for fan-out.

### Fan-Out, Barrier, Reduce, and Synthesize

- **Fan-out:** Divide work by independent source, angle, jurisdiction, period, section, or test.
- **Barrier:** Wait only when downstream work requires all critical branch artifacts.
- **Reduce:** Normalize branch outputs into the same evidence schema; deduplicate claims without erasing disagreements.
- **Synthesize:** Answer the user or produce the artifact using only normalized, verified inputs.

Use a pipeline for true transformations such as PDF → text → quality report → ingestion. Use a barrier for independently produced evidence that must be complete before verification or synthesis.

### Fresh-Context Verification

The verifier receives:

- the approved scope,
- relevant anchors,
- normalized worker artifacts,
- the source passages needed to test material claims.

The verifier should not receive worker chain-of-thought or rely on worker confidence. It checks:

- source existence and locator accuracy,
- claim-to-source support,
- quotation fidelity,
- missing counterevidence,
- contradictions,
- freshness,
- schema completeness,
- whether the conclusion exceeds the evidence.

### Failure Handling

- Independent branches continue when another non-critical branch fails.
- A node may retry only when the failure is safe and reproducible; record why the retry is justified.
- Preserve usable partial results and label them `partial`.
- Do not cross a barrier when a critical dependency is missing.
- Do not synthesize a complete-looking answer from incomplete critical evidence.
- Report blocked, skipped, failed, and partial nodes explicitly.
- Escalate to the user when completion requires a new source, authority, or material scope decision.

### Write-Back Node

Write-back is a separate gated action.

Before write-back:

1. Validate the artifact against its schema.
2. Confirm verification and freshness requirements.
3. Search for an existing canonical destination.
4. Request approval for destructive, broad, or interpretive restructuring.
5. Update the appropriate index, log, project state, or decision record.

---

## 7. Knowledge-Graph Link Contract

Wikilinks represent navigable relationships, but not every missing target is an error.

The current vault-specific classification snapshot is maintained in `00-System/LINK-REGISTRY.md`.

Classify link targets as:

- `resolved`: the target page exists,
- `planned`: a deliberately proposed future atomic page,
- `broken`: the target should exist but does not,
- `renamed`: an alias or redirect must be repaired,
- `external-to-wiki`: the target is intentionally elsewhere in the vault.

Rules:

- Missing links under a clearly labeled `Potential Atomic Pages` section are treated as planned.
- Missing targets elsewhere are broken unless explicitly marked as planned.
- Do not create empty pages solely to make lint counts reach zero.
- Prefer typed or explained relationships over large undifferentiated link lists.
- Add reciprocal links only when they improve retrieval.
- Preserve aliases when a rename would otherwise disconnect the graph.

---

## 8. Maintenance and Deduplication

The canonical schedule, safety gates, and completion checklists are maintained in `00-System/MAINTENANCE.md`.

### Weekly Review

Review without automatic mutation:

- index coverage and stale index targets,
- new broken and planned links,
- project-state freshness,
- active source next actions,
- dynamic pages whose `review_after` date has passed.

### Monthly Review

Review:

- exact and near-duplicate pages,
- pages with no meaningful incoming or outgoing links,
- emerging hub candidates,
- superseded handoffs and summaries,
- unresolved contradictions,
- high-value pages still needing verification.

Do not automatically delete, merge, rename, archive, or rewrite personal notes. Generate a report and obtain approval for material changes.

---

## 9. Completion Criteria

System-level changes should also pass the checks documented in `00-System/ACCEPTANCE-TESTS.md`; the latest reviewed run is recorded in `00-System/ACCEPTANCE-RESULTS.md`.

A non-trivial task is complete only when:

- the requested output exists,
- all critical nodes passed their completion gates,
- material claims are traceable or explicitly uncertain,
- verification and freshness requirements are satisfied,
- failures and partial results are disclosed,
- authorized writes reached the correct memory location,
- relevant state, decision, index, or log records were updated.

Stop retrieval when the conditions in `00-System/START-HERE.md` are satisfied. More context is not automatically better context.
