---
name: axa
description: "HITL multi-agent workflow; GitHub issues are the state backend. Use when: plan/execute/QA a feature as a GitHub issue. ID: bikin tiket, kerjain issue, QA issue. Requires gh CLI authenticated. Skip: one-liners, commit messages, snippets."
---

# Axa

One agent, one job. HITL·Work pipeline, state in a GitHub issue: body = plan + status, comments = log, labels = stage. Chain: `decomposer.md` → `planner.md` → `doubt-review.md` → `executor.md` → `unit-test-writer.md` → `qa.md` → specialist reviews → `documentation.md` → `skill-extractor.md`. Read the stage file before acting.

STOP gates BEFORE agents run. 1) `gh` authenticated (`gh auth status`); if not: STOP. 2) One feature = one issue (`.hitl-work/tickets.md`); none yet → `gh issue create`. 3) Show the plan in chat; write to issue body only after approval. 4) Present Full / Standard / Quick, wait for the explicit choice; refuse unsafe picks.

State mapping, labels, checkpoints: `RULES.md`.
