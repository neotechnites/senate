"""The scope ratchet: as the ship date approaches, scope may only SHRINK.

WHY.  A dated creative project does not fail by running out of money; it fails by
arriving at the date with a pile of half-finished features and nothing playable.  The
mechanism that produces that outcome is always the same and always feels reasonable in
the moment: a good idea arrives in month four and is added, because adding it costs
nothing today.  This module makes adding cost something today.

THE RULE
  - Before feature freeze, a new SHIP_BLOCKING feature must DISPLACE an existing one.
    Naming the displaced feature is mandatory; there is no "we'll find the time" path.
  - After feature freeze (milestone `feature_freeze`), nothing may be added at any tier.
    The ledger only cuts.
  - WANTED and STRETCH may be added freely before freeze -- they are honest about being
    droppable, and pretending otherwise is what fills a ledger with lies.
  - Nothing is ever deleted.  A cut feature stays as a CUT row with its date, so the
    same idea does not get re-added in March by someone who forgot it was already killed.
"""
from __future__ import annotations

from datetime import date
from typing import List, Optional, Tuple


class ScopeViolation(Exception):
    pass


def _freeze_date(conn) -> Optional[date]:
    row = conn.execute("SELECT due_on FROM milestones WHERE name='feature_freeze'").fetchone()
    return date.fromisoformat(row["due_on"]) if row else None


def is_frozen(conn, today: Optional[date] = None) -> bool:
    fd = _freeze_date(conn)
    return bool(fd and (today or date.today()) >= fd)


def add_feature(conn, feature: str, tier: str, displaced: str = "",
                today: Optional[date] = None, notes: str = "") -> None:
    """Add to the ledger, enforcing the ratchet. Raises ScopeViolation when it must."""
    today = today or date.today()
    if tier not in ("SHIP_BLOCKING", "WANTED", "STRETCH"):
        raise ScopeViolation(f"unknown tier {tier!r}")

    if is_frozen(conn, today):
        raise ScopeViolation(
            f"feature freeze passed ({_freeze_date(conn)}); the ledger only cuts now. "
            f"Refusing to add {feature!r}.")

    if tier == "SHIP_BLOCKING":
        if not displaced:
            raise ScopeViolation(
                f"{feature!r} is SHIP_BLOCKING, so it must displace an existing "
                "SHIP_BLOCKING feature. Name what gets cut, or add it as WANTED.")
        row = conn.execute(
            "SELECT status FROM scope_ledger WHERE feature=? AND tier='SHIP_BLOCKING'",
            (displaced,)).fetchone()
        if row is None:
            raise ScopeViolation(
                f"displaced feature {displaced!r} is not a SHIP_BLOCKING row; "
                "a displacement must be real.")
        if row["status"] == "CUT":
            raise ScopeViolation(f"{displaced!r} was already cut; it cannot pay twice.")
        conn.execute(
            "UPDATE scope_ledger SET status='CUT', cut_on=? , notes=notes||? "
            "WHERE feature=?",
            (today.isoformat(), f" [displaced by {feature} on {today.isoformat()}]", displaced))

    conn.execute(
        "INSERT INTO scope_ledger (feature, tier, added_on, displaced, notes) VALUES (?,?,?,?,?)",
        (feature, tier, today.isoformat(), displaced, notes))
    conn.commit()


def cut_feature(conn, feature: str, why: str, today: Optional[date] = None) -> None:
    """Cutting is always allowed. The row stays, so the idea cannot quietly return."""
    today = today or date.today()
    cur = conn.execute(
        "UPDATE scope_ledger SET status='CUT', cut_on=?, notes=notes||? WHERE feature=?",
        (today.isoformat(), f" [cut {today.isoformat()}: {why}]", feature))
    if cur.rowcount == 0:
        raise ScopeViolation(f"no ledger row named {feature!r}")
    conn.commit()


def counts(conn) -> dict:
    rows = conn.execute(
        "SELECT tier, status, count(*) n FROM scope_ledger GROUP BY tier, status").fetchall()
    out: dict = {}
    for r in rows:
        out.setdefault(r["tier"], {})[r["status"]] = r["n"]
    return out


def open_ship_blocking(conn) -> List[str]:
    return [r["feature"] for r in conn.execute(
        "SELECT feature FROM scope_ledger WHERE tier='SHIP_BLOCKING' AND status!='CUT' "
        "AND status!='DONE' ORDER BY id")]


def block(conn, today: Optional[date] = None) -> str:
    c = counts(conn)
    sb = c.get("SHIP_BLOCKING", {})
    remaining = open_ship_blocking(conn)
    frozen = "FROZEN" if is_frozen(conn, today) else f"open until {_freeze_date(conn)}"
    lines = [f"SCOPE LEDGER ({frozen}; a fact may only shrink it — verify/scope.py):",
             f"  SHIP_BLOCKING: {sb.get('DONE', 0)} done / {len(remaining)} remaining / "
             f"{sb.get('CUT', 0)} cut"]
    for f in remaining[:12]:
        lines.append(f"    - {f}")
    if len(remaining) > 12:
        lines.append(f"    … {len(remaining) - 12} more")
    for tier in ("WANTED", "STRETCH"):
        t = c.get(tier, {})
        if t:
            lines.append(f"  {tier}: " + ", ".join(f"{k.lower()} {v}" for k, v in sorted(t.items())))
    return "\n".join(lines)
