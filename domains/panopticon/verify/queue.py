"""The work queue: what should be happening right now, and by whom.

WHY IT IS SPLIT BY LANE, not by priority.  Ryan has ~233 PC hours left and ~60 remote
hours a week.  Those are not interchangeable, so a single ranked to-do list would lie:
it would let a task that needs the PC sit at the top of a list being read on a Mac at
work, and it would let remote-capable work idle while the head waits for Ryan.

  REMOTE        the head can start it now, unattended. This queue should never be empty
                while ship-blocking work remains -- an empty one is an ESCALATION, not a
                rest. Ryan asked for the head to always be working on something.
  PC_REQUIRED   needs the machine and Ryan's eyes: playing, judging feel, laying out
                geometry, reacting to art, capturing footage. Costs the scarce resource.
                A PC task may only be READY when every remote prerequisite is DONE --
                that is the mechanism that protects the 8 hours.
  RYAN_DECISION only Ryan can answer it. Blocking these is expensive; surface them first.
  EXTERNAL      someone else's clock (Valve review, a Fiverr composer). Track, do not push.
"""
from __future__ import annotations

from datetime import date
from typing import Dict, List, Optional

ACTIVE = ("BACKLOG", "READY", "IN_PROGRESS", "BLOCKED")


def _rows(conn, where: str = "", args=()) -> List[dict]:
    q = "SELECT * FROM tasks"
    if where:
        q += " WHERE " + where
    return [dict(r) for r in conn.execute(q + " ORDER BY id", args)]


def unmet_blockers(conn, task: dict) -> List[str]:
    """Blocker titles that are not DONE. A blocker that does not exist is itself a
    blocker -- a typo must not silently unblock work."""
    names = [b.strip() for b in (task.get("blocked_by") or "").split(",") if b.strip()]
    if not names:
        return []
    unmet = []
    for n in names:
        r = conn.execute("SELECT status FROM tasks WHERE title=?", (n,)).fetchone()
        if r is None or r["status"] != "DONE":
            unmet.append(n)
    return unmet


def refresh(conn) -> Dict[str, int]:
    """Recompute READY/BLOCKED for every active task. Idempotent; run it before reading."""
    moved = {"ready": 0, "blocked": 0}
    for t in _rows(conn, "status IN ('BACKLOG','READY','BLOCKED')"):
        unmet = unmet_blockers(conn, t)
        want = "BLOCKED" if unmet else "READY"
        if t["status"] != want:
            conn.execute("UPDATE tasks SET status=? WHERE id=?", (want, t["id"]))
            moved["blocked" if want == "BLOCKED" else "ready"] += 1
    conn.commit()
    return moved


def next_remote(conn, limit: int = 5) -> List[dict]:
    """What the head can pick up right now, without Ryan and without the PC."""
    refresh(conn)
    return _rows(conn, "lane='REMOTE' AND status='READY'")[:limit]


def pc_session_plan(conn, limit: int = 8) -> List[dict]:
    """The next PC session, in order.  Nothing enters this list until its remote
    prerequisites are finished, so Ryan never burns a PC hour waiting.

    NO HOUR BUDGET.  This used to fill the list to an 8.0h estimate.  Ryan's ruling
    2026-09-09: 'i have never ever ever seen you estimate hours correctly. rip it out of
    your brain.'  block() stopped printing hours that day; this function and
    `./panopticon.py plan` kept computing with them, which is the same fabricated
    precision one layer down.  Ryan sets the cadence and stops when he stops.
    """
    refresh(conn)
    return _rows(conn, "lane='PC_REQUIRED' AND status='READY'")[:limit]


def awaiting_ryan(conn) -> List[dict]:
    refresh(conn)
    return _rows(conn, "lane='RYAN_DECISION' AND status IN ('READY','IN_PROGRESS')")


def head_is_idle(conn) -> bool:
    """True when the head has nothing it can do alone while ship-blocking work remains.
    Ryan's instruction: it should always be evaluating and always be working. An idle
    head with open work is a planning failure to escalate, not a quiet success."""
    if next_remote(conn, limit=1):
        return False
    return bool(_rows(conn, "status IN ('BACKLOG','READY','IN_PROGRESS','BLOCKED') "
                            "AND lane!='EXTERNAL'"))


def last_movement(conn) -> str:
    """The most recent date any task row was created, started or finished."""
    r = conn.execute(
        "SELECT max(d) d FROM (SELECT max(created_on) d FROM tasks "
        "UNION ALL SELECT max(started_on) FROM tasks "
        "UNION ALL SELECT max(done_on) FROM tasks)").fetchone()
    return (r["d"] or "") if r else ""


def burn(conn) -> Dict[str, float]:
    """Estimated hours of open work, by lane. PC hours are the ones that can run out."""
    out: Dict[str, float] = {}
    for r in conn.execute(
            "SELECT lane, sum(estimate_hours) h FROM tasks "
            "WHERE status IN ('BACKLOG','READY','IN_PROGRESS','BLOCKED') GROUP BY lane"):
        out[r["lane"]] = round(r["h"] or 0.0, 1)
    return out


def block(conn, today: Optional[date] = None, hours: float = 8.0) -> str:
    """The queue, reported as WORK, never as hours.

    Ryan's ruling 2026-09-09: per-task hour estimates were consistently wrong and are
    not surfaced.  He sets the cadence; this block says what is ready, what is next at
    the machine, and what is stuck on him.  Nothing here pretends to know how long
    anything takes."""
    refresh(conn)
    lines = ["WORK QUEUE (verify/queue.py — split by WHERE the work can happen):"]
    counts = {}
    for r in conn.execute("SELECT lane, count(*) n FROM tasks "
                          "WHERE status IN ('BACKLOG','READY','IN_PROGRESS','BLOCKED') "
                          "GROUP BY lane"):
        counts[r["lane"]] = r["n"]
    lines.append("  open: " + (", ".join(f"{k} {v}" for k, v in sorted(counts.items()))
                               or "nothing open"))

    ip = _rows(conn, "status='IN_PROGRESS'")
    if ip:
        lines.append("  IN PROGRESS (finish or reclassify before starting anything new):")
        for t in ip:
            since = t["started_on"] or "?"
            lines.append(f"    - [{t['id']}] {t['title']}  (since {since})")

    pc = [t for t in _rows(conn, "status='READY' AND lane='PC_REQUIRED'")][:4]
    if pc:
        lines.append("  NEXT AT THE PC:")
        for t in pc:
            lines.append(f"    - [{t['id']}] {t['title']}")

    ar = awaiting_ryan(conn)
    if ar:
        lines.append(f"  WAITING ON RYAN ({len(ar)}):")
        for t in ar:
            lines.append(f"    - [{t['id']}] {t['title']}")
    return "\n".join(lines)
