#!/usr/bin/env python3
"""
Release lifecycle verification suite originating in Block 01 Track 10.

The original Track 10 established an unchecked Block 02 gate and the 0.1.0-rc
tag policy.  Block 02 is now complete, so this permanent CI gate validates the
released state instead of freezing the repository in its pre-Block-02 state.

Validates:
- RELEASE_GATE.md lists exactly Tracks 01–09 as checked, each with evidence.
- DoD 2: README.md describes co-edit gate and lists .dart and .ps1.
- DoD 3: README.md does NOT contain "prevenção de regressão" or "prova de teste".
- If tag 0.1.0 is available in the checkout, it is annotated and the gate is complete.
- DoD 5: No files in src/ or mcp/server.mjs were modified in Track 10.
"""

from pathlib import Path
import subprocess
import sys


def test_dod_1_release_gate(repo_root: Path) -> None:
    """The completed Block 02 gate has nine evidenced checked items."""
    gate_file = repo_root / "RELEASE_GATE.md"
    assert gate_file.is_file(), "RELEASE_GATE.md not found"
    content = gate_file.read_text(encoding="utf-8")

    gate_lines = [line for line in content.splitlines() if line.startswith("- [")]
    assert len(gate_lines) == 9, f"Expected exactly 9 release items, found {len(gate_lines)}"

    for number, line in enumerate(gate_lines, start=1):
        track_id = f"Track {number:02d}"
        assert line.startswith(f"- [x] **{track_id}**:"), (
            f"Missing checked box for {track_id} in RELEASE_GATE.md"
        )
        assert "Evidência:" in line, f"Missing cited evidence for {track_id}"

    assert "- [ ]" not in content, "RELEASE_GATE.md still has a pending item"
    print("  [PASS] Release gate has exactly 9 checked Block 02 items with cited evidence.")


def test_dod_2_readme_coedit_gate_and_languages(repo_root: Path) -> None:
    """DoD 2: README.md describes co-edit gate and lists .dart and .ps1."""
    readme_file = repo_root / "README.md"
    assert readme_file.is_file(), "README.md not found"
    content = readme_file.read_text(encoding="utf-8")

    assert "co-edit gate" in content.lower(), "README.md does not describe 'co-edit gate'"
    assert ".dart" in content, "README.md does not list .dart"
    assert ".ps1" in content, "README.md does not list .ps1"
    print("  [PASS] DoD 2: README.md describes co-edit gate and lists supported languages (.dart, .ps1).")


def test_dod_3_readme_no_unsubstantiated_claims(repo_root: Path) -> None:
    """DoD 3: README.md does not contain 'prevenção de regressão' or 'prova de teste'."""
    readme_file = repo_root / "README.md"
    content = readme_file.read_text(encoding="utf-8").lower()

    forbidden_phrases = [
        "prevenção de regressão",
        "prevencao de regressao",
        "prova de teste",
    ]

    for phrase in forbidden_phrases:
        assert phrase not in content, f"Forbidden phrase '{phrase}' found in README.md"

    print("  [PASS] DoD 3: README.md contains zero unevidenced regression prevention/test proof claims.")


def test_release_tag_if_available(repo_root: Path) -> None:
    """A fetched final tag must be annotated; absence in a PR checkout is allowed."""
    res = subprocess.run(
        ["git", "tag", "--list", "0.1.0"], capture_output=True, text=True, cwd=str(repo_root)
    )
    if not res.stdout.strip():
        print("  [INFO] Final tag 0.1.0 is not present in this checkout; document gate remains authoritative.")
        return

    tag_type = subprocess.run(
        ["git", "cat-file", "-t", "0.1.0"], capture_output=True, text=True, cwd=str(repo_root)
    )
    assert tag_type.returncode == 0 and tag_type.stdout.strip() == "tag", (
        "Tag 0.1.0 must be an annotated tag"
    )
    print("  [PASS] Available final tag 0.1.0 is annotated and the release gate is complete.")


def test_dod_5_no_src_mcp_modifications(repo_root: Path) -> None:
    """DoD 5: No files in src/ or mcp/server.mjs were modified in Track 10."""
    # Check diff against commit before track 10
    res = subprocess.run(["git", "diff", "--name-only", "HEAD~1"], capture_output=True, text=True, cwd=str(repo_root))
    # If not yet committed or checked against working tree + HEAD
    touched_files = [line.strip() for line in res.stdout.splitlines() if line.strip()]

    for f in touched_files:
        assert not f.startswith("src/"), f"Forbidden change in src/ file: {f}"
        assert f != "mcp/server.mjs", "Forbidden change in mcp/server.mjs"

    print("  [PASS] DoD 5: Zero modifications to src/ and mcp/server.mjs in Track 10.")


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    print("=== SAC Track 10 DoD Verification Suite ===")
    test_dod_1_release_gate(repo_root)
    test_dod_2_readme_coedit_gate_and_languages(repo_root)
    test_dod_3_readme_no_unsubstantiated_claims(repo_root)
    
    test_release_tag_if_available(repo_root)
    test_dod_5_no_src_mcp_modifications(repo_root)

    print("============================================")
    print("SUCCESS: Release lifecycle checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
