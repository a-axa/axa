# Axa — Vibe Coding with a Paper Trail

Vibe coding is fast. It's also how you ship bugs, lose context between sessions, and end up with code nobody can audit — including your team.

Axa keeps the speed. It adds structure. 17 agents, one job each. The workflow state lives in **local YAML**: `.axa/tasks/<task-id>/state.yaml` holds the live plan + status + handoff thread, and `thread.html` renders it as a readable timeline. Full audit trail in git, zero network calls, minimal token cost.

> Ponytail teaches what to build. Axa teaches how to build it.

![skill](https://img.shields.io/badge/skill-axa-0e7c7b?style=flat-square)
![agents](https://img.shields.io/badge/agents-17-slate?style=flat-square)
![taste](https://img.shields.io/badge/taste-learning-7c3aed?style=flat-square)
![license](https://img.shields.io/badge/license-MIT-green?style=flat-square)

## 🛡️ Whoever built it never grades it

Most agent pipelines let the same session write the code and review it — that's how "looks good" happens. Axa enforces separation of duties:

- review stages (QA, Doubt Review, specialists) run in **fresh sessions**, never the one that built the work
- reviewers read **blind-first**: plan → code → own findings → *then* the builder's summary
- verdicts are **bound to the exact commit SHA** — a new commit invalidates them
- fix ping-pong is **capped at 2 rounds**, then it escalates to you

And if you have more than one model available, reviewers run on a **different model** than builders. Best effort, honestly reported. See `RULES.md` § Separation of Duties (pattern paired from [claudex-loop](https://github.com/chaseai-yt/claudex-loop)). Example output: [`examples/task-0042/thread.html`](examples/task-0042/thread.html).

## 🧠 It learns your taste

Every pipeline run makes the next one smarter. When the Planner picks a pattern, Doubt Review accepts a risk, or QA rejects AI slop — Axa writes it down in `.axa/preferences.md`, a living document every agent reads before acting. No rules to write, no prompts to maintain: your taste accumulates automatically, one decision at a time.

- **Planner** records non-obvious spec decisions — pattern chosen, approach ruled out
- **Doubt Review** records risks knowingly taken, and why
- **Executor** records what you preferred when the spec got revised mid-flight
- **QA** records what got flagged as slop — so it never ships twice
- **Specialist reviews** record which patterns to avoid or reuse in *this* codebase

The patterns you keep, it remembers. The ones you delete, it forgets.

Inspired by [Command Code](https://commandcode.ai/)'s taste learning.

## Prerequisites

- Python 3 with PyYAML (`pip install pyyaml`) — for rendering `thread.html`. No CLI auth needed; agents read/write `state.yaml` directly.

## Quick Start

### Terminal

```bash
npx skills add a-axa/axa
```

That's it. Axa sets up `.axa/` on first run.

### Prompt

If you prefer not to use the terminal, copy this and paste it into your AI agent:

```
Load the Axa skill from https://github.com/a-axa/axa and start a new feature.
Ask me which workflow mode to use (Full / Standard / Quick), then create a task state file
and run the pipeline from there.
```

Axa will handle the rest — creating the task file, running the agents, and keeping the state in `state.yaml`.

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

Axa adds process. Every feature gets a task file, a plan, a QA report, and a findings ledger. That overhead is worth it when you need audit trails and a verifiable build record. It's not worth it for a quick one-liner fix — use Quick mode or skip Axa entirely.

v2.0 moved the state backend from GitHub issues to local YAML — see [docs/adr/001-local-yaml-html-state-backend.md](docs/adr/001-local-yaml-html-state-backend.md). For the same pipeline with plain-Markdown local tracking (no thread model), see [HITL·Work](https://github.com/a-axa/hitl-work).

## License

MIT
