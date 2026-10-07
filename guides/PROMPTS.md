# Prompts for the Second Brain

Start Claude Code in your vault folder, copy a prompt, replace the [brackets] and paste it in. Three prompts cover a whole project: start it, resume it each session, and end each session.

## 1. Start a new project

*Once, when a project begins. Replace every [bracket].*

```text
Create a new project in the Second Brain.

Project name: [short name, e.g. Drivers of Civil War]
Objective: [one or two sentences: the question this project answers]
Audience: [who will read the outputs, e.g. students, executives, reviewers]
Final deliverables: [e.g. Word report, infographic, diagrams, slide deck]
Available sources: [vault folders, Zotero collections or files, or "find relevant notes in the vault"]
Scope and limits: [what is in and out: period, regions, source types]
Success criteria: [how the result will be judged, e.g. "I will review the outputs"]
Deadline or review date: [YYYY-MM-DD]
Language: [e.g. English]

Based on this information:
1. Briefly show the folders and files you plan to create, then wait for my approval before writing anything.
2. Create the project folder in 03-Projects/.
3. Write PROJECT-STATE.md: objective, current state, open items, last decision, tried and rejected, session log.
4. Create DECISIONS.md for genuine, consequential decisions only, each with its reason.
5. If the work has several dependent steps, create PROJECT-GRAPH.md and map only real dependencies.
6. Add the project to the project router in 00-System/START-HERE.md.
7. Find relevant existing notes through index.md; do not load the whole vault.
8. List any missing information and every assumption you had to make.
9. Follow RESEARCH_PROTOCOL.md: no invented sources, citations or quotations; mark unverified claims.
10. At the end of every work session, update PROJECT-STATE.md and add a session-log entry, including approaches tried and rejected.
11. Do not delete, merge, rename or restructure existing notes without my permission.
```

## 2. Resume a project

*At the start of every work session.*

```text
Continue the project [project name].

1. Read its PROJECT-STATE.md first, then only the parts of DECISIONS.md and PROJECT-GRAPH.md you need.
2. In a few lines, tell me the current state, the open items and what you propose to do next.
3. Do not retry anything listed under "Tried and rejected" unless I ask.
4. Today I want to: [task].
```

## 3. End a session

*Before you stop working. The model forgets; the files remember.*

```text
We are stopping for today. Before we finish:

1. Update PROJECT-STATE.md: current state, open items, last decision and why.
2. Add one session-log entry: done, decided and why, still open, tried and rejected.
3. Record any genuine decisions in DECISIONS.md.
4. Copy any scripts or results from temporary folders into the project's _build/ folder.
5. Tell me exactly which files you changed.
```

## Short commands

Type these inside Claude Code. Each runs a workflow written in the vault (`00-System/VAULT-WORKFLOWS.md`), so the same words always mean the same steps.

| Command | What it does | Writes files? |
|---|---|---|
| `inspect raw` | Reads the new files in 01-Library/Originals/ and proposes source pages and notes, with what is missing or uncertain. | No: it waits for your approval |
| `approved, ingest` | Carries out the plan you just approved. New notes are marked needs-verification; index.md and log.md are updated. | Yes |
| `ingest this` | Takes a source through the full intake, from inspection to notes. For more control, use inspect raw first. | Yes |
| `query vault: [question]` | Answers from your notes only, with citations, and says when the vault does not contain enough evidence. | No |
| `save this answer` | Saves the last answer as a note, or updates an existing one, with sources; updates index.md and log.md. | Yes |
| `lint wiki` | Health check: unsupported claims, weak citations, broken links. Returns a prioritised report. | No: report only |
| `weekly review` | Reviews what was added in the last seven days and points out gaps. | No |

Books and sources over about 100 pages: ask Claude to process them one chapter at a time. It proposes a chapter plan first.

## Tips that make the biggest difference

- **Name the audience and the format.** They change structure, tone and depth more than anything else.
- **Ask for the plan first,** and approve it before files are written.
- **One project per session.** Begin with "Resume a project" and end with "End a session".
- **Write dates as YYYY-MM-DD.** 10-03-2026 could mean 3 October or 10 March.
- **Say what not to touch.** Existing notes are never deleted, merged or renamed without your permission, but saying so keeps it explicit.

---

© 2026 Isa Haskologlu, PhD · Licensed under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).
