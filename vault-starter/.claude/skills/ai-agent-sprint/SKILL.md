---
name: ai-agent-sprint
description: Design, prototype, test and pitch a small AI agent fast (hackathons, faculty workshops, pilot proposals) for teaching, research or university administration, inside your institution's responsible-use rules. Use when the user wants to build or pitch an "agent", run an AI design sprint, or turn an idea into a demo in an hour.
---

# AI Agent Sprint

## Purpose

Take an idea from "we should have an AI that…" to a **working, tested, pitchable agent** in 60–120 minutes. The agent must be one a university could actually run.

First used to prepare for a university AI hackathon (2026-10). Keep your own event's prep sheet and idea bank in a project folder, e.g. `03-Projects/<Event>/PROJECT-STATE.md`.

## Day-of mode (trigger: "hackathon challenge: …")

Work in `03-Projects/<Event>/day-of/team/`.
1. Restate the challenge in one sentence. Write `team/options.md` with **3 agent options**. For each: problem, users, knowledge, human in the loop, demo moment, and a 1–5 score each for creative, impactful, scalable and policy risk. Recommend one. The team decides.
2. Write `team/spec.json`: job, users, instructions, knowledge, guardrails, test cases, demo moment. Only real or clearly fictional content.
3. Give the user a platform-ready instruction block and knowledge file for the event's platform.
4. Write 6 test cases (see Steps › 4). After the user runs them, record the score and one fixed failure in the spec.
5. Build a short pitch deck from the spec with the `presentation-builder` skill (or `00-System/Scripts/deck_kit.py`). Look at the slides once.
6. Write a 3-minute spoken script into the deck notes. Rehearse once with the user if time allows.
7. After the event: update the project's `PROJECT-STATE.md`, `log.md` and memory.

Keep replies short on the day. The user is in a room with a team and a clock.

## An agent, in five parts

The parts are the same on every platform.

1. **Job:** one problem, one kind of user, one sentence.
2. **Instructions:** behaviour, tone, what to refuse, answer format.
3. **Knowledge:** the only text it may answer from (syllabus, policy, routing table, source passage).
4. **Tools (optional):** search, a form, a calendar, a file store. Add them only when the demo needs them.
5. **Guardrails:**
   - a human decides anything about a person;
   - no confidential data;
   - AI use is disclosed;
   - the agent says "I don't know" outside its knowledge.

## Steps

1. **Pick the problem (10 min).** Choose one that is frequent, painful and low-risk. Prefer "the agent drafts, a human approves" over "the agent decides". Score candidates on creative, impactful and scalable, or on the criteria your event states.
2. **Fill the canvas (10 min).** Use a table with the five parts. Paste only public, fictional or approved knowledge.
3. **Build on the event's platform (20–30 min).** The same spec moves across platforms:
   - **Microsoft Copilot** (if your institution has Copilot Chat through M365): instructions go in the agent's description and instructions; knowledge is files or SharePoint (only if approved for university data).
   - **Custom GPT / Gemini Gem / Claude Project:** instructions plus uploaded knowledge files.
   - **A claude.ai artifact page:** works at once; Claude runs on the viewer's account.
4. **Test (15 min).** Write 4–8 cases:
   - 2 normal;
   - 1 edge case (missing information);
   - 1 that must be refused or handed to a human;
   - 1 with sensitive data;
   - 1 prompt-injection attempt ("ignore your rules…").

   Run them, fix the instructions, and run again. Keep the score and one fixed failure for the pitch.
5. **Pitch (3 min).** Problem → agent in one sentence → live demo moment → guardrails → test evidence → how it scales. Keep a screenshot or recording as a backup if the live demo fails.

## Institutional guardrails

Read your institution's responsible-use-of-AI policy (usually from IT or the provost) before the event, record its URL and the date you checked it, and re-check before reuse. Typical rules:

- **Data:** only approved tools for university data. Anything in an open tool is public. No confidential data without approval.
- **People:** no decisions about people (grades, admission, hiring, financial, student affairs) by AI alone. Final grades are human.
- **Transparency:** disclose AI use. Student work is uploaded only with respect for their IP.
- **Research:** disclose tools and versions. No AI in peer review. The PI verifies and discloses AI help with grants or IRB submissions.
- **Procurement:** new tools go through the institution's risk-review process.

## Rules

- `RESEARCH_PROTOCOL.md` applies. Demo knowledge is either real and cited, or **fictional and labelled**. Never invent statistics, testimonials or user counts for a pitch.
- Never put student records, grades, emails or personal data into a demo.
- Do not claim an agent is "approved", "deployed" or "used by" anyone unless that is true.
- A published demo page stays private until the owner shares it. Say so whenever you hand over a link.
