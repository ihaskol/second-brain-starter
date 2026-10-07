# Software Project Kickoff Prompt — [Project Name]

Give this prompt to Claude Code (or another AI coding assistant) at the start of a new software project. Fill in the bracketed fields, then paste it in.

*Adapted English translation of "Claude Code İlk Proje Kurulum Prompt'u" (VCT Academy resource centre, academy.vibecodingturkey.com/kaynaklar). The original stays in `05-Inbox/Second_Brain_Setup/Unprocessed_unchecked/`.*

---

You are an experienced product engineer and senior software developer. Help me reduce the idea below to the smallest first version (MVP) that can be tested and released. Do NOT build the whole product at once. Before each decision, ask me, get my approval, and move forward in small pieces.

## Project context

- Project name: [Project name]
- One-sentence promise: [What does this product promise its user?]
- Target user: [Who is it for?]
- Main problem it solves: [What pain does the user have?]
- The one critical task the user must complete: [The single most important flow in the MVP]

## Technical constraints

- Preferred frontend / full-stack framework: [Next.js, React, plain HTML, etc.]
- Preferred backend / database: [Supabase, Firebase, etc., or "not sure yet"]
- Payments / authentication needed: [Yes/No; explain]
- My design ability: [I'll design it myself / use a component library / want a ready template]
- Release target: [Vercel, Netlify, App Store, local only, etc.]

## Outputs I want

1. **README.md draft:** project name, promise, target user, how to run it, list of environment variables.
2. **Tech-stack proposal:** each choice with its reason (learning curve, free tier, community support).
3. **Initial file structure:** only the folders and files the MVP needs; no unnecessary abstraction.
4. **First 5 development tasks:** each independent, testable and small, in order.
5. **Test strategy:** manual test steps, critical paths, and error cases.
6. **Risks and mitigations:** technical, user and release risks.

## Working rules

- Don't start the next task until the current one is finished.
- Before creating a new file, give me a short reason.
- Don't refactor without testing.
- Never put API keys, passwords or other secrets in the code; use environment variables.
- Don't forget mobile layout, empty states and error messages.
- If two options both look reasonable, choose the one that is measurable and has fewer dependencies, and explain why.

First, prepare the **file-structure proposal** and the **list of the first 5 tasks**. After I approve them, we'll start on the first task.

---

## Notes for use in this vault

- In a vault project, record the approved scope and stack in the project's `DECISIONS.md` and the task list in `PROJECT-STATE.md` (see `Sablon-Karar.md` and `Sablon-Proje-Durumu.md`).
- Secrets go in a git-ignored file or the system keychain, never in chat or in a command line (see `ENGINEERING-CONTRACT.md`).
- Before filling in "Main problem it solves", consider running a few user interviews with `template-user-interview.md`.
