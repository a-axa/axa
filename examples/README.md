# Axa thread example

What the local state backend looks like in practice. Modeled on a real validation run (46 tests / 107 assertions, one real bug caught mid-run).

- [`task-0042/state.yaml`](task-0042/state.yaml) — the source of truth agents read and write: plan, handoff thread, findings ledger, verification evidence
- [`task-0042/thread.html`](task-0042/thread.html) — generated from it; **open in a browser**

Regenerate from the YAML any time:

```bash
python3 .axa/render-thread.py --task task-0042
```

(The script ships in `templates/` and is copied to your project's `.axa/` on first run.)

Note the `model:` on each handoff — plan + review stages ran on a strong-reasoning model (`sonnet-4.5`), execution stages on a fast one (`deepseek-flash`). That's the anti-bias rule in action (RULES.md § Separation of Duties).
