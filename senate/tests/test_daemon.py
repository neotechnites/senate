"""Unit tests for Autonomous Cadence Daemons (Senate & Kalshi)."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from domains.kalshi.harness.cadence_daemon import KalshiCadenceDaemon
from domains.kalshi.state.fact_store import FactStore as KalshiFactStore
from domains.kalshi.state.db import Database as KalshiDatabase
from senate.harness.daemon import SenateCadenceDaemon
from senate.state.fact_store import FactStore as SenateFactStore
from senate.state.db import Database as SenateDatabase


class TestCadenceDaemons(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.senate_db = SenateDatabase(Path(self.temp_dir.name) / "test_senate.db")
        self.kalshi_db = KalshiDatabase(Path(self.temp_dir.name) / "test_kalshi.db")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_senate_cadence_daemon_runs_and_logs(self):
        """Verify Senate cadence daemon executes cycle and records to SQLite lane_runs."""
        daemon = SenateCadenceDaemon(interval_seconds=1, max_cycles=1)
        daemon.store = SenateFactStore(self.senate_db)
        
        res = daemon.run_cycle(1)
        self.assertEqual(res["cycle"], 1)
        self.assertGreater(len(res["actions_taken"]), 0)

        with self.senate_db.get_connection() as conn:
            cur = conn.execute("SELECT COUNT(*) as c FROM lane_runs WHERE lane = 'senate_cadence_daemon'")
            row = cur.fetchone()
            self.assertEqual(row["c"], 1)

    def test_kalshi_cadence_daemon_runs_and_logs(self):
        """Verify Kalshi cadence daemon scans families and records to SQLite lane_runs."""
        daemon = KalshiCadenceDaemon(interval_seconds=1, max_cycles=1)
        daemon.store = KalshiFactStore(self.kalshi_db)

        res = daemon.run_cycle(1)
        self.assertEqual(res["cycle"], 1)
        self.assertTrue(any("Census Scan" in a for a in res["actions_taken"]))

        with self.kalshi_db.get_connection() as conn:
            cur = conn.execute("SELECT COUNT(*) as c FROM lane_runs WHERE lane = 'kalshi_cadence_daemon'")
            row = cur.fetchone()
            self.assertEqual(row["c"], 1)


if __name__ == "__main__":
    unittest.main()
