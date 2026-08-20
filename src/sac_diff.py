#!/usr/bin/env python3
"""SAC diff-check engine.

Parses unified diffs, maps changed lines to declared symbols, and enforces
SAC:REGR coverage rules (C5, C9, C16). Pure Python 3.12 stdlib.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Iterable

# Make the script runnable both as `python sac-context/src/sac_diff.py` and from the
# project root, without requiring `tools` to be a Python package.
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from sac_engine import scan, lookup  # noqa: E402


# ---------------------------------------------------------------------------
# Symbol declaration registry (contract C14)
# ---------------------------------------------------------------------------
#
# Each entry maps a file extension to a list of regexes. A regex must have a
# capturing group named ``symbol`` that yields the declared symbol name.
# These regexes are intentionally simple: the engine performs lexical
# enforcement; AST-based validation is deferred to V2.1 (C4).

_SYMBOL_REGISTRY: dict[str, list[re.Pattern]] = {
    ".py": [
        re.compile(r"^\s*class\s+(?P<symbol>[A-Za-z_]\w*)\b"),
        re.compile(r"^\s*(?:async\s+)?def\s+(?P<symbol>[A-Za-z_]\w*)\s*\("),
    ],
    ".js": [
        re.compile(r"^\s*(?:export\s+)?(?:default\s+)?class\s+(?P<symbol>[A-Za-z_$][\w$]*)\b"),
        re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+(?P<symbol>[A-Za-z_$][\w$]*)\s*\("),
        re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+(?P<symbol>[A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>"),
    ],
    ".jsx": [
        re.compile(r"^\s*(?:export\s+)?(?:default\s+)?class\s+(?P<symbol>[A-Za-z_$][\w$]*)\b"),
        re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+(?P<symbol>[A-Za-z_$][\w$]*)\s*\("),
        re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+(?P<symbol>[A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>"),
    ],
    ".ts": [
        re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:abstract\s+)?class\s+(?P<symbol>[A-Za-z_$][\w$]*)\b"),
        re.compile(r"^\s*(?:export\s+)?(?:interface|type|enum)\s+(?P<symbol>[A-Za-z_$][\w$]*)\b"),
        re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+(?P<symbol>[A-Za-z_$][\w$]*)\s*(?:<[^>]+>\s*)?\("),
        re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+(?P<symbol>[A-Za-z_$][\w$]*)\s*(?::[^=]+)?=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>"),
    ],
    ".tsx": [
        re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:abstract\s+)?class\s+(?P<symbol>[A-Za-z_$][\w$]*)\b"),
        re.compile(r"^\s*(?:export\s+)?(?:interface|type|enum)\s+(?P<symbol>[A-Za-z_$][\w$]*)\b"),
        re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+(?P<symbol>[A-Za-z_$][\w$]*)\s*(?:<[^>]+>\s*)?\("),
        re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+(?P<symbol>[A-Za-z_$][\w$]*)\s*(?::[^=]+)?=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>"),
    ],
    ".go": [
        re.compile(r"^\s*func\s+(?:\([^)]*\)\s*)?(?P<symbol>[A-Za-z_]\w*)\s*(?:\[[^]]+\]\s*)?\("),
        re.compile(r"^\s*type\s+(?P<symbol>[A-Za-z_]\w*)\s+(?:struct|interface)\b"),
    ],
    ".dart": [
        # class Foo, abstract class Foo, extension Foo, enum Foo, mixin Foo
        re.compile(r"^\s*(?:abstract\s+)?(?:class|extension|enum|mixin)\s+(?P<symbol>\w+)"),
        # function / getter / setter-like top-level members
        re.compile(r"^\s*(?:void|Future|Stream|dynamic|Object|String|int|double|bool|num|Widget|List|Map|Set)\s+(?P<symbol>\w+)\s*[\(<]"),
    ],
    ".ps1": [
        # function Foo
        re.compile(r"^\s*function\s+(?P<symbol>\w+)"),
        # $foo = ...
        re.compile(r"^\s*\$(?P<symbol>\w+)\s*="),
    ],
}


def _registry_extensions() -> frozenset[str]:
    return frozenset(_SYMBOL_REGISTRY.keys())


# ---------------------------------------------------------------------------
# Unified diff parser
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class HunkLine:
    file_path: str
    new_line_no: int
    line_text: str


def _iter_changed_lines(diff_text: str) -> Iterable[HunkLine]:
    """Yield changed lines (in the new file) from a unified diff.

    Parses ``---``/``+++`` headers and ``@@`` hunks. Ignores context lines and
    handles ``No newline at end of file`` markers.
    """
    current_old = 0
    current_new = 0
    in_hunk = False
    file_path: str | None = None

    for raw_line in diff_text.splitlines():
        line = raw_line.rstrip("\n")

        if line.startswith("--- "):
            in_hunk = False
            continue

        if line.startswith("+++ "):
            in_hunk = False
            # "+++ b/path/to/file" or "+++ /dev/null"
            parts = line[4:].split("\t", 1)
            path_token = parts[0]
            if path_token.startswith("b/"):
                file_path = path_token[2:]
            elif path_token == "/dev/null":
                file_path = None
            else:
                file_path = path_token
            continue

        hunk_header_match = re.match(
            r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@",
            line,
        )
        if hunk_header_match:
            in_hunk = True
            current_old = int(hunk_header_match.group(1))
            current_new = int(hunk_header_match.group(2))
            continue

        if not in_hunk or file_path is None:
            continue

        if line.startswith(" "):
            current_old += 1
            current_new += 1
        elif line.startswith("-"):
            current_old += 1
        elif line.startswith("+"):
            yield HunkLine(file_path, current_new, line[1:])
            current_new += 1
        elif line.startswith("\\"):
            # "\ No newline at end of file" - not a content line.
            continue
        elif line == "":
            # Empty added line represented as a bare "+" in the diff.
            yield HunkLine(file_path, current_new, "")
            current_new += 1


# ---------------------------------------------------------------------------
# Symbol mapping
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SymbolBlock:
    start_line: int
    end_line: int
    name: str
    kind: str  # "class-like" or "function-like"


def _find_block_end(lines: list[str], start_line: int) -> int:
    """Return the 1-indexed line number of the closing brace for the block
    that starts at ``start_line`` (1-indexed). Returns the last line if the
    block is unclosed.
    """
    idx = start_line - 1
    while idx < len(lines):
        if "{" in lines[idx]:
            break
        idx += 1
    if idx >= len(lines):
        return len(lines)

    depth = 0
    for i in range(idx, len(lines)):
        for ch in lines[i]:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return i + 1
    return len(lines)


# Regexes for class-like scopes take precedence over function-like scopes.
_CLASS_LIKE_RE = re.compile(
    r"^\s*(?:abstract\s+)?(?:class|extension|enum|mixin)\s+(?P<symbol>\w+)"
)


def _symbol_blocks(path: str, ext: str) -> list[SymbolBlock]:
    """Return symbol blocks (declarations with start/end lines) for a file.

    For Dart, class-like scopes take precedence: a changed line inside a
    method is attributed to the containing class. For PowerShell, functions
    and script-scope variables are treated as top-level blocks.
    """
    patterns = _SYMBOL_REGISTRY.get(ext)
    if not patterns:
        return []

    try:
        with open(path, "r", encoding="utf-8", errors="surrogateescape") as fh:
            lines = fh.readlines()
    except OSError:
        return []

    blocks: list[SymbolBlock] = []
    for line_no, raw_line in enumerate(lines, start=1):
        line = raw_line.rstrip("\n")

        class_match = _CLASS_LIKE_RE.match(line)
        if class_match:
            end_line = _find_block_end(lines, line_no)
            blocks.append(
                SymbolBlock(
                    start_line=line_no,
                    end_line=end_line,
                    name=class_match.group("symbol"),
                    kind="class-like",
                )
            )
            continue

        for pattern in patterns:
            match = pattern.match(line)
            if match:
                end_line = _find_block_end(lines, line_no)
                blocks.append(
                    SymbolBlock(
                        start_line=line_no,
                        end_line=end_line,
                        name=match.group("symbol"),
                        kind="function-like",
                    )
                )
                break

    return blocks


def _symbol_at_line(path: str, line_no: int, ext: str) -> str | None:
    """Return the symbol whose declaration scope contains ``line_no``.

    Class-like scopes take precedence over function-like scopes, so a changed
    line inside a method is attributed to the containing class.
    """
    blocks = _symbol_blocks(path, ext)
    if not blocks:
        return None

    # Innermost class-like block containing the line.
    for block in reversed(blocks):
        if block.kind == "class-like" and block.start_line <= line_no <= block.end_line:
            return block.name

    # Otherwise, innermost top-level function-like block.
    for block in reversed(blocks):
        if block.kind == "function-like" and block.start_line <= line_no <= block.end_line:
            return block.name

    return None


# ---------------------------------------------------------------------------
# Diff-check core
# ---------------------------------------------------------------------------

@dataclass
class ChangedSymbol:
    file_path: str
    symbol: str
    line_numbers: set[int] = field(default_factory=set)


@dataclass
class Violation:
    file_path: str
    symbol: str
    tag_type: str
    trigger: str
    constraint: str
    verify: list[str]
    uncovered: list[str]
    acked: bool = False


@dataclass
class DiffCheckResult:
    exit_code: int
    changed_symbols: list[ChangedSymbol]
    violations: list[Violation]
    acks: list[str]
    unknown_language_files: list[dict]
    report: dict


def _group_changed_lines(diff_text: str) -> dict[str, set[int]]:
    grouped: dict[str, set[int]] = {}
    for hunk_line in _iter_changed_lines(diff_text):
        grouped.setdefault(hunk_line.file_path, set()).add(hunk_line.new_line_no)
    return grouped


def _extract_acks(text: str) -> set[str]:
    """Extract explicit SAC-ACK tokens from a block of text.

    Format: ``SAC-ACK: <symbol>`` (per-symbol only; ``all`` is rejected).
    """
    acks: set[str] = set()
    for match in re.finditer(r"SAC-ACK:\s*(\S+)", text, re.IGNORECASE):
        symbol = match.group(1)
        if symbol.lower() == "all":
            # Per contract C5, blanket ACK is prohibited and ignored.
            continue
        acks.add(symbol)
    return acks


def _gather_acks(base: str | None, pr_body: str | None, root: str) -> set[str]:
    acks: set[str] = set()

    if base:
        try:
            result = subprocess.run(
                ["git", "log", f"{base}..HEAD", "--format=%B"],
                capture_output=True,
                text=True,
                check=False,
                cwd=root,
            )
            if result.returncode == 0:
                acks.update(_extract_acks(result.stdout))
        except FileNotFoundError:
            pass

    if pr_body:
        acks.update(_extract_acks(pr_body))

    return acks


def _is_covered(
    target: str,
    changed_symbols: list[ChangedSymbol],
    changed_files: set[str],
) -> bool:
    """Return True if ``target`` is covered per contract C16.

    Coverage occurs when:
      (a) a changed symbol name exactly matches ``target``; or
      (b) the basename (without extension) of a changed file matches ``target``.
    """
    for changed in changed_symbols:
        if changed.symbol == target:
            return True
    for file_path in changed_files:
        basename = os.path.splitext(os.path.basename(file_path))[0]
        if basename == target:
            return True
    return False


def _tags_for_file(file_path: str, root: str, ext: str | None = None) -> list[dict]:
    """Return all SAC tags found in ``file_path`` under ``root``.

    If ``ext`` is provided and not in the default engine allowlist, it is
    passed as an extra extension so that fail-closed detection (C9) can see
    tags in unsupported languages.
    """
    warnings: list[str] = []
    registry_exts = _registry_extensions()
    extra_exts = [ext] if ext is not None and ext not in registry_exts else None
    all_tags = scan(root, extra_exts=extra_exts, warnings=warnings)
    return [tag.to_dict() for tag in all_tags if tag.file == file_path]


def diff_check(
    diff_text: str,
    root: str,
    base: str | None = None,
    pr_body: str | None = None,
) -> DiffCheckResult:
    """Run SAC diff-check over a unified diff.

    Args:
        diff_text: Unified diff content.
        root: Project root (used for SAC tag scanning).
        base: Git ref for ACK lookup via ``git log <base>..HEAD``.
        pr_body: Pull-request body text for ACK lookup.

    Returns:
        ``DiffCheckResult`` with exit code and detailed report.
    """
    root = os.path.abspath(root)
    changed_lines = _group_changed_lines(diff_text)
    changed_files = set(changed_lines.keys())

    acks = _gather_acks(base, pr_body, root)
    registry_exts = _registry_extensions()

    changed_symbols: list[ChangedSymbol] = []
    changed_symbols_by_file: dict[str, list[ChangedSymbol]] = {}
    unknown_language_files: list[dict] = []
    violations: list[Violation] = []

    for file_path, line_numbers in changed_lines.items():
        full_path = os.path.join(root, file_path)
        ext = os.path.splitext(file_path)[1].lower()

        file_tags = _tags_for_file(full_path, root, ext=ext)

        if ext not in registry_exts:
            # Contract C9: fail closed for files with SAC tags in unknown langs.
            if file_tags:
                unknown_language_files.append(
                    {
                        "file_path": file_path,
                        "tags": file_tags,
                    }
                )
            continue

        symbol_map: dict[str, ChangedSymbol] = {}
        for line_no in line_numbers:
            symbol = _symbol_at_line(full_path, line_no, ext)
            if symbol is None:
                continue
            if symbol not in symbol_map:
                symbol_map[symbol] = ChangedSymbol(
                    file_path=file_path,
                    symbol=symbol,
                )
            symbol_map[symbol].line_numbers.add(line_no)

        file_symbols = list(symbol_map.values())
        changed_symbols_by_file[file_path] = file_symbols
        changed_symbols.extend(file_symbols)

    for file_path in changed_lines:
        full_path = os.path.join(root, file_path)
        for changed in changed_symbols_by_file.get(file_path, []):
            symbol_name = changed.symbol
            result = lookup(symbol_name, root, filepath=full_path)
            for match in result.get("matches", []):
                tag_type = match.get("tag_type")
                if tag_type != "REGR":
                    continue

                verify = match.get("verify", [])
                uncovered = [
                    target
                    for target in verify
                    if not _is_covered(target, changed_symbols, changed_files)
                ]

                acked = symbol_name in acks
                if uncovered and not acked:
                    violations.append(
                        Violation(
                            file_path=file_path,
                            symbol=symbol_name,
                            tag_type=tag_type,
                            trigger=match.get("trigger", ""),
                            constraint=match.get("constraint", ""),
                            verify=verify,
                            uncovered=uncovered,
                            acked=acked,
                        )
                    )

    blocked = bool(violations) or bool(unknown_language_files)
    exit_code = 1 if blocked else 0

    report = {
        "exit_code": exit_code,
        "changed_files": sorted(changed_files),
        "changed_symbols": [
            {
                "file_path": cs.file_path,
                "symbol": cs.symbol,
                "lines": sorted(cs.line_numbers),
            }
            for cs in changed_symbols
        ],
        "acks": sorted(acks),
        "violations": [
            {
                "file_path": v.file_path,
                "symbol": v.symbol,
                "tag_type": v.tag_type,
                "trigger": v.trigger,
                "constraint": v.constraint,
                "verify": v.verify,
                "uncovered": v.uncovered,
                "acked": v.acked,
            }
            for v in violations
        ],
        "unknown_language_files": unknown_language_files,
    }

    return DiffCheckResult(
        exit_code=exit_code,
        changed_symbols=changed_symbols,
        violations=violations,
        acks=sorted(acks),
        unknown_language_files=unknown_language_files,
        report=report,
    )


def _git_diff(base: str, root: str) -> str:
    """Return unified diff from ``base`` to HEAD."""
    try:
        result = subprocess.run(
            ["git", "diff", f"{base}...HEAD"],
            capture_output=True,
            text=True,
            check=False,
            cwd=root,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("git executable not found") from exc

    if result.returncode != 0:
        raise RuntimeError(
            f"git diff failed (exit {result.returncode}): {result.stderr.strip()}"
        )

    return result.stdout


def run_diff_check(
    patch: str | None,
    base: str | None,
    root: str,
    pr_body: str | None,
    json_output: bool = False,
) -> tuple[int, str]:
    """High-level entry point used by the CLI.

    Returns ``(exit_code, output)``.
    """
    if patch is not None and base is not None:
        raise ValueError("use either --patch or --base, not both")

    if patch is not None:
        try:
            with open(patch, "r", encoding="utf-8") as fh:
                diff_text = fh.read()
        except OSError as exc:
            raise RuntimeError(f"cannot read patch file: {exc}") from exc
    elif base is not None:
        diff_text = _git_diff(base, root)
    else:
        raise ValueError("either --patch or --base is required")

    result = diff_check(diff_text, root, base=base, pr_body=pr_body)

    if json_output:
        return result.exit_code, json.dumps(result.report, indent=1)

    lines: list[str] = []
    lines.append(f"SAC diff-check: exit {result.exit_code}")
    lines.append("")

    if result.acks:
        lines.append("ACKs recognized:")
        for ack in result.acks:
            lines.append(f"  - SAC-ACK: {ack}")
        lines.append("")

    if result.unknown_language_files:
        lines.append("FAIL CLOSED - changed files in unsupported languages with SAC tags:")
        for entry in result.unknown_language_files:
            lines.append(f"  {entry['file_path']}")
            for tag in entry["tags"]:
                lines.append(
                    f"    {tag['file']}:{tag['line']} SAC:{tag['tag_type']} - {tag['symbol']}"
                )
        lines.append("")

    if result.violations:
        lines.append("REGR violations (blocked):")
        for v in result.violations:
            status = "ACKED" if v.acked else "NOT ACKED"
            lines.append(f"  {v.file_path}:{v.symbol} [{status}]")
            lines.append(f"    constraint: {v.constraint}")
            lines.append(f"    verify: {', '.join(v.verify)}")
            lines.append(f"    uncovered: {', '.join(v.uncovered)}")
        lines.append("")

    if not result.unknown_language_files and not result.violations:
        lines.append("No SAC violations found.")
        lines.append("")

    lines.append("Changed symbols:")
    for cs in result.changed_symbols:
        lines.append(
            f"  {cs.file_path}:{cs.symbol} (lines {sorted(cs.line_numbers)})"
        )

    return result.exit_code, "\n".join(lines)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="SAC diff-check")
    parser.add_argument("--patch", help="Path to unified diff patch file")
    parser.add_argument("--base", help="Git base ref (e.g. origin/main)")
    parser.add_argument("--root", default=os.getcwd(), help="Project root")
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    args = parser.parse_args()

    try:
        exit_code, output = run_diff_check(
            patch=args.patch,
            base=args.base,
            root=args.root,
            pr_body=os.environ.get("SAC_PR_BODY"),
            json_output=args.json,
        )
    except (ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)

    print(output)
    sys.exit(exit_code)
