# Changelog

All notable changes to Axa are documented here.

## [Unreleased]

## [0.1.0] - 2026-10-15

### Added
- Initial release: HITL·Work 17-agent pipeline with GitHub issues as the state backend
- `SKILL.md` (980 chars): issue-based orchestrator with STOP gates (gh prerequisite, ticket mapping, plan review in chat, explicit mode choice)
- `RULES.md`: full rules adapted for issues — state mapping (`status.md` -> issue body), label conventions, two-channel checkpoints (chat + issue comments), issue-based session recovery
- `issue-template.md`: issue body template (plan + live status + findings ledger + session log)
- `tickets.template.md`: local `.hitl-work/tickets.md` registry mapping feature slugs to issue numbers
- Prerequisite gate: `gh` CLI must be installed and authenticated before any agent runs
- Plan review gate: the plan is written to the issue body only after the user approves the draft in chat
- All 17 agent files adapted to issue-based outputs: plan/reviews/specs go to the issue body or comments, never local files
