"""Oracle ground-truth money balance synchronization.

Reads authentic venue balance from oracle JSON artifact and stores it in FactStore.
Zero fabricated numbers: fails closed if oracle artifact is missing or invalid.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from senate.state.fact_store import FactStore
from senate.state.models import Fact

DEFAULT_ORACLE_SEARCH_PATHS = [
    Path("data/oracle/truth_latest.json"),
    Path(os.path.expanduser("~/kalshi_data/oracle/truth_latest.json")),
]


def parse_oracle_json(payload: Dict[str, Any], max_age_hours: float = 24.0) -> Dict[str, Any]:
    """Parse and validate oracle balance payload.
    
    Required fields:
    - cash_usd (float)
    - open_positions_usd (float)
    - lifetime_deposits_usd (float)
    - timestamp (ISO string or unix timestamp)
    """
    if not isinstance(payload, dict):
        raise ValueError("Oracle payload must be a JSON dictionary.")

    # 1. Required numeric fields
    for field in ["cash_usd", "open_positions_usd", "lifetime_deposits_usd"]:
        if field not in payload or payload[field] is None:
            raise ValueError(f"Oracle payload missing required field: '{field}'")
        try:
            float(payload[field])
        except (ValueError, TypeError):
            raise ValueError(f"Oracle field '{field}' must be a valid numeric dollar amount.")

    cash = float(payload["cash_usd"])
    positions = float(payload["open_positions_usd"])
    deposits = float(payload["lifetime_deposits_usd"])
    pnl = round(cash + positions - deposits, 2)

    # 2. Timestamp & Staleness check
    raw_ts = payload.get("timestamp") or payload.get("ts")
    if not raw_ts:
        raise ValueError("Oracle payload missing required timestamp field ('timestamp' or 'ts').")

    if isinstance(raw_ts, (int, float)):
        record_dt = datetime.fromtimestamp(raw_ts, tz=timezone.utc)
    else:
        try:
            record_dt = datetime.fromisoformat(str(raw_ts).replace("Z", "+00:00"))
        except Exception:
            raise ValueError(f"Oracle timestamp '{raw_ts}' is not a valid ISO datetime or timestamp.")

    now_dt = datetime.now(timezone.utc)
    age_seconds = (now_dt - record_dt).total_seconds()
    is_stale = age_seconds > (max_age_hours * 3600)

    return {
        "cash_usd": cash,
        "open_positions_usd": positions,
        "lifetime_deposits_usd": deposits,
        "lifetime_pnl_usd": pnl,
        "timestamp": record_dt.isoformat(),
        "age_hours": round(age_seconds / 3600, 2),
        "is_stale": is_stale,
    }


def sync_oracle_fact(
    store: FactStore,
    file_path: Optional[Path] = None,
    max_age_hours: float = 24.0,
) -> Tuple[bool, str, Optional[Fact]]:
    """Read authentic oracle file and write timestamped fact to SQLite.
    
    Returns (success, message, fact).
    Fails closed if file does not exist or payload is corrupt.
    """
    target_path: Optional[Path] = None
    if file_path:
        target_path = Path(file_path)
    else:
        for p in DEFAULT_ORACLE_SEARCH_PATHS:
            if p.exists():
                target_path = p
                break

    if not target_path or not target_path.exists():
        return False, f"Oracle file not found in search paths: {[str(p) for p in (DEFAULT_ORACLE_SEARCH_PATHS if not file_path else [file_path])]}", None

    try:
        raw_text = target_path.read_text(encoding="utf-8")
        payload = json.loads(raw_text)
        parsed = parse_oracle_json(payload, max_age_hours=max_age_hours)
    except Exception as e:
        return False, f"Failed to parse oracle file '{target_path}': {e}", None

    fact = Fact(
        key="kalshi.oracle.balance",
        domain="kalshi",
        value=parsed,
        source_artifact=str(target_path),
        verified_at=parsed["timestamp"],
        verified_by="oracle_sync",
        is_immutable=False,  # Oracle balances update over time with fact_history audit
    )

    store.set_fact(fact)
    staleness_msg = "⚠️ STALE" if parsed["is_stale"] else "✅ FRESH"
    msg = f"{staleness_msg} (age: {parsed['age_hours']}h) — Cash: ${parsed['cash_usd']:.2f}, Pos: ${parsed['open_positions_usd']:.2f}, P&L: ${parsed['lifetime_pnl_usd']:.2f}"
    return True, msg, fact
