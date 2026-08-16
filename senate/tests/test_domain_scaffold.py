"""Unit and integration tests for Domain Pod scaffolding in The Senate."""

import shutil
import tempfile
import unittest
from pathlib import Path

import senate.scaffold.domain_builder as builder
from senate.scaffold.domain_builder import list_domain_pods, scaffold_domain_pod
from senate.state.db import Database
from senate.state.fact_store import FactStore


class TestDomainScaffolding(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_senate.db"
        self.db = Database(self.db_path)
        self.store = FactStore(self.db)
        
        # Override DOMAINS_ROOT to isolated temp directory
        self.orig_domains_root = builder.DOMAINS_ROOT
        builder.DOMAINS_ROOT = Path(self.temp_dir.name) / "domains"

    def tearDown(self):
        builder.DOMAINS_ROOT = self.orig_domains_root
        self.temp_dir.cleanup()

    def test_scaffold_domain_pod_structure(self):
        """Verify that scaffolding a new domain provisions all 4 engines and dedicated launcher."""
        pod_path = scaffold_domain_pod(
            domain_id="automotive_chassis",
            name="Automotive Chassis Design",
            description="CAD stress-strain and aerodynamic simulation engine.",
            category="physical_engineering",
            store=self.store,
        )

        self.assertTrue(pod_path.exists())
        self.assertTrue((pod_path / "state" / "models.py").exists())
        self.assertTrue((pod_path / "verify" / "invariants.py").exists())
        self.assertTrue((pod_path / "harness" / "runner.py").exists())
        self.assertTrue((pod_path / "tests" / "test_domain.py").exists())
        self.assertTrue((pod_path / "config.json").exists())
        self.assertTrue((pod_path / "spinup.py").exists())
        self.assertTrue((pod_path / "spinup.sh").exists())

        # Verify registered in root SQLite FactStore
        proj = self.store.get_project_state("automotive_chassis")
        self.assertIsNotNone(proj)
        self.assertEqual(proj.name, "Automotive Chassis Design")
        self.assertEqual(proj.variables["category"], "physical_engineering")

    def test_duplicate_domain_creation_rejected(self):
        """Verify that scaffolding a domain with an existing ID raises ValueError."""
        scaffold_domain_pod("jujitsu", "Jujitsu Curriculum", "Training drills", store=self.store)
        with self.assertRaises(ValueError):
            scaffold_domain_pod("jujitsu", "Jujitsu Curriculum", "Duplicate", store=self.store)

    def test_list_domain_pods(self):
        """Verify discovery of multiple active domain pods."""
        scaffold_domain_pod("game_dev", "Game Development", "60hz physics sim", store=self.store)
        scaffold_domain_pod("fintech", "Fintech Trading", "Market making", store=self.store)

        pods = list_domain_pods(self.store)
        self.assertEqual(len(pods), 2)
        pod_ids = [p.domain_id for p in pods]
        self.assertIn("game_dev", pod_ids)
        self.assertIn("fintech", pod_ids)


if __name__ == "__main__":
    unittest.main()
