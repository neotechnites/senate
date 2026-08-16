"""End-to-End CLI Smoke and Lifecycle Tests for The Senate Meta-Hub."""

import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from senate.interface.cli import main as senate_main


class TestSenateCLISmoke(unittest.TestCase):
    def test_cli_status(self):
        """Verify senate status runs with code 0."""
        rc = senate_main(["status"])
        self.assertEqual(rc, 0)

    def test_cli_domain_list(self):
        """Verify senate domain list runs with code 0."""
        rc = senate_main(["domain", "list"])
        self.assertEqual(rc, 0)

    def test_domain_lifecycle_scaffold_test_sync_delete(self):
        """CRITICAL: End-to-end lifecycle test for domain scaffolding, testing, sync, and deletion."""
        test_id = "test_smoke_pod"
        
        # 1. Create domain
        rc_create = senate_main(["domain", "create", test_id, "Smoke Test Pod", "--category", "software"])
        self.assertEqual(rc_create, 0)

        pod_dir = REPO_ROOT / "domains" / test_id
        self.assertTrue(pod_dir.exists())

        # 2. Run the newly scaffolded pod's tests — MUST PASS with 0 errors!
        res_test = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
            cwd=str(pod_dir),
            capture_output=True,
            text=True,
        )
        self.assertEqual(res_test.returncode, 0, f"Scaffolded pod tests failed: {res_test.stderr}")

        # 3. Pull telemetry via exported pod interface
        rc_sync = senate_main(["domain", "sync", test_id])
        self.assertEqual(rc_sync, 0)

        # 4. Delete domain
        rc_del = senate_main(["domain", "delete", test_id])
        self.assertEqual(rc_del, 0)
        self.assertFalse(pod_dir.exists())

        # 5. Verify ghost row is gone from Senate state
        from senate.state.fact_store import FactStore
        store = FactStore()
        proj = store.get_project_state(test_id)
        self.assertIsNone(proj, "Ghost row remained in Senate DB after domain delete.")


if __name__ == "__main__":
    unittest.main()
