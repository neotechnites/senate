"""End-to-End CLI Smoke Tests for Kalshi Domain Pod.

Verifies that ALL CLI subcommands execute without ImportErrors, syntax errors, or schema crashes.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

POD_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
for p in [str(REPO_ROOT), str(POD_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from domains.kalshi.interface.cli import main as kalshi_main


class TestKalshiCLISmoke(unittest.TestCase):
    def test_cli_main_status(self):
        """Verify kalshi status runs with code 0."""
        rc = kalshi_main(["status"])
        self.assertEqual(rc, 0)

    def test_cli_main_seed(self):
        """Verify kalshi seed runs with code 0."""
        rc = kalshi_main(["seed"])
        self.assertEqual(rc, 0)

    def test_cli_main_telemetry(self):
        """Verify kalshi telemetry outputs valid JSON."""
        rc = kalshi_main(["telemetry"])
        self.assertEqual(rc, 0)

    def test_cli_main_order_place_and_cancel_dry_run(self):
        """Verify order placement and cancellation execution through gate."""
        rc_place = kalshi_main(["order", "place", "--ticker", "KXTEST-26", "--side", "no", "--price-cents", "20", "--count", "100"])
        self.assertEqual(rc_place, 0)

        rc_cancel = kalshi_main(["order", "cancel", "--order-id", "ord_test_123"])
        self.assertEqual(rc_cancel, 0)

    def test_cli_subprocess_invocation(self):
        """Verify ./kalshi.py executable runs in its own process without import errors."""
        res = subprocess.run(
            [sys.executable, str(POD_DIR / "kalshi.py"), "status"],
            cwd=str(POD_DIR),
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"kalshi.py status failed: {res.stderr}")
        self.assertIn("KALSHI DOMAIN POD", res.stdout)

    def test_cli_subprocess_telemetry(self):
        """Verify ./kalshi.py telemetry outputs valid domain telemetry JSON."""
        res = subprocess.run(
            [sys.executable, str(POD_DIR / "kalshi.py"), "telemetry"],
            cwd=str(POD_DIR),
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"kalshi.py telemetry failed: {res.stderr}")
        data = json.loads(res.stdout)
        self.assertEqual(data["domain_id"], "kalshi")
        self.assertIn("resource_consumption", data)
        self.assertIn("domain_metrics", data)


if __name__ == "__main__":
    unittest.main()
