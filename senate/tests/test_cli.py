"""End-to-end CLI command tests for The Senate."""

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


from senate.interface.cli import main
from senate.state.db import Database
from senate.state.fact_store import FactStore


class TestSenateCLI(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "cli_test.db"
        # Monkeypatch DEFAULT_DB_PATH for isolated test run
        import senate.state.db
        self.orig_path = senate.state.db.DEFAULT_DB_PATH
        senate.state.db.DEFAULT_DB_PATH = self.db_path

    def tearDown(self):
        import senate.state.db
        senate.state.db.DEFAULT_DB_PATH = self.orig_path
        self.temp_dir.cleanup()

    def run_cli(self, args_list):
        f = io.StringIO()
        with redirect_stdout(f):
            code = main(args_list)
        return code, f.getvalue()

    def test_cli_lifecycle(self):
        # 1. Seed
        code, out = self.run_cli(["seed"])
        self.assertEqual(code, 0)
        self.assertIn("seeded successfully", out)

        # 2. Status
        code, out = self.run_cli(["status"])
        self.assertEqual(code, 0)
        self.assertIn("THE SENATE — SYSTEM STATUS", out)
        self.assertIn("Verified Sovereign Laws", out)

        # 3. Fact Get
        code, out = self.run_cli(["fact", "get", "senate.constitution.statements"])
        self.assertEqual(code, 0)
        self.assertIn("statement_1_goal", out)


        # 4. Trials Log & Summary
        code, out = self.run_cli(["trials", "log", "nestor", "test_config_v1", "--count", "5"])
        self.assertEqual(code, 0)
        self.assertIn("Logged trial", out)

        code, out = self.run_cli(["trials", "summary"])
        self.assertEqual(code, 0)
        self.assertIn("Global Trial Count N = 5", out)

        # 5. Verify Payoff (Provisional call)
        code, out = self.run_cli([
            "verify-payoff",
            "--ticker", "KXSTATEBALLOTMEASURE-AL-A4",
            "--dist", "2",
            "--reward", "4.00",
        ])
        self.assertEqual(code, 0)
        self.assertIn("HOLD", out)
        self.assertIn("UNSOURCED / SELF-REPORTED", out)
        self.assertIn("$1.0000/day", out)

        # 6. Verify Payoff (Venue Sourced call)
        source_json = Path(self.temp_dir.name) / "venue_sample.json"
        source_json.write_text(json.dumps({
            "order": {"ticker": "KXSTATEBALLOTMEASURE-AL-A4", "price": 0.20},
            "book": {"touch_price": 0.22, "tick_size": 0.01, "pool_daily_reward": 31.10, "qualifying_sides": 2, "our_share_pct": 0.25}
        }))
        code, out = self.run_cli(["verify-payoff", "--source-file", str(source_json)])
        self.assertEqual(code, 0)
        self.assertIn("FILE-SOURCED (VENUE RECORD)", out)
        self.assertIn("HOLD", out)




if __name__ == "__main__":
    unittest.main()
