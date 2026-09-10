#!/usr/bin/env python3
"""CLI for the Panopticon Domain Pod. Every number it prints comes from the pod DB."""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

POD_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[2]
for p in (str(REPO_ROOT), str(POD_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from domains.panopticon.state.db import Database                      # noqa: E402
from domains.panopticon.state.canon import seed as seed_canon         # noqa: E402
from domains.panopticon.verify import oracle, queue, schedule, scope         # noqa: E402
from domains.panopticon.interface import head_prompt as hp            # noqa: E402


def _conn(readonly=False):
    return Database(readonly=readonly).get_connection()


def main(argv=None):
    ap = argparse.ArgumentParser(prog="panopticon", description="Panopticon Domain CLI")
    sub = ap.add_subparsers(dest="command", required=True)
    sub.add_parser("status", help="Burn, scope, oracle — the whole picture")
    sub.add_parser("seed", help="Re-assert canon, milestones and the scope seed")
    sub.add_parser("schedule", help="Days left and milestone gates")
    sub.add_parser("scope", help="The scope ledger")
    sub.add_parser("prompt", help="Print the head's DB-built system prompt")
    sub.add_parser("next", help="The work queue: what to do now, and by whom")
    pl = sub.add_parser("plan", help="Fill the next PC session to an hour budget")
    pl.add_argument("--hours", type=float, default=8.0)

    ta = sub.add_parser("task-add", help="Add a task")
    ta.add_argument("title"); ta.add_argument("lane",
        choices=["REMOTE", "PC_REQUIRED", "RYAN_DECISION", "EXTERNAL"])
    ta.add_argument("--owner", choices=["HEAD", "RYAN"], default="HEAD")
    ta.add_argument("--detail", default=""); ta.add_argument("--hours", type=float, default=1.0)
    ta.add_argument("--blocked-by", default=""); ta.add_argument("--feature", default="")
    ta.add_argument("--milestone", default="")

    td = sub.add_parser("task-done", help="Mark a task done, with evidence")
    td.add_argument("id", type=int); td.add_argument("--evidence", required=True)

    ts = sub.add_parser("task-start", help="Mark a task in progress"); ts.add_argument("id", type=int)
    f = sub.add_parser("fact", help="Print one canon fact verbatim"); f.add_argument("key")
    sub.add_parser("facts", help="List canon fact keys")

    a = sub.add_parser("scope-add", help="Add a feature (enforces the ratchet)")
    a.add_argument("feature"); a.add_argument("tier", choices=["SHIP_BLOCKING", "WANTED", "STRETCH"])
    a.add_argument("--displaces", default=""); a.add_argument("--notes", default="")

    c = sub.add_parser("scope-cut", help="Cut a feature (always allowed)")
    c.add_argument("feature"); c.add_argument("why")

    d = sub.add_parser("decide", help="Record a design decision so it is never re-litigated")
    d.add_argument("topic"); d.add_argument("ruling")
    d.add_argument("--rationale", required=True); d.add_argument("--evidence", default="")

    b = sub.add_parser("build", help="Record a build")
    b.add_argument("tag"); b.add_argument("commit"); b.add_argument("--platform", default="windows")
    b.add_argument("--launched", action="store_true"); b.add_argument("--match-passed", action="store_true")

    pt = sub.add_parser("playtest", help="Record a playtest session")
    pt.add_argument("kind", choices=["BOT", "HUMAN", "MIXED"]); pt.add_argument("build_tag")
    pt.add_argument("guards", type=int); pt.add_argument("prisoners", type=int)
    pt.add_argument("--matches", type=int, default=1); pt.add_argument("--guard-wins", type=int, default=0)
    pt.add_argument("--prisoner-wins", type=int, default=0); pt.add_argument("--verdict", default="")
    pt.add_argument("--footage", default="")

    m = sub.add_parser("milestone", help="Mark a milestone done"); m.add_argument("name")
    m.add_argument("--evidence", required=True)

    args = ap.parse_args(argv)

    if args.command == "status":
        with _conn() as conn:
            print("══════════════════════════════════════════════════════════════")
            print("             PANOPTICON — DOMAIN STATUS")
            print("══════════════════════════════════════════════════════════════")
            print(hp.host_block(conn)); print()
            print(schedule.block(conn)); print()
            print(scope.block(conn)); print()
            print(queue.block(conn)); print()
            print(oracle.block(conn))
            brs = schedule.breaches(conn)
            hard = [b for b in brs if b["hard"]]
            if hard:
                print(f"\n!! {len(hard)} HARD gate(s) breached — the ship date has moved.")
        return 0

    if args.command == "seed":
        with _conn() as conn:
            print(json.dumps(seed_canon(conn), indent=2))
        return 0

    if args.command == "schedule":
        with _conn(readonly=True) as conn:
            print(schedule.block(conn, limit=20))
        return 0

    if args.command == "scope":
        with _conn(readonly=True) as conn:
            print(scope.block(conn))
        return 0

    if args.command == "prompt":
        with _conn(readonly=True) as conn:
            print(hp.build_head_prompt(conn))
        return 0

    if args.command == "next":
        with _conn() as conn:
            print(queue.block(conn))
        return 0

    if args.command == "plan":
        with _conn() as conn:
            plan = queue.pc_session_plan(conn, args.hours)
            if not plan:
                # State the fact, name the blockers, stop.  This used to append "which is
                # the queue working as intended" -- the tool narrating its own blocked
                # state as a success.  A status command editorialising about itself is how
                # a blocked project reads as a healthy one.
                blocked = conn.execute(
                    "SELECT title, blocked_by FROM tasks WHERE lane='PC_REQUIRED' "
                    "AND status='BLOCKED' ORDER BY id").fetchall()
                print("No PC task is READY.")
                for b in blocked:
                    unmet = queue.unmet_blockers(conn, dict(b))
                    print(f"  {b['title']}  <- waiting on: {', '.join(unmet)}")
                return 0
            total = sum(t["estimate_hours"] for t in plan)
            print(f"NEXT PC SESSION — {total}h of {args.hours}h:")
            for t in plan:
                print(f"  [{t['id']}] {t['title']} ({t['estimate_hours']}h)")
                if t["detail"]:
                    print(f"        {t['detail']}")
        return 0

    if args.command == "task-add":
        with _conn() as conn:
            conn.execute(
                "INSERT INTO tasks (title, detail, lane, owner, estimate_hours, blocked_by, "
                "feature, milestone, created_on) VALUES (?,?,?,?,?,?,?,?,?)",
                (args.title, args.detail, args.lane, args.owner, args.hours,
                 args.blocked_by, args.feature, args.milestone, date.today().isoformat()))
            conn.commit()
            queue.refresh(conn)
            print(f"added: {args.title}")
        return 0

    if args.command == "task-start":
        with _conn() as conn:
            conn.execute("UPDATE tasks SET status='IN_PROGRESS', started_on=? WHERE id=?",
                         (date.today().isoformat(), args.id))
            conn.commit(); print(f"task {args.id} in progress")
        return 0

    if args.command == "task-done":
        with _conn() as conn:
            cur = conn.execute("UPDATE tasks SET status='DONE', done_on=?, evidence=? WHERE id=?",
                               (date.today().isoformat(), args.evidence, args.id))
            conn.commit()
            if cur.rowcount == 0:
                print(f"no task {args.id}", file=sys.stderr); return 1
            queue.refresh(conn)
            print(f"task {args.id} done — {args.evidence}")
            print(); print(queue.block(conn))
        return 0

    if args.command == "facts":
        with _conn(readonly=True) as conn:
            for r in conn.execute("SELECT key, verified_by FROM facts ORDER BY key"):
                print(f"{r['key']}  [{r['verified_by']}]")
        return 0

    if args.command == "fact":
        with _conn(readonly=True) as conn:
            r = conn.execute("SELECT * FROM facts WHERE key=?", (args.key,)).fetchone()
            if not r:
                print(f"MISSING FROM DB: {args.key}", file=sys.stderr); return 1
            print(json.dumps({k: r[k] for k in r.keys()}, indent=2))
        return 0

    if args.command == "scope-add":
        with _conn() as conn:
            try:
                scope.add_feature(conn, args.feature, args.tier, args.displaces, notes=args.notes)
            except scope.ScopeViolation as e:
                print(f"REFUSED: {e}", file=sys.stderr); return 1
            print(f"added {args.feature!r} as {args.tier}"
                  + (f", displacing {args.displaces!r}" if args.displaces else ""))
        return 0

    if args.command == "scope-cut":
        with _conn() as conn:
            scope.cut_feature(conn, args.feature, args.why)
            print(f"cut {args.feature!r}")
        return 0

    if args.command == "decide":
        with _conn() as conn:
            conn.execute("INSERT INTO decisions (decided_on, topic, ruling, rationale, evidence) "
                         "VALUES (?,?,?,?,?)",
                         (date.today().isoformat(), args.topic, args.ruling, args.rationale,
                          args.evidence))
            conn.commit()
            print(f"recorded: {args.topic}")
        return 0

    if args.command == "build":
        with _conn() as conn:
            conn.execute("INSERT INTO builds (tag, built_on, commit_sha, platform, launched, "
                         "headless_match_passed) VALUES (?,?,?,?,?,?)",
                         (args.tag, date.today().isoformat(), args.commit, args.platform,
                          int(args.launched), int(args.match_passed)))
            conn.commit()
            print(f"build {args.tag}: launched={args.launched} match_passed={args.match_passed}")
        return 0

    if args.command == "playtest":
        with _conn() as conn:
            conn.execute(
                "INSERT INTO playtests (played_on, kind, build_tag, guards, prisoners, matches, "
                "guard_wins, prisoner_wins, verdict, footage_path) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (date.today().isoformat(), args.kind, args.build_tag, args.guards,
                 args.prisoners, args.matches, args.guard_wins, args.prisoner_wins,
                 args.verdict, args.footage))
            conn.commit()
            print(json.dumps(oracle.balance_evidence(conn, args.guards, args.prisoners), indent=2))
        return 0

    if args.command == "milestone":
        with _conn() as conn:
            cur = conn.execute("UPDATE milestones SET status='DONE', evidence=? WHERE name=?",
                               (args.evidence, args.name))
            conn.commit()
            if cur.rowcount == 0:
                print(f"no milestone named {args.name!r}", file=sys.stderr); return 1
            print(f"{args.name} DONE — {args.evidence}")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
