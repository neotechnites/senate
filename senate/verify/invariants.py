"""Invariant validation engine for The Senate.

Evaluates proposals, strategies, and hypotheses against formal property invariants.
"""

from typing import Any, Dict, List, Optional, Tuple
from senate.state.fact_store import FactStore
from senate.verify.statistics import required_t_stat


class InvariantEngine:
    def __init__(self, fact_store: Optional[FactStore] = None):
        self.facts = fact_store or FactStore()

    def validate_market_order_proposal(self, proposal: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """Verify an order placement proposal against venue invariants."""
        violations: List[str] = []
        passes: List[str] = []

        # 1. Order type invariant (Maker-only)
        order_type = str(proposal.get("order_type", "limit")).lower()
        if order_type in ["market", "taker"]:
            violations.append("Invariant Breach: Market/Taker orders are prohibited. Must be limit maker.")
        else:
            passes.append("Order type is limit.")

        if proposal.get("cross_spread", False):
            violations.append("Invariant Breach: Crossing the spread is strictly prohibited.")
        else:
            passes.append("Spread crossing disabled.")

        # 2. Toxic middle band invariant (0.10 < P < 0.90)
        price = float(proposal.get("price", 0.0))
        allow_midband = proposal.get("allow_midband", False)
        if 0.10 < price < 0.90 and not allow_midband:
            violations.append(f"Invariant Breach: Price {price:.2f} lies in toxic mid-band (0.10-0.90) without midband clearance.")
        else:
            passes.append(f"Price {price:.2f} satisfies band constraints.")

        # 3. Capital exposure cap
        notional_usd = float(proposal.get("notional_usd", 0.0))
        caps_fact = self.facts.get_fact("sovereign.risk.caps") or self.facts.get_fact("kalshi.exposure.caps")
        if not caps_fact or not isinstance(caps_fact.value, dict):
            violations.append("Invariant Breach: Capital caps fact is missing or unverified. Fails closed.")
        else:
            max_per_mkt = float(caps_fact.value.get("max_single_deployment_usd") or caps_fact.value.get("max_per_market_usd", 0.0))
            if notional_usd > max_per_mkt:
                violations.append(f"Invariant Breach: Allocation ${notional_usd:.2f} exceeds per-market cap of ${max_per_mkt:.2f}.")
            else:
                passes.append(f"Allocation ${notional_usd:.2f} is within limit.")



        is_valid = len(violations) == 0
        return is_valid, violations, passes

    def validate_hypothesis_statistical_bar(self, n_trials: int, reported_t_stat: float) -> Tuple[bool, str]:
        """Validate if a reported t-stat clears the Bonferroni multiple testing hurdle."""
        req_t = required_t_stat(n_trials)
        if reported_t_stat < req_t:
            return False, f"Reported |t|={reported_t_stat:.2f} fails required hurdle |t|>={req_t:.2f} at N={n_trials} trials."
        return True, f"Reported |t|={reported_t_stat:.2f} clears Bonferroni hurdle |t|>={req_t:.2f} at N={n_trials} trials."
