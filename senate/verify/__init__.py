"""Senate Verify Engine module."""

from senate.verify.invariants import InvariantEngine
from senate.verify.payoff import (
    OrderAction,
    PositionEvaluation,
    calculate_discounted_reward,
    evaluate_order_payoff,
)
from senate.verify.statistics import (
    expected_max_sharpe,
    price_n_hurdle,
    required_t_stat,
)

__all__ = [
    "InvariantEngine",
    "OrderAction",
    "PositionEvaluation",
    "calculate_discounted_reward",
    "evaluate_order_payoff",
    "expected_max_sharpe",
    "price_n_hurdle",
    "required_t_stat",
]
