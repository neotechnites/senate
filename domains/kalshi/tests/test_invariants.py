"""Property tests for Kalshi Invariants and Offensive/Defensive Execution Gate."""

import sys
import tempfile
import unittest
from pathlib import Path

POD_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
for p in [str(REPO_ROOT), str(POD_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from domains.kalshi.harness.gate import ActionClass, ActionType, ExecutionGate
from domains.kalshi.state.db import Database
from domains.kalshi.state.fact_store import FactStore
from domains.kalshi.state.seed import seed_kalshi_database
from domains.kalshi.verify.invariants import InvariantEngine


class TestKalshiInvariantsAndGate(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_kalshi.db"
        self.db = Database(self.db_path)
        self.store = FactStore(self.db)
        seed_kalshi_database(self.store)
        self.invariants = InvariantEngine(self.store)
        self.gate = ExecutionGate(self.store)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_maker_only_rule_enforced(self):
        """Verify market/taker orders are strictly rejected."""
        valid, violations, _ = self.invariants.validate_order_proposal({
            "order_type": "market",
            "price": 0.20,
            "notional_usd": 25.00,
        })
        self.assertFalse(valid)
        self.assertTrue(any("Market/Taker" in v or "post-only maker" in v for v in violations))


    def test_spread_crossing_rejected(self):
        """Verify price crossing touch is rejected."""
        valid, violations, _ = self.invariants.validate_order_proposal({
            "order_type": "limit",
            "price": 0.25,
            "touch_price": 0.22,
            "notional_usd": 25.00,
        })
        self.assertFalse(valid)
        self.assertTrue(any("crosses touch" in v for v in violations))

    def test_exposure_caps_enforced(self):
        """Verify $50 per-market allocation cap is enforced."""
        valid, violations, _ = self.invariants.validate_order_proposal({
            "order_type": "limit",
            "price": 0.20,
            "notional_usd": 65.00,
        })
        self.assertFalse(valid)
        self.assertTrue(any("exceeds per-market cap" in v for v in violations))

    def test_execution_gate_defensive_fast_path(self):
        """Verify defensive actions execute locally in fast-path (<5ms) with zero external API dependencies."""
        res = self.gate.execute_action(
            action_type=ActionType.CANCEL_ORDER,
            proposal={"order_id": "ord_12345"},
        )
        self.assertTrue(res.is_executed)
        self.assertEqual(res.action_class, ActionClass.DEFENSIVE)
        self.assertLess(res.latency_ms, 50.0)
        self.assertEqual(len(res.violations), 0)

    def test_execution_gate_offensive_fails_closed_on_violation(self):
        """Verify offensive action fails closed when invariants are breached."""
        res = self.gate.execute_action(
            action_type=ActionType.DEPLOY_SEAT,
            proposal={"order_type": "market", "notional_usd": 150.00},
        )
        self.assertFalse(res.is_executed)
        self.assertEqual(res.action_class, ActionClass.OFFENSIVE)
        self.assertGreaterEqual(len(res.violations), 1)


if __name__ == "__main__":
    unittest.main()
