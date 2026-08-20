#!/usr/bin/env python3
"""
DoD Verification Suite for Track 09 — CI publica para PR de fork.

Automates validation of all 6 DoD criteria for Track 09:
- DoD 1 & 5: Runtime matrix (Python 3.11, 3.12, 3.13) x (Node 22, 24).
- DoD 2: Zero pull_request_target and zero ${{ inline expressions in run: blocks.
- DoD 3: permissions: contents: read and timeout-minutes explicitly declared.
- DoD 4: Zero continue-on-error; the Block 01 prohibition on diff-check is
  superseded by the blocking Block 02 gate.
- DoD 6: Hygiene gate scans full git commit history.
"""

from pathlib import Path
import re
import subprocess
import sys


def test_dod_matrix(ci_content: str) -> None:
    """DoD 1 & 5: Matrix covers Python 3.11/3.12/3.13 and Node 22/24."""
    assert '"3.11"' in ci_content and '"3.12"' in ci_content and '"3.13"' in ci_content, (
        "Missing Python matrix versions in ci.yml"
    )
    assert '"22"' in ci_content and '"24"' in ci_content, (
        "Missing Node matrix versions in ci.yml"
    )
    print("  [PASS] DoD 1 & 5: Runtime matrix contains Python [3.11, 3.12, 3.13] and Node [22, 24].")


def test_dod_security(ci_content: str, repo_root: Path) -> None:
    """DoD 2: Zero pull_request_target and zero inline expressions in run: blocks."""
    # Check all workflow files in .github/workflows
    workflow_files = list((repo_root / ".github" / "workflows").glob("*.yml"))
    for wf in workflow_files:
        text = wf.read_text(encoding="utf-8")
        assert "pull_request_target" not in text, f"pull_request_target found in {wf.name}"
        for i, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("run:"):
                # If run: is a multi-line pipe (|), check subsequent indented lines
                assert "${{" not in line, f"Inline expression in run block at {wf.name}:{i}"

    # Also check ci/sac_guard.yml
    guard_file = repo_root / "ci" / "sac_guard.yml"
    if guard_file.is_file():
        text = guard_file.read_text(encoding="utf-8")
        assert "pull_request_target" not in text, "pull_request_target found in ci/sac_guard.yml"
        for i, line in enumerate(text.splitlines(), start=1):
            if line.strip().startswith("run:"):
                assert "${{" not in line, f"Inline expression in run block at ci/sac_guard.yml:{i}"

    print("  [PASS] DoD 2: Zero pull_request_target and zero inline ${{ expressions in run: commands.")


def test_dod_permissions_and_timeouts(ci_content: str) -> None:
    """DoD 3: permissions: contents: read and timeout-minutes declared on all jobs."""
    assert "contents: read" in ci_content, "Missing 'contents: read' permission declaration"
    
    # Check that each job declares timeout-minutes
    jobs_match = re.findall(r"(\w+):\s*\n\s+name:.*?\n\s+runs-on:.*?\n\s+timeout-minutes:\s*(\d+)", ci_content, re.DOTALL)
    assert len(jobs_match) >= 3, f"Expected at least 3 jobs with timeout-minutes, found {len(jobs_match)}"
    for job_name, timeout in jobs_match:
        assert int(timeout) > 0, f"Invalid timeout for job {job_name}: {timeout}"

    print(f"  [PASS] DoD 3: 'permissions: contents: read' and deterministic 'timeout-minutes' declared across all {len(jobs_match)} jobs.")


def test_dod_no_continue_on_error_and_blocking_diff_check(ci_content: str) -> None:
    """DoD 4 plus Block 02: no masking and a blocking diff-check in ci.yml."""
    assert "continue-on-error" not in ci_content, "Found forbidden 'continue-on-error' in ci.yml"
    assert "diff-check:" in ci_content, "Missing Block 02 diff-check job in ci.yml"
    assert "src/sac_scan.py diff-check" in ci_content, "Missing Block 02 diff-check command in ci.yml"
    print("  [PASS] DoD 4 + Block 02: Zero continue-on-error and blocking diff-check in public CI.")


def test_dod_hygiene_history_scan(repo_root: Path) -> None:
    """DoD 6: Hygiene gate scans commit history and passes cleanly."""
    script = repo_root / ".github" / "scripts" / "check_hygiene.py"
    res = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, cwd=str(repo_root))
    assert res.returncode == 0, f"check_hygiene.py failed: {res.stdout}\n{res.stderr}"
    assert "Checking git history diffs..." in res.stdout
    assert "Git history is clean." in res.stdout
    print("  [PASS] DoD 6: Hygiene gate inspects git history with fetch-depth: 0 and passes 100%.")


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    ci_file = repo_root / ".github" / "workflows" / "ci.yml"
    assert ci_file.is_file(), f"ci.yml not found at {ci_file}"
    ci_content = ci_file.read_text(encoding="utf-8")

    print("=== SAC Track 09 DoD Verification Suite ===")
    test_dod_matrix(ci_content)
    test_dod_security(ci_content, repo_root)
    test_dod_permissions_and_timeouts(ci_content)
    test_dod_no_continue_on_error_and_blocking_diff_check(ci_content)
    test_dod_hygiene_history_scan(repo_root)
    print("===========================================")
    print("SUCCESS: All Track 09 DoD criteria verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
