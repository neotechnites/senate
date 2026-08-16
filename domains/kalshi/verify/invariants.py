"""Invariant and boundary condition validator for Kalshi Domain Pod.

Enforces:
1. Maker-Only Rules (Market orders prohibited)
2. Spread Crossing Protection (Never cross the touch)
3. Exposure Limits: Single market cap ($50.00) & Total portfolio risk cap ($250.00)
4. Terminal Window Curfew: Zero order entry within 24h of window expiry (anti-evacuation)
5. Fundamental Base-Rate Side-Gate: Zero quoting against asymmetric fundamental distributions
"""

from typing import Any, Dict, List, Optional, Tuple

from domains.kalshi.state.fact_store import FactStore
from domains.kalshi.verify.base_rates import evaluate_fundamental_base_rate


class InvariantEngine:
    def __init__(self, facts: Optional[FactStore] = None):
        self.facts = facts or FactStore()

    def validate_order_proposal(self, proposal: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """Validate order against Kalshi compiled invariants."""
        violations: List[str] = []
        passes: List[str] = []

        # 1. Maker-only check
        order_type = str(proposal.get("order_type", "limit")).lower()
        if order_type == "market":
            violations.append("Invariant Breach: Market/Taker orders are forbidden. Must be post-only maker.")
        else:
            passes.append("Maker-only rule satisfied.")

        # 2. Spread crossing check
        price = float(proposal.get("price", 0.0))
        touch_px = proposal.get("touch_price")
        if touch_px is not None:
            touch_float = float(touch_px)
            if price > touch_float:
                violations.append(f"Invariant Breach: Price ${price:.2f} crosses touch ${touch_float:.2f}.")
            else:
                passes.append(f"Price ${price:.2f} does not cross touch.")

        # 3. Terminal Window Curfew (>= 24h to window expiry)
        hours_to_close = proposal.get("hours_to_window_expiry")
        if hours_to_close is not None:
            if float(hours_to_close) < 24.0:
                violations.append(
                    f"Invariant Breach: Terminal window curfew breached ({float(hours_to_close):.1f}h < 24.0h to close). "
                    f"High book evacuation and adverse selection fill risk."
                )
            else:
                passes.append(f"Terminal window margin satisfied ({float(hours_to_close):.1f}h >= 24.0h).")

        # 4. Fundamental Base-Rate Side-Gate Check
        ticker = str(proposal.get("ticker", ""))
        side = str(proposal.get("side", "yes"))
        mkt_title = str(proposal.get("title", ""))
        mkt_sub = str(proposal.get("subtitle", ""))
        is_safe_rate, rate_violation, _ = evaluate_fundamental_base_rate(
            ticker=ticker,
            side=side,
            price=price,
            market_title=mkt_title,
            market_subtitle=mkt_sub,
        )
        if not is_safe_rate and rate_violation:
            violations.append(rate_violation)
        else:
            passes.append("Fundamental base-rate side check passed.")

        # 5. Capital Exposure Caps (Single Market & Total Portfolio Cap)
        notional_usd = float(proposal.get("notional_usd", 0.0))
        caps_fact = self.facts.get_fact("kalshi.exposure.caps")
        if not caps_fact or not isinstance(caps_fact.value, dict) or "max_per_market_usd" not in caps_fact.value:
            violations.append("Invariant Breach: Capital caps fact 'kalshi.exposure.caps' is missing or unverified. Fails closed.")
        else:
            max_per_mkt = float(caps_fact.value.get("max_per_market_usd", 50.00))
            max_total_cap = float(caps_fact.value.get("max_total_portfolio_usd", 250.00))

            if notional_usd > max_per_mkt:
                violations.append(f"Invariant Breach: Allocation ${notional_usd:.2f} exceeds per-market cap of ${max_per_mkt:.2f}.")
            else:
                passes.append(f"Single market allocation ${notional_usd:.2f} is within limit.")

            # Compute total deployed capital (Positions + Resting Orders + Proposed Order)
            active_orders = self.facts.list_active_orders()
            resting_collateral = sum(o.collateral_usd for o in active_orders)
            
            # Check for filled positions in oracle balance fact if present
            oracle_fact = self.facts.get_fact("kalshi.oracle.balance")
            positions_val = 0.0
            if oracle_fact and isinstance(oracle_fact.value, dict):
                positions_val = float(oracle_fact.value.get("open_positions_usd", 0.0))

            total_deployed = resting_collateral + positions_val + notional_usd
            if total_deployed > max_total_cap:
                violations.append(
                    f"Invariant Breach: Total portfolio exposure ${total_deployed:.2f} "
                    f"(Positions ${positions_val:.2f} + Resting ${resting_collateral:.2f} + Proposed ${notional_usd:.2f}) "
                    f"exceeds total portfolio budget of ${max_total_cap:.2f}."
                )
            else:
                passes.append(f"Total portfolio exposure ${total_deployed:.2f} <= ${max_total_cap:.2f}.")

        is_valid = len(violations) == 0
        return is_valid, violations, passes
