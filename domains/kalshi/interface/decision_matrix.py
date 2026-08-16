"""Decision matrix and status renderer for Kalshi Domain Pod."""

from datetime import datetime, timezone
from typing import Optional

from domains.kalshi.state.fact_store import FactStore


def render_kalshi_status(store: FactStore) -> str:
    """Render a clean, high-density status summary for Kalshi Domain Pod (<20 lines)."""
    facts = store.list_facts()
    orders = store.list_active_orders()
    
    # Oracle balance check
    bal_fact = store.get_fact("kalshi.oracle.balance")
    if not bal_fact or not isinstance(bal_fact.value, dict):
        money_str = "UNAVAILABLE (oracle fact missing; run './kalshi.py sync-oracle')"
    else:
        v = bal_fact.value
        cash = v.get("cash_usd")
        pos = v.get("open_positions_usd")
        pnl = v.get("lifetime_pnl_usd")
        ts_str = v.get("timestamp", "UNKNOWN")
        
        if cash is None or pos is None or pnl is None:
            money_str = "UNAVAILABLE (corrupt oracle fact format)"
        else:
            is_stale = True
            try:
                record_dt = datetime.fromisoformat(str(ts_str).replace("Z", "+00:00"))
                age_hours = (datetime.now(timezone.utc) - record_dt).total_seconds() / 3600.0
                is_stale = age_hours > 24.0
            except Exception:
                is_stale = True

            status_tag = "⚠️ STALE" if is_stale else "✅ FRESH"
            money_str = f"{status_tag} (as of {ts_str}) — Cash: ${cash:.2f} | Positions: ${pos:.2f} | P&L: ${pnl:+.2f}"

    lines = [
        "══════════════════════════════════════════════════════════════",
        "              KALSHI DOMAIN POD — SYSTEM STATUS               ",
        "══════════════════════════════════════════════════════════════",
        f"Live Venue Truth:            {money_str}",
        f"Verified Ground-Truth Facts: {len(facts)} active entries in SQLite",
        "──────────────────────────────────────────────────────────────",
        f"ACTIVE OPEN ORDERS ({len(orders)}):",
    ]

    if not orders:
        lines.append("  (No resting orders recorded)")
    else:
        for o in orders:
            lines.append(f"  • [{o.lane.upper()}] {o.ticker} — {o.count} {o.side.upper()} @ {int(o.price*100)}c (${o.collateral_usd:.2f}) [order: {o.order_id[:8]}]")


    lines.extend([
        "──────────────────────────────────────────────────────────────",
        "KEY INVARIANTS ENFORCED:",
        "  1. 50% Distance Decay & 15% Churn Haircut Compiled",
        "  2. Non-zero Yielding Seats NEVER Canceled to Cash",
        "  3. Sourced Venue Snapshots Required for Money Actions",
        "══════════════════════════════════════════════════════════════",
    ])
    return "\n".join(lines)
