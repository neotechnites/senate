"""Typed data models for Kalshi Domain Pod."""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _utc_now_iso() -> str:
    """Fresh UTC timestamp, evaluated PER INSTANCE.

    VR-8 receipt (2026-09-05): `placed_at: str = datetime.now(...).isoformat()`
    was evaluated ONCE at class definition, so every ActiveOrder / Fact built
    without an explicit timestamp carried the process START time -- on the
    VPS, a daemon that has been up for days stamps every adopted order as
    days old.  save_order's ON CONFLICT clause deliberately never rewrites
    placed_at (first placement wins), so a bad birth time is permanent, and
    the reconciler's 10-minute "gone from venue" grace (the guard added after
    two live orphans were created by a premature retire) measured age from
    that unrelated moment: a freshly adopted row could look older than the
    grace and be retired/cancelled in the very cycle it appeared.  A
    default_factory is evaluated on each construction, which is what the
    timestamp always meant.
    """
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Fact:
    key: str
    domain: str
    value: Dict[str, Any]
    source_artifact: str
    verified_at: str = field(default_factory=_utc_now_iso)  # VR-8: per instance
    verified_by: str = "oracle"
    is_immutable: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ActiveOrder:
    order_id: str
    ticker: str
    side: str
    price: float
    count: int
    collateral_usd: float
    status: str
    lane: str
    # VR-8 (2026-09-05): default_factory, NOT a class-level datetime.now()
    # -- see _utc_now_iso.  Callers that know the venue's created_time
    # (harness/venue_reconciler.py adopt/mirror/orphan paths) pass it
    # explicitly; this default only covers rows born in this process.
    placed_at: str = field(default_factory=_utc_now_iso)
    updated_at: str = field(default_factory=_utc_now_iso)
    # ATTRIBUTION-1 (2026-09-16).  The venue's accrual feed is keyed by LIP
    # program id; this mirror carries the [placed_at, terminal) interval.  With
    # both, per-seat earnings are a query.  Without it, 365 of 407 program ids in
    # the accrual log -- 90% of everything the pod has earned -- cannot be tied
    # to a ticker, because the live index lists only CURRENTLY-LIVE programs.
    # Optional: a row adopted from the venue or mirrored by the reconciler may
    # legitimately not know it, and None must never block a mirror write.
    program_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)



@dataclass
class OrderProposal:
    ticker: str
    side: str
    price: float
    count: int
    notional_usd: float
    order_type: str = "limit"
    post_only: bool = True
    lane: str = "autoseat"
