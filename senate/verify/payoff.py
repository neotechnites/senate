"""Economic Payoff and Invariant State Machine for The Senate.

Replaces conversational heuristic logic with compiled mathematical payoff functions.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class OrderAction(str, Enum):
    HOLD = "HOLD"
    RECYCLE = "RECYCLE"
    CANCEL_TO_CASH = "CANCEL_TO_CASH"


@dataclass
class PositionEvaluation:
    ticker: str
    action: OrderAction
    ev_hold_daily_usd: float
    ev_recycle_daily_usd: float
    target_ticker: Optional[str]
    reason: str
    metadata: Dict[str, Any]


def calculate_discounted_reward(
    base_reward_daily_usd: float,
    distance_ticks: int,
    decay_rate: Optional[float] = None,
    fact_store: Optional[Any] = None,
) -> float:
    """Compute daily accrual given tick distance from qualifying touch.
    
    Pulls dynamic decay rate from FactStore if available, else defaults to 0.50.
    Formula: Base * (decay_rate ^ distance_ticks)
    """
    if decay_rate is None:
        if fact_store is not None:
            df_fact = fact_store.get_fact("kalshi.lip.discount_factor")
            if df_fact and isinstance(df_fact.value, dict):
                decay_rate = float(df_fact.value.get("decay_rate_per_tick", 0.50))
        if decay_rate is None:
            decay_rate = 0.50

    if distance_ticks < 0:
        distance_ticks = 0
    discount = decay_rate ** distance_ticks
    return base_reward_daily_usd * discount


def evaluate_order_payoff(
    current_ticker: str,
    distance_ticks: int,
    base_reward_daily_usd: float,
    candidate_markets: List[Dict[str, Any]],
    hurdle_multiplier: float = 1.5,
    min_candidate_ev_usd: float = 1.0,
    decay_rate: Optional[float] = None,
    churn_queue_discount: float = 0.85,
    fact_store: Optional[Any] = None,
) -> PositionEvaluation:
    """Evaluate whether an order should HOLD, RECYCLE, or CANCEL_TO_CASH.
    
    INVARIANTS:
    1. Never cancel an order earning positive yield (even discounted) to hold cash.
    2. Only recycle if a candidate offers at least hurdle_multiplier * current_discounted_yield.
    3. Churn penalty: Candidate EV is discounted by churn_queue_discount (default 15% discount for queue entry & latency).
    4. Candidate must meet min_candidate_ev_usd absolute threshold.
    """
    ev_hold = calculate_discounted_reward(base_reward_daily_usd, distance_ticks, decay_rate, fact_store)

    best_candidate: Optional[Dict[str, Any]] = None
    best_candidate_ev = 0.0

    for cand in candidate_markets:
        c_dist = cand.get("distance_ticks", 0)
        c_base = cand.get("base_reward_daily_usd", 0.0)
        # Apply churn & queue entry discount to candidate
        c_ev_raw = calculate_discounted_reward(c_base, c_dist, decay_rate, fact_store)
        c_ev_net = c_ev_raw * churn_queue_discount
        if c_ev_net > best_candidate_ev:
            best_candidate_ev = c_ev_net
            best_candidate = cand


    metadata = {
        "distance_ticks": distance_ticks,
        "base_reward_daily_usd": base_reward_daily_usd,
        "ev_hold": round(ev_hold, 4),
        "best_candidate_ev": round(best_candidate_ev, 4),
        "hurdle_multiplier": hurdle_multiplier,
    }

    # Case 1: Best candidate beats current yield with hurdle rate
    if best_candidate and best_candidate_ev >= (ev_hold * hurdle_multiplier) and best_candidate_ev >= min_candidate_ev_usd:
        return PositionEvaluation(
            ticker=current_ticker,
            action=OrderAction.RECYCLE,
            ev_hold_daily_usd=ev_hold,
            ev_recycle_daily_usd=best_candidate_ev,
            target_ticker=best_candidate.get("ticker"),
            reason=(
                f"Candidate {best_candidate.get('ticker')} daily EV (${best_candidate_ev:.2f}) "
                f"exceeds current hold EV (${ev_hold:.2f}) by hurdle factor {hurdle_multiplier}x."
            ),
            metadata=metadata,
        )

    # Case 2: Current order is earning positive discounted yield -> HOLD
    if ev_hold > 0.001:
        return PositionEvaluation(
            ticker=current_ticker,
            action=OrderAction.HOLD,
            ev_hold_daily_usd=ev_hold,
            ev_recycle_daily_usd=best_candidate_ev,
            target_ticker=None,
            reason=(
                f"Current seat is earning ${ev_hold:.2f}/day (discounted at {distance_ticks} tick(s) off touch). "
                f"No candidate meets the {hurdle_multiplier}x hurdle rate."
            ),
            metadata=metadata,
        )

    # Case 3: Current order earns $0 and candidate is available -> RECYCLE
    if best_candidate and best_candidate_ev >= min_candidate_ev_usd:
        return PositionEvaluation(
            ticker=current_ticker,
            action=OrderAction.RECYCLE,
            ev_hold_daily_usd=0.0,
            ev_recycle_daily_usd=best_candidate_ev,
            target_ticker=best_candidate.get("ticker"),
            reason=f"Current seat earns $0.00; recycling into candidate {best_candidate.get('ticker')} (${best_candidate_ev:.2f}/day).",
            metadata=metadata,
        )

    # Case 4: Current order earns $0 and no candidate available -> CANCEL_TO_CASH
    return PositionEvaluation(
        ticker=current_ticker,
        action=OrderAction.CANCEL_TO_CASH,
        ev_hold_daily_usd=0.0,
        ev_recycle_daily_usd=0.0,
        target_ticker=None,
        reason="Current seat earns $0.00 and no qualifying candidate exists. Holding cash.",
        metadata=metadata,
    )


def evaluate_order_payoff_from_venue_record(
    order_record: Dict[str, Any],
    market_book: Dict[str, Any],
    candidate_books: Optional[List[Dict[str, Any]]] = None,
    hurdle_multiplier: float = 1.5,
    fact_store: Optional[Any] = None,
) -> PositionEvaluation:
    """Evaluate order payoff strictly from authentic venue order and book records.
    
    STRICT FAIL-CLOSED: Rejects malformed, empty, or truncated records with ValueError.
    """
    if not isinstance(order_record, dict) or not isinstance(market_book, dict):
        raise ValueError("Invalid venue record: order_record and market_book must be valid dictionaries.")

    # 1. Validate required order fields
    ticker = order_record.get("ticker")
    if not ticker or str(ticker).strip() == "" or str(ticker).upper() == "UNKNOWN":
        raise ValueError("Invalid venue record: missing or invalid 'ticker' in order_record.")

    if "price" not in order_record or order_record["price"] is None:
        raise ValueError("Invalid venue record: missing 'price' in order_record.")
    try:
        order_price = float(order_record["price"])
    except (ValueError, TypeError):
        raise ValueError(f"Invalid venue record: unparseable order price '{order_record['price']}'.")

    # 2. Validate required book fields
    if "touch_price" not in market_book or market_book["touch_price"] is None:
        raise ValueError("Invalid venue record: missing 'touch_price' in market_book.")
    try:
        touch_price = float(market_book["touch_price"])
    except (ValueError, TypeError):
        raise ValueError(f"Invalid venue record: unparseable touch_price '{market_book['touch_price']}'.")

    if "pool_daily_reward" not in market_book or market_book["pool_daily_reward"] is None:
        raise ValueError("Invalid venue record: missing 'pool_daily_reward' in market_book.")
    try:
        pool_daily_reward = float(market_book["pool_daily_reward"])
    except (ValueError, TypeError):
        raise ValueError(f"Invalid venue record: unparseable pool_daily_reward '{market_book['pool_daily_reward']}'.")

    tick_size = float(market_book.get("tick_size", 0.01))
    if tick_size <= 0:
        tick_size = 0.01

    distance_ticks = int(round(abs(order_price - touch_price) / tick_size))
    
    qualifying_sides = int(market_book.get("qualifying_sides", 2))
    our_share_pct = float(market_book.get("our_share_pct", 1.0))
    
    base_reward_daily = (pool_daily_reward / max(qualifying_sides, 1)) * our_share_pct
    
    candidates = []
    if candidate_books:
        for c in candidate_books:
            if not isinstance(c, dict) or not c.get("ticker"):
                continue
            c_tick_size = float(c.get("tick_size", 0.01))
            c_order_px = float(c.get("our_price", c.get("touch_price", 0.0)))
            c_touch_px = float(c.get("touch_price", c_order_px))
            c_dist = int(round(abs(c_order_px - c_touch_px) / max(c_tick_size, 0.01)))
            c_pool = float(c.get("pool_daily_reward", 0.0))
            c_sides = int(c.get("qualifying_sides", 2))
            c_share = float(c.get("our_share_pct", 1.0))
            c_base = (c_pool / max(c_sides, 1)) * c_share
            candidates.append({
                "ticker": c.get("ticker"),
                "distance_ticks": c_dist,
                "base_reward_daily_usd": c_base,
            })
            
    eval_res = evaluate_order_payoff(
        current_ticker=ticker,
        distance_ticks=distance_ticks,
        base_reward_daily_usd=base_reward_daily,
        candidate_markets=candidates,
        hurdle_multiplier=hurdle_multiplier,
        fact_store=fact_store,
    )
    eval_res.metadata["is_venue_sourced"] = True
    eval_res.metadata["source_order_price"] = order_price
    eval_res.metadata["source_touch_price"] = touch_price
    eval_res.metadata["source_pool_reward"] = pool_daily_reward
    return eval_res


