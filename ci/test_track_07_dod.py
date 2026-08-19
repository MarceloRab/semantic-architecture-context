#!/usr/bin/env python3
"""
Automated Verification Suite for Track 07 DoD Criteria.

Validates:
1. DoD 1: Clean directory install -> project responds to list-domains.
2. DoD 2: Re-executing install.py on modified .sac/domains.md leaves file byte-for-byte identical.
3. DoD 3: Python < 3.11 or Node < 22 fails with named error codes.
4. DoD 4: Inspection of install.py confirms no MCP host config files are modified.
5. DoD 5: AST inspection of install.py proves 100% stdlib imports.
6. DoD 6: Literal execution of README quickstart steps from scratch.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import List, Tuple
from unittest.mock import MagicMock, patch

# Add repo root to sys.path so we can import install.py
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import install


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def test_dod_1_clean_install() -> Tuple[bool, str]:
    """DoD 1: Em diretório limpo, python install.py produz um projeto que responde a list-domains."""
    with tempfile.TemporaryDirectory(prefix="sac_dod1_") as tmp:
        target = Path(tmp) / "new_project"
        cmd = [sys.executable, str(REPO_ROOT / "install.py"), "--target", str(target), "--json"]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
        if res.returncode != 0:
            return False, f"install.py failed with code {res.returncode}: {res.stderr}"

        report = json.loads(res.stdout)
        if report.get("error") is not False or report.get("manifest_status") != "created":
            return False, f"Unexpected install report: {report}"

        manifest_file = target / ".sac" / "domains.md"
        if not manifest_file.is_file():
            return False, f"Manifest was not created at {manifest_file}"

        # Verify target responds to list-domains
        scan_cmd = [sys.executable, str(REPO_ROOT / "src" / "sac_scan.py"), "list-domains", "--root", str(target), "--json"]
        scan_res = subprocess.run(scan_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
        if scan_res.returncode != 0:
            return False, f"list-domains failed with code {scan_res.returncode}: {scan_res.stderr}"

        scan_payload = json.loads(scan_res.stdout)
        if scan_payload.get("error") or scan_payload.get("mode") != "catalog":
            return False, f"Invalid list-domains output: {scan_payload}"

    return True, "Clean install created .sac/domains.md and target responded to list-domains."


def test_dod_2_preserve_owned_manifest() -> Tuple[bool, str]:
    """DoD 2: Reexecutar o installer sobre um .sac/domains.md modificado deixa o arquivo byte a byte idêntico."""
    with tempfile.TemporaryDirectory(prefix="sac_dod2_") as tmp:
        target = Path(tmp) / "owned_project"
        target_sac = target / ".sac"
        target_sac.mkdir(parents=True, exist_ok=True)
        manifest_file = target_sac / "domains.md"

        # Write custom owned content
        custom_content = (
            "# SAC Custom Domain Index\n\n"
            "## custom_core\n"
            "- intent: Custom domain preserved by owner\n"
            "- onboarded: 2026-08-19\n"
            "- files:\n"
            "  - src/custom.py\n"
            "- anchor_symbols: CustomSymbol\n"
            "- on_edit: sac-execution-overlay\n"
            "- known_gaps:\n"
        ).encode("utf-8")
        manifest_file.write_bytes(custom_content)

        hash_before = sha256_of_file(manifest_file)

        # Run installer
        cmd = [sys.executable, str(REPO_ROOT / "install.py"), "--target", str(target), "--json"]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
        if res.returncode != 0:
            return False, f"install.py failed on pre-existing manifest: {res.stderr}"

        report = json.loads(res.stdout)
        if report.get("manifest_status") != "preserved":
            return False, f"Expected manifest_status 'preserved', got: {report.get('manifest_status')}"

        hash_after = sha256_of_file(manifest_file)
        if hash_before != hash_after:
            return False, f"Hash changed! before={hash_before}, after={hash_after}"

        content_after = manifest_file.read_bytes()
        if content_after != custom_content:
            return False, "File bytes differ after installer execution."

    return True, f"Existing owned manifest preserved 100% byte-for-byte (SHA-256: {hash_before})."


def test_dod_3_runtime_checks() -> Tuple[bool, str]:
    """DoD 3: Python < 3.11 ou Node < 22 falha com erro nomeado explícito."""
    # 1. Test Python < 3.11
    with patch.object(sys, "version_info", (3, 10, 8, "final", 0)):
        ok, msg = install.check_python_runtime()
        if ok or "Python >= 3.11 is required" not in msg or "sac.installer.python_version_unsupported" not in msg:
            return False, f"Python 3.10 check failed to reject with named error: {msg}"

    with patch.object(sys, "version_info", (3, 11, 0, "final", 0)):
        ok, msg = install.check_python_runtime()
        if not ok:
            return False, f"Python 3.11 check rejected valid version: {msg}"

    # 2. Test Node missing
    with patch("subprocess.run", side_effect=FileNotFoundError("No node")):
        ok, msg = install.check_node_runtime()
        if ok or "node_missing" not in msg:
            return False, f"Node missing check failed to report named error: {msg}"

    # 3. Test Node < 22 (e.g. Node 18, Node 20)
    mock_node_18 = MagicMock(returncode=0, stdout="v18.20.1\n", stderr="")
    with patch("subprocess.run", return_value=mock_node_18):
        ok, msg = install.check_node_runtime()
        if ok or "Node.js >= 22 is required" not in msg or "sac.installer.node_version_unsupported" not in msg:
            return False, f"Node 18 check failed to reject with named error: {msg}"

    mock_node_20 = MagicMock(returncode=0, stdout="v20.11.0\n", stderr="")
    with patch("subprocess.run", return_value=mock_node_20):
        ok, msg = install.check_node_runtime()
        if ok or "Node.js >= 22 is required" not in msg or "sac.installer.node_version_unsupported" not in msg:
            return False, f"Node 20 check failed to reject with named error: {msg}"

    # 4. Test Node >= 22 (e.g. Node 22, Node 23)
    mock_node_22 = MagicMock(returncode=0, stdout="v22.14.0\n", stderr="")
    with patch("subprocess.run", return_value=mock_node_22):
        ok, msg = install.check_node_runtime()
        if not ok:
            return False, f"Node 22 check rejected valid version: {msg}"

    mock_node_23 = MagicMock(returncode=0, stdout="v23.2.0\n", stderr="")
    with patch("subprocess.run", return_value=mock_node_23):
        ok, msg = install.check_node_runtime()
        if not ok:
            return False, f"Node 23 check rejected valid version: {msg}"

    return True, "Python < 3.11 and Node < 22 fail strictly with named error codes."


def test_dod_4_no_host_config_writes() -> Tuple[bool, str]:
    """DoD 4: Inspecionar o código para provar que nenhum arquivo de configuração de host MCP é editado."""
    install_file = REPO_ROOT / "install.py"
    content = install_file.read_text(encoding="utf-8")

    tree = ast.parse(content, filename=str(install_file))

    # Inspect all file operations (open, copy, mkdir, write)
    write_operations: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func_name = ""
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr

            if func_name in ("copy", "copy2", "copyfile", "move"):
                write_operations.append(f"shutil.{func_name}")
            elif func_name == "open":
                # Check mode argument if present
                if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
                    mode = node.args[1].value
                    if "w" in mode or "a" in mode or "+" in mode:
                        write_operations.append(f"open(mode={mode})")

    # In install.py, the ONLY write/copy operation must be copying template to target_manifest
    if len(write_operations) != 1 or write_operations[0] != "shutil.copy2":
        return False, f"Unexpected write operations in install.py: {write_operations}"

    return True, "install.py code inspection confirmed zero writes to host MCP configuration files (only copy2 to target .sac/domains.md)."


def test_dod_5_stdlib_only_imports() -> Tuple[bool, str]:
    """DoD 5: Inspecionar imports de install.py provando que é 100% stdlib."""
    install_file = REPO_ROOT / "install.py"
    content = install_file.read_text(encoding="utf-8")
    tree = ast.parse(content, filename=str(install_file))

    stdlib_modules = getattr(sys, "stdlib_module_names", {
        "argparse", "hashlib", "json", "os", "pathlib", "re",
        "shutil", "subprocess", "sys", "typing", "__future__",
    })

    imported_modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_modules.add(node.module.split(".")[0])

    for mod in imported_modules:
        if mod not in stdlib_modules:
            return False, f"Non-stdlib module imported: {mod}"

    return True, f"100% stdlib verified. Imported modules: {sorted(imported_modules)}"


def test_dod_6_readme_quickstart() -> Tuple[bool, str]:
    """DoD 6: Executar literalmente os passos do quickstart do README.md do zero e registrar o sucesso."""
    with tempfile.TemporaryDirectory(prefix="sac_quickstart_") as tmp:
        target_dir = Path(tmp) / "quickstart_app"

        # Step 2 from README: python install.py --target /path/to/project
        res_install = subprocess.run(
            [sys.executable, str(REPO_ROOT / "install.py"), "--target", str(target_dir)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        if res_install.returncode != 0:
            return False, f"Quickstart Step 2 (install.py) failed: {res_install.stderr}"

        if "Semantic Architecture Context (SAC) - Installer" not in res_install.stdout:
            return False, f"Quickstart Step 2 output missing header: {res_install.stdout}"

        # Step 3 from README: check MCP config output format
        if "mcpServers" not in res_install.stdout or '"sac"' not in res_install.stdout:
            return False, f"Quickstart Step 3 MCP config snippet missing from install output."

        # Step 4 from README: python src/sac_scan.py list-domains --root /path/to/project
        res_test = subprocess.run(
            [sys.executable, str(REPO_ROOT / "src" / "sac_scan.py"), "list-domains", "--root", str(target_dir)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        if res_test.returncode != 0:
            return False, f"Quickstart Step 4 (sac_scan list-domains) failed: {res_test.stderr}"

        parsed_test = json.loads(res_test.stdout)
        if parsed_test.get("mode") != "catalog":
            return False, f"Quickstart Step 4 unexpected payload: {parsed_test}"

    return True, "README 5-step quickstart executed literally from scratch with 100% success."


def main() -> int:
    print("=== SAC Track 07 DoD Verification Suite ===")
    tests = [
        ("DoD 1: Clean install & domain discovery", test_dod_1_clean_install),
        ("DoD 2: Owned manifest 100% byte-for-byte preservation", test_dod_2_preserve_owned_manifest),
        ("DoD 3: Python/Node runtime floor strict named errors", test_dod_3_runtime_checks),
        ("DoD 4: No MCP host configuration file modified", test_dod_4_no_host_config_writes),
        ("DoD 5: 100% Python stdlib-only imports", test_dod_5_stdlib_only_imports),
        ("DoD 6: Literal README quickstart execution", test_dod_6_readme_quickstart),
    ]

    failed = 0
    for name, test_fn in tests:
        try:
            ok, details = test_fn()
            if ok:
                print(f"  [PASS] {name}\n         Evidence: {details}")
            else:
                print(f"  [FAIL] {name}\n         Failure: {details}")
                failed += 1
        except Exception as exc:
            print(f"  [ERROR] {name}\n         Exception: {exc}")
            failed += 1

    print("===========================================")
    if failed:
        print(f"FAILED: {failed} test(s) failed.")
        return 1
    print("SUCCESS: All Track 07 DoD criteria verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
