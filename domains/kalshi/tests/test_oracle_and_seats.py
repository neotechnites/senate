"""Property tests for Oracle Balance Sync, Zero Seed Money Invariant, and Local N-Pricing."""

import json
import sys
import tempfile
import unittest
from unittest.mock import MagicMock
from pathlib import Path

POD_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
for p in [str(REPO_ROOT), str(POD_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from domains.kalshi.harness.gate import ActionType, ExecutionGate
from domains.kalshi.harness.oracle_sync import sync_kalshi_oracle
from domains.kalshi.harness.venue_client import KalshiVenueClient
from domains.kalshi.state.db import Database
from domains.kalshi.state.fact_store import FactStore
from domains.kalshi.state.models import ActiveOrder
from domains.kalshi.state.seed import seed_kalshi_database
from domains.kalshi.verify.statistics import price_n_hurdle


class TestKalshiOracleAndState(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_kalshi.db"
        self.db = Database(self.db_path)
        self.store = FactStore(self.db)
        seed_kalshi_database(self.store)
        self.gate = ExecutionGate(self.store)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_zero_seed_money_invariant(self):
        """CRITICAL: Proves seed_kalshi_database creates ZERO active orders and ZERO fabricated balances."""
        orders = self.store.list_active_orders()
        self.assertEqual(len(orders), 0, "INVARIANT BREACH: Seed file created active orders.")

        oracle_fact = self.store.get_fact("kalshi.oracle.balance")
        self.assertIsNone(oracle_fact, "INVARIANT BREACH: Seed file created unbacked oracle balance.")

        # Exactly 6 platform facts must exist
        facts = self.store.list_facts()
        self.assertEqual(len(facts), 6, f"Expected exactly 6 platform facts, got {len(facts)}")
        for f in facts:
            self.assertTrue(f.is_immutable)
            self.assertTrue(Path(f.source_artifact).exists(), f"Source artifact {f.source_artifact} missing on disk.")

    def test_oracle_sync_with_live_client(self):
        """Verify direct live venue client parsing and P&L arithmetic."""
        mock_client = MagicMock(spec=KalshiVenueClient)
        mock_client.fetch_balance.return_value = {
            "balance": 110000,          # $1,100.00
            "payout": 10000,            # $100.00
            "lifetime_deposits": 250000 # $2,500.00
        }

        ok, msg, fact = sync_kalshi_oracle(self.store, live_client=mock_client)
        self.assertTrue(ok)
        self.assertIsNotNone(fact)
        # P&L = 1100 + 100 - 2500 = -1300
        self.assertEqual(fact.value["cash_usd"], 1100.00)
        self.assertEqual(fact.value["open_positions_usd"], 100.00)
        self.assertEqual(fact.value["lifetime_pnl_usd"], -1300.00)
        self.assertEqual(fact.value["source_type"], "live_kalshi_api_authenticated")

    def test_oracle_sync_fails_closed_without_source(self):
        """Verify sync fails closed when no valid live client is supplied."""
        ok, msg, fact = sync_kalshi_oracle(self.store, live_client=None)
        self.assertFalse(ok)
        self.assertIn("No live venue balance fetched", msg)

    def test_order_placement_gate_validation(self):
        """Verify offensive gate validates proposal against caps and maker rules."""
        # 1. Valid proposal <= $50 cap
        p1 = {"order_type": "limit", "price": 0.20, "count": 100, "notional_usd": 20.00}
        res1 = self.gate.execute_action(ActionType.DEPLOY_SEAT, p1)
        self.assertTrue(res1.is_executed)

        # 2. Invalid proposal > $50 cap
        p2 = {"order_type": "limit", "price": 0.20, "count": 300, "notional_usd": 60.00}
        res2 = self.gate.execute_action(ActionType.DEPLOY_SEAT, p2)
        self.assertFalse(res2.is_executed)
        self.assertTrue(any("exceeds per-market cap" in v for v in res2.violations))

    def test_local_n_pricing_hurdles(self):
        """Verify Bailey & López de Prado statistical hurdles for domain research."""
        h1 = price_n_hurdle(1)
        self.assertAlmostEqual(h1.bonferroni_t_hurdle, 1.96, delta=0.01)

        h10 = price_n_hurdle(10)
        self.assertAlmostEqual(h10.bonferroni_t_hurdle, 2.81, delta=0.01)

        h45 = price_n_hurdle(45)
        self.assertAlmostEqual(h45.bonferroni_t_hurdle, 3.26, delta=0.01)


if __name__ == "__main__":
    unittest.main()
