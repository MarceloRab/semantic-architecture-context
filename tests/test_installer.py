"""
Unit tests for SAC universal installer (install.py).
Validates AGENTS.md and domains.md creation, preservation and CLI discovery.
"""

from pathlib import Path
import shutil
import tempfile
import unittest

from install import install_target, check_python_runtime, check_node_runtime


class TestInstaller(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="sac_test_install_")
        self.target_root = Path(self.tmp_dir)
        self.sac_repo_root = Path(__file__).resolve().parent.parent

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_runtime_checks(self):
        py_ok, _ = check_python_runtime()
        self.assertTrue(py_ok)
        node_ok, _ = check_node_runtime()
        self.assertTrue(node_ok)

    def test_fresh_install_creates_domains_and_agents_md(self):
        report = install_target(self.sac_repo_root, self.target_root)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["manifest_status"], "created")
        self.assertEqual(report["agents_md_status"], "created")

        domains_file = self.target_root / ".sac" / "domains.md"
        agents_file = self.target_root / "AGENTS.md"

        self.assertTrue(domains_file.is_file())
        self.assertTrue(agents_file.is_file())

        with open(agents_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("SAC — entrada para agentes", content)
        self.assertIn("sac_scan.py", content)

    def test_idempotent_install_preserves_manifest_and_agents(self):
        # 1st run
        install_target(self.sac_repo_root, self.target_root)

        # Modify manifest with custom owned domain
        domains_file = self.target_root / ".sac" / "domains.md"
        with open(domains_file, "a", encoding="utf-8") as f:
            f.write("\n## custom_domain\n- intent: Custom\n- files:\n")

        with open(domains_file, "rb") as f:
            before_sha = f.read()

        # 2nd run
        report2 = install_target(self.sac_repo_root, self.target_root)
        self.assertEqual(report2["errors"], [])
        self.assertEqual(report2["manifest_status"], "preserved")
        self.assertEqual(report2["agents_md_status"], "preserved")

        with open(domains_file, "rb") as f:
            after_sha = f.read()
        self.assertEqual(before_sha, after_sha)


if __name__ == "__main__":
    unittest.main()
