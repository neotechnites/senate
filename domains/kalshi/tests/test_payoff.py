"""Property tests for Kalshi Payoff Engine and Yield Preservation."""

import sys
import tempfile
import unittest
from pathlib import Path

POD_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
for p in [str(REPO_ROOT), str(POD_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from domains.kalshi.state.db import Database
from domains.kalshi.state.fact_store import FactStore
from domains.kalshi.state.seed import seed_kalshi_database
from domains.kalshi.verify.payoff import (
    OrderAction,
    calculate_discounted_reward,
    evaluate_order_payoff,
    evaluate_order_payoff_from_venue_record,
)


class TestKalshiPayoffProperties(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_kalshi.db"
        self.db = Database(self.db_path)
        self.store = FactStore(self.db)
        seed_kalshi_database(self.store)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_discounted_reward_decay(self):
        """Verify 50% exponential distance decay."""
        # 0 ticks = $10.00
        self.assertAlmostEqual(calculate_discounted_reward(10.0, 0, fact_store=self.store), 10.00)
        # 1 tick = $5.00
        self.assertAlmostEqual(calculate_discounted_reward(10.0, 1, fact_store=self.store), 5.00)
        # 2 ticks = $2.50
        self.assertAlmostEqual(calculate_discounted_reward(10.0, 2, fact_store=self.store), 2.50)
        # 3 ticks = $1.25
        self.assertAlmostEqual(calculate_discounted_reward(10.0, 3, fact_store=self.store), 1.25)

    def test_alabama_yield_preservation(self):
        """CRITICAL: Proves an off-touch earner is NEVER cancelled to hold cash."""
        # Seat 2 ticks off touch earning $1.00/day
        decision = evaluate_order_payoff(
            current_ticker="KXSTATEBALLOTMEASURE-AL-A4",
            distance_ticks=2,
            base_reward_daily_usd=4.00,
            candidate_markets=[],
            fact_store=self.store,
        )
        self.assertEqual(decision.action, OrderAction.HOLD)
        self.assertAlmostEqual(decision.ev_hold_daily_usd, 1.00, delta=0.01)
        self.assertIn("earning $1.00/day", decision.reason)

    def test_recycle_requires_1_5x_hurdle_and_churn_discount(self):
        """Verify that recycling requires candidate to beat hold EV by 1.5x after 15% churn haircut."""
        # Current seat earns $2.00/day. 1.5x hurdle = $3.00/day net required.
        # Candidate 1: $3.20 raw * 0.85 = $2.72 net (FAILS hurdle -> HOLD)
        cand1 = [{"ticker": "CAND1", "distance_ticks": 0, "base_reward_daily_usd": 3.20}]
        d1 = evaluate_order_payoff("SEAT_A", 0, 2.00, cand1, fact_store=self.store)
        self.assertEqual(d1.action, OrderAction.HOLD)

        # Candidate 2: $4.00 raw * 0.85 = $3.40 net (BEATS hurdle -> RECYCLE)
        cand2 = [{"ticker": "CAND2", "distance_ticks": 0, "base_reward_daily_usd": 4.00}]
        d2 = evaluate_order_payoff("SEAT_A", 0, 2.00, cand2, fact_store=self.store)
        self.assertEqual(d2.action, OrderAction.RECYCLE)
        self.assertEqual(d2.target_ticker, "CAND2")

    def test_venue_sourced_payoff_resolution(self):
        """Verify authentic venue order and book JSON resolution."""
        order_record = {
            "ticker": "KXSTATEBALLOTMEASURE-AL-A4",
            "price": 0.20,
            "side": "no",
        }
        market_book = {
            "touch_price": 0.22,
            "tick_size": 0.01,
            "pool_daily_reward": 32.00,
            "qualifying_sides": 2,
            "our_share_pct": 0.25,
        }
        # base reward = 32 / 2 * 0.25 = $4.00/day
        # distance = 2 ticks -> EV(Hold) = $1.00/day
        decision = evaluate_order_payoff_from_venue_record(
            order_record=order_record,
            market_book=market_book,
            fact_store=self.store,
        )
        self.assertEqual(decision.action, OrderAction.HOLD)
        self.assertTrue(decision.metadata["is_venue_sourced"])
        self.assertEqual(decision.metadata["distance_ticks"], 2)


if __name__ == "__main__":
    unittest.main()
