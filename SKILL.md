---
name: axa
description: "Human-in-the-loop multi-agent workflow; local YAML is the state backend. Use when: plan/execute/QA a feature with threaded local tracking. ID: bikin task, kerjain task, QA task. State in .axa/tasks/<id>/state.yaml; human-readable thread generated as thread.html. Skip: one-liners, commit messages, snippets."
---

# Axa

One agent, one job. Axa pipeline, state in local YAML: `.axa/tasks/<task-id>/state.yaml` holds the plan, live status, and the handoff thread; `thread.html` (generated) renders it as a readable timeline. Chain: `agents/decomposer.md` → `agents/planner.md` → `agents/executor.md` → `agents/qa.md` → specialist reviews → `agents/documentation.md` → `agents/skill-extractor.md`. Read the stage file first.

STOP gates BEFORE agents run. 1) One feature = one task: `.axa/tasks/<task-id>/state.yaml` (copied from `templates/state-template.yaml`); none yet → create it. 2) Show plan in chat; write to `state.yaml` only after approval. 3) Offer Full / Standard / Quick, wait for explicit choice; refuse unsafe picks.

Token protocol (binding). Start every stage by reading ONLY: `current:`, the latest handoff's `summary`, and the `plan` steps for your own stage. Read `detail` or older handoffs only when the summary is insufficient — and say why in your own handoff. Write handoffs as `summary` (≤ ~280 chars, decision-focused) + `detail` (evidence/logs). After every handoff, regenerate the thread view: `python3 .axa/render-thread.py --task <task-id>`.

Mapping, stages, checkpoints: `RULES.md`.
