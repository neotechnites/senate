"""Execution Gate for Kalshi Domain Pod.

Partitions actions into Offensive (gated, strict fail-closed) vs Defensive (fast-path, zero API latency).
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from domains.kalshi.state.fact_store import FactStore
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
        if action_type in [
            ActionType.CANCEL_ORDER,
            ActionType.EJECT_OUTBID,
            ActionType.RETREAT_TOXIC,
            ActionType.STOP_LOSS,
        ]:
            # Local compiled check only (e.g. order_id present)
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
                "Capital allocation must be <= $50.00 per market.",
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
