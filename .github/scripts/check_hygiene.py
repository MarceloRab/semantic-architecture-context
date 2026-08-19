#!/usr/bin/env python3
"""
Hygiene Gate for semantic-architecture-context repository.

Verifies:
1. No compiled bytecode (*.pyc) or __pycache__ directories are tracked in git.
2. No machine paths (e.g. C:\\Users\\) are present in tracked product files.
3. No private monorepo references (e.g. rabelo-standards) are present in tracked product files.
4. Git commit history does not contain forbidden strings in non-audit commits.

Exits with code 0 on success, or code 1 with detailed findings on failure.
"""

import subprocess
import sys
from typing import List, Tuple

# Patterns constructed to avoid self-match false positives
FORBIDDEN_STRINGS = [
    "C:" + "\\Users\\",
    "rabelo" + "-standards",
]

EXCLUDED_PATHSPECS = [
    ":!.context",
    ":!AUDIT.md",
    ":!.github/workflows/hygiene.yml",
    ":!.github/scripts/check_hygiene.py",
]


def run_git_command(args: List[str]) -> Tuple[int, str, str]:
    """Execute a git command and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        ["git"] + args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def check_tracked_bytecode() -> List[str]:
    """Check if any *.pyc or __pycache__ files are tracked in git index."""
    violations = []
    code, out, _ = run_git_command(["ls-files", "*.pyc", "*__pycache__*"])
    if out:
        for line in out.splitlines():
            line = line.strip()
            if line:
                violations.append(f"Tracked compiled bytecode/cache: {line}")
    return violations


def check_forbidden_strings_tracked() -> List[str]:
    """Check for forbidden strings in tracked files."""
    violations = []
    for pattern in FORBIDDEN_STRINGS:
        cmd = ["grep", "-I", "-n", "-F", pattern, "--"] + EXCLUDED_PATHSPECS
        code, out, _ = run_git_command(cmd)
        if code == 0 and out:
            for line in out.splitlines():
                line = line.strip()
                if line:
                    violations.append(f"Forbidden string '{pattern}' found -> {line}")
    return violations


def check_commit_history() -> List[str]:
    """Check git commit history for forbidden strings outside excluded audit paths."""
    violations = []
    # Check if there are any commits yet
    code, head_check, _ = run_git_command(["rev-parse", "--verify", "HEAD"])
    if code != 0:
        return violations  # No commits yet, clean

    cmd = ["log", "-p", "--"] + EXCLUDED_PATHSPECS
    code, log_out, _ = run_git_command(cmd)
    if code == 0 and log_out:
        current_commit = "unknown"
        for line in log_out.splitlines():
            if line.startswith("commit "):
                current_commit = line.split()[1][:8]
            if line.startswith("+") and not line.startswith("+++"):
                added_content = line[1:]
                for pattern in FORBIDDEN_STRINGS:
                    if pattern in added_content:
                        violations.append(
                            f"Forbidden string '{pattern}' in commit {current_commit} diff: {added_content.strip()}"
                        )
    return violations


def main() -> int:
    print("=== SAC Hygiene Gate Verification ===")
    all_violations = []

    print("[1/3] Checking for tracked bytecode (*.pyc) and __pycache__...")
    bytecode_violations = check_tracked_bytecode()
    if bytecode_violations:
        print("  [FAIL] Tracked bytecode detected:")
        for v in bytecode_violations:
            print(f"    - {v}")
        all_violations.extend(bytecode_violations)
    else:
        print("  [PASS] No tracked bytecode or __pycache__.")

    print("[2/3] Checking for forbidden machine paths and private monorepo strings...")
    string_violations = check_forbidden_strings_tracked()
    if string_violations:
        print("  [FAIL] Forbidden strings detected in tracked files:")
        for v in string_violations:
            print(f"    - {v}")
        all_violations.extend(string_violations)
    else:
        print("  [PASS] No forbidden strings in tracked files.")

    print("[3/3] Checking git history diffs...")
    history_violations = check_commit_history()
    if history_violations:
        print("  [FAIL] Forbidden strings detected in commit history:")
        for v in history_violations:
            print(f"    - {v}")
        all_violations.extend(history_violations)
    else:
        print("  [PASS] Git history is clean.")

    print("=======================================")
    if all_violations:
        print(f"FAILED: {len(all_violations)} hygiene violation(s) found.")
        return 1

    print("SUCCESS: All hygiene checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
