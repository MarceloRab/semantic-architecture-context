"""
Unit tests for SAC universal installer (install.py).
Validates AGENTS.md, domains.md, and meta-harness boot hooks (.cursorrules, CLAUDE.md).
"""

from pathlib import Path
import shutil
import tempfile
import unittest

from install import (
    install_target,
    check_python_runtime,
    check_node_runtime,
    inject_harness_boot_hooks,
    SAC_BOOT_START_MARKER,
)


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
        self.assertIn("sac list-domains", content)

    def test_harness_boot_hooks_injection(self):
        # Create mock .cursorrules and CLAUDE.md
        cursorrules_file = self.target_root / ".cursorrules"
        with open(cursorrules_file, "w", encoding="utf-8") as f:
            f.write('context_mode:{\n  auto_read_only: [".cursorrules", ".antigravityignore"],\n}\nread_hierarchy:{\n  L1_gate: [".cursorrules", ".antigravityignore"],\n}\n')

        claude_file = self.target_root / "CLAUDE.md"
        with open(claude_file, "w", encoding="utf-8") as f:
            f.write("# Project Guidelines\n\nSome guidelines here.\n")

        # Run install
        report = install_target(self.sac_repo_root, self.target_root)
        self.assertEqual(report["errors"], [])

        # Verify .cursorrules updated
        with open(cursorrules_file, "r", encoding="utf-8") as f:
            cr_content = f.read()
        self.assertIn(SAC_BOOT_START_MARKER, cr_content)
        self.assertIn('"AGENTS.md"', cr_content)

        # Verify CLAUDE.md updated
        with open(claude_file, "r", encoding="utf-8") as f:
            cl_content = f.read()
        self.assertIn(SAC_BOOT_START_MARKER, cl_content)

        # Re-run install and verify idempotency (no duplicate markers)
        report2 = install_target(self.sac_repo_root, self.target_root)
        self.assertEqual(report2["errors"], [])

        with open(cursorrules_file, "r", encoding="utf-8") as f:
            cr_content2 = f.read()
        self.assertEqual(cr_content2.count(SAC_BOOT_START_MARKER), 1)

        with open(claude_file, "r", encoding="utf-8") as f:
            cl_content2 = f.read()
        self.assertEqual(cl_content2.count(SAC_BOOT_START_MARKER), 1)

    def test_no_ghost_harness_files_created(self):
        # If target has neither .cursorrules nor CLAUDE.md, they should NOT be created
        report = install_target(self.sac_repo_root, self.target_root)
        self.assertEqual(report["errors"], [])
        self.assertFalse((self.target_root / ".cursorrules").exists())
        self.assertFalse((self.target_root / "CLAUDE.md").exists())
        self.assertFalse((self.target_root / ".github" / "copilot-instructions.md").exists())


if __name__ == "__main__":
    unittest.main()
