"""Unit tests for Autonomous Cadence Daemons (Senate Core Framework)."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from senate.harness.daemon import SenateCadenceDaemon
from senate.state.fact_store import FactStore as SenateFactStore
from senate.state.db import Database as SenateDatabase
from senate.state.models import Goal, ProjectState


class TestSenateCadenceDaemon(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.senate_db = SenateDatabase(Path(self.temp_dir.name) / "test_senate.db")
        self.store = SenateFactStore(self.senate_db)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_senate_cadence_daemon_runs_and_logs(self):
        """Verify Senate cadence daemon executes cycle and records to SQLite lane_runs offline."""
        self.store.save_project_state(
            ProjectState(
                project_id="test_pod",
                name="Test Pod",
                status="ACTIVE",
                variables={"mission": "Test mission", "category": "software"},
            )
        )
        self.store.save_goal(
            Goal(
                goal_id="test_goal",
                title="Test Goal",
                category="software",
                target_metric="usd_day",
                target_value=100.0,
                current_value=0.0,
                unit="USD/day",
            )
        )

        daemon = SenateCadenceDaemon(interval_seconds=1, max_cycles=1, fact_store=self.store)
        
        res = daemon.run_cycle(1)
        self.assertEqual(res["cycle"], 1)
        self.assertGreater(len(res["actions_taken"]), 0)

        with self.senate_db.get_connection() as conn:
            cur = conn.execute("SELECT COUNT(*) as c FROM lane_runs WHERE lane = 'senate_cadence_daemon'")
            row = cur.fetchone()
            self.assertEqual(row["c"], 1)


if __name__ == "__main__":
    unittest.main()

