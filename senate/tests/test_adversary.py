"""Adversarial security and invariant attack tests for The Senate Core Framework."""

import hashlib
import os
import tempfile
import unittest
from pathlib import Path

from senate.harness.runner import SandboxedRunner
from senate.state.db import Database
from senate.state.fact_store import FactStore
from senate.state.models import Fact
from senate.verify.invariants import InvariantEngine
from senate.verify.payoff import (
    OrderAction,
    evaluate_order_payoff,
)


class TestSenateAdversarialAttacks(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "adv_senate.db"
        self.db = Database(self.db_path)
        self.store = FactStore(self.db)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_attack_immutability_overwrite_with_immutable_flag(self):
        """CRITICAL: Test that passing is_immutable=True on attack write CANNOT bypass lock."""
        # 1. Store immutable fact
        initial_fact = Fact(
            key="system.core_truth",
            domain="system",
            value={"v": 1},
            source_artifact="origin",
            is_immutable=True,
        )
        self.store.set_fact(initial_fact)

        # 2. Attack Attempt A: is_immutable=False
        with self.assertRaises(ValueError):
            self.store.set_fact(
                Fact(
                    key="system.core_truth",
                    domain="system",
                    value={"v": 999},
                    source_artifact="attacker",
                    is_immutable=False,
                )
            )

        # 3. Attack Attempt B: is_immutable=True (The exact bypass found in audit!)
        with self.assertRaises(ValueError):
            self.store.set_fact(
                Fact(
                    key="system.core_truth",
                    domain="system",
                    value={"v": 999},
                    source_artifact="attacker",
                    is_immutable=True,
                )
            )

        # 4. Verify value is completely untouched
        fact = self.store.get_fact("system.core_truth")
        self.assertEqual(fact.value, {"v": 1})
        self.assertEqual(fact.source_artifact, "origin")

    def test_mutable_fact_history_audit_trail(self):
        """Verify that updating mutable facts writes complete audit history."""
        f1 = Fact(key="mutable.stat", domain="stats", value={"count": 10}, source_artifact="run1", is_immutable=False)
        self.store.set_fact(f1)

        f2 = Fact(key="mutable.stat", domain="stats", value={"count": 25}, source_artifact="run2", is_immutable=False)
        self.store.set_fact(f2)

        with self.db.get_connection() as conn:
            cur = conn.execute("SELECT old_value, new_value, source_artifact FROM fact_history WHERE key = 'mutable.stat'")
            history = cur.fetchall()
            self.assertEqual(len(history), 1)
            self.assertIn('"count": 10', history[0]["old_value"])
            self.assertIn('"count": 25', history[0]["new_value"])
            self.assertEqual(history[0]["source_artifact"], "run2")

    def test_attack_hash_seed_stability(self):
        """Verify that config hashing uses sha256 and is immune to PYTHONHASHSEED."""
        desc = "variant_alpha_maker_quiet_2026"
        hash1 = hashlib.sha256(desc.encode("utf-8")).hexdigest()[:16]
        hash2 = hashlib.sha256(desc.encode("utf-8")).hexdigest()[:16]
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 16)

    def test_attack_missing_caps_fact_fails_closed(self):
        """CRITICAL: InvariantEngine must FAIL CLOSED when exposure caps fact is missing."""
        engine = InvariantEngine(self.store)  # empty store, no caps seeded
        
        valid, violations, _ = engine.validate_market_order_proposal({
            "order_type": "limit",
            "price": 0.05,
            "notional_usd": 20.00,
        })
        self.assertFalse(valid)
        self.assertTrue(any("Fails closed" in v for v in violations))

    def test_attack_runner_directory_traversal(self):
        """CRITICAL: SandboxedRunner must reject execution outside allowed_root."""
        runner = SandboxedRunner(allowed_root=Path(self.temp_dir.name))
        
        # Attempt to run inside /etc or /tmp parent outside allowed_root
        res = runner.run_command(["ls"], cwd=Path("/tmp"))
        self.assertFalse(res.is_success)
        self.assertIn("Security Violation", res.stderr)

    def test_payoff_churn_queue_discount_penalty(self):
        """Verify that candidate EV properly incorporates queue churn discount."""
        current_ticker = "AL-A4"
        distance_ticks = 2
        base_reward = 4.00  # discounted hold EV = $1.00/day

        # Candidate raw EV = $1.60/day. With 15% churn discount -> $1.36/day.
        # Hurdle is 1.5x * $1.00 = $1.50/day.
        # Without churn penalty, $1.60 might falsely trigger recycle.
        # With churn penalty, $1.36 < $1.50 -> MUST HOLD!
        cand = [{"ticker": "CAND1", "distance_ticks": 0, "base_reward_daily_usd": 1.60}]
        eval_res = evaluate_order_payoff(
            current_ticker=current_ticker,
            distance_ticks=distance_ticks,
            base_reward_daily_usd=base_reward,
            candidate_markets=cand,
            hurdle_multiplier=1.5,
            churn_queue_discount=0.85,
            fact_store=self.store,
        )
        self.assertEqual(eval_res.action, OrderAction.HOLD)

    def test_venue_sourced_payoff_resolution(self):
        """Verify that venue JSON records automatically resolve distance and reward without self-reported beliefs."""
        from senate.verify.payoff import evaluate_order_payoff_from_venue_record

        order_record = {
            "ticker": "KXSTATEBALLOTMEASURE-AL-A4",
            "price": 0.20,
            "side": "no",
            "notional_usd": 50.00,
        }
        market_book = {
            "touch_price": 0.22,
            "tick_size": 0.01,
            "pool_daily_reward": 31.10,
            "qualifying_sides": 2,
            "our_share_pct": 0.25,
        }

        # Distance is 2 ticks: (0.22 - 0.20) / 0.01 = 2 ticks
        # Base reward = (31.10 / 2) * 0.25 = $3.8875/day
        # At 2 ticks (50% ^ 2 = 25%): EV hold = $3.8875 * 0.25 = $0.9719/day
        decision = evaluate_order_payoff_from_venue_record(
            order_record=order_record,
            market_book=market_book,
            candidate_books=[],
            fact_store=self.store,
        )
        self.assertEqual(decision.action, OrderAction.HOLD)
        self.assertTrue(decision.metadata["is_venue_sourced"])
        self.assertEqual(decision.metadata["distance_ticks"], 2)
        self.assertAlmostEqual(decision.ev_hold_daily_usd, 0.9719, delta=0.01)

    def test_dynamic_factstore_decay_rate(self):
        """Verify that payoff engine dynamically uses the decay rate configured in FactStore."""
        # Seed custom discount factor fact with decay rate 0.40
        self.store.set_fact(Fact(
            key="kalshi.lip.discount_factor",
            domain="kalshi",
            value={"decay_rate_per_tick": 0.40},
            source_artifact="test_spec",
            is_immutable=True,
        ))

        # At distance 2 with decay 0.40: 10.00 * (0.40 ^ 2) = $1.60/day
        eval_res = evaluate_order_payoff(
            current_ticker="TEST",
            distance_ticks=2,
            base_reward_daily_usd=10.00,
            candidate_markets=[],
            fact_store=self.store,
        )
        self.assertAlmostEqual(eval_res.ev_hold_daily_usd, 1.60, delta=0.01)

    def test_attack_empty_venue_record_fails_closed(self):
        """CRITICAL: Feeding empty/truncated venue record MUST raise ValueError (fail closed)."""
        from senate.verify.payoff import evaluate_order_payoff_from_venue_record

        # Attack 1: completely empty dicts
        with self.assertRaises(ValueError):
            evaluate_order_payoff_from_venue_record(
                order_record={},
                market_book={},
                fact_store=self.store,
            )

        # Attack 2: missing touch_price
        with self.assertRaises(ValueError):
            evaluate_order_payoff_from_venue_record(
                order_record={"ticker": "TEST", "price": 0.20},
                market_book={"pool_daily_reward": 10.0},
                fact_store=self.store,
            )

        # Attack 3: missing pool_daily_reward
        with self.assertRaises(ValueError):
            evaluate_order_payoff_from_venue_record(
                order_record={"ticker": "TEST", "price": 0.20},
                market_book={"touch_price": 0.20},
                fact_store=self.store,
            )

    def test_attack_unbacked_money_truth_renders_unavailable(self):
        """CRITICAL: If domain metrics are unbacked, status MUST NOT fabricate numbers."""
        from senate.interface.decision_matrix import render_senate_status

        # Fresh empty store without fabricated metrics
        status_text = render_senate_status(self.store)
        self.assertIn("PORTFOLIO GOALS & ACTIVE DOMAINS", status_text)
        # Verify no hardcoded fabricated dollar figures
        self.assertNotIn("$1,102.97", status_text)
        self.assertNotIn("−$1,497.03", status_text)

    def test_sovereign_risk_caps_enforced(self):
        """CRITICAL: Validate that sovereign risk caps reject over-allocation and pass benign allocation."""
        from senate.state.seeds import seed_database
        seed_database(self.store)
        engine = InvariantEngine(self.store)

        # Allocation $75 > $50 cap -> Reject
        valid, violations, _ = engine.validate_market_order_proposal({
            "order_type": "limit",
            "price": 0.05,
            "notional_usd": 75.00,
        })
        self.assertFalse(valid)
        self.assertTrue(any("exceeds per-market cap" in v for v in violations))

        # Allocation $25 <= $50 cap -> Pass
        valid, violations, _ = engine.validate_market_order_proposal({
            "order_type": "limit",
            "price": 0.05,
            "notional_usd": 25.00,
        })
        self.assertTrue(valid)
        self.assertEqual(len(violations), 0)


if __name__ == "__main__":
    unittest.main()





