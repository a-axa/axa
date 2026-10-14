---
name: axa
description: "Human-in-the-loop multi-agent workflow; GitHub issues are the state backend. Use when: plan/execute/QA a feature as a GitHub issue. ID: bikin tiket, kerjain issue, QA issue. Needs gh CLI auth. Skip: one-liners, commit messages, snippets."
---

# Axa

One agent, one job. Axa pipeline, state in a GitHub issue: body = plan + status, comments = log, labels = stage. Chain: `agents/decomposer.md` → `agents/planner.md` → `agents/executor.md` → `agents/qa.md` → specialist reviews → `agents/documentation.md` → `agents/skill-extractor.md`. Read the stage file first.

STOP gates BEFORE agents run. 1) `gh` authenticated (`gh auth status`); if not: STOP. 2) One feature = one issue (`.axa/tickets.md`); none yet → `gh issue create`. 3) Show plan in chat; write to issue body only after approval. 4) Offer Full / Standard / Quick, wait for explicit choice; refuse unsafe picks.

Mapping, labels, checkpoints: `RULES.md`.
