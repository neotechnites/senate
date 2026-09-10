"""Days, not vibes.  The burn against 2027-04-01 and the gates other people own.

Two kinds of date live in `milestones` and they are not the same kind of thing:
  hard=1  an EXTERNAL clock owns it (Valve's 30-day wait, review queues). No amount of
          effort moves it. Missing one moves the ship date, full stop.
  hard=0  derived by this pod. The head may move it, and should say so when it does.
"""
from __future__ import annotations

from datetime import date
from typing import List, Optional

SHIP = date(2027, 4, 1)


def days_left(today: Optional[date] = None) -> int:
    return (SHIP - (today or date.today())).days


def pc_hours_left(today: Optional[date] = None, hours_per_week: float = 8.0) -> float:
    """The scarce resource, in the only unit that matters.

    Ryan gets ~8 hours a week at the machine that can run Godot. Everything else is
    remote. This number, not the calendar, is the real budget."""
    return round(days_left(today) / 7.0 * hours_per_week, 1)


def milestones(conn, today: Optional[date] = None) -> List[dict]:
    today = today or date.today()
    out = []
    for r in conn.execute("SELECT * FROM milestones ORDER BY due_on"):
        due = date.fromisoformat(r["due_on"])
        out.append({"name": r["name"], "due": due, "kind": r["kind"], "hard": bool(r["hard"]),
                    "status": r["status"], "days": (due - today).days,
                    "overdue": r["status"] == "OPEN" and due < today,
                    "notes": r["notes"]})
    return out


def breaches(conn, today: Optional[date] = None) -> List[dict]:
    """Open milestones already past due. A hard breach is a ship-date event."""
    return [m for m in milestones(conn, today) if m["overdue"]]


def block(conn, today: Optional[date] = None, limit: int = 5) -> str:
    today = today or date.today()
    ms = milestones(conn, today)
    brs = [m for m in ms if m["overdue"]]
    upcoming = [m for m in ms if m["status"] == "OPEN" and not m["overdue"]][:limit]
    lines = [f"SCHEDULE: {days_left(today)} days to 2027-04-01 "
             f"(~{pc_hours_left(today)} PC hours left at 8/week — the scarce resource)."]
    if brs:
        lines.append(f"  BREACHED ({len(brs)}):")
        for m in brs:
            tag = "HARD — this moves the ship date" if m["hard"] else "derived"
            lines.append(f"    ! {m['name']} due {m['due']} ({-m['days']}d ago) [{tag}]")
    else:
        lines.append("  No breached milestones.")
    lines.append("  NEXT:")
    for m in upcoming:
        lines.append(f"    - {m['due']} ({m['days']}d) {m['name']}"
                     + ("  [HARD]" if m["hard"] else ""))
    return "\n".join(lines)
