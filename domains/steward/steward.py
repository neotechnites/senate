#!/usr/bin/env python3
"""Steward pod CLI.  The Senate hub talks to this pod ONLY through `telemetry --json`;
it never SQLs steward.db directly."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

POD_DIR = Path(__file__).resolve().parent
REPO_ROOT = POD_DIR.parents[1]
for p in (str(REPO_ROOT), str(POD_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from domains.steward.state.db import Database          # noqa: E402
from domains.steward.state.canon import seed           # noqa: E402
from domains.steward.verify import recurrence          # noqa: E402


def _refresh_due(conn, oid: int) -> str:
    r = conn.execute("SELECT * FROM obligations WHERE id=?", (oid,)).fetchone()
    nxt = recurrence.next_due(r["kind"], r["interval_days"],
                              r["anchor_date"], r["last_completed_at"])
    conn.execute("UPDATE obligations SET next_due_at=? WHERE id=?", (nxt, oid))
    return nxt


def cmd_add(args) -> int:
    db = Database()
    with db.get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO obligations (title, detail, kind, domain, asset, "
            "interval_days, interval_source, anchor_date, effort_hours, season) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (args.title, args.detail, args.kind, args.domain, args.asset,
             args.interval_days, args.interval_source, args.anchor, args.hours,
             args.season))
        oid = cur.lastrowid
        nxt = _refresh_due(conn, oid)
    src = "measured" if args.interval_source else "SELF-MARKED"
    print(f"[{oid}] {args.title} ({args.kind}) next due {nxt or 'unscheduled'} "
          f"| interval provenance: {src}")
    return 0


def cmd_done(args) -> int:
    """Record a completion.  ONLY Ryan is a valid reporter."""
    db = Database()
    with db.get_connection() as conn:
        r = conn.execute("SELECT * FROM obligations WHERE id=?", (args.id,)).fetchone()
        if not r:
            print(f"no obligation {args.id}", file=sys.stderr)
            return 1
        on = args.on or date.today().isoformat()
        conn.execute(
            "INSERT INTO completions (obligation_id, completed_on, reported_by, "
            "verbatim, notes) VALUES (?,?,'ryan',?,?)",
            (args.id, on, args.verbatim, args.notes))
        conn.execute("UPDATE obligations SET last_completed_at=? WHERE id=?",
                     (on, args.id))
        if recurrence.closes_on_completion(r["kind"]):
            conn.execute("UPDATE obligations SET status='CLOSED' WHERE id=?", (args.id,))
            nxt = _refresh_due(conn, args.id)
            print(f"[{args.id}] {r['title']} CLOSED on {on}")
        else:
            nxt = _refresh_due(conn, args.id)
            print(f"[{args.id}] {r['title']} re-armed -- next due {nxt}")
    return 0


def cmd_status(args) -> int:
    db = Database()
    with db.get_connection() as conn:
        seed(conn)
        rows = conn.execute(
            "SELECT * FROM obligations WHERE status='OPEN' ORDER BY next_due_at"
        ).fetchall()
        comps = conn.execute("SELECT COUNT(*) c FROM completions").fetchone()["c"]
        spoke = conn.execute(
            "SELECT COUNT(*) c FROM conversation WHERE direction='TO_RYAN'"
        ).fetchone()["c"]
    print("══════════════════════════════════════════════════════════════")
    print("               STEWARD — HOUSEHOLD MANAGER                    ")
    print("══════════════════════════════════════════════════════════════")
    if not rows:
        print("  BACKLOG EMPTY — nothing has been captured yet.")
    for r in rows:
        state, days = recurrence.due_state(r["next_due_at"] or "")
        src = "measured" if r["interval_source"] else "SELF-MARKED"
        when = f"{days:+d}d" if days is not None else "unscheduled"
        print(f'  [{r["id"]:>3}] {state:<11} {when:>8}  {r["title"]}'
              + (f'  (every {r["interval_days"]}d, {src})' if r["interval_days"] else ""))
    print("──────────────────────────────────────────────────────────────")
    print(f"  Completions reported by Ryan: {comps}"
          + ("   <- ZERO. No progress is verified." if comps == 0 else ""))
    print(f"  Messages ever delivered to Ryan: {spoke}"
          + ("   <- ZERO. This pod has never reached his phone." if spoke == 0 else ""))
    print("══════════════════════════════════════════════════════════════")
    return 0


def cmd_telemetry(args) -> int:
    db = Database()
    with db.get_connection() as conn:
        openn = conn.execute(
            "SELECT COUNT(*) c FROM obligations WHERE status='OPEN'").fetchone()["c"]
        closed = conn.execute(
            "SELECT COUNT(*) c FROM obligations WHERE status='CLOSED'").fetchone()["c"]
        comps = conn.execute("SELECT COUNT(*) c FROM completions").fetchone()["c"]
        spoke = conn.execute(
            "SELECT COUNT(*) c FROM conversation WHERE direction='TO_RYAN'"
        ).fetchone()["c"]
        overdue = 0
        for r in conn.execute(
                "SELECT next_due_at FROM obligations WHERE status='OPEN'"):
            if recurrence.due_state(r["next_due_at"] or "")[0] == recurrence.OVERDUE:
                overdue += 1
    payload = {
        "domain_id": "steward",
        "obligations_open": openn,
        "obligations_closed": closed,
        "overdue": overdue,
        "completions_reported_by_ryan": comps,
        "messages_delivered_to_ryan": spoke,
        "progress_verified": comps > 0,
        "provenance": "measured from steward.db" if comps else "NO RECEIPTS — nothing verified",
    }
    print(json.dumps(payload, indent=2) if not args.json else json.dumps(payload))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Steward — Ryan's household manager")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="Backlog and whether anything is verified")

    t = sub.add_parser("telemetry", help="Machine-readable state for the Senate hub")
    t.add_argument("--json", action="store_true")

    a = sub.add_parser("add", help="Capture an obligation")
    a.add_argument("title")
    a.add_argument("--kind", choices=["ONESHOT", "RECURRING", "EVENT"], default="ONESHOT")
    a.add_argument("--domain", default="HOUSE")
    a.add_argument("--asset", default="")
    a.add_argument("--detail", default="")
    a.add_argument("--interval-days", type=int, dest="interval_days")
    a.add_argument("--interval-source", default="", dest="interval_source",
                   help="citation URL; empty means SELF-MARKED")
    a.add_argument("--anchor", default="", help="ISO date: event date or first-due")
    a.add_argument("--hours", type=float, default=0.0)
    a.add_argument("--season", default="")

    d = sub.add_parser("done", help="Record a completion RYAN reported")
    d.add_argument("id", type=int)
    d.add_argument("--on", default="", help="ISO date (default today)")
    d.add_argument("--verbatim", default="", help="what Ryan actually said")
    d.add_argument("--notes", default="")

    args = ap.parse_args()
    return {"status": cmd_status, "telemetry": cmd_telemetry,
            "add": cmd_add, "done": cmd_done}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
