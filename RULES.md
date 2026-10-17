# Axa Rules

Detail rules behind `SKILL.md` (the index). The workflow state lives in a GitHub issue instead of local files. Read the sections relevant to your stage before acting.

## Prerequisites

- `gh` CLI installed and authenticated (`gh auth status`). STOP if it is not: ask the user to set it up before any agent runs.
- Minimum `gh` CLI version: **2.40.0** (`gh --version`). Earlier versions have GraphQL issues with `gh issue view`. If older: ask the user to update before continuing.
- The repository must be a GitHub repo (`gh` resolves the current repo). Axa does not work outside GitHub.
- Use `gh issue view <number> --json body,comments,labels` instead of plain `gh issue view` to avoid GraphQL deprecation errors from Projects (classic).

## First Run Setup

Before any agent runs, check whether `.axa/` exists in the project root:

```
if .axa/ does not exist:
  mkdir -p .axa
  cp <skill-root>/templates/tickets.template.md .axa/tickets.md
  touch .axa/preferences.md
```

`<skill-root>` is wherever `npx skills` installed Axa — check `.claude/skills/axa/`, `.agents/skills/axa/`, `~/.claude/skills/axa/`, or `~/.agents/skills/axa/`. Use the first match found.

If `tickets.md` already exists, do not overwrite it. If the template cannot be found, create `.axa/tickets.md` with this content:

```markdown
# Axa Ticket Registry

slug -> issue number

```

Only after `.axa/` is confirmed to exist may the pipeline continue.

## Project Preferences Learning

`.axa/preferences.md` is a living document that grows with the project. This is the taste-learning loop, and it has two mandatory halves:

1. **READ FIRST.** No agent plans, executes, reviews, or decides before reading `.axa/preferences.md` in full and applying what it finds. An agent that acts without this read is violating the pipeline — the learning only works if every agent starts from the accumulated taste.
2. **APPEND AFTER.** Every agent appends to it when a pipeline decision reveals a project preference — a pattern chosen, a risk accepted, an approach ruled out, a mistake corrected.

**Never overwrite — append only. One entry per decision, short and specific.**

### When to read

| Agent | Read before |
|-------|-------------|
| Decomposer | Splitting scope — apply recorded structural preferences |
| Planner | Writing the spec — apply chosen patterns, respect ruled-out approaches |
| Doubt Review | Assessing risk — check already-accepted risks so they are not re-flagged |
| Executor | Writing code — use preferred patterns, avoid flagged ones |
| Unit Test Writer | Writing the test plan — use the recorded test approach for this project |
| QA | Giving a verdict — check accepted/rejected findings and recorded slop patterns |
| Specialist Reviews | Reviewing — check recorded pattern approvals and avoidances |
| UI/UX Planner | Designing — apply recorded visual decisions to new screens |
| Documentation | Writing docs — match recorded documentation conventions |
| Skill Extractor | Extracting — skip patterns already captured in preferences |

If `.axa/preferences.md` is empty or missing, the read still happens (confirm the file state) and the agent proceeds — then appends the first entries as decisions are made.

### When to write

| Agent | Write when |
|-------|-----------|
| Planner | Spec approved with a non-obvious decision — pattern chosen over another, approach explicitly ruled out |
| Doubt Review | Warning accepted — record what risk was knowingly taken and why |
| Executor | Step revised from spec — record what the user preferred instead |
| Unit Test Writer | Test approach decided for this project (e.g. RefreshDatabase over pure mocks) |
| QA | Finding accepted or rejected — record the preference it reveals |
| Specialist Reviews | Pattern flagged as avoid or approved for this codebase |
| UI/UX Planner | Visual decision that should propagate to future screens |

### Format

```markdown
## YYYY-MM-DD · [Agent] — [short title]
[One line: what was decided and why.]
```

### Examples

```markdown
## 2026-10-15 · Architecture Review — prefer two middleware classes over one parameterized
Two separate classes (EnsureUserIsSuperAdmin, EnsureUserIsAdmin) are clearer than one
parameterized middleware. Do not consolidate unless roles multiply beyond 3.

## 2026-10-15 · Doubt Review — global email uniqueness accepted for MVP
Two tenants cannot share an email address. Accepted: target use case makes collision
unlikely. Revisit if multi-org self-signup is added.

## 2026-10-15 · QA — border-right on active nav is AI slop
Removed border-right: 2px solid and shadow-sm from active nav state. Active state is
teal-dark text + teal-soft background + font-weight 600. No decoration.
```

### What NOT to write
- Decisions obvious from the spec or skill file
- Temporary workarounds that will be removed next sprint
- Anything already captured in a codebase skill file
- Duplicate of an existing entry — check before appending

## Issue State & Artifacts

For each non-trivial feature, create one GitHub issue and record `slug -> issue number` in `.axa/tickets.md`. The issue body is the live state: copy `templates/issue-template.md` into it at creation. Every agent must read the issue body before acting (`gh issue view <number> --json body,comments,labels`) and update only the fields belonging to its role before handoff. Keep the plan, routing decisions, findings ledger, verification evidence, and session log current at every handoff.

- **Issue body** = plan + live status (updated in place via `gh issue edit`)
- **Issue comments** = handoff log and reports (each stage posts one summary comment: what was done, key decisions, what is next)
- **Labels** = pipeline stage: `axa:planning`, `axa:executing`, `axa:qa`, `axa:review`, `axa:done`
- **Local files** = only `.axa/preferences.md` (project preferences) and `.axa/tickets.md` (slug -> issue number registry)

**Start where:**
- Large PRD -> **Decomposer** (task list posted as an issue comment)
- New feature/bug/refactor -> **Planner**
- Plan approved in issue body -> **Executor**
- Code written -> **QA** or specialist review
- Code needs triage -> **Debug**
- Markdown spec to test -> **Unit Test Writer**

## Companion Skill: anti-slop (opt-in)

Axa pairs well with [anti-slop](https://github.com/miqdadbadjuber/anti-slop), a skill set that filters generic AI-generated code, UI, and copy. Integration is strictly opt-in. Run this gate ONCE per project, BEFORE any agent runs:

1. **Detect.** Run `npx skills list | grep -i antislop`. If nothing matches, inspect the active agent's skill directories (`.claude/skills/`, `.agents/skills/`, `~/.claude/skills/`, `~/.agents/skills/`, or the equivalent). The result must be exactly one of: INSTALLED or NOT INSTALLED. Write the result to `.axa/preferences.md` (create `.axa/` and the file if they do not exist).
2. **Gate.** If the result is NOT INSTALLED and `.axa/preferences.md` contains no `antislop:` entry: STOP. Do not start the Planner, Executor, QA, or any other agent. Ask the user exactly this: "anti-slop is not installed. Install it and combine with Axa so QA and Documentation also check outputs for AI slop? (yes / yes, always / no / never ask again)". Wait for the user's answer, then:
   - `yes` → run `npx skills add miqdadbadjuber/anti-slop`; record `antislop: installed` in `.axa/preferences.md`.
   - `yes, always` → same as `yes`, plus record in `~/.axa/preferences.md` so future projects skip this gate.
   - `no` → record `antislop: declined` in `.axa/preferences.md`; continue without it.
   - `never ask again` → record in `~/.axa/preferences.md`; never run this gate again on any project.
   Only after the answer is recorded may the pipeline continue.
3. **Combine only when present.** When the anti-slop skill is available (pre-installed or just installed), the Planner, QA, and Documentation agents must read its core rules. The Planner applies them while writing the plan (see the Anti-slop hard rules in `agents/planner.md`); QA and Documentation add an explicit slop check to their verdicts: reject generic AI-pattern code, copy, and UI. Note: `npx skills add` copies the skill folders but does not write a session auto-load pointer; Axa agents load the anti-slop rules explicitly, so no pointer is needed.

## Companion Skill: ponytail (opt-in)

Axa pairs well with [ponytail](https://github.com/DietrichGebert/ponytail), a skill that makes your agent think like the laziest senior dev in the room: the best code is the code you never wrote. Where anti-slop guards output quality (QA, Documentation), ponytail shapes what gets built and how lean (Planner, Executor). Integration is strictly opt-in. Run this gate ONCE per project, BEFORE any agent runs:

1. **Detect.** Run `npx skills list | grep -i ponytail`. If nothing matches, inspect the active agent's skill directories (`.claude/skills/`, `.agents/skills/`, `~/.claude/skills/`, `~/.agents/skills/`, or the equivalent). The result must be exactly one of: INSTALLED or NOT INSTALLED. Write the result to `.axa/preferences.md` (create `.axa/` and the file if they do not exist).
2. **Gate.** If the result is NOT INSTALLED and `.axa/preferences.md` contains no `ponytail:` entry: STOP. Do not start the Planner, Executor, QA, or any other agent. Ask the user exactly this: "ponytail is not installed. Install it and combine with Axa so the Planner and Executor build lean (minimality ladder, reuse-first)? (yes / yes, always / no / never ask again)". Wait for the user's answer, then:
   - `yes` → run `npx skills add DietrichGebert/ponytail`; record `ponytail: installed` in `.axa/preferences.md`.
   - `yes, always` → same as `yes`, plus record in `~/.axa/preferences.md` so future projects skip this gate.
   - `no` → record `ponytail: declined` in `.axa/preferences.md`; continue without it.
   - `never ask again` → record in `~/.axa/preferences.md`; never run this gate again on any project.
   Only after the answer is recorded may the pipeline continue.
3. **Combine only when present.** When the ponytail skill is available (pre-installed or just installed), the Planner and Executor must read its rules. The Planner runs the minimality ladder for every planned piece of new code while writing the spec (see `agents/planner.md`). Rungs: 1. does it need to exist, 2. already in this codebase, 3. standard library or platform feature, 4. installed dependency (never add one for a few lines), 5. one line a reader gets at a glance, 6. otherwise the minimum that works. Record the justifying rung (or the existing code reused) per spec item. Full Pipeline uses the full ladder; Standard+ and Standard keep the YAGNI check without per-item records; Quick is trivially minimal by definition. The Executor implements the minimum per spec, reuse-first: no abstraction, wrapper, type conversion, option, config, boilerplate, or "for later" code nobody asked for. Deletion beats addition. Bug fixes: grep every caller first, then fix the root cause once in the shared code. A deliberate shortcut gets a `shortcut: <the limit>, <when to upgrade>` comment. QA adds a cut-list to Phase 5 findings: flag over-engineering (unasked abstractions, wrappers, boilerplate, speculative flexibility) as Warning findings. Never flag the never-cut list: validation at trust boundaries, error handling that prevents data loss, security, accessibility, anything the user explicitly asked for. Harvest `shortcut:` comments into the issue body `## Tech Debt` section. Note: `npx skills add` copies the skill folders but does not write a session auto-load pointer; Axa agents load the ponytail rules explicitly, so no pointer is needed.

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

The user explicitly chooses the mode. Before any agent runs: STOP, present all four modes below with your recommendation (the lowest safe mode per the eligibility rules), and wait for the user's choice. Do not proceed until the user has chosen. If the chosen mode violates the eligibility rules, refuse with a concrete explanation and ask again. Record the chosen mode in the issue body. In non-interactive runs where the user cannot be reached, use the lowest safe mode and record that the choice was automatic. Any risk signal escalates the work immediately; never use Quick mode to bypass a required review.

| Mode | Use for | Required path | Not allowed when |
|---|---|---|---|
| 🔴 **Full Pipeline** | New feature, multi-module work, migration, security-sensitive change, external integration, unclear/high blast radius | Decomposer when scope needs splitting → full Planner → required reviews → Executor → tests when applicable → QA → docs/skill extraction as applicable | Never downgrade merely to save time |
| 🟠 **Standard+** | Multi-file low-risk change: 3–6 files, no security/DB/auth/logic surface, pattern already established in the codebase (e.g. applying an existing design system across views) | Planner Lite → Executor → QA; Architecture Review only when structural (not visual); UI/UX Planner in lite mode when pattern is established | Migration, auth/authz, external API, business logic, DB queries, unclear root cause, or new patterns not yet established in the codebase |
| 🟡 **Standard** | Scoped bug fix or enhancement, understood root cause, normally 1–2 files and no high-risk surface | Planner Lite → Executor → QA; add only reviews triggered by routing | Migration, auth/authz, external API, user-controlled input, cross-module change, unclear root cause, or more than 2 expected files |
| 🟢 **Quick** | Typo, comment, documentation-only correction, known-safe config value, or isolated hotfix with an obvious one-file fix | Executor with Quick Change Record → minimal QA | Migration, secrets, auth/authz, security surface, external API, user input, dependency, public API/contract, database query, unclear root cause, or more than 1 expected file |

**Quick Change Record** must state: target file, exact intended change, expected behavior, rollback method, and why the change is eligible for Quick mode. Executor stops and escalates to Standard or Full if the actual code contradicts that record.

**Standard+ UI/UX Planner (lite mode):** when `pattern: established` is recorded in the issue body (the design system tokens, components, and states are already documented and applied on at least one other screen), the UI/UX Planner skips token sheet, full wireframe, and interaction spec. It produces only: which existing components to reuse, which states apply (populated/empty — skip loading/error for server-rendered pages), and copy/microcopy if it differs from existing screens. Full UI/UX spec is still required when introducing a new pattern, a new component, or a new interaction.

## Lean Code Discipline

Axa wraps code in a lot of process; the shipped code itself stays lean. Those values come from ponytail (see Companion Skill: ponytail above): the Planner runs the minimality ladder before speccing, the Executor implements reuse-first with no unasked abstraction, and QA keeps a cut-list for over-engineering in Phase 5 findings. Leanness applies to shipped code only, never to Axa process artifacts: the paper trail stays complete, the code stays lean.

## Required Routing

| Change condition | Required stages |
|---|---|
| New endpoint, auth/authz, webhook, user-controlled input, external API | Security Review |
| Schema change, index, backfill, or data migration | Doubt Review + Migration Review |
| New query, bulk operation, caching, queue/job, or high-traffic endpoint | Performance Review |
| Cross-module **architectural** change (layer boundaries, dependency direction, new patterns) | Architecture Review |
| Cross-module **visual** change (CSS tokens, design system classes, view partials only) | UI/UX Planner only — not Architecture Review |
| New screen, critical UI flow, reusable UI component, or new pattern | UI/UX Planner (full); UI Skill Extractor after QA |
| Established-pattern redesign (applying existing design system to additional screens) | UI/UX Planner (lite mode); UI Skill Extractor only if new tokens/components were introduced |
| Non-trivial business logic | Unit Test Writer, including approved Test Plan |
| Bug with unknown root cause | Debug Agent before planning a fix |

A required stage may be skipped only when the issue body records the reason and the human accepts the risk.

## Re-verification Loop

1. QA or specialist findings receive IDs (`QA-001`, `SEC-001`, `PERF-001`, and so on) in the issue body.
2. Executor fixes only approved findings and marks them `Fixed` with the changed files.
3. QA verifies the regression after every fix. The specialist who reported a Critical finding re-checks it before closure.
4. A finding is closed only as `Fixed`, `Accepted risk` (human decision recorded), or `Deferred` (owner and follow-up recorded).

### Conflicting findings

When two specialist reviews contradict each other (for example Security requires X while Performance requires Y):

1. Do not let the Executor pick a side on its own.
2. Record both findings in the issue body with status `Open` and note the conflict explicitly.
3. STOP and present the trade-off to the human. The human arbitrates.
4. Record the decision and its rationale in the issue body. Only then may the Executor proceed.

## Session Recovery

If your context was compacted, the session restarted, or you are picking up existing work:

1. Find the feature state: look up the slug in `.axa/tickets.md` to get the issue number. If several features exist, continue the most recently updated one, or ask the user which one.
2. Read the issue body and recent comments in full (`gh issue view <number> --json body,comments,labels`). Trust them over your memory of this conversation.
3. Continue from the **Current Handoff** field in the issue body. Do not re-run stages already marked complete.
4. If no ticket exists for the requested work, start the pipeline normally (create the issue first).

## Instructions

1. **Read the agent file before acting.** Never summarize from memory.
2. **Read `.axa/preferences.md` before acting — no exceptions.** This is the taste-learning loop: apply the recorded taste first, then work. An agent that skips this read is violating the pipeline.
3. **Follow each agent's process exactly.** Boundaries are intentional.
4. **Respect the selected mode.** Full Pipeline requires Planner and QA; Standard+ and Standard require Planner Lite and QA; Quick may skip Planner only with a recorded Quick Change Record and minimal QA. Don't skip QA to ship.
5. **Checkpoints (two channels):**
   - Chat (primary): stop and wait for the user's approval in the harness.
   - Issue (async): at every checkpoint also post a comment (`gh issue comment`) summarizing what needs approval. A teammate may approve via issue reply or reaction.
   - Either channel unblocks; record which channel approved and by whom.
   - After Decomposer -> human reviews task list. After Planner -> optionally run Doubt Review. After Executor -> optionally run Unit Test Writer (recommended for non-trivial logic). After Unit Test Writer -> QA uses generated tests as baseline. QA FAIL -> return to Executor.
6. **Specialist reviews report only** — findings go back to Executor to fix.
7. **Close the loop** with Docs + Skill Extractor after QA passes.

## Workflow

1. **Setup**: confirm `.axa/` exists and `tickets.md` is present. If not, create them per First Run Setup above. Then run the companion skill gates (anti-slop, ponytail).
2. **Read preferences** — hard gate: read `.axa/preferences.md` in full before any agent starts work. No agent plans, executes, or reviews until this read is done. Apply all recorded project preferences before any planning or execution.
3. **Select mode** — STOP and ask the user to choose explicitly (Full / Standard+ / Standard / Quick), presenting your recommendation. Validate the choice against the eligibility rules; refuse unsafe picks with an explanation. Record the mode and reason in the issue body.
4. **Decompose** *(Full only, optional)* — `agents/decomposer.md`. Output the task list as an issue comment. Stop for review.
5. **Plan** — Full: `agents/planner.md` full spec. Standard+/Standard: Planner Lite spec. Quick: Quick Change Record only. Show the plan in chat; write it to the issue body only after the user's explicit approval.
6. **Doubt Review** *(required by routing; otherwise Full only when risk warrants it)* — `agents/doubt-review.md`. Verdict: READY / BLOCKED / NEEDS CLARIFICATION.
7. **Execute** — `agents/executor.md`. One step at a time. Stop and escalate if scope exceeds the selected mode.
8. **Unit Test Writer** *(required by routing; otherwise optional)* — `agents/unit-test-writer.md`. Test Plan -> approval -> Test Code.
9. **QA** — Full/Standard+/Standard: full QA. Quick: minimal QA. All modes require a clear PASS / FAIL / PASS WITH WARNINGS verdict and recorded evidence.
10. **Specialist Reviews** *(required by the routing table; otherwise as needed, parallel ok)* — findings by severity -> Executor -> re-verification.
11. **Docs & Skill Extraction** — Full when applicable; Standard+/Standard/Quick only when the change establishes a reusable or user-facing behavior, after all blocking findings are closed.

## Rules

- Never let one agent do another's job.
- No agent acts before reading `.axa/preferences.md` in full — read first, apply the recorded taste, then work. This is what makes taste actually learning.
- Always read codebase skill files before speccing.
- Every spec must include "What NOT to Touch" and "Breaking Changes".
- Executor stops and asks on ambiguity — never improvises.
- Unit Test Writer never skips Test Plan approval.
- Standard+ is not a shortcut around security or logic reviews — it only relaxes process checks for pure visual/structural changes with established patterns.
- Append to `.axa/preferences.md` after every meaningful pipeline decision — never overwrite.
