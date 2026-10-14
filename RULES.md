# Axa Rules

Detail rules behind `SKILL.md` (the index). Same HITL·Work pipeline, but the workflow state lives in a GitHub issue instead of local files. Read the sections relevant to your stage before acting.

## Prerequisites

- `gh` CLI installed and authenticated (`gh auth status`). STOP if it is not: ask the user to set it up before any agent runs.
- The repository must be a GitHub repo (`gh` resolves the current repo). Axa does not work outside GitHub.

## State mapping

Agent files were written for HITL·Work's local files. In Axa, translate every reference:
- `status.md` -> the GitHub issue body for this feature (read: `gh issue view <number>`; write: `gh issue edit <number> --body-file <file>`)
- `.hitl-work/features/<slug>/` artifacts (`plan.md`, `qa-report.md`, etc.) -> the issue body (plan + live status) and issue comments (reports, handoffs)
- Never create `.hitl-work/features/` directories. The only local files are `.hitl-work/preferences.md` and `.hitl-work/tickets.md`.

## Issue State & Artifacts

For each non-trivial feature, create one GitHub issue and record `slug -> issue number` in `.hitl-work/tickets.md`. The issue body is the live state: copy `templates/issue-template.md` into it at creation. Every agent must read the issue body before acting (`gh issue view <number>`) and update only the fields belonging to its role before handoff. Keep the plan, routing decisions, findings ledger, verification evidence, and session log current at every handoff.

- **Issue body** = plan + live status (updated in place via `gh issue edit`)
- **Issue comments** = handoff log and reports (each stage posts one summary comment: what was done, key decisions, what is next)
- **Labels** = pipeline stage: `axa:planning`, `axa:executing`, `axa:qa`, `axa:review`, `axa:done`
- **Local files** = only `.hitl-work/preferences.md` (anti-slop etc.) and `.hitl-work/tickets.md` (slug -> issue number registry)

**Start where:**
- Large PRD -> **Decomposer** (task list posted as an issue comment)
- New feature/bug/refactor -> **Planner**
- Plan approved in issue body -> **Executor**
- Code written -> **QA** or specialist review
- Code needs triage -> **Debug**
- Markdown spec to test -> **Unit Test Writer**

## Companion Skill: anti-slop (opt-in)

HITL·Work pairs well with [anti-slop](https://github.com/miqdadbadjuber/anti-slop), a skill set that filters generic AI-generated code, UI, and copy. Integration is strictly opt-in. Run this gate ONCE per project, BEFORE any agent runs:

1. **Detect.** Run `npx skills list | grep -i antislop`. If nothing matches, inspect the active agent's skill directories (`.claude/skills/`, `.agents/skills/`, `~/.claude/skills/`, `~/.agents/skills/`, or the equivalent). The result must be exactly one of: INSTALLED or NOT INSTALLED. Write the result to `.hitl-work/preferences.md` (create `.hitl-work/` and the file if they do not exist).
2. **Gate.** If the result is NOT INSTALLED and `.hitl-work/preferences.md` contains no `antislop:` entry: STOP. Do not start the Planner, Executor, QA, or any other agent. Ask the user exactly this: "anti-slop is not installed. Install it and combine with HITL·Work so QA and Documentation also check outputs for AI slop? (yes / yes, always / no / never ask again)". Wait for the user's answer, then:
   - `yes` → run `npx skills add miqdadbadjuber/anti-slop`; record `antislop: installed` in `.hitl-work/preferences.md`.
   - `yes, always` → same as `yes`, plus record in `~/.hitl-work/preferences.md` so future projects skip this gate.
   - `no` → record `antislop: declined` in `.hitl-work/preferences.md`; continue without it.
   - `never ask again` → record in `~/.hitl-work/preferences.md`; never run this gate again on any project.
   Only after the answer is recorded may the pipeline continue.
3. **Combine only when present.** When the anti-slop skill is available (pre-installed or just installed), the Planner, QA, and Documentation agents must read its core rules. The Planner applies them while writing `plan.md` (see the Anti-slop hard rules in `agents/planner.md`); QA and Documentation add an explicit slop check to their verdicts: reject generic AI-pattern code, copy, and UI. Note: `npx skills add` copies the skill folders but does not write a session auto-load pointer; HITL·Work agents load the anti-slop rules explicitly, so no pointer is needed.

## Agents

| Agent | File | When |
|-------|------|------|
| Decomposer | `agents/decomposer.md` | PRD too large for one spec |
| Planner | `agents/planner.md` | No spec yet |
| Doubt Review | `agents/doubt-review.md` | After Planner, before Executor — risky/multi-tenant/DB changes |
| Executor | `agents/executor.md` | `plan.md` exists |
| Unit Test Writer | `agents/unit-test-writer.md` | After Executor — test plan + code from markdown spec |
| QA | `agents/qa.md` | After Executor reports done |
| Architecture Review | `agents/architecture-review.md` | Layer boundaries, duplication |
| Security Review | `agents/security-review.md` | New endpoints, auth, input handling |
| Performance Review | `agents/performance-review.md` | N+1, indexing, caching |
| Migration Review | `agents/migration-review.md` | Any DB migration |
| Refactor Agent | `agents/refactor-agent.md` | Code works but needs cleanup |
| API Agent | `agents/api-agent.md` | DESIGN / INTEGRATION / AUDIT |
| Debug Agent | `agents/debug.md` | Root-cause investigation (no fixes) |
| Documentation | `agents/documentation.md` | After QA passes |
| Skill Extractor | `agents/skill-extractor.md` | After QA, distill patterns |
| UI/UX Planner | `agents/ui-ux-planner.md` | When Planner delegates UI |
| UI Skill Extractor | `agents/ui-skill-extractor.md` | After QA, extract visual tokens |

## Workflow Modes

The user explicitly chooses the mode. Before any agent runs: STOP, present all three modes below with your recommendation (the lowest safe mode per the eligibility rules), and wait for the user's choice. Do not proceed until the user has chosen. If the chosen mode violates the eligibility rules, refuse with a concrete explanation and ask again. Record the chosen mode in `status.md`. In non-interactive runs where the user cannot be reached, use the lowest safe mode and record that the choice was automatic. Any risk signal escalates the work immediately; never use Quick mode to bypass a required review.

| Mode | Use for | Required path | Not allowed when |
|---|---|---|---|
| 🔴 **Full Pipeline** | New feature, multi-module work, migration, security-sensitive change, external integration, unclear/high blast radius | Decomposer when scope needs splitting → full Planner → required reviews → Executor → tests when applicable → QA → docs/skill extraction as applicable | Never downgrade merely to save time |
| 🟡 **Standard** | Scoped bug fix or enhancement, understood root cause, normally 1–2 files and no high-risk surface | Planner Lite → Executor → QA; add only reviews triggered by routing | Migration, auth/authz, external API, user-controlled input, cross-module change, unclear root cause, or more than 2 expected files |
| 🟢 **Quick** | Typo, comment, documentation-only correction, known-safe config value, or isolated hotfix with an obvious one-file fix | Executor with Quick Change Record → minimal QA | Migration, secrets, auth/authz, security surface, external API, user input, dependency, public API/contract, database query, unclear root cause, or more than 1 expected file |

**Quick Change Record** must state: target file, exact intended change, expected behavior, rollback method, and why the change is eligible for Quick mode. Executor stops and escalates to Standard or Full if the actual code contradicts that record.

## Lean Code Discipline

HITL·Work wraps code in a lot of process. These values keep the code itself lean. They were adapted from an audit of ponytail (https://github.com/DietrichGebert/ponytail, MIT). No external skill is required: the values below are native HITL·Work rules.

**Planner:** before writing the spec, run the minimality ladder for every planned piece of new code. Rungs: 1. does it need to exist, 2. already in this codebase, 3. standard library or platform feature, 4. installed dependency (never add one for a few lines), 5. one line a reader gets at a glance, 6. otherwise the minimum that works. Record the justifying rung (or the existing code reused) per spec item. This replaces the checkbox-style YAGNI check with per-item justification. Full Pipeline uses the full ladder; Standard keeps the YAGNI check without per-item records; Quick is trivially minimal by definition.

**Executor:** implement the minimum per spec, reuse-first. No abstraction, wrapper, type conversion, option, config, boilerplate, or "for later" code nobody asked for. Deletion beats addition. Bug fixes: grep every caller first, then fix the root cause once in the shared code. A deliberate shortcut gets a `shortcut: <the limit>, <when to upgrade>` comment.

**QA:** add a cut-list to Phase 5 findings. Flag over-engineering (unasked abstractions, wrappers, boilerplate, speculative flexibility) as Warning findings. Never flag the never-cut list: validation at trust boundaries, error handling that prevents data loss, security, accessibility, anything the user explicitly asked for. Harvest `shortcut:` comments into TECH-DEBT.md entries.

**Unit Test Writer:** already aligned. New non-trivial logic (a branch, a loop, a parser, money or security handling) leaves one small test; trivial changes need none.

**Explicit non-goal:** leanness applies to shipped code only, never to HITL·Work process artifacts (`plan.md`, `status.md`, `qa-report.md`, `TECH-DEBT.md`, reviews). The paper trail stays complete; the code stays lean.

## Required Routing

| Change condition | Required stages |
|---|---|
| New endpoint, auth/authz, webhook, user-controlled input, external API | Security Review |
| Schema change, index, backfill, or data migration | Doubt Review + Migration Review |
| New query, bulk operation, caching, queue/job, or high-traffic endpoint | Performance Review |
| Cross-module change, new architectural pattern, or substantial refactor | Architecture Review |
| New screen, critical UI flow, reusable UI component, or substantial redesign | UI/UX Planner; UI Skill Extractor after QA |
| Non-trivial business logic | Unit Test Writer, including approved Test Plan |
| Bug with unknown root cause | Debug Agent before planning a fix |

A required stage may be skipped only when `status.md` records the reason and the human accepts the risk.

## Re-verification Loop

1. QA or specialist findings receive IDs (`QA-001`, `SEC-001`, `PERF-001`, and so on) in `status.md`.
2. Executor fixes only approved findings and marks them `Fixed` with the changed files.
3. QA verifies the regression after every fix. The specialist who reported a Critical finding re-checks it before closure.
4. A finding is closed only as `Fixed`, `Accepted risk` (human decision recorded), or `Deferred` (owner and follow-up recorded).

### Conflicting findings

When two specialist reviews contradict each other (for example Security requires X while Performance requires Y):

1. Do not let the Executor pick a side on its own.
2. Record both findings in `status.md` with status `Open` and note the conflict explicitly.
3. STOP and present the trade-off to the human. The human arbitrates.
4. Record the decision and its rationale in `status.md`. Only then may the Executor proceed.

## Session Recovery

If your context was compacted, the session restarted, or you are picking up existing work:

1. Find the feature state: look up the slug in `.hitl-work/tickets.md` to get the issue number. If several features exist, continue the most recently updated one, or ask the user which one.
2. Read the issue body and recent comments in full (`gh issue view <number> --comments`). Trust them over your memory of this conversation.
3. Continue from the **Current Handoff** field in the issue body. Do not re-run stages already marked complete.
4. If no ticket exists for the requested work, start the pipeline normally (create the issue first).

## Instructions

1. **Read the agent file before acting.** Never summarize from memory.
2. **Follow each agent's process exactly.** Boundaries are intentional.
3. **Respect the selected mode.** Full Pipeline requires Planner and QA; Standard requires Planner Lite and QA; Quick may skip Planner only with a recorded Quick Change Record and minimal QA. Don't skip QA to ship.
4. **HITL checkpoints (two channels):**
   - Chat (primary): stop and wait for the user's approval in the harness, exactly like HITL·Work.
   - Issue (async): at every checkpoint also post a comment (`gh issue comment`) summarizing what needs approval. A teammate may approve via issue reply or reaction.
   - Either channel unblocks; record which channel approved and by whom.
   - After Decomposer -> human reviews task list. After Planner -> optionally run Doubt Review. After Executor -> optionally run Unit Test Writer (recommended for non-trivial logic). After Unit Test Writer -> QA uses generated tests as baseline. QA FAIL -> return to Executor.
5. **Specialist reviews report only** — findings go back to Executor to fix.
6. **Close the loop** with Docs + Skill Extractor after QA passes.

## Workflow

1. **Select mode** — STOP and ask the user to choose explicitly (Full / Standard / Quick), presenting your recommendation. Validate the choice against the eligibility rules; refuse unsafe picks with an explanation. Record the mode and reason in the issue body.
2. **Decompose** *(Full only, optional)* — `agents/decomposer.md`. Output the task list as an issue comment. Stop for review.
3. **Plan** — Full: `agents/planner.md` full spec. Standard: Planner Lite spec. Quick: Quick Change Record only. Show the plan in chat; write it to the issue body only after the user's explicit approval.
4. **Doubt Review** *(required by routing; otherwise Full only when risk warrants it)* — `agents/doubt-review.md`. Verdict: READY / BLOCKED / NEEDS CLARIFICATION.
5. **Execute** — `agents/executor.md`. One step at a time. Stop and escalate if scope exceeds the selected mode.
6. **Unit Test Writer** *(required by routing; otherwise optional)* — `agents/unit-test-writer.md`. Test Plan -> approval -> Test Code.
7. **QA** — Full/Standard: full QA. Quick: minimal QA. All modes require a clear PASS / FAIL / PASS WITH WARNINGS verdict and recorded evidence.
8. **Specialist Reviews** *(required by the routing table; otherwise as needed, parallel ok)* — findings by severity -> Executor -> re-verification.
9. **Docs & Skill Extraction** — Full when applicable; Standard/Quick only when the change establishes a reusable or user-facing behavior, after all blocking findings are closed.

## Rules

- Never let one agent do another's job.
- Always read codebase skill files before speccing.
- Every spec must include "What NOT to Touch" and "Breaking Changes".
- Executor stops and asks on ambiguity — never improvises.
- Unit Test Writer never skips Test Plan approval.
