# Axa — Vibe Coding with a Paper Trail

Vibe coding is fast. It's also how you ship bugs, lose context between sessions, and end up with code nobody can audit — including your team.

Axa keeps the speed. It adds structure. 17 agents, one job each. The workflow state lives in a **GitHub issue**: the issue body is the live plan + status, comments are the handoff log, labels track the stage. Your team can follow, review, and audit every feature without cloning anything.

> Ponytail teaches what to build. Axa teaches how to build it.

![skill](https://img.shields.io/badge/skill-axa-0e7c7b?style=flat-square)
![agents](https://img.shields.io/badge/agents-17-slate?style=flat-square)
![license](https://img.shields.io/badge/license-MIT-green?style=flat-square)

## Prerequisites

- `gh` CLI installed and authenticated (`gh auth status`). Axa stops before any agent runs if this is missing.

## Quick Start

### Terminal

```bash
npx skills add iskandar221201/axa
```

That's it. Axa sets up `.axa/` on first run.

### Prompt

If you prefer not to use the terminal, copy this and paste it into your AI agent:

```
Load the Axa skill from https://github.com/iskandar221201/axa and start a new feature.
Ask me which workflow mode to use (Full / Standard / Quick), then create a GitHub issue
and run the pipeline from there.
```

Axa will handle the rest — creating the issue, running the agents, and keeping the state in the issue body.

## Agents

Decomposer → Planner → Doubt Review → Executor → Unit Test Writer → QA → Specialist Reviews (Architecture, Security, Performance, Migration, API, Debug, Refactor) → Documentation → Skill Extractor. UI/UX Planner and UI Skill Extractor for visual work. See `RULES.md` for the full routing table.

## 🤝 Pairs well with: [anti-slop](https://github.com/miqdadbadjuber/anti-slop)

Axa gives your agents structure. [anti-slop](https://github.com/miqdadbadjuber/anti-slop) gives their output taste: it filters generic AI-generated code, UI, and copy.

The pairing is opt-in and handled automatically. On the first run in a project, Axa checks whether the anti-slop skill is installed:

- **Installed** → the Planner, QA, and Documentation agents read its rules and add an explicit slop check to their verdicts.
- **Not installed** → the agent stops and asks you first (`yes` / `yes, always` / `no` / `never ask again`). Nothing is ever installed silently, and your answer is saved (`.axa/preferences.md` per project, `~/.axa/preferences.md` global) so you are only asked once.

Install it manually any time:

```bash
npx skills add miqdadbadjuber/anti-slop
```

## 🤝 Pairs well with: [ponytail](https://github.com/dietrichgebert/ponytail)

Axa teaches how to build. [ponytail](https://github.com/dietrichgebert/ponytail) teaches what to build: lazy-first, native-first, minimum viable code. The Planner reads ponytail's constraints before writing a spec — so the plan stays lean before the pipeline even starts.

## Not for everyone

Axa adds process. Every feature gets a GitHub issue, a plan, a QA report, and a findings ledger. That overhead is worth it when you need audit trails, async team visibility, or a ticket-driven workflow. It's not worth it for a quick one-liner fix — use Quick mode or skip Axa entirely.

If you want the same pipeline without GitHub Issues, see [HITL·Work](https://github.com/iskandar221201/hitl-work) — same agents, local files.

## License

MIT
