"""Unit tests for Senate Tool Harness."""

import sys
import unittest
from senate.harness.runner import SandboxedRunner
from senate.harness.schema import ToolExecutionResult


class TestToolHarness(unittest.TestCase):
    def setUp(self):
        self.runner = SandboxedRunner(default_timeout_s=5.0)

    def test_run_command_success(self):
        result = self.runner.run_command([sys.executable, "-c", "print('hello from sandbox')"])
        self.assertTrue(result.is_success)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("hello from sandbox", result.stdout)
        self.assertFalse(result.timed_out)

    def test_run_command_failure_captured(self):
        result = self.runner.run_command([sys.executable, "-c", "import sys; sys.stderr.write('fatal error'); sys.exit(2)"])
        self.assertFalse(result.is_success)
        self.assertEqual(result.exit_code, 2)
        self.assertIn("fatal error", result.stderr)

    def test_run_command_timeout_enforced(self):
        # Run a sleep longer than 1.0s timeout
        result = self.runner.run_command(
            [sys.executable, "-c", "import time; time.sleep(3.0)"],
            timeout_s=0.5,
        )
        self.assertFalse(result.is_success)
        self.assertTrue(result.timed_out)
        self.assertEqual(result.exit_code, -1)


if __name__ == "__main__":
    unittest.main()
