"""Mistake-to-Impossibility Enforcement Engine for The Senate.

INVARIANT: EVERY HISTORICAL PROCESS FAILURE OR LOSS IS COMPILED AS AN IMPOSSIBLE TEST.
No mistake is managed by "someone remembers"; it must be physically impossible on disk.
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Tuple
from senate.state.fact_store import FactStore


@dataclass
class MistakeInvariant:
    mistake_id: str
    name: str
    incident_description: str
    enforced_by_module: str
    test_function: str
    status: str = "COMPILED_IMPOSSIBLE"


HISTORICAL_MISTAKES = [
    MistakeInvariant(
        mistake_id="MISTAKE_01_UNPAGINATED_READS",
        name="Unpaginated Venue Reads (Silent Truncation)",
        incident_description="Settlements endpoint read only 100 of 313 rows, understating realized P&L.",
        enforced_by_module="domains.kalshi.harness.venue_client",
        test_function="test_pagination_reads_all_pages",
    ),
    MistakeInvariant(
        mistake_id="MISTAKE_02_FEE_FORMULA_REGRESSION",
        name="Fee Schedule Whole-Cent Rounding",
        incident_description="Fee formula regressed to integer rounding, distorting maker/taker math.",
        enforced_by_module="domains.kalshi.state.seed",
        test_function="test_fee_schedule_exact_formula",
    ),
    MistakeInvariant(
        mistake_id="MISTAKE_03_SIDE_INVERTED_BALLOTS",
        name="Quoting Wrong Side of Asymmetric Base Rate",
        incident_description="Bot placed NO bids on 76% pass rate ballot bonds, creating adverse selection bait.",
        enforced_by_module="domains.kalshi.verify.base_rates",
        test_function="test_fundamental_base_rate_rejects_toxic_no_on_ballots",
    ),
    MistakeInvariant(
        mistake_id="MISTAKE_04_TERMINAL_EVACUATION_FILLS",
        name="Terminal Window Book Evacuation Fills",
        incident_description="Makers evacuated sub-24h window, leaving resting bids exposed to sweepers.",
        enforced_by_module="domains.kalshi.verify.invariants",
        test_function="test_terminal_window_curfew_rejects_sub_24h_entry",
    ),
    MistakeInvariant(
        mistake_id="MISTAKE_05_RESTING_ONLY_BUDGET_LEAK",
        name="Resting-Only Budget Cap Leak",
        incident_description="Bot only counted resting orders against budget, deploying $337 on $250 cap after fills.",
        enforced_by_module="domains.kalshi.verify.invariants",
        test_function="test_total_portfolio_budget_cap_includes_positions_and_resting",
    ),
    MistakeInvariant(
        mistake_id="MISTAKE_06_ZERO_SEED_FICTION",
        name="Invented Money and Ghost Orders in Seeds",
        incident_description="Framework previously initialized with fabricated $1,102.97 balances.",
        enforced_by_module="domains.kalshi.state.seed",
        test_function="test_zero_seed_money_invariant",
    ),
    MistakeInvariant(
        mistake_id="MISTAKE_07_PROVISIONAL_MATH_IN_CHAT",
        name="Chat Arithmetic and Rate Hallucination",
        incident_description="Claude added collateral dollars ($149) and called it 'estimates over $1/day'.",
        enforced_by_module="domains.kalshi.verify.payoff",
        test_function="test_discounted_reward_decay",
    ),
    MistakeInvariant(
        mistake_id="MISTAKE_08_YIELD_DESTROYING_CANCELS",
        name="Yield-Destroying Order Cancellations",
        incident_description="Bot canceled positive-yielding 2-tick earner to hold cash.",
        enforced_by_module="domains.kalshi.verify.payoff",
        test_function="test_alabama_yield_preservation",
    ),
    MistakeInvariant(
        mistake_id="MISTAKE_09_SINGLE_MODEL_ECHO_CHAMBER",
        name="Unchecked Single-Model Coding and Speculation",
        incident_description="Claude pushed code and rationalizations without independent multi-model review.",
        enforced_by_module="senate.models.adversary",
        test_function="test_adversary_fails_closed_on_rejection",
    ),
    MistakeInvariant(
        mistake_id="MISTAKE_10_CHAT_DENOMINATOR_ERRORS",
        name="Subagent Denominator Errors and Unverified Yields",
        incident_description="Subagent calculated $2.04 rate by dividing by total budget rather than time-weighted escrow.",
        enforced_by_module="domains.kalshi.verify.accrual",
        test_function="test_time_weighted_accrual_calculation",
    ),
]


def seed_mistakes_into_db(conn) -> int:
    """Populate mistake_invariants table in SQLite."""
    count = 0
    for m in HISTORICAL_MISTAKES:
        conn.execute(
            """INSERT OR REPLACE INTO mistake_invariants 
               (mistake_id, name, incident_description, enforced_by_module, verification_test, status)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (m.mistake_id, m.name, m.incident_description, m.enforced_by_module, m.test_function, m.status),
        )
        count += 1
    conn.commit()
    return count
