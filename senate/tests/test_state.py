"""Unit and property tests for Senate State Engine."""

import os
import tempfile
import unittest
from pathlib import Path

from senate.state.db import Database
from senate.state.fact_store import FactStore
from senate.state.models import Fact, Hypothesis, ProjectState, Trial
from senate.state.seeds import seed_database


class TestStateEngine(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_senate.db"
        self.db = Database(self.db_path)
        self.store = FactStore(self.db)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_database_initialization(self):
        self.assertTrue(self.db_path.exists())
        with self.db.get_connection() as conn:
            cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {r[0] for r in cur.fetchall()}
            self.assertIn("facts", tables)
            self.assertIn("hypotheses", tables)
            self.assertIn("trials_ledger", tables)
            self.assertIn("project_state", tables)

    def test_facts_crud_and_immutability(self):
        # Create fact
        fact = Fact(
            key="kalshi.test_fee",
            domain="kalshi",
            value={"maker": 0.0, "taker": 0.07},
            source_artifact="test_doc",
            is_immutable=True,
        )
        self.store.set_fact(fact)

        # Read fact
        retrieved = self.store.get_fact("kalshi.test_fee")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.key, "kalshi.test_fee")
        self.assertEqual(retrieved.value["taker"], 0.07)
        self.assertTrue(retrieved.is_immutable)

        # Overwriting immutable fact with non-immutable must fail
        f2 = Fact(
            key="kalshi.test_fee",
            domain="kalshi",
            value={"maker": 0.05},
            source_artifact="hacked_doc",
            is_immutable=False,
        )
        with self.assertRaises(ValueError):
            self.store.set_fact(f2)

        # Deleting immutable fact must fail silently / return False
        deleted = self.store.delete_fact("kalshi.test_fee")
        self.assertFalse(deleted)
        self.assertIsNotNone(self.store.get_fact("kalshi.test_fee"))

    def test_seed_database(self):
        seed_database(self.store)
        facts = self.store.list_facts()
        self.assertGreaterEqual(len(facts), 2)
        
        # Verify Senate Sovereign Constitution is present
        const = self.store.get_fact("senate.constitution.statements")
        self.assertIsNotNone(const)
        self.assertIn("statement_1_goal", const.value)


    def test_trials_ledger(self):
        self.store.log_trial(Trial(project="nestor", config_hash="sha1", description="variant 1", count=5))
        self.store.log_trial(Trial(project="nestor", config_hash="sha2", description="variant 2", count=10))
        self.store.log_trial(Trial(project="polyus", config_hash="sha3", description="poly 1", count=2))

        per_proj, total = self.store.get_trial_counts()
        self.assertEqual(per_proj["nestor"], 15)
        self.assertEqual(per_proj["polyus"], 2)
        self.assertEqual(total, 17)


if __name__ == "__main__":
    unittest.main()
