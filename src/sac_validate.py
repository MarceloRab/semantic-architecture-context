"""SAC AST-based validate.

Detects orphan SAC:ARCH/SAC:REGR/SAC:DEPRECATED tags — tags whose line does not
correspond to a real symbol declaration in the source file.

API:
    validate(root, extra_exts=None, ignore_dirs=None)
        -> tuple[list[orphan], list[warning]]

Exit codes (consumed by sac_scan.py):
    0  — no orphans found
    1  — orphans found
    2  — fatal error (invalid root, etc.)
"""

from __future__ import annotations

import ast
import os
import sys
from dataclasses import dataclass, field
from typing import Iterable

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from sac_engine import SacTag, scan, _IGNORE_DIRS, _DEFAULT_EXTS  # noqa: E402
from sac_domains import (  # noqa: E402
    normalize_repo_path,
    parse_sac_domains,
    relativize_under_root,
    sac_domains_path,
)

_ORPHAN_REASONS = {
    "no_declaration": "no symbol declaration found on this line",
    "unsupported_language": "no parser available for this language",
    "parse_error": "could not parse file",
}


@dataclass(frozen=True)
class Orphan:
    file: str
    line: int
    tag_type: str
    symbol: str
    reason: str

    def to_dict(self) -> dict:
        return {
            "file": self.file,
            "line": self.line,
            "tag_type": self.tag_type,
            "symbol": self.symbol,
            "reason": self.reason,
        }


def _is_tree_sitter_available() -> bool:
    try:
        import tree_sitter  # noqa: F401
    except ImportError:
        return False
    return True


def _load_tree_sitter_dart() -> tuple:
    try:
        from tree_sitter import Language, Parser
        import tree_sitter_dart
        dart_lang = Language(tree_sitter_dart.language())
        return (Parser, dart_lang)
    except Exception:
        return (None, None)


_PARSER_CACHE: dict[str, object] = {}


def _get_declarations_dart(content: str) -> list[tuple[int, int]]:
    if "tree_sitter" not in _PARSER_CACHE:
        result = _load_tree_sitter_dart()
        if result[0] is None:
            return []
        _PARSER_CACHE["tree_sitter"] = result

    parser_cls, dart_lang = _PARSER_CACHE["tree_sitter"]
    if parser_cls is None:
        return []

    parser = parser_cls(dart_lang)
    tree = parser.parse(bytes(content, "utf-8"))
    root = tree.root_node

    ranges: list[tuple[int, int]] = []

    def _add_declaration(node) -> None:
        start = node.start_point[0] + 1
        end = node.end_point[0] + 1
        if end >= start:
            ranges.append((start, end))

    def _walk(node) -> None:
        if node.type in (
            "class_declaration",
            "function_declaration",
            "method_declaration",
            "constructorDeclaration",
            "getterDeclaration",
            "setterDeclaration",
            "fieldDeclaration",
            "variable_declaration",
            "type_alias",
            "enum_declaration",
            "extension_declaration",
            "mixin_declaration",
        ):
            _add_declaration(node)
        for child in node.children:
            _walk(child)

    _walk(root)
    return ranges


def _get_declarations_python(content: str) -> list[tuple[int, int]]:
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return []
    ranges: list[tuple[int, int]] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            if hasattr(node, "name"):
                ranges.append((node.lineno, node.end_lineno or node.lineno))
        elif isinstance(node, ast.Assign):
            if node.col_offset == 0 and node.lineno:
                ranges.append((node.lineno, node.end_lineno or node.lineno))

    return ranges


def _is_line_declared(
    line_no: int,
    declarations: list[tuple[int, int]],
    tag_lines: set[int],
) -> bool:
    for start, end in declarations:
        # Preserve tags inside declarations and accept a contiguous SAC block
        # immediately above the signature. A blank/non-tag line breaks the block.
        if start - 1 <= line_no <= end:
            return True
        if line_no < start - 1 and all(
            candidate in tag_lines for candidate in range(line_no, start)
        ):
            return True
    return False


_LANG_EXT = {
    ".dart": "dart",
    ".py": "python",
}


def _validate_file(path: str, tags: list[SacTag]) -> tuple[list[Orphan], list[str]]:
    orphans: list[Orphan] = []
    warnings: list[str] = []

    ext = os.path.splitext(path)[1].lower()
    lang = _LANG_EXT.get(ext)

    if lang is None:
        return orphans, warnings

    try:
        with open(path, "r", encoding="utf-8", errors="surrogateescape") as fh:
            content = fh.read()
    except OSError as exc:
        warnings.append(f"{path}:0: read_error {exc}")
        return orphans, warnings

    if lang == "dart":
        if not _is_tree_sitter_available():
            warnings.append(f"{path}:0: unsupported_language dart (tree-sitter not installed)")
            return orphans, warnings
        declarations = _get_declarations_dart(content)
    elif lang == "python":
        declarations = _get_declarations_python(content)
    else:
        warnings.append(f"{path}:0: unsupported_language {lang}")
        return orphans, warnings

    if not declarations and lang == "dart":
        warnings.append(f"{path}:0: unsupported_language dart (tree-sitter-dart not available)")
        return orphans, warnings

    file_tags = [t for t in tags if t.file == path]
    tag_lines = {tag.line for tag in file_tags}
    for tag in file_tags:
        if not _is_line_declared(tag.line, declarations, tag_lines):
            orphans.append(
                Orphan(
                    file=path,
                    line=tag.line,
                    tag_type=tag.tag_type,
                    symbol=tag.symbol,
                    reason=_ORPHAN_REASONS["no_declaration"],
                )
            )

    return orphans, warnings


def validate(
    root: str,
    extra_exts: Iterable[str] | None = None,
    ignore_dirs: Iterable[str] | None = None,
) -> tuple[list[Orphan], list[str]]:
    """Scan root for orphan SAC tags.

    Args:
        root: Directory to scan.
        extra_exts: Additional file extensions to include.
        ignore_dirs: Directory names to skip.

    Returns:
        (orphans, warnings) where orphans is a list of Orphan objects
        and warnings is a list of human-readable warning strings.
    """
    warnings: list[str] = []
    all_tags = scan(
        root,
        extra_exts=extra_exts,
        ignore_dirs=ignore_dirs,
        warnings=warnings,
    )

    symbols_by_file: dict[str, set[str]] = {}
    for tag in all_tags:
        rel = normalize_repo_path(relativize_under_root(root, tag.file))
        symbols_by_file.setdefault(rel, set()).add(tag.symbol)

    for domain in parse_sac_domains(root):
        allowed_files = {
            normalize_repo_path(str(path)) for path in (domain.get("files") or [])
        }
        mapped_symbols: set[str] = set()
        for path in allowed_files:
            mapped_symbols.update(symbols_by_file.get(path, set()))
        for anchor in dict.fromkeys(domain.get("anchor_symbols") or []):
            if anchor not in mapped_symbols:
                warnings.append(
                    f"{sac_domains_path(root)}:0: UNMAPPED_ANCHOR_SYMBOL "
                    f"domain={domain.get('domain_id')} symbol={anchor}"
                )

    orphans: list[Orphan] = []
    validated_files: set[str] = set()

    for tag in all_tags:
        if tag.file in validated_files:
            continue
        validated_files.add(tag.file)
        file_orphans, file_warnings = _validate_file(tag.file, all_tags)
        orphans.extend(file_orphans)
        warnings.extend(file_warnings)

    orphans.sort(key=lambda o: (o.file, o.line))
    return orphans, warnings


def render_orphans(orphans: list[Orphan]) -> str:
    if not orphans:
        return "SAC validate: no orphan tags found."
    lines = [f"SAC validate: {len(orphans)} orphan tag(s) found:"]
    for o in orphans:
        lines.append(f"  {o.file}:{o.line} [{o.tag_type}/{o.symbol}] — {o.reason}")
    return "\n".join(lines)
