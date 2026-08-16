"""Typed data models for Kalshi Domain Pod."""

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class Fact:
    key: str
    domain: str
    value: Dict[str, Any]
    source_artifact: str
    verified_at: str = datetime.now(timezone.utc).isoformat()
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
    placed_at: str = datetime.now(timezone.utc).isoformat()
    updated_at: str = datetime.now(timezone.utc).isoformat()

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
