"""Completion-based recurrence.  The one piece of arithmetic this pod cannot get wrong.

A calendar-based interval says "drain the water heater every 1 January".  A
completion-based interval says "drain it 365 days after you ACTUALLY drained it".
Ryan does the work late; calendar recurrence would mark him permanently overdue and
the nag would become noise he mutes.  Completion-based is the only correct semantics
for maintenance, and it is why no off-the-shelf task app survived selection
(research 2026-09-09: Motion caps recurrence at quarterly and never reschedules a
missed instance).

A RECURRING obligation NEVER reaches status CLOSED.  It re-arms.  Only a ONESHOT or a
past EVENT closes.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Optional

OVERDUE = "OVERDUE"
DUE_SOON = "DUE_SOON"
FUTURE = "FUTURE"
UNSCHEDULED = "UNSCHEDULED"

DUE_SOON_WINDOW_DAYS = 30


def _parse(d: str) -> Optional[date]:
    if not d:
        return None
    try:
        return datetime.strptime(d.strip()[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def next_due(kind: str, interval_days: Optional[int], anchor_date: str,
             last_completed_at: str) -> str:
    """Return the ISO date this obligation is next due, or '' if unscheduled.

    RECURRING: last completion + interval.  Never completed => anchor_date.
    ONESHOT:   anchor_date if one was given (a self-imposed deadline), else ''.
    EVENT:     anchor_date, always.  An event does not move because you ignored it.
    """
    if kind == "RECURRING":
        if not interval_days or interval_days <= 0:
            return ""
        last = _parse(last_completed_at)
        if last is not None:
            return (last + timedelta(days=int(interval_days))).isoformat()
        return (_parse(anchor_date) or date.today()).isoformat()
    if kind in ("ONESHOT", "EVENT"):
        anchor = _parse(anchor_date)
        return anchor.isoformat() if anchor else ""
    raise ValueError(f"unknown obligation kind: {kind!r}")


def due_state(next_due_at: str, today: Optional[date] = None) -> tuple[str, Optional[int]]:
    """(state, days_until).  Negative days_until means that many days overdue."""
    today = today or date.today()
    due = _parse(next_due_at)
    if due is None:
        return UNSCHEDULED, None
    delta = (due - today).days
    if delta < 0:
        return OVERDUE, delta
    if delta <= DUE_SOON_WINDOW_DAYS:
        return DUE_SOON, delta
    return FUTURE, delta


def closes_on_completion(kind: str) -> bool:
    """RECURRING re-arms forever; everything else closes."""
    return kind != "RECURRING"
