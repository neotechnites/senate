"""Execution Gate for Kalshi Domain Pod.

Partitions actions into Offensive (gated, strict fail-closed) vs Defensive (fast-path, zero API latency).
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from domains.kalshi.state.fact_store import FactStore
from domains.kalshi.verify.caps import PER_MARKET_HARD_USD
from domains.kalshi.verify.invariants import InvariantEngine


class ActionClass(str, Enum):
    OFFENSIVE = "OFFENSIVE"
    DEFENSIVE = "DEFENSIVE"


class ActionType(str, Enum):
    # Offensive Actions: Require strict invariant & adversarial gates
    DEPLOY_SEAT = "DEPLOY_SEAT"
    INCREASE_NOTIONAL = "INCREASE_NOTIONAL"
    ENTER_MARKET = "ENTER_MARKET"

    # Defensive Actions: Fast-path execution, zero third-party API dependencies
    CANCEL_ORDER = "CANCEL_ORDER"
    EJECT_OUTBID = "EJECT_OUTBID"
    RETREAT_TOXIC = "RETREAT_TOXIC"
    STOP_LOSS = "STOP_LOSS"
    # FLAT-2 (2026-09-05): reduce-only sell of a position we are ALREADY
    # holding.  Distinct from the four order-scoped defensive types above:
    # a flatten has no order_id before it is placed, so the shared
    # "order_id present" check could never admit it.
    FLATTEN_POSITION = "FLATTEN_POSITION"


# Defensive types never touch InvariantEngine.validate_order_proposal.
DEFENSIVE_ACTION_TYPES = (
    ActionType.CANCEL_ORDER,
    ActionType.EJECT_OUTBID,
    ActionType.RETREAT_TOXIC,
    ActionType.STOP_LOSS,
    ActionType.FLATTEN_POSITION,
)

# Fields a FLATTEN_POSITION proposal must carry.  Kept deliberately small:
# the venue-side reduce_only flag is what guarantees the sell cannot open
# an opposite position, so the gate refuses any proposal that omits it.
FLATTEN_REQUIRED_KEYS = ("ticker", "held_side", "count", "sell_price_cents", "reduce_only")


def _flatten_violations(proposal: Dict[str, Any]) -> List[str]:
    """Local, API-free validation of a reduce-only flatten proposal.

    FLAT-2 (2026-09-05): a flatten REMOVES exposure, so it is judged on its
    own shape only -- never on the per-market cap that governs adding
    exposure.  Returns an empty list when the proposal is admissible.
    """
    v: List[str] = []
    ticker = proposal.get("ticker")
    if not isinstance(ticker, str) or not ticker.strip():
        v.append("Missing ticker")
    held_side = proposal.get("held_side")
    if held_side not in ("yes", "no"):
        v.append("held_side must be 'yes' or 'no'")
    count = proposal.get("count")
    if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
        v.append("count must be a positive integer")
    px = proposal.get("sell_price_cents")
    if isinstance(px, bool) or not isinstance(px, int) or not (1 <= px <= 99):
        v.append("sell_price_cents must be an integer in 1..99")
    if proposal.get("reduce_only") is not True:
        v.append("reduce_only must be True")
    return v


@dataclass
class GateResult:
    is_executed: bool
    action_class: ActionClass
    action_type: ActionType
    reason: str
    violations: List[str]
    latency_ms: float


class ExecutionGate:
    """Enforces execution policies across offensive and defensive market actions."""

    def __init__(self, store: Optional[FactStore] = None):
        self.store = store or FactStore()
        self.invariants = InvariantEngine(self.store)

    def execute_action(
        self,
        action_type: ActionType,
        proposal: Dict[str, Any],
        adversary: Optional[Any] = None,
        receipts: Optional[Dict[str, Any]] = None,
    ) -> GateResult:
        """Route and execute action according to class policy."""
        import time
        start_ts = time.time()

        # 1. Defensive Fast-Path (Never gated on third-party APIs)
        if action_type in DEFENSIVE_ACTION_TYPES:
            # Local compiled check only -- per action type.
            #
            # FLAT-2 (2026-09-05, paid-for lesson): 25 lifetime fills, every
            # one an informed sweep that left an open position the system
            # could never sell (KXSNOWCRABCATCH from 09-03 still open).
            # STOP_LOSS existed on paper but was unroutable: the only
            # defensive check demanded an order_id, which a not-yet-placed
            # flatten cannot have, and pushing it through the OFFENSIVE
            # branch made InvariantEngine.validate_order_proposal add the
            # filled row's max_escrow_usd to same_mkt and refuse with
            # "exceeds per-market cap".  Ryan's $25/market cap exists to
            # stop ADDING exposure; it must never stop REMOVING it.  So a
            # reduce-only flatten is validated here, locally, and is never
            # handed to validate_order_proposal.
            if action_type == ActionType.FLATTEN_POSITION:
                violations = _flatten_violations(proposal)
                latency = (time.time() - start_ts) * 1000.0
                if violations:
                    return GateResult(
                        is_executed=False,
                        action_class=ActionClass.DEFENSIVE,
                        action_type=action_type,
                        reason="FLATTEN_POSITION proposal failed local reduce-only checks.",
                        violations=violations,
                        latency_ms=round(latency, 2),
                    )
                return GateResult(
                    is_executed=True,
                    action_class=ActionClass.DEFENSIVE,
                    action_type=action_type,
                    reason=(
                        "Fast-path defensive action 'FLATTEN_POSITION' executed locally "
                        "(reduce-only; per-market cap not consulted)."
                    ),
                    violations=[],
                    latency_ms=round(latency, 2),
                )

            # The four order-scoped defensive types keep the order_id rule.
            order_id = proposal.get("order_id")
            if not order_id:
                latency = (time.time() - start_ts) * 1000.0
                return GateResult(
                    is_executed=False,
                    action_class=ActionClass.DEFENSIVE,
                    action_type=action_type,
                    reason="Defensive action missing required 'order_id'.",
                    violations=["Missing order_id"],
                    latency_ms=round(latency, 2),
                )

            latency = (time.time() - start_ts) * 1000.0
            return GateResult(
                is_executed=True,
                action_class=ActionClass.DEFENSIVE,
                action_type=action_type,
                reason=f"Fast-path defensive action '{action_type.value}' executed locally.",
                violations=[],
                latency_ms=round(latency, 2),
            )

        # 2. Offensive Action Gate (Strict Fail-Closed)
        is_valid, violations, _ = self.invariants.validate_order_proposal(proposal)
        if not is_valid:
            latency = (time.time() - start_ts) * 1000.0
            return GateResult(
                is_executed=False,
                action_class=ActionClass.OFFENSIVE,
                action_type=action_type,
                reason="Offensive action failed compiled invariant checks (Fails closed).",
                violations=violations,
                latency_ms=round(latency, 2),
            )

        # 3. Optional Adversarial Audit with Ground-Truth Receipts
        if adversary is not None:
            invariants_list = [
                # FG-03 (2026-09-05): was a literal "$50.00" — a fifth private
                # copy of the per-market number.  The referee model was being
                # told to approve $50 seats while Ryan's limit is "never to
                # have more than 25$ in any market".  Derived from
                # verify/caps.py so the adversary reads the same ceiling the
                # wire enforces.
                f"Capital allocation must be <= ${PER_MARKET_HARD_USD:.2f} per market "
                f"(orders + positions, per ticker).",
                "Orders must be post-only maker (no taker fees).",
                "Order price must not cross the touch.",
            ]
            
            # Pack receipts into proposal description for referee model
            receipt_str = f"RECEIPTS: {receipts}" if receipts else "RECEIPTS: None"
            proposal_desc = f"PROPOSAL: {proposal}\n{receipt_str}"

            audit_res = adversary.audit_proposal(
                proposal_description=proposal_desc,
                invariants_list=invariants_list,
            )
            if not audit_res.is_approved:
                latency = (time.time() - start_ts) * 1000.0
                return GateResult(
                    is_executed=False,
                    action_class=ActionClass.OFFENSIVE,
                    action_type=action_type,
                    reason=f"Adversarial referee rejected proposal: {audit_res.critique}",
                    violations=audit_res.violations,
                    latency_ms=round(latency, 2),
                )

        latency = (time.time() - start_ts) * 1000.0
        return GateResult(
            is_executed=True,
            action_class=ActionClass.OFFENSIVE,
            action_type=action_type,
            reason=f"Offensive action '{action_type.value}' passed all invariant gates.",
            violations=[],
            latency_ms=round(latency, 2),
        )
