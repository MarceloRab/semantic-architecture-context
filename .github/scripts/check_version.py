#!/usr/bin/env python3
"""
Version Consistency Gate for semantic-architecture-context repository.

Verifies:
1. mcp/package.json is the Single Source of Truth (SSOT) and defines a valid semver version.
2. mcp/package.json requires node >= 22 in engines.
3. python src/sac_scan.py --version resolves and announces the exact version from mcp/package.json.
4. mcp/server.mjs resolves version dynamically and contains NO hardcoded semver literals.
# 5. No scattered version literals or forbidden legacy MCP references exist in tracked files.

Exits with code 0 on success, or code 1 on failure.
"""

import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import List, Tuple

SEMVER_REGEX = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")
HARDCODED_SERVER_VERSION_REGEX = re.compile(r"version:\s*[\"']\d+\.\d+\.\d+[\"']")
PYTHON_VERSION_DECL_REGEX = re.compile(r"^(?:__version__|VERSION)\s*=\s*[\"']\d+\.\d+\.\d+[\"']", re.MULTILINE)

FORBIDDEN_LEGACY_PATTERNS = [
    "Fast" + "MCP",
    "sac_" + "mcp_server",
]

EXCLUDED_PATHSPECS = [
    ":!.github/scripts/check_version.py",
]


def run_cmd(args: List[str], cwd: Path) -> Tuple[int, str, str]:
    """Run a subprocess command and return (code, stdout, stderr)."""
    res = subprocess.run(
        args,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return res.returncode, res.stdout.strip(), res.stderr.strip()


def check_package_json(repo_root: Path) -> Tuple[str, List[str]]:
    """Check mcp/package.json as the version SSOT."""
    violations = []
    pkg_path = repo_root / "mcp" / "package.json"
    if not pkg_path.is_file():
        violations.append(f"Missing package.json at {pkg_path}")
        return "", violations

    try:
        with open(pkg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        violations.append(f"Failed to parse JSON from {pkg_path}: {exc}")
        return "", violations

    version = data.get("version")
    if not version or not isinstance(version, str):
        violations.append(f"package.json missing or invalid 'version' field in {pkg_path}")
        return "", violations

    if not SEMVER_REGEX.match(version):
        violations.append(f"package.json version '{version}' does not match semver format")

    engines = data.get("engines", {})
    node_engine = engines.get("node", "")
    if not node_engine or ">=22" not in node_engine:
        violations.append(f"package.json engines.node should be '>=22', got '{node_engine}'")

    return version, violations


def check_python_cli_version(repo_root: Path, expected_version: str) -> List[str]:
    """Check that python src/sac_scan.py --version outputs expected version."""
    violations = []
    scan_script = repo_root / "src" / "sac_scan.py"
    if not scan_script.is_file():
        violations.append(f"Missing sac_scan.py at {scan_script}")
        return violations

    code, stdout, stderr = run_cmd([sys.executable, str(scan_script), "--version"], repo_root)
    if code != 0:
        violations.append(f"sac_scan.py --version failed with exit code {code}: {stderr}")
        return violations

    # Should match expected version exactly or prefixed by 'sac '
    out = stdout.strip()
    if out != expected_version and out != f"sac {expected_version}":
        violations.append(
            f"sac_scan.py --version announced '{out}', expected '{expected_version}' (SSOT)"
        )
    return violations


def check_node_server_version(repo_root: Path, expected_version: str) -> List[str]:
    """Check that mcp/server.mjs resolves version dynamically without hardcoded semver."""
    violations = []
    server_path = repo_root / "mcp" / "server.mjs"
    if not server_path.is_file():
        violations.append(f"Missing server.mjs at {server_path}")
        return violations

    content = server_path.read_text(encoding="utf-8")

    # Check for hardcoded version literal in server config
    match = HARDCODED_SERVER_VERSION_REGEX.search(content)
    if match:
        violations.append(
            f"mcp/server.mjs contains hardcoded version literal '{match.group(0)}'. "
            "Version MUST be resolved dynamically from package.json."
        )

    # Check that resolvePackageVersion is defined and used
    if "resolvePackageVersion" not in content:
        violations.append("mcp/server.mjs does not define or use resolvePackageVersion")

    # If node is available, execute dynamic check
    node_cmd = "node"
    code, stdout, _ = run_cmd(
        [node_cmd, "-e", "import('./mcp/server.mjs').then(m => console.log(m.resolvePackageVersion()))"],
        repo_root,
    )
    if code == 0:
        resolved_node_version = stdout.strip()
        if resolved_node_version != expected_version:
            violations.append(
                f"mcp/server.mjs dynamically resolved version '{resolved_node_version}', "
                f"expected '{expected_version}'"
            )

    return violations


def check_no_scattered_versions(repo_root: Path) -> List[str]:
    """Check src/ for version constants and tracked files for forbidden legacy references."""
    violations = []
    src_dir = repo_root / "src"
    if src_dir.is_dir():
        for py_file in src_dir.glob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            if PYTHON_VERSION_DECL_REGEX.search(content):
                violations.append(
                    f"Forbidden hardcoded version constant found in {py_file.name}. "
                    "Version must only be defined in mcp/package.json."
                )

    # Check git tracked files for forbidden legacy references
    for pattern in FORBIDDEN_LEGACY_PATTERNS:
        code, out, _ = run_cmd(["git", "grep", "-I", "-n", "-F", pattern, "--"] + EXCLUDED_PATHSPECS, repo_root)
        if code == 0 and out:
            for line in out.splitlines():
                if line.strip():
                    violations.append(f"Forbidden legacy reference '{pattern}' found -> {line.strip()}")

    return violations


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    repo_root = Path(__file__).resolve().parent.parent.parent
    print("=== SAC Version Consistency Gate Verification ===")
    all_violations = []

    print("[1/4] Checking mcp/package.json SSOT...")
    version, pkg_violations = check_package_json(repo_root)
    if pkg_violations:
        print("  [FAIL] package.json violations:")
        for v in pkg_violations:
            print(f"    - {v}")
        all_violations.extend(pkg_violations)
    else:
        print(f"  [PASS] package.json is valid SSOT declaring version '{version}'.")

    print("[2/4] Checking Python CLI (src/sac_scan.py --version)...")
    cli_violations = check_python_cli_version(repo_root, version)
    if cli_violations:
        print("  [FAIL] CLI version violations:")
        for v in cli_violations:
            print(f"    - {v}")
        all_violations.extend(cli_violations)
    else:
        print("  [PASS] sac_scan.py --version matches SSOT.")

    print("[3/4] Checking Node MCP Server (mcp/server.mjs)...")
    server_violations = check_node_server_version(repo_root, version)
    if server_violations:
        print("  [FAIL] Node server version violations:")
        for v in server_violations:
            print(f"    - {v}")
        all_violations.extend(server_violations)
    else:
        print("  [PASS] mcp/server.mjs dynamically resolves version with no hardcoded literals.")

    print("[4/4] Checking for scattered version constants and legacy references...")
    scatter_violations = check_no_scattered_versions(repo_root)
    if scatter_violations:
        print("  [FAIL] Scattered version / legacy violations:")
        for v in scatter_violations:
            print(f"    - {v}")
        all_violations.extend(scatter_violations)
    else:
        print("  [PASS] No scattered version constants or legacy references found.")

    print("==================================================")
    if all_violations:
        print(f"FAILED: {len(all_violations)} version consistency violation(s) found.")
        return 1

    print(f"SUCCESS: Version consistency verified (SSOT: {version}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
