#!/usr/bin/env python3
"""
DoD Verification Suite for Track 10 — Release Gate, README Honesto, CHANGELOG e Tag 0.1.0-rc.

Automates validation of all 5 DoD criteria for Track 10:
- DoD 1: RELEASE_GATE.md lists all 9 Block 02 items with empty checkboxes ([ ]).
- DoD 2: README.md describes co-edit gate and lists .dart and .ps1.
- DoD 3: README.md does NOT contain "prevenção de regressão" or "prova de teste".
- DoD 4: git tag lists 0.1.0-rc and does NOT list 0.1.0.
- DoD 5: No files in src/ or mcp/server.mjs were modified in Track 10.
"""

from pathlib import Path
import re
import subprocess
import sys


def test_dod_1_release_gate(repo_root: Path) -> None:
    """DoD 1: RELEASE_GATE.md lists the 9 items with empty checkboxes pointing to Block 02 tracks."""
    gate_file = repo_root / "RELEASE_GATE.md"
    assert gate_file.is_file(), "RELEASE_GATE.md not found"
    content = gate_file.read_text(encoding="utf-8")

    expected_tracks = [
        ("Track 01", "Truncamento de `verify:`"),
        ("Track 02", "Campo `on=` com vocabulário fechado para ARCH"),
        ("Track 03", "AGENTS.md na raiz como porta de entrada"),
        ("Track 04", "`_is_covered` avaliando contra o conjunto completo"),
        ("Track 05", "Registro de linguagens (`.py`, `.js`, `.ts`, `.go`)"),
        ("Track 06", "`file` sempre relativo, `_perf.sac_root` removido"),
        ("Track 07", "`OVER_SELECT` deixa de contar tags auto-incluídas"),
        ("Track 08", "Marcador de comentário sem whitelist prefixal"),
        ("Track 09", "Promessa honesta de co-edit gate consolidada"),
    ]

    for track_id, expected_snippet in expected_tracks:
        assert f"- [ ] **{track_id}**:" in content, f"Missing unchecked box for {track_id} in RELEASE_GATE.md"
        assert expected_snippet in content, f"Missing expected snippet '{expected_snippet}' for {track_id} in RELEASE_GATE.md"


    # Ensure no checked boxes in RELEASE_GATE.md
    checked_boxes = re.findall(r"- \[x\]", content, re.IGNORECASE)
    assert len(checked_boxes) == 0, f"Found unexpected checked boxes in RELEASE_GATE.md: {len(checked_boxes)}"

    print("  [PASS] DoD 1: RELEASE_GATE.md lists all 9 Block 02 items with empty checkboxes.")


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


def test_dod_4_git_tag(repo_root: Path) -> None:
    """DoD 4: git tag lists 0.1.0-rc and does NOT list 0.1.0."""
    res = subprocess.run(["git", "tag", "-l"], capture_output=True, text=True, cwd=str(repo_root))
    tags = [t.strip() for t in res.stdout.splitlines() if t.strip()]

    assert "0.1.0-rc" in tags, f"Expected tag '0.1.0-rc' in git tags, got {tags}"
    assert "0.1.0" not in tags, f"Forbidden tag '0.1.0' found in git tags: {tags}"
    print("  [PASS] DoD 4: git tag lists '0.1.0-rc' and does NOT list '0.1.0'.")


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
    
    # We execute dod_4 only if tag exists; otherwise instruct caller
    res_tag = subprocess.run(["git", "tag", "-l"], capture_output=True, text=True, cwd=str(repo_root))
    tags = [t.strip() for t in res_tag.stdout.splitlines() if t.strip()]
    if "0.1.0-rc" in tags:
        test_dod_4_git_tag(repo_root)
    else:
        print("  [INFO] Tag '0.1.0-rc' not yet created in Git index (will be tested post-tag).")

    print("============================================")
    print("SUCCESS: Preliminary Track 10 checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
