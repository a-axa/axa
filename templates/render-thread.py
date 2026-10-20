#!/usr/bin/env python3
"""Render Axa thread.html (per task) and index.html from .axa/tasks/*/state.yaml.

Usage (from repo root):
    python3 .axa/render-thread.py            # render all tasks + index
    python3 .axa/render-thread.py --task task-0042

thread.html is a build artifact: generated, never hand-edited (gitignore it).
Requires: PyYAML (pip install pyyaml).
"""
import argparse
import html
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

REPO_ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = REPO_ROOT / ".axa" / "tasks"

STAGE_COLORS = {
    "decomposing":  "#6e7781",
    "planning":     "#0969da",
    "doubt-review": "#9a6700",
    "executing":    "#1a7f37",
    "qa":           "#8250df",
    "review":       "#b35900",
    "documenting":  "#0a3069",
    "extracting":   "#6e7781",
    "done":         "#1a7f37",
}

CSS = """
:root { color-scheme: light; }
* { box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
       margin: 0; background: #f6f8fa; color: #1f2328; line-height: 1.5; }
.wrap { max-width: 880px; margin: 0 auto; padding: 24px 20px 64px; }
a { color: #0969da; text-decoration: none; }
a:hover { text-decoration: underline; }
.header { background: #fff; border: 1px solid #d0d7de; border-radius: 6px; padding: 20px 24px; margin-bottom: 16px; }
.header h1 { font-size: 22px; margin: 0 0 8px; font-weight: 600; }
.header h1 .tid { color: #59636e; font-weight: 400; }
.meta { color: #59636e; font-size: 13px; }
.badge { display: inline-block; padding: 2px 10px; border-radius: 2em; color: #fff;
         font-size: 12px; font-weight: 600; vertical-align: middle; }
.badge.done::before { content: "\\2713  "; }
.current { background: #ddf4ff; border: 1px solid #54aeff66; border-radius: 6px;
           padding: 14px 18px; margin-bottom: 16px; font-size: 14px; }
.current strong { display: block; margin-bottom: 4px; }
.section { background: #fff; border: 1px solid #d0d7de; border-radius: 6px;
           padding: 18px 22px; margin-bottom: 16px; }
.section h2 { font-size: 15px; margin: 0 0 12px; padding-bottom: 8px;
              border-bottom: 1px solid #d0d7de; }
.plan li { list-style: none; margin: 6px 0; }
.plan { padding: 0; margin: 0; }
.plan .st { display: inline-block; width: 74px; font-size: 12px; font-weight: 600;
            border-radius: 2em; text-align: center; padding: 1px 0; margin-right: 8px;}
.st.done { background: #1a7f37; color: #fff; }
.st.in-progress { background: #9a6700; color: #fff; }
.st.pending { background: #eaeef2; color: #59636e; }
.progress { height: 8px; background: #eaeef2; border-radius: 4px; margin: 12px 0 4px; }
.progress > div { height: 8px; background: #1a7f37; border-radius: 4px; }
.timeline { position: relative; margin: 0; padding: 0 0 0 26px; }
.timeline::before { content: ""; position: absolute; left: 8px; top: 8px; bottom: 8px;
                   width: 2px; background: #d0d7de; }
.handoff { position: relative; background: #fff; border: 1px solid #d0d7de;
          border-radius: 6px; margin-bottom: 14px; }
.handoff::before { content: ""; position: absolute; left: -24px; top: 18px;
                  width: 10px; height: 10px; border-radius: 50%;
                  background: #0969da; border: 2px solid #f6f8fa; }
.handoff .chead { background: #f6f8fa; border-bottom: 1px solid #d0d7de;
                 padding: 8px 14px; font-size: 13px; border-radius: 6px 6px 0 0; }
.handoff .chead .route { font-weight: 600; }
.handoff .chead time { color: #59636e; float: right; }
.handoff .cbody { padding: 12px 14px; font-size: 14px; }
.handoff .cbody .summary { font-size: 15px; margin: 0 0 8px; }
.handoff details { margin-top: 8px; font-size: 13px; color: #333; }
.handoff details summary { cursor: pointer; color: #0969da; }
.chips { margin-top: 10px; }
.chip { display: inline-block; background: #eaeef2; border-radius: 2em;
        font-size: 12px; padding: 2px 10px; margin: 0 6px 6px 0;
        font-family: ui-monospace, monospace; }
.via { display: inline-block; font-size: 11px; color: #59636e; border: 1px solid #d0d7de;
       border-radius: 2em; padding: 1px 8px; margin-left: 8px; vertical-align: middle;}
table.ledger { width: 100%; border-collapse: collapse; font-size: 13px; }
table.ledger th, table.ledger td { border: 1px solid #d0d7de; padding: 8px 10px; text-align: left; }
table.ledger th { background: #f6f8fa; }
dl.verif { margin: 0; font-size: 14px; }
dl.verif dt { font-weight: 600; margin-top: 8px; }
dl.verif dd { margin: 2px 0 0; color: #333; }
dl.verif code, .mono { font-family: ui-monospace, monospace; font-size: 13px;
                       background: #eaeef2; padding: 1px 6px; border-radius: 4px; }
ul.debt { margin: 0; padding-left: 20px; font-size: 14px; }
.footer { color: #59636e; font-size: 12px; text-align: center; margin-top: 24px; }
.idx-table { width: 100%; border-collapse: collapse; font-size: 14px; background: #fff; }
.idx-table th, .idx-table td { border: 1px solid #d0d7de; padding: 10px 14px; text-align: left; }
.idx-table th { background: #f6f8fa; }
.empty { color: #59636e; font-style: italic; font-size: 14px; }
"""


def esc(text):
    return html.escape(str(text if text is not None else ""))


def nl2br(text):
    return esc(text).replace("\n", "<br>")


def badge(stage):
    color = STAGE_COLORS.get(stage, "#6e7781")
    return f'<span class="badge{" done" if stage == "done" else ""}" style="background:{color}">{esc(stage)}</span>'


def fmt_time(value):
    return esc(value)


def render_plan(plan):
    if not plan:
        return '<p class="empty">No plan steps yet.</p>'
    total = len(plan)
    done = sum(1 for p in plan if p.get("status") == "done")
    pct = int(done / total * 100) if total else 0
    items = []
    for p in plan:
        st = p.get("status", "pending")
        items.append(
            f'<li><span class="st {esc(st)}">{esc(st)}</span>'
            f'<span class="mono">{esc(p.get("id", ""))}</span> {esc(p.get("text", ""))}</li>'
        )
    return (
        f'<div class="progress"><div style="width:{pct}%"></div></div>'
        f'<p class="meta">{done}/{total} steps done</p>'
        f'<ul class="plan">{"".join(items)}</ul>'
    )


def render_handoffs(handoffs):
    if not handoffs:
        return '<p class="empty">No handoffs yet.</p>'
    cards = []
    for h in handoffs:
        detail = (h.get("detail") or "").strip()
        detail_html = (
            f"<details><summary>full detail</summary><p>{nl2br(detail)}</p></details>"
            if detail else ""
        )
        artifacts = "".join(
            f'<span class="chip">{esc(a)}</span>' for a in (h.get("artifacts") or [])
        )
        chips = f'<div class="chips">{artifacts}</div>' if artifacts else ""
        cards.append(f"""
        <div class="handoff">
          <div class="chead">
            <span class="route">{esc(h.get("from", "?"))} &rarr; {esc(h.get("to", "?"))}</span>
            <span class="via">approved via {esc(h.get("approved_via", "pipeline"))}</span>
            <time>{fmt_time(h.get("at", ""))}</time>
          </div>
          <div class="cbody">
            <p class="summary">{nl2br(h.get("summary", ""))}</p>
            {detail_html}{chips}
          </div>
        </div>""")
    return f'<div class="timeline">{"".join(cards)}</div>'


def render_findings(findings):
    if not findings:
        return '<p class="empty">No findings ledgered.</p>'
    rows = "".join(
        "<tr>" + "".join(f"<td>{esc(f.get(k, ''))}</td>"
                         for k in ("id", "source", "severity", "status", "owner", "verification")) + "</tr>"
        for f in findings
    )
    return ("""<table class="ledger"><tr><th>ID</th><th>Source</th><th>Severity</th>
               <th>Status</th><th>Owner</th><th>Verification</th></tr>"""
            f"{rows}</table>")


def render_verification(v):
    v = v or {}
    def cmdval(d):
        d = d or {}
        return f'<span class="mono">{esc(d.get("command", ""))}</span> &mdash; {esc(d.get("result", ""))}'
    return f"""<dl class="verif">
      <dt>Tests</dt><dd>{cmdval(v.get("tests"))}</dd>
      <dt>Build / lint / typecheck</dt><dd>{cmdval(v.get("build_lint"))}</dd>
      <dt>Manual verification</dt><dd>{nl2br(v.get("manual", "")) or "<span class='empty'>&mdash;</span>"}</dd>
      <dt>Not verified</dt><dd>{nl2br(v.get("not_verified", "")) or "<span class='empty'>&mdash;</span>"}</dd>
    </dl>"""


def render_thread(state):
    tid = state.get("id", "task-????")
    title = state.get("title", "(untitled)")
    stage = state.get("stage", "?")
    cur = state.get("current") or {}
    backend = state.get("backend", "local")
    issue_url = state.get("issue_url")
    backend_html = (f' &middot; <a href="{esc(issue_url)}">GitHub issue</a>'
                    if backend == "github" and issue_url else f" &middot; backend: {esc(backend)}")

    plan = state.get("plan") or []
    handoffs = state.get("handoffs") or []
    findings = state.get("findings") or []
    debt = state.get("tech_debt") or []
    feat = state.get("feature") or {}

    debt_html = ("<ul class='debt'>" + "".join(f"<li>{esc(d)}</li>" for d in debt) + "</ul>"
                 if debt else '<p class="empty">None.</p>')
    blocking = cur.get("blocking")
    blocking_html = esc(blocking) if blocking else '<span class="empty">none</span>'
    generated = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %Z")

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(tid)} — {esc(title)} · Axa thread</title>
<style>{CSS}</style></head>
<body><div class="wrap">

<div class="header">
  <h1><span class="tid">{esc(tid)}</span> {esc(title)}</h1>
  <div>{badge(stage)} <span class="meta">mode: {esc(state.get("mode", ""))} ·
  created {esc(state.get("created", ""))}{backend_html}</span></div>
</div>

<div class="current">
  <strong>Current handoff</strong>
  stage: {badge(cur.get("stage", stage))} &nbsp;·&nbsp;
  next: <b>{esc(cur.get("next_agent", "?"))}</b> &nbsp;·&nbsp;
  blocking: {blocking_html} &nbsp;·&nbsp;
  <span class="meta">updated {esc(cur.get("last_updated", ""))}</span>
</div>

<div class="section"><h2>Feature</h2>
  <dl class="verif">
    <dt>Owner</dt><dd>{esc(feat.get("owner", "")) or "<span class='empty'>&mdash;</span>"}</dd>
    <dt>Branch</dt><dd><span class="mono">{esc(feat.get("branch", ""))}</span></dd>
    <dt>Scope</dt><dd>{nl2br(feat.get("scope_summary", ""))}</dd>
    <dt>Mode rationale</dt><dd>{nl2br(state.get("mode_rationale", ""))}</dd>
  </dl>
</div>

<div class="section"><h2>Plan</h2>{render_plan(plan)}</div>

<div class="section"><h2>Thread &mdash; {len(handoffs)} handoff(s)</h2>{render_handoffs(handoffs)}</div>

<div class="section"><h2>Findings ledger</h2>{render_findings(findings)}</div>

<div class="section"><h2>Verification evidence</h2>{render_verification(state.get("verification"))}</div>

<div class="section"><h2>Tech debt <span class="meta">(append-only)</span></h2>{debt_html}</div>

<div class="footer">generated {esc(generated)} from <span class="mono">state.yaml</span>
&mdash; do not edit this file by hand &middot; <a href="index.html">&larr; all tasks</a></div>

</div></body></html>
"""


def render_index(tasks):
    rows = []
    for tid, state in sorted(tasks.items()):
        stage = state.get("stage", "?")
        title = state.get("title", "(untitled)")
        backend = state.get("backend", "local")
        cur = state.get("current") or {}
        nxt = cur.get("next_agent", "?")
        plan = state.get("plan") or []
        done = sum(1 for p in plan if p.get("status") == "done")
        prog = f"{done}/{len(plan)}" if plan else "&mdash;"
        rows.append(
            f"<tr><td><span class='mono'>{esc(tid)}</span></td>"
            f"<td><a href='{esc(tid)}/thread.html'>{esc(title)}</a></td>"
            f"<td>{badge(stage)}</td><td>{esc(nxt)}</td>"
            f"<td>{esc(backend)}</td><td>{prog}</td></tr>"
        )
    body = ("<table class='idx-table'><tr><th>ID</th><th>Title</th><th>Stage</th>"
            "<th>Next agent</th><th>Backend</th><th>Plan</th></tr>"
            f"{''.join(rows)}</table>" if rows
            else '<p class="empty">No tasks yet.</p>')
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Axa tasks</title><style>{CSS}</style></head>
<body><div class="wrap">
<div class="header"><h1>Axa tasks</h1>
<div class="meta">{len(tasks)} task(s) &middot; rendered from <span class="mono">.axa/tasks/*/state.yaml</span></div></div>
{body}
<div class="footer">generated {esc(datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %Z"))}
&mdash; do not edit by hand</div>
</div></body></html>
"""


def load_tasks(only=None):
    tasks = {}
    if not TASKS_DIR.is_dir():
        sys.exit(f"tasks dir not found: {TASKS_DIR}")
    for path in sorted(TASKS_DIR.glob("*/state.yaml")):
        tid = path.parent.name
        if only and tid != only:
            continue
        with open(path, encoding="utf-8") as f:
            tasks[tid] = yaml.safe_load(f) or {}
        tasks[tid].setdefault("id", tid)
    return tasks


def main():
    ap = argparse.ArgumentParser(description="Render Axa thread.html + index.html")
    ap.add_argument("--task", help="render only this task id")
    args = ap.parse_args()

    tasks = load_tasks(args.task)
    if not tasks:
        sys.exit("no tasks found" + (f" matching {args.task}" if args.task else ""))

    for tid, state in tasks.items():
        out = TASKS_DIR / tid / "thread.html"
        out.write_text(render_thread(state), encoding="utf-8")
        print(f"wrote {out.relative_to(REPO_ROOT)}")

    if not args.task:
        idx = TASKS_DIR / "index.html"
        idx.write_text(render_index(tasks), encoding="utf-8")
        print(f"wrote {idx.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
