#!/usr/bin/env python3
"""
Semantic Architecture Context (SAC) Universal Installer.

100% Python Standard Library (no third-party dependencies).
Installs / initializes SAC for a target project, verifies runtimes,
ensures .sac/domains.md exists without ever modifying existing owned manifests,
verifies domain discovery, and outputs MCP host configuration.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any, Dict, Optional, Tuple

MIN_PYTHON_VERSION = (3, 11)
MIN_NODE_VERSION = 22


def check_python_runtime() -> Tuple[bool, str]:
    """Verify Python runtime >= 3.11."""
    curr = sys.version_info
    major = getattr(curr, "major", curr[0] if len(curr) > 0 else 0)
    minor = getattr(curr, "minor", curr[1] if len(curr) > 1 else 0)
    micro = getattr(curr, "micro", curr[2] if len(curr) > 2 else 0)
    if (major, minor) < MIN_PYTHON_VERSION:
        return False, (
            f"Python >= 3.11 is required (found {major}.{minor}.{micro}). "
            "Error code: sac.installer.python_version_unsupported"
        )
    return True, f"Python {major}.{minor}.{micro} (>= 3.11)"


def check_node_runtime() -> Tuple[bool, str]:
    """Verify Node.js runtime >= 22 by running `node --version`."""
    try:
        res = subprocess.run(
            ["node", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError:
        return False, (
            "Node.js >= 22 is required, but 'node' executable was not found in PATH. "
            "Error code: sac.installer.node_missing"
        )
    except Exception as exc:
        return False, (
            f"Failed to check Node.js version: {exc}. "
            "Error code: sac.installer.node_check_failed"
        )

    if res.returncode != 0:
        return False, (
            f"Node.js check failed with exit code {res.returncode}: {res.stderr.strip()}. "
            "Error code: sac.installer.node_check_failed"
        )

    raw_version = res.stdout.strip()
    match = re.search(r"v?(\d+)(?:\.(\d+))?", raw_version)
    if not match:
        return False, (
            f"Could not parse Node.js version from '{raw_version}'. "
            "Error code: sac.installer.node_version_parse_error"
        )

    major = int(match.group(1))
    if major < MIN_NODE_VERSION:
        return False, (
            f"Node.js >= 22 is required (found {raw_version}). "
            "Error code: sac.installer.node_version_unsupported"
        )

    return True, f"Node.js {raw_version} (>= 22)"


def compute_file_sha256(filepath: Path) -> Optional[str]:
    """Compute SHA-256 hash of a file, or return None if file does not exist."""
    if not filepath.is_file():
        return None
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def install_target(
    sac_repo_root: Path,
    target_root: Path,
    check_only: bool = False,
) -> Dict[str, Any]:
    """
    Install / initialize SAC in target_root.
    Never overwrites or modifies existing .sac/domains.md.
    """
    report: Dict[str, Any] = {
        "sac_repo_root": str(sac_repo_root),
        "target_root": str(target_root),
        "check_only": check_only,
        "actions": [],
        "manifest_status": "unknown",
        "errors": [],
    }

    # Verify templates source
    template_path = sac_repo_root / "templates" / "domains.template.md"
    if not template_path.is_file():
        err_msg = (
            f"Template file not found at {template_path}. "
            "Error code: sac.installer.template_missing"
        )
        report["errors"].append(err_msg)
        return report

    if check_only:
        report["actions"].append("Runtime checks passed (check-only mode).")
        return report

    # Ensure target directory exists
    target_root.mkdir(parents=True, exist_ok=True)
    sac_dir = target_root / ".sac"
    sac_dir.mkdir(parents=True, exist_ok=True)

    target_manifest = sac_dir / "domains.md"
    if target_manifest.exists():
        # NEVER overwrite or touch existing owned manifest
        report["manifest_status"] = "preserved"
        report["manifest_sha256"] = compute_file_sha256(target_manifest)
        report["actions"].append(
            f"Preserved existing owned manifest at {target_manifest} (untouched)."
        )
    else:
        # Create from template
        try:
            shutil.copy2(template_path, target_manifest)
            report["manifest_status"] = "created"
            report["manifest_sha256"] = compute_file_sha256(target_manifest)
            report["actions"].append(
                f"Created .sac/domains.md from {template_path.name}."
            )
        except Exception as exc:
            err_msg = (
                f"Failed to copy template to {target_manifest}: {exc}. "
                "Error code: sac.installer.manifest_creation_failed"
            )
            report["errors"].append(err_msg)
            return report

    # Verify that target responds to list-domains CLI
    scan_script = sac_repo_root / "src" / "sac_scan.py"
    if not scan_script.is_file():
        err_msg = (
            f"SAC scanner not found at {scan_script}. "
            "Error code: sac.installer.scanner_missing"
        )
        report["errors"].append(err_msg)
        return report

    scan_cmd = [
        sys.executable,
        str(scan_script),
        "list-domains",
        "--root",
        str(target_root),
        "--json",
    ]
    try:
        scan_res = subprocess.run(
            scan_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except Exception as exc:
        err_msg = (
            f"Failed to execute scanner: {exc}. "
            "Error code: sac.installer.scan_execution_failed"
        )
        report["errors"].append(err_msg)
        return report

    if scan_res.returncode != 0:
        err_msg = (
            f"SAC scan validation failed (exit code {scan_res.returncode}): {scan_res.stderr.strip() or scan_res.stdout.strip()}. "
            "Error code: sac.installer.scan_validation_failed"
        )
        report["errors"].append(err_msg)
        return report

    try:
        scan_json = json.loads(scan_res.stdout)
        if scan_json.get("error"):
            err_msg = (
                f"SAC scan returned error payload: {scan_json}. "
                "Error code: sac.installer.scan_payload_error"
            )
            report["errors"].append(err_msg)
            return report
        report["scan_result"] = {
            "mode": scan_json.get("mode"),
            "domains_count": scan_json.get("count", len(scan_json.get("domains", []))),
        }
        report["actions"].append("Verified SAC domains discovery on target project.")
    except Exception as exc:
        err_msg = (
            f"Failed to parse scanner output: {exc}. Raw: {scan_res.stdout[:200]}. "
            "Error code: sac.installer.scan_output_parse_error"
        )
        report["errors"].append(err_msg)
        return report

    return report


def build_mcp_config(sac_repo_root: Path, target_root: Path) -> Dict[str, Any]:
    """Generate MCP host configuration snippet."""
    server_mjs = (sac_repo_root / "mcp" / "server.mjs").resolve()
    python_exe = Path(sys.executable).resolve()

    return {
        "mcpServers": {
            "sac": {
                "command": "node",
                "args": [server_mjs.as_posix()],
                "env": {
                    "SAC_ROOT": target_root.resolve().as_posix(),
                    "SAC_PYTHON": python_exe.as_posix(),
                },
            }
        }
    }


def format_cli_output(
    report: Dict[str, Any],
    mcp_config: Optional[Dict[str, Any]] = None,
) -> str:
    """Format user-facing installation summary and instructions."""
    lines: list[str] = []
    lines.append("=======================================================")
    lines.append(" Semantic Architecture Context (SAC) - Installer")
    lines.append("=======================================================")

    if report.get("errors"):
        lines.append("\n[FAIL] Installation encountered errors:")
        for err in report["errors"]:
            lines.append(f"  - {err}")
        lines.append("\nRemediation: Resolve the issues above and re-run install.py.")
        return "\n".join(lines)

    lines.append("\n[OK] Environment and Runtime Validation:")
    for action in report.get("actions", []):
        lines.append(f"  - {action}")

    manifest_status = report.get("manifest_status")
    if manifest_status == "created":
        lines.append("  - Status: Initialized new .sac/domains.md manifest from template.")
    elif manifest_status == "preserved":
        lines.append("  - Status: Existing .sac/domains.md preserved (100% byte-for-byte).")

    if mcp_config:
        lines.append("\n-------------------------------------------------------")
        lines.append(" MCP Host Configuration Snippet")
        lines.append("-------------------------------------------------------")
        lines.append(
            "Note: SAC does NOT modify your host configuration files automatically.\n"
            "Copy the configuration below into your MCP host (e.g. claude_desktop_config.json\n"
            "or your IDE's .mcp.json / settings.json):\n"
        )
        lines.append(json.dumps(mcp_config, indent=2))
        lines.append("\n-------------------------------------------------------")
        lines.append(" Next Steps:")
        lines.append("  1. Copy the JSON block above into your MCP client config.")
        lines.append("  2. Restart your MCP client (Claude Desktop / Cursor / IDE).")
        lines.append("  3. Call list_sac_domains() to begin using SAC.")
        lines.append("=======================================================")

    return "\n".join(lines)


def parse_arguments(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="install.py",
        description="Universal stdlib installer for Semantic Architecture Context (SAC).",
    )
    parser.add_argument(
        "--target",
        "-t",
        default=".",
        help="Target project directory to initialize/install SAC for (default: current working directory).",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only verify system runtime requirements (Python >= 3.11, Node >= 22) without modifying target.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output installation report as machine-readable JSON.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    # Ensure UTF-8 stdout if supported
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    args = parse_arguments(argv)
    sac_repo_root = Path(__file__).resolve().parent
    target_root = Path(args.target).resolve()

    # 1. Strict Runtime Checks
    py_ok, py_msg = check_python_runtime()
    if not py_ok:
        if args.json:
            print(json.dumps({"error": True, "message": py_msg, "code": "sac.installer.python_version_unsupported"}, indent=2))
        else:
            print(f"[FAIL] {py_msg}", file=sys.stderr)
        return 1

    node_ok, node_msg = check_node_runtime()
    if not node_ok:
        if args.json:
            print(json.dumps({"error": True, "message": node_msg, "code": "sac.installer.node_runtime_error"}, indent=2))
        else:
            print(f"[FAIL] {node_msg}", file=sys.stderr)
        return 1

    # 2. Perform target installation
    report = install_target(
        sac_repo_root=sac_repo_root,
        target_root=target_root,
        check_only=args.check_only,
    )
    report["runtimes"] = {
        "python": py_msg,
        "node": node_msg,
    }

    if report.get("errors"):
        if args.json:
            report["error"] = True
            print(json.dumps(report, indent=2))
        else:
            print(format_cli_output(report), file=sys.stderr)
        return 1

    # 3. Generate MCP config
    mcp_config = None
    if not args.check_only:
        mcp_config = build_mcp_config(sac_repo_root, target_root)
        report["mcp_config"] = mcp_config

    if args.json:
        report["error"] = False
        print(json.dumps(report, indent=2))
    else:
        print(format_cli_output(report, mcp_config))

    return 0


if __name__ == "__main__":
    sys.exit(main())
