# ADR: Local YAML + HTML state backend for Axa (default)

- **Status:** Accepted (core decision by Aska; detail decisions delegated to Miu 2026-10-20 — final veto stays with Aska on read-through)
- **Amended:** 2026-10-20 — the GitHub-issue opt-in backend is **dropped entirely**
  (see Amendment below). Axa is local-only from v2.0.0.
- **Date:** 2026-10-20
- **Author:** Aska (drafted with Miu)
- **Decided:** 2026-10-20 — Aska approved the direction; the six detail
  questions below were delegated to Miu and are recorded as Decisions.
- **Supersedes:** "GitHub issues are the state backend" (v0.1.0, documented in
  `SKILL.md` / `RULES.md`; this ADR retroactively records the backend decision
  so it can be changed deliberately)

## Amendment (2026-10-20): GitHub backend removed

The original decision kept the GitHub-issue backend as a per-task opt-in for
teams needing remote visibility. **Aska killed it the same day**: nobody uses
Axa besides him, so the dual-backend maintenance cost is unjustified.

Consequences of the amendment:

- There is no `backend:` field. `state.yaml` is the only state backend. Period.
- `templates/issue-template.md` and `templates/tickets.template.md` are deleted.
- Every `gh` CLI reference is removed from `SKILL.md`, `RULES.md`, `README.md`,
  and `agents/*.md`. The `gh` STOP gate is gone; the hard prerequisites are now
  Python 3 + PyYAML (for `render-thread.py`).
- `.axa/tickets.md` (v0.1.x) is legacy and ignored; the task registry is derived
  from `.axa/tasks/`.
- If a team ever needs remote visibility again, that is a new ADR — not a
  resurrection of this one.

## Context

Axa v0.1.0 stores all workflow state in a GitHub issue:

- **Issue body** = live plan + status (updated in place after each stage;
  see `templates/issue-template.md`: Feature, Plan, Required Routing,
  Findings Ledger, Verification Evidence, Session Log, Tech Debt,
  Current Handoff).
- **Issue comments** = the handoff log between agents (the *thread*).
- **Labels** (`axa:planning`, `axa:executing`, `axa:qa`, `axa:review`,
  `axa:done`) = pipeline stage.
- `gh` CLI authenticated is a hard prerequisite (STOP gate in `SKILL.md`).

This works. It was validated end-to-end on ORBIT issue #4. The threaded
handoff log is precisely what fixed HITL·Work's weakness: flat markdown
tracking that is hard to follow because it is not shaped like a thread.

The problem is **token cost**, not mechanics:

1. Every stage, each agent runs `gh issue view --comments`, which returns the
   **entire thread** — full body plus all comments — as one unstructured
   markdown blob. There is no way to read selectively.
2. Comments are free-form, so nothing enforces compactness; the body grows
   monotonically (Session Log table, Findings Ledger, Verification Evidence).
3. API/CLI output carries metadata noise (URLs, author fields, timestamps)
   that costs tokens but carries no signal.
4. `gh` CLI + auth is a heavy prerequisite for a solo user who never needed
   the remote side of issues.

Goal: keep the threaded model, kill the token tax. Local files can do both —
**if** the format is designed for selective reads instead of being markdown
with extra steps.

## Decision

**Local YAML + generated HTML is the only state backend.** (Amended 2026-10-20:
the GitHub-issue opt-in originally proposed here was dropped — see Amendment.)

- `.axa/tasks/<task-id>/state.yaml` — the source of truth. Read and written
  by agents. Committed to git (the audit trail survives in version history).
- `.axa/tasks/<task-id>/thread.html` — **generated** from `state.yaml`, never
  hand-written. A GitHub-comment-style timeline for human eyes. Regenerated
  by each agent after it updates the YAML, so a human checks progress in a
  browser at **zero token cost** instead of interrogating an agent.
- `backend:` field: **removed** (amendment 2026-10-20) — there is exactly one
  backend. `gh` CLI is not a prerequisite for anything anymore.

This is deliberately **not** a return to HITL·Work's flat markdown. The
handoff list is an ordered thread (the thing issues got right), and the HTML
render preserves the thread-shaped reading experience.

## state.yaml schema

One task = one file. Field mapping from the v0.1.0 issue body is 1:1 so
nothing is lost in translation:

| Issue body section (v0.1.0) | `state.yaml` field |
|---|---|
| Title / Feature block | `id`, `title`, `feature:`, `mode:`, `mode_rationale:` |
| Labels (`axa:*`) | `stage:` enum |
| Plan | `plan:` (list of `{id, text, status}`) |
| Required Routing checklist | `routing:` (map agent → `{required, reason}`) |
| Findings Ledger table | `findings:` (list of records) |
| Verification Evidence | `verification:` |
| Session Log table + comments | `handoffs:` (the thread — see below) |
| Tech Debt (append-only) | `tech_debt:` (append-only) |
| Current Handoff | `current:` (the cheap entry point — see below) |

```yaml
axa_version: "0.2"
id: task-0042
title: "Salespersons & Lead Tables"
created: 2026-10-20
stage: executing                    # decomposing|planning|doubt-review|executing|qa|review|documenting|extracting|done
mode: Standard                      # Full Pipeline | Standard | Quick
mode_rationale: "CRUD + UI, no migration risk"

feature:
  owner: aska
  branch: feat/salespersons-lead-tables
  scope_summary: "Salesperson CRUD + lead assignment table..."

plan:                               # written only after user approves the draft in chat
  - {id: P1, text: "Model + migration salespersons", status: done}
  - {id: P2, text: "Lead assignment table UI", status: in-progress}
  - {id: P3, text: "QA pass", status: pending}

routing:
  planner:      {required: true,  reason: "new tables, needs spec"}
  doubt_review: {required: true,  reason: "assignment logic has edge cases"}
  unit_test_writer: {required: true, reason: "per ORBIT lesson"}

findings:
  - {id: QA-001, source: QA, severity: Warning, status: Open,
     owner: qa, verification: "repro steps..."}

verification:
  tests:      {command: "phpunit", result: "46 passed / 107 assertions"}
  build_lint: {command: "...", result: "..."}
  manual:     "scenario + observed result"
  not_verified: "reason + remaining risk"

handoffs:                           # THE THREAD — ordered, append-only
  - at: 2026-10-20T10:05:00+07:00
    from: planner
    to: executor
    summary: "Plan approved in chat: 3 steps. P2 is the risky one (see detail)."
    detail: "Full planner output, decisions, ruled-out approaches..."
    approved_via: chat
    artifacts: ["commit 6c0196c", "docs/plan.md"]
  - at: 2026-10-20T11:40:00+07:00
    from: executor
    to: qa
    summary: "P1+P2 done. Unit Test Writer caught N+1 on assignment query; fixed."
    detail: "..."
    approved_via: pipeline
    artifacts: ["commit a1b2c3d"]

tech_debt:                          # append-only, harvested by QA
  - "FK cascade delete on leads untested (MySQL)"

current:                            # CHEAP ENTRY POINT — read this first, always
  stage: qa
  next_agent: qa
  blocking: null
  last_updated: 2026-10-20
  pointer: "handoffs[-1]"           # where the next agent resumes reading
```

### The token mechanics (why this is cheaper than issues)

The file format alone saves little. The savings come from the **read/write
protocol** that a structured format makes enforceable (to be written into
`SKILL.md` / `RULES.md`):

1. **Selective reads.** An agent starting a stage reads, in order:
   `current:` → latest `handoffs[-1].summary` → `plan` steps for its own
   stage. It reads `detail` or older handoffs **only** when the summary is
   insufficient — and must say why in its own handoff. With issues this
   discipline is impossible: `gh issue view --comments` returns everything.
2. **summary/detail split.** `summary` ≤ ~280 chars, decision-focused, always
   read. `detail` carries evidence and logs, read on demand. Free-form issue
   comments cannot enforce this split.
3. **No metadata noise.** No API envelopes, author URLs, or HTML links in
   what the agent reads.
4. **Git is the history.** Agents never re-read "just in case" — older state
   is recoverable from git, so working reads stay small.

### thread.html

- Generated by `.axa/render-thread.py` (stdlib + PyYAML — see Decisions)
  from `state.yaml`. Runs after every handoff write — a pipeline rule, not a
  suggestion.
- Renders like a GitHub issue page: header with stage badge, plan checklist
  with progress, handoff cards in chronological order (the thread), findings
  ledger table, verification evidence, tech debt.
- `.axa/tasks/index.html` (in scope for v2.0, minimal — see Decisions): task
  list with stage badges — the local equivalent of the issue list. Both
  backends appear; GitHub-backed tasks link out via `issue_url`.
- `thread.html` is a build artifact: gitignored, regenerable at any time.

## GitHub backend: removed (amendment 2026-10-20)

The v0.1.0 GitHub-issue backend is gone, not opt-in. `templates/issue-template.md`
and `templates/tickets.template.md` are deleted; every `gh` reference is removed
from docs and agents. Rationale: the only user is Aska; carrying a second backend
for hypothetical teams is unjustified maintenance.

## What this is not

- **Not HITL·Work local mode.** HITL·Work's local tracking is flat markdown —
  the weakness this design explicitly avoids. Axa-local keeps the ordered,
  per-handoff thread and renders it as a thread.
- **Not a second source of truth.** `state.yaml` is the only writable state.
  `thread.html` is derived.

## Changes required (v2.0.0)

1. `SKILL.md`: STOP gates rewritten — the `gh` auth gate is deleted; task
   creation writes `state.yaml` from `templates/state-template.yaml`; add the
   selective-read and summary/detail handoff protocols; `render-thread.py`
   runs after each handoff.
2. New: `templates/state-template.yaml`, `templates/render-thread.py`
   (copied to the project's `.axa/` on first run), `.axa/tasks/` layout,
   `.gitignore` entry for `thread.html`.
   (In the skill repo the renderer ships as `templates/render-thread.py` and
   is copied to the project's `.axa/` on first run — same convention as
   `templates/tickets.template.md` → `.axa/tickets.md`. `.axa/tasks/` lives
   in the user's project, not in this repo.)
3. `RULES.md`: label mapping (`axa:*`) → `stage:` enum; First Run Setup creates
   `.axa/tasks/` and copies the renderer instead of `tickets.md`; routing
   table unchanged.
4. `README.md`: prerequisites drop `gh` entirely (now: Python 3 + PyYAML);
   document the local backend.
5. `CHANGELOG.md`: v2.0.0 entry. `templates/issue-template.md` and
   `templates/tickets.template.md` **deleted**.

## Consequences

**Good:**
- Token cost per stage drops from "whole thread, every time" to
  "current + latest summary + own plan steps". The saving compounds with
  thread length — exactly where issues hurt most.
- No `gh` CLI, no auth, no network, no API rate limits for the default path.
  Works offline, on any machine with the repo.
- Human progress checks cost zero tokens (open `thread.html`).
- Full audit trail preserved — better, in fact: `state.yaml` diffs in git are
  cleaner than issue-body edit history.

**Bad / accepted:**
- Lose GitHub-native collaboration: teammate comments, notifications, search,
  label dashboards. Accepted outright — the only user is Aska (amendment
  2026-10-20); a team backend would be a new ADR, not a resurrection.
- Concurrent writers to one `state.yaml` can clobber each other. Accepted:
  Axa is single-user; one task = one agent at a time is already the pipeline
  invariant.
- New soft dependency for the renderer (PyYAML — see Decisions).

## Decisions (open questions resolved 2026-10-20, delegated to Miu)

1. **Gitignore `thread.html`.** It is regenerable from `state.yaml`; HTML
   diffs in git are noise. `state.yaml` is committed — the audit trail is
   cleaner than issue-body edit history.
2. **`index.html` is in scope for v2.0, minimal.** Without it there is no
   "issue list" equivalent and a human must hunt through directories. It is
   ~20 extra lines in the same generator script.
3. **PyYAML for the renderer.** Agents write YAML as plain text (no parser
   needed); only the renderer parses. One `pip install pyyaml`, battle-tested,
   strictly lighter than the `gh` CLI + auth prerequisite it replaces. A
   hand-rolled YAML-subset parser would be a new maintenance burden with
   real indentation edge-case risk. The script must fail with a clear
   one-liner install hint when PyYAML is missing.
4. **ADR location: `docs/adr/NNN-slug.md`, starting at 001.** Standard
   convention. This ADR becomes `docs/adr/001-local-yaml-html-state-backend.md`.
5. **Retire `.axa/tickets.md` as the registry.** The task list is derived from
   `.axa/tasks/` — single source of truth stays `state.yaml`. The `SKILL.md`
   STOP gate referencing `tickets.md` is updated to check `.axa/tasks/`
   instead. (One-time migration of existing `tickets.md` entries on first
   v2.0 run.)
6. **Sequential IDs: `task-0042`** (zero-padded, continuing existing ticket
   numbering). Stable and sortable; slugs rot when titles change and make
   for annoying directory names.
