"""Compact, high-density decision matrix and status reporter for The Senate Meta-Hub."""

from typing import Any, Dict, List
from senate.state.fact_store import FactStore
from senate.verify.statistics import price_n_hurdle


def render_senate_status(store: FactStore) -> str:
    """Render a clean, high-density status summary (<25 lines)."""
    facts = store.list_facts()
    projects = store.list_project_states()
    goals = store.list_goals(status="ACTIVE")
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
        "RYAN'S ACTIVE GOALS (STATEMENT 1 PRIORITY):",
    ]

    # ONE goal renderer (2026-09-09).  This block used to print
    # "{ryan_hours_saved}h saved" as a measurement; those values were seeded on
    # 2026-08-17 with zero rows in trials_ledger.  head_prompt.goals_block is now the
    # single renderer and it tags an unbacked number SELF-MARKED, UNVERIFIED.
    # Ledger: goal_progress_self_marked.
    from senate.interface.head_prompt import goals_block
    lines.extend("  " + ln for ln in goals_block(store).splitlines()[1:])

    lines.extend([
        "──────────────────────────────────────────────────────────────",
        "PORTFOLIO GOALS & ACTIVE DOMAINS:",
    ])

    if not projects:
        lines.append("  (No active domain pods registered)")
    else:
        for p in projects:
            cat = str(p.variables.get("category", "general")).upper()
            mission = p.variables.get("mission", p.name)
            lines.append(f"  • [{cat}] {p.name} ({p.project_id}) — {mission}")

    lines.extend([
        "──────────────────────────────────────────────────────────────",
        "SOVEREIGN SENATE INVARIANTS:",
        "  1. Ryan's Goal Progress & Hours Saved Outrank All Artifacts",
        "  2. Single Sovereign State in SQLite (Zero Context Rot)",
        "  3. Multiple-Testing Penalization Priced via FWER Hurdles (K>=10)",
        "══════════════════════════════════════════════════════════════",
    ])
    return "\n".join(lines)
