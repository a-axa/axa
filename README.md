# Axa — HITL Workflow on GitHub Issues

Vibe coding is fast. It's also how you ship bugs, lose context between sessions, and end up with code nobody can audit — including your team.

Axa keeps the speed. It adds structure. Same 17-agent HITL·Work pipeline, but the workflow state lives in a **GitHub issue** instead of local files: the issue body is the live plan + status, comments are the handoff log, labels track the stage. Your team can follow, review, and audit every feature without cloning anything.

## Axa vs HITL·Work

| | HITL·Work | Axa |
|---|---|---|
| Workflow state | `.hitl-work/features/<slug>/status.md` | GitHub issue body |
| Handoff log | Session Log table in `status.md` | Issue comments |
| Stage tracking | Local files | Labels (`axa:planning` … `axa:done`) |
| Ticket registry | n/a | `.hitl-work/tickets.md` (slug → issue #) |
| Works offline | Yes | No — requires GitHub |
| Best for | Solo dev, local-first | Teams, shared audit trail |

The 17 agent files are the same pipeline with one translation rule: wherever an agent file says `status.md`, read the issue body instead.

## Prerequisites

- `gh` CLI installed and authenticated (`gh auth status`). Axa stops before any agent runs if this is missing.

## Quick start

1. Install the skill: `npx skills add iskandar221201/axa`
2. In your project: `mkdir -p .hitl-work && cp <skill>/tickets.template.md .hitl-work/tickets.md`
3. Start a feature: the agent creates a GitHub issue from `issue-template.md`, records it in `tickets.md`, and runs the pipeline.
4. Checkpoints happen in chat (primary) and as issue comments (async for teammates). The plan is written to the issue body only after you approve the draft in chat.

## Agents

Decomposer → Planner → Doubt Review → Executor → Unit Test Writer → QA → Specialist Reviews (Architecture, Security, Performance, Migration, API, Debug, Refactor) → Documentation → Skill Extractor. UI/UX Planner and UI Skill Extractor for visual work. See `RULES.md` for the full routing table.

## License

MIT
