"""Unit and property tests for Fundamental Base Rates, 24h Curfew, and Total Budget Gates."""

import sys
import tempfile
import unittest
from pathlib import Path

POD_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
for p in [str(REPO_ROOT), str(POD_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from domains.kalshi.harness.gate import ActionType, ExecutionGate
from domains.kalshi.harness.census_scanner import CensusScanner
from domains.kalshi.state.db import Database
from domains.kalshi.state.fact_store import FactStore
from domains.kalshi.state.models import ActiveOrder, Fact
from domains.kalshi.state.seed import seed_kalshi_database
from domains.kalshi.verify.base_rates import evaluate_fundamental_base_rate
from domains.kalshi.verify.invariants import InvariantEngine


class TestBaseRatesCurfewAndBudget(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_safety.db"
        self.db = Database(self.db_path)
        self.store = FactStore(self.db)
        seed_kalshi_database(self.store)
        self.gate = ExecutionGate(self.store)
        self.engine = InvariantEngine(self.store)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_fundamental_base_rate_rejects_toxic_no_on_ballots(self):
        """CRITICAL: Proves selling cheap NO on high-probability state ballot bond/fund measures is REJECTED."""
        # Proposal: Sell NO @ 22c on 911 emergency fund amendment
        is_safe, violation, rule = evaluate_fundamental_base_rate(
            ticker="KXSTATEBALLOTMEASURE-GA-A2",
            side="no",
            price=0.22,
            market_title="Will Amendment 2 pass?",
            market_subtitle="9-1-1 Fund Amendment",
        )
        self.assertFalse(is_safe)
        self.assertIn("Fundamental Base-Rate Breach", violation)
        self.assertIn("76%", violation)

        # Gate execution must FAIL CLOSED
        proposal = {
            "ticker": "KXSTATEBALLOTMEASURE-GA-A2",
            "side": "no",
            "price": 0.22,
            "count": 100,
            "notional_usd": 22.00,
            "title": "Will Amendment 2 pass?",
            "subtitle": "9-1-1 Fund Amendment",
        }
        res = self.gate.execute_action(ActionType.DEPLOY_SEAT, proposal)
        self.assertFalse(res.is_executed)
        self.assertTrue(any("Fundamental Base-Rate Breach" in v for v in res.violations))

    def test_terminal_window_curfew_rejects_sub_24h_entry(self):
        """CRITICAL: Proves order entry inside 24h of window expiry is strictly REJECTED (anti-evacuation)."""
        proposal = {
            "ticker": "KXFEDFUNDSYEAR-26-HOLD",
            "side": "yes",
            "price": 0.20,
            "count": 100,
            "notional_usd": 20.00,
            "hours_to_window_expiry": 12.5,  # < 24h
        }
        valid, violations, _ = self.engine.validate_order_proposal(proposal)
        self.assertFalse(valid)
        self.assertTrue(any("Terminal window curfew breached" in v for v in violations))

        # At >= 24h margin -> Pass
        proposal["hours_to_window_expiry"] = 36.0
        valid2, violations2, _ = self.engine.validate_order_proposal(proposal)
        self.assertTrue(valid2)

    def test_total_portfolio_budget_cap_includes_positions_and_resting(self):
        """CRITICAL: Proves fills into positions DO NOT create headroom; total capital <= $250 is enforced."""
        # 1. Simulate $137.27 locked in positions in oracle balance
        self.store.set_fact(Fact(
            key="kalshi.oracle.balance",
            domain="kalshi",
            value={
                "cash_usd": 850.00,
                "open_positions_usd": 137.27,
                "lifetime_deposits_usd": 1000.00,
                "timestamp": "2026-08-15T12:00:00Z",
            },
            source_artifact="live_test",
            is_immutable=False,
        ))

        # 2. Add 2 resting orders totaling $99.88 collateral
        self.store.save_order(ActiveOrder(
            order_id="ord1", ticker="T1", side="yes", price=0.22, count=227, collateral_usd=49.94, status="RESTING", lane="autoseat"
        ))
        self.store.save_order(ActiveOrder(
            order_id="ord2", ticker="T2", side="yes", price=0.22, count=227, collateral_usd=49.94, status="RESTING", lane="autoseat"
        ))

        # Total currently deployed = $137.27 (positions) + $99.88 (resting) = $237.15
        # Attempting to deploy another $49.94 (Total = $287.09 > $250 cap) MUST BE REJECTED!
        over_proposal = {
            "ticker": "KXFEDFUNDSYEAR-26-HOLD",
            "side": "yes",
            "price": 0.22,
            "count": 227,
            "notional_usd": 49.94,
        }
        valid, violations, _ = self.engine.validate_order_proposal(over_proposal)
        self.assertFalse(valid)
        self.assertTrue(any("exceeds total portfolio budget" in v for v in violations))

    def test_multi_family_census_scanner(self):
        """Verify multi-family scanner classifies families across 7 days."""
        scanner = CensusScanner()
        opps = scanner.scan_family_opportunities()
        self.assertGreaterEqual(len(opps), 5)
        families = [o["family"] for o in opps]
        self.assertIn("KXFEDFUNDSYEAR", families)
        self.assertIn("KXUSCPIYEAR", families)
        self.assertIn("KXSTATEBALLOTMEASURE", families)


if __name__ == "__main__":
    unittest.main()
