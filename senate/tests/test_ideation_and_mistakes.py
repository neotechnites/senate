"""Unit and property tests for Standing Ideation Organ, Accrual Math, and Mistake Invariants."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from domains.kalshi.verify.accrual import compute_time_weighted_accrual
from senate.models.adversary import AdversarialAuditResult, MultiModelAdversary
from senate.models.ideation_engine import StandingIdeator
from senate.state.db import Database
from senate.state.mistake_enforcer import HISTORICAL_MISTAKES, seed_mistakes_into_db


class TestIdeationAndMistakeInvariants(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_senate_ideation.db"
        self.db = Database(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_time_weighted_accrual_calculation(self):
        """CRITICAL: Proves accrual math uses exact seat-hours and escrow dollars, preventing chat rate errors."""
        # 163 cycles of 5-min intervals = 13.58 hours on $183.37 average escrow with $10.84 realized credit
        res = compute_time_weighted_accrual(
            ticker="KXSTATEBALLOTMEASURE-NC-A2",
            seat_hours=13.58,
            escrow_usd=183.37,
            realized_credit_usd=10.84,
        )
        self.assertAlmostEqual(res.effective_daily_per_100_usd, 10.46, delta=0.05)
        self.assertAlmostEqual(res.hourly_rate_usd, 0.798, delta=0.01)

        # Negative or zero denominators must raise ValueError
        with self.assertRaises(ValueError):
            compute_time_weighted_accrual(ticker="TEST", seat_hours=0.0, escrow_usd=100.0, realized_credit_usd=5.0)

        with self.assertRaises(ValueError):
            compute_time_weighted_accrual(ticker="TEST", seat_hours=10.0, escrow_usd=0.0, realized_credit_usd=5.0)

    def test_mistake_invariants_seeded_in_sqlite(self):
        """CRITICAL: Proves all 10 historical process failures are seeded as compiled impossible invariants."""
        with self.db.get_connection() as conn:
            count = seed_mistakes_into_db(conn)
            self.assertEqual(count, 10)


            cur = conn.execute("SELECT COUNT(*) as c FROM mistake_invariants WHERE status = 'COMPILED_IMPOSSIBLE'")
            row = cur.fetchone()
            self.assertEqual(row["c"], 10)

    def test_standing_ideation_organ_persists_survivors_and_graveyard(self):
        """CRITICAL: Proves Multi-Model Ideator submits to adversary and saves to SQLite registry."""
        mock_adversary = MagicMock(spec=MultiModelAdversary)
        
        # Test 1: Flawed hypothesis killed by adversary -> GRAVEYARD
        mock_adversary.audit_proposal.return_value = AdversarialAuditResult(
            is_approved=False,
            risk_score=8,
            auditor_model="gemini-2.5-pro",
            auditor_provider="google",
            violations=["Violates terminal book evacuation curfew"],
            critique="Thin target LIP pocket lacks absorption during book sweeps.",
            raw_response="{}",
        )

        ideator = StandingIdeator(self.db, mock_adversary)
        rec1 = ideator.submit_and_audit_idea(
            domain="kalshi",
            hypothesis="Quote thin-target LIP pockets 3h before window close",
            kill_test_spec={"test": "measure_sweeps_below_250ct"},
        )
        self.assertEqual(rec1.status, "GRAVEYARD")
        self.assertEqual(rec1.adversary_status, "KILLED")

        # Test 2: Sound hypothesis approved by adversary -> VALIDATED
        mock_adversary.audit_proposal.return_value = AdversarialAuditResult(
            is_approved=True,
            risk_score=2,
            auditor_model="gemini-2.5-pro",
            auditor_provider="google",
            violations=[],
            critique="Sustained touch depth > 250ct provides robust absorption.",
            raw_response="{}",
        )

        rec2 = ideator.submit_and_audit_idea(
            domain="kalshi",
            hypothesis="Filter seats where rival touch depth > 250ct to minimize dislocation risk",
            kill_test_spec={"test": "verify_dislocation_frequency_at_depth"},
        )
        self.assertEqual(rec2.status, "VALIDATED")
        self.assertEqual(rec2.adversary_status, "SURVIVED")

        # Verify both are queryable from SQLite
        all_ideas = ideator.list_ideas()
        self.assertEqual(len(all_ideas), 2)
        graveyard = ideator.list_ideas(status="GRAVEYARD")
        self.assertEqual(len(graveyard), 1)
        validated = ideator.list_ideas(status="VALIDATED")
        self.assertEqual(len(validated), 1)


if __name__ == "__main__":
    unittest.main()
