"""Unit and mathematical invariant tests for Senate Verify Engine."""

import tempfile
import unittest
from pathlib import Path

from senate.state.db import Database
from senate.state.fact_store import FactStore
from senate.state.seeds import seed_database
from senate.verify.invariants import InvariantEngine
from senate.verify.payoff import (
    OrderAction,
    calculate_discounted_reward,
    evaluate_order_payoff,
)
from senate.verify.statistics import (
    expected_max_sharpe,
    price_n_hurdle,
    required_t_stat,
)


class TestVerifyEngine(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_verify.db"
        self.db = Database(self.db_path)
        self.store = FactStore(self.db)
        seed_database(self.store)
        self.engine = InvariantEngine(self.store)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_bailey_lopez_de_prado_statistics(self):
        """Regression lock Bailey & Lopez de Prado reference numbers."""
        # N=10 -> expected noise Sharpe ~1.57
        sr_10 = expected_max_sharpe(10)
        self.assertAlmostEqual(sr_10, 1.57, delta=0.03)

        # N=45 -> |t| >= 3.26
        t_45 = required_t_stat(45, alpha=0.05)
        self.assertAlmostEqual(t_45, 3.26, delta=0.03)

        # N=202 -> |t| >= 3.66
        t_202 = required_t_stat(202, alpha=0.05)
        self.assertAlmostEqual(t_202, 3.66, delta=0.03)

    def test_discounted_reward_decay(self):
        """Verify exponential distance decay formula."""
        base_reward = 10.00  # $10/day at touch
        
        # At touch (distance=0) -> 100% ($10.00)
        self.assertEqual(calculate_discounted_reward(base_reward, 0), 10.00)

        # 1 tick off (distance=1) -> 50% ($5.00)
        self.assertEqual(calculate_discounted_reward(base_reward, 1), 5.00)

        # 2 ticks off (distance=2) -> 25% ($2.50)
        self.assertEqual(calculate_discounted_reward(base_reward, 2), 2.50)

        # 3 ticks off (distance=3) -> 12.5% ($1.25)
        self.assertEqual(calculate_discounted_reward(base_reward, 3), 1.25)

    def test_payoff_state_machine_prevents_yield_destruction(self):
        """CRITICAL TEST: Proves the Alabama scenario will NEVER cancel a discounted earner to hold cash."""
        # Current seat: Alabama (2 ticks off touch, base reward $4.00/day -> discounted $1.00/day)
        current_ticker = "KXSTATEBALLOTMEASURE-AL-A4"
        distance_ticks = 2
        base_reward = 4.00  # discounted = $1.00/day

        # Case A: Board is empty (no qualifying candidate markets)
        candidates_empty = []
        eval_a = evaluate_order_payoff(
            current_ticker=current_ticker,
            distance_ticks=distance_ticks,
            base_reward_daily_usd=base_reward,
            candidate_markets=candidates_empty,
        )
        # MUST BE HOLD! Canceling to cash would destroy $1.00/day passive yield.
        self.assertEqual(eval_a.action, OrderAction.HOLD)
        self.assertAlmostEqual(eval_a.ev_hold_daily_usd, 1.00, delta=0.01)

        # Case B: Inferior candidate exists ($0.50/day) -> STILL HOLD
        candidates_inferior = [{"ticker": "CAND1", "distance_ticks": 0, "base_reward_daily_usd": 0.50}]
        eval_b = evaluate_order_payoff(
            current_ticker=current_ticker,
            distance_ticks=distance_ticks,
            base_reward_daily_usd=base_reward,
            candidate_markets=candidates_inferior,
        )
        self.assertEqual(eval_b.action, OrderAction.HOLD)

        # Case C: Superior candidate exists ($3.00/day at touch) -> RECYCLE
        candidates_superior = [{"ticker": "CAND_TOP", "distance_ticks": 0, "base_reward_daily_usd": 3.00}]
        eval_c = evaluate_order_payoff(
            current_ticker=current_ticker,
            distance_ticks=distance_ticks,
            base_reward_daily_usd=base_reward,
            candidate_markets=candidates_superior,
            hurdle_multiplier=1.5,
        )
        self.assertEqual(eval_c.action, OrderAction.RECYCLE)
        self.assertEqual(eval_c.target_ticker, "CAND_TOP")

    def test_invariant_engine_enforces_venue_bounds(self):
        engine = self.engine

        # 1. Reject market order
        valid, violations, _ = engine.validate_market_order_proposal({
            "order_type": "market",
            "price": 0.05,
            "notional_usd": 20.00,
        })
        self.assertFalse(valid)
        self.assertTrue(any("Market/Taker" in v for v in violations))


        # 2. Reject spread crossing
        valid, violations, _ = engine.validate_market_order_proposal({
            "order_type": "limit",
            "cross_spread": True,
            "price": 0.05,
            "notional_usd": 20.00,
        })
        self.assertFalse(valid)
        self.assertTrue(any("Crossing the spread" in v for v in violations))

        # 3. Reject toxic middle band (0.50) without exception
        valid, violations, _ = engine.validate_market_order_proposal({
            "order_type": "limit",
            "price": 0.50,
            "notional_usd": 20.00,
        })
        self.assertFalse(valid)
        self.assertTrue(any("toxic mid-band" in v for v in violations))

        # 4. Reject allocation > $50.00
        valid, violations, _ = engine.validate_market_order_proposal({
            "order_type": "limit",
            "price": 0.05,
            "notional_usd": 75.00,
        })
        self.assertFalse(valid)
        self.assertTrue(any("exceeds per-market cap" in v for v in violations))

        # 5. Clean maker order at benign extreme (0.05) <= $50 -> PASS
        valid, violations, passes = engine.validate_market_order_proposal({
            "order_type": "limit",
            "cross_spread": False,
            "price": 0.05,
            "notional_usd": 40.00,
        })
        self.assertTrue(valid)
        self.assertEqual(len(violations), 0)


if __name__ == "__main__":
    unittest.main()
