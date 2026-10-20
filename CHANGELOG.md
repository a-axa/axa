# Changelog

All notable changes to Axa are documented here.

## [Unreleased]

### Added
- Anti-bias rules (`RULES.md` § Separation of Duties, pattern paired from claudex-loop): never review your own work, fresh session per review stage, blind-first review order, adversarial stance, re-run-don't-trust, verdicts bound to commit SHA, 2-round fix budgets, coverage + limitations reporting, per-handoff `model:` recording (use a different model for review stages when available, e.g. via 9router)
- `thread.html` now shows the model per handoff

## [2.0.0] - 2026-10-20

### Breaking
- State backend moved from GitHub issues to local YAML (`docs/adr/001-local-yaml-html-state-backend.md`): `.axa/tasks/<task-id>/state.yaml` is the single source of truth (plan + status + handoff thread); `thread.html` is generated for human review
- `gh` CLI is no longer required — or referenced — anywhere; hard prerequisite is now Python 3 + PyYAML (for the renderer)
- Deleted: `templates/issue-template.md`, `templates/tickets.template.md`; legacy `.axa/tickets.md` ignored

### Added
- `templates/state-template.yaml`: local task state template with the binding token protocol in its header comments
- `templates/render-thread.py`: generates per-task `thread.html` + `index.html` from `state.yaml` (copied to the project's `.axa/` on first run)
- Token protocol: agents read only `current:`, the latest handoff `summary`, and their own `plan` steps per stage; handoffs split into `summary` (≤ ~280 chars) + `detail`

## [1.0.1] - Unreleased

### Added
- Taste preference learning: `.axa/preferences.md` is now a living document — every agent appends a short entry when a pipeline decision reveals a project preference (pattern chosen, risk accepted, approach ruled out, mistake corrected); append-only, one entry per decision, read by all agents before acting so past decisions are never repeated

## [1.0.0] - 2026-10-15

### Added
- Initial release: 17-agent human-in-the-loop pipeline with GitHub issues as the state backend
- `SKILL.md` (980 chars): issue-based orchestrator with STOP gates (gh prerequisite, ticket mapping, plan review in chat, explicit mode choice)
- `RULES.md`: full rules adapted for issues — state mapping (`status.md` -> issue body), label conventions, two-channel checkpoints (chat + issue comments), issue-based session recovery
- `issue-template.md`: issue body template (plan + live status + findings ledger + session log)
- `tickets.template.md`: local `.axa/tickets.md` registry mapping feature slugs to issue numbers
- Prerequisite gate: `gh` CLI must be installed and authenticated before any agent runs
- Plan review gate: the plan is written to the issue body only after the user approves the draft in chat
- All 17 agent files adapted to issue-based outputs: plan/reviews/specs go to the issue body or comments, never local files
