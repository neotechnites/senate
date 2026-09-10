"""What counts as DONE.  A game has no venue to ask, so this file is the substitute.

Kalshi can ask a venue whether it was paid.  Panopticon cannot, and the failure that
follows is a project that reports progress out of documents.  So:

  DONE means a row in `builds` with launched=1 AND headless_match_passed=1.
  A design doc is not done. A merged commit is not done. A passing unit test is not done.
  A build that started and played a full bot match to completion is done.

  A BALANCE claim requires a `playtests` row. A BOT row can settle a number
  (win rates, times, distances). Only a HUMAN row can settle whether it is fun --
  and with no friends available, human rows are scarce and must not be spent on
  anything a bot could have measured.
"""
from __future__ import annotations

from typing import List, Optional, Tuple


def latest_good_build(conn) -> Optional[dict]:
    r = conn.execute(
        "SELECT * FROM builds WHERE launched=1 AND headless_match_passed=1 "
        "ORDER BY built_on DESC, id DESC LIMIT 1").fetchone()
    return dict(r) if r else None


def can_claim_done(conn, feature: str) -> Tuple[bool, str]:
    """Gate a DONE transition on the scope ledger."""
    b = latest_good_build(conn)
    if b is None:
        return False, ("no build has both launched and passed a headless bot match; "
                       "nothing can be called done yet (verify/oracle.py)")
    return True, f"backed by build {b['tag']} ({b['built_on']})"


def mark_done(conn, feature: str) -> str:
    ok, why = can_claim_done(conn, feature)
    if not ok:
        raise ValueError(f"refusing to mark {feature!r} DONE: {why}")
    cur = conn.execute("UPDATE scope_ledger SET status='DONE', notes=notes||? WHERE feature=?",
                       (f" [done: {why}]", feature))
    if cur.rowcount == 0:
        raise ValueError(f"no ledger row named {feature!r}")
    conn.commit()
    return why


def balance_evidence(conn, guards: int, prisoners: int) -> dict:
    """What the tape says about a configuration. Empty means: go run matches."""
    r = conn.execute(
        "SELECT sum(matches) m, sum(guard_wins) gw, sum(prisoner_wins) pw, "
        "count(*) sessions, sum(kind='HUMAN') human "
        "FROM playtests WHERE guards=? AND prisoners=?", (guards, prisoners)).fetchone()
    m = r["m"] or 0
    return {"matches": m, "sessions": r["sessions"] or 0, "human_sessions": r["human"] or 0,
            "guard_wins": r["gw"] or 0, "prisoner_wins": r["pw"] or 0,
            "guard_win_rate": (round((r["gw"] or 0) / m, 3) if m else None)}


def block(conn) -> str:
    b = latest_good_build(conn)
    lines = ["ORACLE (verify/oracle.py — done means a build that ran, never a document):"]
    if b:
        lines.append(f"  latest good build: {b['tag']} ({b['built_on']}, {b['platform']})")
    else:
        lines.append("  NO build has launched and passed a headless bot match. "
                     "Nothing may be reported as done.")
    r = conn.execute("SELECT count(*) n, sum(matches) m, sum(kind='HUMAN') h "
                     "FROM playtests").fetchone()
    lines.append(f"  playtests: {r['n'] or 0} sessions / {r['m'] or 0} matches / "
                 f"{r['h'] or 0} human")
    return "\n".join(lines)
