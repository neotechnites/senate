"""Authentic Oracle balance synchronization for Kalshi Domain Pod.

INVARIANT: ZERO HAND-AUTHORED / DROP-FILE INGESTION.
Money state originates strictly from the live authenticated Kalshi Venue API (`live_client.fetch_balance()`).
No local drop-files or intermediate human-editable files are permitted.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from domains.kalshi.harness.venue_client import KalshiVenueClient
from domains.kalshi.state.fact_store import FactStore
from domains.kalshi.state.models import Fact


def sync_kalshi_oracle(
    store: FactStore,
    live_client: Optional[KalshiVenueClient] = None,
    max_age_hours: float = 24.0,
) -> Tuple[bool, str, Optional[Fact]]:
    """Synchronize live venue balance directly from authenticated Kalshi API into FactStore."""
    if live_client is None:
        return False, "No live venue balance fetched; configure KALSHI_API_KEY and run './kalshi.py sync-oracle --live'", None

    try:
        raw_bal = live_client.fetch_balance()
        if not isinstance(raw_bal, dict) or "balance" not in raw_bal:
            return False, f"Live venue balance returned unexpected schema: {raw_bal}", None
        
        # Kalshi Trade API returns balance in integer cents
        cents_bal = float(raw_bal.get("balance", 0))
        # 2026-08-15 DEFECT FIX: open positions were read from a "payout" key
        # that does not exist in this response (always 0.0), so the pod
        # reported Positions: $0.00 while $199.69 of filled positions sat on
        # the book through the 08-15 incident.  The venue's mark of all open
        # positions is `portfolio_value` (cents).
        payouts_cents = float(raw_bal.get("portfolio_value",
                                          raw_bal.get("payout", 0)) or 0)
        cash_usd = round(cents_bal / 100.0, 2)
        open_pos_usd = round(payouts_cents / 100.0, 2)
        deposits_usd = round(float(raw_bal.get("lifetime_deposits", cents_bal)) / 100.0, 2)
        
        now_iso = datetime.now(timezone.utc).isoformat()
        lifetime_pnl = round(cash_usd + open_pos_usd - deposits_usd, 2)
        
        fact_value = {
            "cash_usd": cash_usd,
            "open_positions_usd": open_pos_usd,
            "lifetime_deposits_usd": deposits_usd,
            "lifetime_pnl_usd": lifetime_pnl,
            "timestamp": now_iso,
            "is_stale": False,
            "source_type": "live_kalshi_api_authenticated",
            "raw_response": raw_bal,
        }

        fact = Fact(
            key="kalshi.oracle.balance",
            domain="kalshi",
            value=fact_value,
            source_artifact="live_kalshi_api:/trade-api/v2/portfolio/balance",
            verified_at=now_iso,
            verified_by="venue_api_authenticated",
            is_immutable=False,
        )

        store.set_fact(fact)
        msg = f"Synced: Cash=${cash_usd:.2f} | Positions=${open_pos_usd:.2f} | P&L=${lifetime_pnl:.2f} [FRESH]"
        return True, msg, fact
    except Exception as e:
        return False, f"Live venue API balance fetch failed: {e}", None
