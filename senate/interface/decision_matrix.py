"""Compact, high-density decision matrix and status reporter for The Senate Meta-Hub."""

from typing import Any, Dict, List
from senate.state.fact_store import FactStore
from senate.verify.statistics import price_n_hurdle


def render_senate_status(store: FactStore) -> str:
    """Render a clean, high-density status summary (<20 lines)."""
    facts = store.list_facts()
    projects = store.list_project_states()
    per_project_trials, total_trials = store.get_trial_counts()
    hurdle = price_n_hurdle(total_trials if total_trials > 0 else 1)

    lines = [
        "══════════════════════════════════════════════════════════════",
        "                   THE SENATE — SYSTEM STATUS                 ",
        "══════════════════════════════════════════════════════════════",
        f"Verified Sovereign Laws:     {len(facts)} entries in SQLite",
        f"Statistical Ledger (Trials): Total N = {total_trials} | Required Hurdle |t| >= {hurdle['required_t_stat']}",
        f"Expected Noise Sharpe @ N={total_trials or 1}: {hurdle['expected_noise_sharpe']:.2f}",
        "──────────────────────────────────────────────────────────────",
        "PORTFOLIO GOALS & ACTIVE DOMAINS:",
    ]

    if not projects:
        lines.append("  (No active domain projects configured)")
    else:
        for p in projects:
            cat = str(p.variables.get("category", "general")).upper()
            mission = p.variables.get("mission", p.name)
            metrics = p.variables.get("domain_metrics", {})
            m_str = ""
            if "oracle_balance" in metrics and metrics["oracle_balance"]:
                ob = metrics["oracle_balance"]
                m_str = f" | Cash: ${ob.get('cash_usd', 0.0):.2f}, P&L: ${ob.get('lifetime_pnl_usd', 0.0):+.2f}"
            elif "active_orders_count" in metrics:
                m_str = f" | Open Orders: {metrics['active_orders_count']}"
            elif "drills" in metrics:
                m_str = f" | Drills: {metrics['drills']}"
            
            lines.append(f"  • [{cat}] {p.name} ({p.project_id}) — {mission}{m_str}")

    lines.extend([
        "──────────────────────────────────────────────────────────────",
        "SOVEREIGN SENATE INVARIANTS:",
        "  1. Ryan's Goal Progress & Hours Saved Outrank All Artifacts",
        "  2. Single Sovereign State in SQLite (Zero Context Rot)",
        "  3. Multiple-Testing Penalization Priced via FWER Hurdles",
        "══════════════════════════════════════════════════════════════",
    ])
    return "\n".join(lines)
