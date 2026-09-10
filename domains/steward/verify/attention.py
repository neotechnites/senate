"""The interruption budget — a FLOOR on silence, not a schedule for speech.

This module does not decide what to say.  It decides what the manager is FORBIDDEN
from saying because it already said it recently.  The judgement of whether Ryan is
worth interrupting at all belongs to the Domain Head; this is the guardrail under it.

WHY A FLOOR AND NOT A CADENCE.  Ryan ruled on 2026-09-09: "no, not a daily digest, its
an open conversation with my manager ... if i wanted daily reminders i would use daily
reminders."  So nothing here schedules a message.  What it does is enforce the one
thing the measured evidence is clear about:

  - Pop-Eleches 2011 (AIDS 25(6), N=431, 48wk): WEEKLY SMS raised treatment adherence
    13 points; DAILY SMS had NO effect at all.  Authors attribute the null to
    habituation.  [measured, external]
  - Wohllebe et al. 2021 (N=17,500 randomized): app abandonment rose ~2.5pp per
    additional message per week.  [measured, external]

Hence: at most one nag per obligation per week, and a global quiet floor so a wake
storm cannot become a nag storm.  Both are minimums Ryan can loosen by ruling; neither
is a target to hit.  Speaking zero times in a day is a healthy outcome.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Optional

# One nag per obligation per week.  Directly from the Pop-Eleches result above.
PER_OBLIGATION_COOLDOWN_DAYS = 7

# The manager may not open its mouth more than this often, whatever it thinks it has.
# This is a spam brake, NOT a cadence -- it does not oblige it to speak this often.
GLOBAL_MIN_GAP_HOURS = 6


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def last_spoke_at(conn: sqlite3.Connection) -> Optional[datetime]:
    row = conn.execute(
        "SELECT at FROM conversation WHERE direction='TO_RYAN' ORDER BY at DESC LIMIT 1"
    ).fetchone()
    if not row or not row["at"]:
        return None
    try:
        return datetime.fromisoformat(str(row["at"]).replace("Z", ""))
    except ValueError:
        return None


def last_nagged_at(conn: sqlite3.Connection, obligation_id: int) -> Optional[datetime]:
    row = conn.execute(
        "SELECT at FROM conversation WHERE direction='TO_RYAN' AND obligation_id=? "
        "ORDER BY at DESC LIMIT 1", (obligation_id,)
    ).fetchone()
    if not row or not row["at"]:
        return None
    try:
        return datetime.fromisoformat(str(row["at"]).replace("Z", ""))
    except ValueError:
        return None


def may_speak_at_all(conn: sqlite3.Connection, now: Optional[datetime] = None) -> tuple[bool, str]:
    """Global brake.  (allowed, reason)."""
    now = now or _now()
    last = last_spoke_at(conn)
    if last is None:
        return True, "never spoken to Ryan before"
    gap = now - last
    if gap < timedelta(hours=GLOBAL_MIN_GAP_HOURS):
        mins = int(gap.total_seconds() // 60)
        return False, (f"spoke {mins} min ago; global floor is "
                       f"{GLOBAL_MIN_GAP_HOURS}h")
    return True, f"last spoke {int(gap.total_seconds() // 3600)}h ago"


def may_nag(conn: sqlite3.Connection, obligation_id: int,
            now: Optional[datetime] = None) -> tuple[bool, str]:
    """Per-obligation brake.  (allowed, reason)."""
    now = now or _now()
    last = last_nagged_at(conn, obligation_id)
    if last is None:
        return True, "never raised this one"
    gap_days = (now - last).days
    if gap_days < PER_OBLIGATION_COOLDOWN_DAYS:
        return False, (f"raised {gap_days}d ago; cooldown is "
                       f"{PER_OBLIGATION_COOLDOWN_DAYS}d (Pop-Eleches 2011: daily "
                       f"nagging measured zero effect)")
    return True, f"last raised {gap_days}d ago"
