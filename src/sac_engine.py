"""Semantic Architecture Context (SAC) engine.

Stateless scanner/parser for SAC tags embedded in source-code comments.
Pure Python 3.12 stdlib; no third-party dependencies.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Iterable

# Default Context payload budget (bytes). Override via SAC_CONTEXT_MAX_BYTES.
# Overflow returns context_payload_too_large without truncating constraints.
DEFAULT_CONTEXT_MAX_BYTES = 12288


# Canonical form:  <marker> SAC:<TAG>: on=<condition> - <Symbol>: <Constraint>
# where <marker> is the language's inline comment token (// or #).
_CANONICAL_RE = re.compile(
    r"^(?P<marker>\s*(?://|#)\s*)"
    r"SAC:(?P<tag>ARCH|REGR|DEPRECATED):\s+"
    r"on=(?P<trigger>\S+)\s+"
    r"-\s+"
    r"(?P<symbol>[^:]+):\s*"
    r"(?P<constraint>.*)$"
)

# Previous canonical vocabulary. It remains readable through the same dual-parser
# flow, but maps to an empty condition because severity was never executable.
_LEGACY_CANONICAL_RE = re.compile(
    r"^(?P<marker>\s*(?://|#)\s*)"
    r"SAC:(?P<tag>ARCH|REGR|DEPRECATED):\s+"
    r"(?P<legacy_trigger>RULE|CONSTRAINT|WARNING|CRITICAL)\s+"
    r"-\s+"
    r"(?P<symbol>[^:]+):\s*"
    r"(?P<constraint>.*)$"
)

# Legacy REGR form, still parsed per contract C6:
#   // SAC:REGR: <TRIGGER> - If modifying <symbol>, ... verify: a, b.
_LEGACY_REGR_RE = re.compile(
    r"SAC:REGR:\s+(?P<legacy_trigger>WARNING|CRITICAL)\s+"
    r"-\s+"
    r"If modifying\s+(?P<symbol>[^,]+),\s+"
    r".*?"
    r"(?:verify|MUST verify|you MUST verify):\s*(?P<verify>[^;]*)",
    re.IGNORECASE,
)

# Last `verify:` on the line, comma-separated, ending at semicolon or line end.
_VERIFY_TERMINAL_RE = re.compile(
    r".*\bverify:\s*(?P<targets>[^;]*)",
    re.IGNORECASE,
)
_VERIFY_TARGET_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_.$-]*\Z")

_REPLACEMENT_TERMINAL_RE = re.compile(
    r".*\breplacement:\s*(?P<target>[A-Za-z0-9_.$:/-]+)\.?\s*$",
    re.IGNORECASE,
)

# Directories that never contain SAC tags we care about.
_IGNORE_DIRS = frozenset(
    {
        ".git",
        "node_modules",
        "build",
        "dist",
        ".dart_tool",
        "Pods",
        ".gradle",
        "coverage",
        "__pycache__",
        ".venv",
        "vendor",
        ".pub-cache",
        "sac-context",
    }
)

_SYMBOL_INDEX_REL = os.path.join(".sac", "symbol_index.json")
_SYMBOL_INDEX_LEGACY_REL = os.path.join("sac-context", ".sac", "symbol_index.json")
_DEFAULT_WARNINGS_CAP = 20

# Default extensions scanned for SAC tags.
_DEFAULT_EXTS = frozenset(
    {
        ".dart",
        ".py",
        ".ps1",
        ".js",
        ".ts",
        ".kt",
        ".swift",
        ".java",
        ".go",
        ".rs",
        ".cs",
        ".c",
        ".cc",
        ".cpp",
        ".h",
        ".hpp",
    }
)

# One-hop expansion cap per contract C12.
_HOP1_CAP = 10

# Known SAC tag types and canonical trigger matrix.
_KNOWN_TAGS = frozenset({"ARCH", "REGR", "DEPRECATED"})
_ALLOWED_TRIGGERS = {
    "ARCH": ("ssot", "boundary", "ordering", "state", "exclusive", "ownership"),
}
_LEGACY_TRIGGERS = {
    "ARCH": ("RULE", "CONSTRAINT"),
    "REGR": ("WARNING", "CRITICAL"),
    "DEPRECATED": ("WARNING", "CRITICAL"),
}
_CHANGE_TRIGGER_RE = re.compile(r"[a-z][a-z0-9_]{2,47}\Z")
_ARCH_IMPERATIVE_RE = re.compile(r"\b(?:MUST|NEVER|ONLY)\b")


@dataclass(frozen=True)
class SacTag:
    file: str
    line: int
    tag_type: str
    trigger: str
    symbol: str
    constraint: str
    verify: list[str] = field(default_factory=list)
    replacement: str | None = None

    def to_dict(self) -> dict:
        data = {
            "file": self.file,
            "line": self.line,
            "tag_type": self.tag_type,
            "trigger": self.trigger,
            "symbol": self.symbol,
            "constraint": self.constraint,
            "verify": list(self.verify),
        }
        if self.replacement is not None:
            data["replacement"] = self.replacement
        return data


def _parse_verify(constraint: str) -> tuple[list[str], list[str]]:
    """Extract the terminal verify: list from a constraint string.

    Return valid targets and a named warning for every invalid target.
    """
    match = _VERIFY_TERMINAL_RE.match(constraint)
    if not match:
        return [], []
    raw = match.group("targets").strip()
    # A final full stop terminates the sentence; dots inside targets are data.
    if raw.endswith("."):
        raw = raw[:-1].rstrip()
    targets: list[str] = []
    warnings: list[str] = []
    for item in raw.split(","):
        target = item.strip()
        if not target:
            continue
        if _VERIFY_TARGET_RE.fullmatch(target):
            targets.append(target)
        else:
            warnings.append(f"invalid_verify_target target={target}")
    return targets, warnings


def _parse_canonical(
    line: str, pattern: re.Pattern[str] = _CANONICAL_RE
) -> tuple[SacTag | None, list[str]]:
    match = pattern.match(line)
    if not match:
        return None, []
    tag_type = match.group("tag")
    legacy_trigger = match.groupdict().get("legacy_trigger")
    if legacy_trigger and legacy_trigger not in _LEGACY_TRIGGERS[tag_type]:
        return None, []
    constraint = match.group("constraint").strip()
    verify: list[str] = []
    replacement: str | None = None
    warnings: list[str] = []
    if tag_type == "REGR":
        verify, warnings = _parse_verify(constraint)
    elif tag_type == "DEPRECATED":
        replacement_match = _REPLACEMENT_TERMINAL_RE.match(constraint)
        if replacement_match:
            replacement = replacement_match.group("target")
    return SacTag(
        file="",
        line=0,
        tag_type=tag_type,
        trigger=match.groupdict().get("trigger") or "",
        symbol=match.group("symbol").strip(),
        constraint=constraint,
        verify=verify,
        replacement=replacement,
    ), warnings


def _parse_legacy_regr(line: str) -> tuple[SacTag | None, list[str]]:
    match = _LEGACY_REGR_RE.search(line)
    if not match:
        return None, []
    verify, warnings = _parse_verify(f"verify: {match.group('verify')}")
    return SacTag(
        file="",
        line=0,
        tag_type="REGR",
        trigger="",
        symbol=match.group("symbol").strip(),
        constraint=match.group(0).strip(),
        verify=verify,
    ), warnings


def _tag_contract_warnings(tag: SacTag) -> list[str]:
    """Return canonical contract warnings without hiding a parseable tag."""
    warnings: list[str] = []
    if not tag.trigger:
        pass
    elif tag.tag_type == "ARCH" and tag.trigger not in _ALLOWED_TRIGGERS["ARCH"]:
        allowed = _ALLOWED_TRIGGERS["ARCH"]
        warnings.append(
            f"invalid_trigger tag={tag.tag_type} trigger={tag.trigger} "
            f"allowed={'|'.join(allowed)}"
        )
    elif tag.tag_type in {"REGR", "DEPRECATED"} and not _CHANGE_TRIGGER_RE.fullmatch(
        tag.trigger
    ):
        warnings.append(
            f"invalid_trigger tag={tag.tag_type} trigger={tag.trigger} "
            r"allowed=[a-z][a-z0-9_]{2,47}"
        )
    if tag.tag_type == "ARCH" and not _ARCH_IMPERATIVE_RE.search(tag.constraint):
        warnings.append("arch_imperative_required")
    if tag.tag_type == "REGR" and not tag.verify:
        warnings.append("regr_verify_required")
    if tag.tag_type == "DEPRECATED" and tag.replacement is None:
        warnings.append("deprecated_replacement_required")
    return warnings


def _parse_line(line: str) -> tuple[SacTag | None, list[str]]:
    """Parse a SAC line and return every canonical contract warning."""
    if "SAC:" not in line:
        return None, []

    if "If modifying" in line:
        tag, parse_warnings = _parse_legacy_regr(line)
        if tag is not None:
            return tag, parse_warnings + ["legacy_trigger"] + _tag_contract_warnings(tag)

    tag, parse_warnings = _parse_canonical(line)
    if tag is not None:
        return tag, parse_warnings + _tag_contract_warnings(tag)

    tag, parse_warnings = _parse_canonical(line, _LEGACY_CANONICAL_RE)
    if tag is not None:
        return tag, parse_warnings + ["legacy_trigger"] + _tag_contract_warnings(tag)

    tag, parse_warnings = _parse_legacy_regr(line)
    if tag is not None:
        return tag, parse_warnings + ["legacy_trigger"] + _tag_contract_warnings(tag)

    # A SAC marker is present but did not match any supported grammar.
    return None, ["unsupported_sac_grammar"]


def _is_sac_header(line: str) -> bool:
    """Return True if the line contains a SAC marker."""
    return "SAC:" in line


def _extract_unknown_tag_warning(line: str, file: str, line_no: int) -> str | None:
    """If a SAC marker names an unknown tag type, build a warning."""
    if not _is_sac_header(line):
        return None
    # Cheap scan: SAC:<TAG>:
    m = re.search(r"SAC:([A-Za-z0-9_]+):", line)
    if not m:
        return None
    tag_type = m.group(1)
    if tag_type not in _KNOWN_TAGS:
        return f"{file}:{line_no}: unknown_tag SAC:{tag_type}"
    return None


def _scan_file(path: str, warnings: list[str]) -> list[SacTag]:
    """Scan a single file for SAC tags."""
    tags: list[SacTag] = []
    try:
        with open(path, "r", encoding="utf-8", errors="surrogateescape") as fh:
            lines = fh.readlines()
    except UnicodeDecodeError as exc:
        warnings.append(f"{path}:0: decode_error {exc}")
        return tags
    except OSError as exc:
        warnings.append(f"{path}:0: read_error {exc}")
        return tags

    for line_no, raw_line in enumerate(lines, start=1):
        line = raw_line.rstrip("\n")
        if not _is_sac_header(line):
            continue

        unknown_warning = _extract_unknown_tag_warning(line, path, line_no)
        if unknown_warning:
            warnings.append(unknown_warning)

        tag, parse_warnings = _parse_line(line)
        if tag is not None:
            tags.append(
                SacTag(
                    file=path,
                    line=line_no,
                    tag_type=tag.tag_type,
                    trigger=tag.trigger,
                    symbol=tag.symbol,
                    constraint=tag.constraint,
                    verify=tag.verify,
                    replacement=tag.replacement,
                )
            )
            warnings.extend(
                f"{path}:{line_no}: {warning}" for warning in parse_warnings
            )
        elif parse_warnings and not unknown_warning:
            # A known-tag line that still failed grammar is reported; unknown
            # tags are already reported as unknown_tag (C11).
            warnings.extend(
                f"{path}:{line_no}: {warning}" for warning in parse_warnings
            )

    return tags


def scan(
    root: str,
    extra_exts: Iterable[str] | None = None,
    ignore_dirs: Iterable[str] | None = None,
    warnings: list[str] | None = None,
) -> list[SacTag]:
    """Recursively scan ``root`` for SAC tags.

    Args:
        root: Directory to scan.
        extra_exts: Additional file extensions to include.
        ignore_dirs: Directory names to skip. Defaults to a sensible set.
        warnings: Mutable list to collect warnings.

    Returns:
        A list of ``SacTag`` objects found under ``root``.
    """
    allowed_exts = set(_DEFAULT_EXTS)
    if extra_exts:
        allowed_exts.update(ext if ext.startswith(".") else f".{ext}" for ext in extra_exts)

    skip_dirs = set(_IGNORE_DIRS)
    if ignore_dirs:
        skip_dirs.update(ignore_dirs)

    warnings = warnings if warnings is not None else []
    tags: list[SacTag] = []

    for dirpath, dirnames, filenames in os.walk(root):
        # Filter in-place so os.walk does not descend into ignored dirs.
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]

        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext not in allowed_exts:
                continue
            full_path = os.path.normpath(os.path.join(dirpath, filename))
            tags.extend(_scan_file(full_path, warnings))

    return tags


def _lookup_symbol(
    symbol: str,
    tags: list[SacTag],
    filepath: str | None = None,
) -> list[SacTag]:
    """Return all tags for ``symbol`` (and optionally filtered by filepath)."""
    matches: list[SacTag] = []
    for tag in tags:
        if tag.symbol != symbol:
            continue
        if filepath is not None and tag.file != filepath:
            continue
        matches.append(tag)
    return matches


def _expand_hop1(
    tag: SacTag,
    all_tags: list[SacTag],
    warnings: list[str],
    cap: int = _HOP1_CAP,
) -> tuple[list[dict], bool]:
    """Expand 1-hop dependencies for a REGR tag.

    Returns a tuple of (hop1_entries, truncated).
    """
    hop1: list[dict] = []
    if tag.tag_type != "REGR" or not tag.verify:
        return hop1, False

    truncated = False
    for target in tag.verify:
        if len(hop1) >= cap:
            truncated = True
            break

        target_matches = _lookup_symbol(target, all_tags)
        if target_matches:
            for target_tag in target_matches:
                if len(hop1) >= cap:
                    truncated = True
                    break
                hop1.append(
                    {
                        "symbol": target,
                        "found": True,
                        "match": target_tag.to_dict(),
                    }
                )
        else:
            hop1.append(
                {
                    "symbol": target,
                    "found": False,
                    "matches": [],
                    "untagged": True,
                }
            )

    return hop1, truncated


def _normalize_filepath(root: str, filepath: str) -> str:
    """Resolve ``filepath`` relative to ``root`` when not absolute."""
    filepath = os.path.normpath(filepath)
    if not os.path.isabs(filepath):
        filepath = os.path.normpath(os.path.join(root, filepath))
    return filepath


def _needs_hop1_root_scan(matches: list[SacTag]) -> bool:
    """True when any match is REGR with verify targets (hop1 needs root index)."""
    return any(tag.tag_type == "REGR" and tag.verify for tag in matches)


def _rel_norm_under_root(root: str, path: str) -> str | None:
    """Normalize path to repo-relative compare key; None if outside root."""
    from sac_domains import normalize_repo_path

    root_norm = os.path.normpath(root)
    abs_path = os.path.normpath(
        path if os.path.isabs(path) else os.path.join(root, path)
    )
    try:
        rel = os.path.relpath(abs_path, root_norm)
    except ValueError:
        return None
    if rel.startswith(".."):
        return None
    return normalize_repo_path(rel)


def _filter_tags_by_rel_scope(
    root: str,
    tags: list[SacTag],
    scope_rels: list[str],
) -> list[SacTag]:
    from sac_domains import normalize_repo_path

    allowed = {normalize_repo_path(p) for p in scope_rels}
    out: list[SacTag] = []
    for tag in tags:
        key = _rel_norm_under_root(root, tag.file)
        if key is not None and key in allowed:
            out.append(tag)
    return out


def scan_paths(
    paths: Iterable[str],
    warnings: list[str] | None = None,
) -> list[SacTag]:
    """Scan an explicit file list (Discover / scoped hop1)."""
    warnings = warnings if warnings is not None else []
    tags: list[SacTag] = []
    for path in paths:
        if not path or not os.path.isfile(path):
            continue
        tags.extend(_scan_file(os.path.normpath(path), warnings))
    return tags


def discover_domain(
    root: str,
    domain_id: str,
) -> dict:
    """Discover SAC tags only under domain files: (no full-repo walk).

    Token-slim inventory cards (L1): file, line, tag_type, symbol.
    REGR may include verify[]. Constraint/trigger live in Verify (L2).
    """
    from sac_domains import (
        DISCOVER_HINT,
        domain_id_required_error,
        domain_not_found_error,
        find_domain,
        parse_sac_domains,
        relativize_under_root,
        resolve_domains_manifest,
    )

    manifest_path, err = resolve_domains_manifest(root)
    if err is not None:
        return err

    wanted = (domain_id or "").strip()
    if not wanted:
        return domain_id_required_error()

    domains = parse_sac_domains(root)
    match = find_domain(domains, wanted)
    if match is None:
        return domain_not_found_error(domains, wanted, mode="discover")

    warnings: list[str] = []
    files_rel = [str(f).replace("\\", "/") for f in (match.get("files") or [])]
    missing_files: list[str] = []
    abs_paths: list[str] = []
    for rel in files_rel:
        abs_path = os.path.normpath(os.path.join(root, rel))
        if not os.path.isfile(abs_path):
            missing_files.append(rel)
            continue
        abs_paths.append(abs_path)

    tags = scan_paths(abs_paths, warnings)
    compact: list[dict] = []
    for tag in tags:
        entry = {
            "file": relativize_under_root(root, tag.file),
            "line": tag.line,
            "tag_type": tag.tag_type,
            "symbol": tag.symbol,
        }
        if tag.verify:
            entry["verify"] = list(tag.verify)
        if tag.replacement is not None:
            entry["replacement"] = tag.replacement
        compact.append(entry)

    from sac_domains import attach_gates_bypassed

    return attach_gates_bypassed({
        "mode": "discover",
        "domain_id": match.get("domain_id"),
        "index": ".sac/domains.md",
        "files_listed": len(files_rel),
        "files_scanned": len(abs_paths),
        "missing_files": missing_files,
        "tag_count": len(compact),
        "tags": compact,
        "warnings": warnings,
        "pause_hint": DISCOVER_HINT,
        "hint_tool": "get_sac_constraints",
    })


def build_domain_context(root: str, domain_id: str) -> dict:
    """Build a compact overlay from anchors plus every REGR/DEPRECATED tag."""
    from sac_domains import (
        domain_id_required_error,
        domain_not_found_error,
        find_domain,
        parse_sac_domains,
        relativize_under_root,
        resolve_domains_manifest,
    )

    manifest_path, err = resolve_domains_manifest(root)
    if err is not None:
        return err

    wanted = (domain_id or "").strip()
    if not wanted:
        return domain_id_required_error()

    domains = parse_sac_domains(root)
    domain = find_domain(domains, wanted)
    if domain is None:
        return domain_not_found_error(domains, wanted, mode="context")

    warnings: list[str] = []
    files_rel = [str(f).replace("\\", "/") for f in (domain.get("files") or [])]
    missing_files: list[str] = []
    abs_paths: list[str] = []
    for rel in files_rel:
        abs_path = os.path.normpath(os.path.join(root, rel))
        if not os.path.isfile(abs_path):
            missing_files.append(rel)
            continue
        abs_paths.append(abs_path)

    tags = scan_paths(abs_paths, warnings)
    anchors = [str(s) for s in (domain.get("anchor_symbols") or [])]
    anchor_set = set(anchors)
    selected = [
        tag
        for tag in tags
        if tag.symbol in anchor_set or tag.tag_type in {"REGR", "DEPRECATED"}
    ]
    tagged_symbols = {tag.symbol for tag in tags}
    constraints: list[dict] = []
    any_truncated = False

    for tag in selected:
        hop1, truncated = _expand_hop1(tag, tags, warnings)
        any_truncated = any_truncated or truncated
        compact_hop1: list[dict] = []
        for entry in hop1:
            compact_entry = {
                "symbol": entry.get("symbol"),
                "found": bool(entry.get("found")),
            }
            if compact_entry["found"]:
                target = dict(entry.get("match") or {})
                target["file"] = relativize_under_root(root, target.get("file", ""))
                compact_entry["match"] = target
            else:
                compact_entry["untagged"] = True
            compact_hop1.append(compact_entry)

        item = tag.to_dict()
        item["file"] = relativize_under_root(root, tag.file)
        item["hop1"] = compact_hop1
        constraints.append(item)

    intent = str(domain.get("intent") or domain.get("summary") or "").strip()
    missing_anchors = [
        anchor for anchor in anchors if anchor not in tagged_symbols
    ]
    payload = {
        "mode": "context",
        "domain_id": domain.get("domain_id"),
        "intent": intent,
        "files_listed": len(files_rel),
        "files_scanned": len(abs_paths),
        "missing_files": missing_files,
        "anchors_requested": anchors,
        "missing_anchors": missing_anchors,
        "selected_count": len(constraints),
        "constraints": constraints,
        "known_gaps": domain.get("known_gaps") or "",
        "truncated": any_truncated,
        "warnings": warnings,
    }

    raw_limit = os.environ.get(
        "SAC_CONTEXT_MAX_BYTES", str(DEFAULT_CONTEXT_MAX_BYTES)
    )
    try:
        max_bytes = int(raw_limit)
    except ValueError:
        return {
            "error": True,
            "code": "invalid_context_payload_limit",
            "message": "SAC_CONTEXT_MAX_BYTES must be an integer >= 512.",
        }
    if max_bytes < 512:
        return {
            "error": True,
            "code": "invalid_context_payload_limit",
            "message": "SAC_CONTEXT_MAX_BYTES must be an integer >= 512.",
        }

    payload_bytes = len(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    )
    if payload_bytes > max_bytes:
        return {
            "error": True,
            "code": "context_payload_too_large",
            "mode": "context",
            "domain_id": domain.get("domain_id"),
            "source_payload_bytes": payload_bytes,
            "max_payload_bytes": max_bytes,
            "selected_count": len(constraints),
            "missing_anchor_count": len(missing_anchors),
            "message": "Context exceeds the configured token budget; no constraints were returned.",
            "required_action": "Use discover_sac for scoped inventory, then get_sac_constraints for precise targets.",
            "hint_tool": "discover_sac",
        }
    from sac_domains import attach_gates_bypassed

    return attach_gates_bypassed(payload)


def symbol_index_path(root: str) -> str:
    """Absolute path to the per-project symbol index artifact."""
    return os.path.normpath(os.path.join(root, _SYMBOL_INDEX_REL))


def _tag_from_dict(data: dict) -> SacTag:
    return SacTag(
        file=data.get("file", ""),
        line=int(data.get("line", 0)),
        tag_type=data.get("tag_type", ""),
        trigger=data.get("trigger", ""),
        symbol=data.get("symbol", ""),
        constraint=data.get("constraint", ""),
        verify=list(data.get("verify") or []),
        replacement=data.get("replacement"),
    )


def _tags_from_symbol_index(index: dict) -> list[SacTag]:
    tags: list[SacTag] = []
    for entries in index.get("symbols", {}).values():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if isinstance(entry, dict):
                tags.append(_tag_from_dict(entry))
    return tags


def load_symbol_index(root: str) -> dict | None:
    path = symbol_index_path(root)
    if not os.path.isfile(path):
        legacy_path = os.path.normpath(os.path.join(root, _SYMBOL_INDEX_LEGACY_REL))
        if os.path.isfile(legacy_path):
            path = legacy_path
        else:
            return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None
    if data.get("version") != 1 or not isinstance(data.get("symbols"), dict):
        return None
    return data


def build_symbol_index(
    root: str,
    extra_exts: Iterable[str] | None = None,
    ignore_dirs: Iterable[str] | None = None,
) -> dict:
    """Build a symbol index dict from a full scan (excludes sac-context via ignore_dirs)."""
    warnings: list[str] = []
    tags = scan(
        root,
        extra_exts=extra_exts,
        ignore_dirs=ignore_dirs,
        warnings=warnings,
    )
    symbols: dict[str, list[dict]] = {}
    for tag in tags:
        symbols.setdefault(tag.symbol, []).append(tag.to_dict())
    return {
        "version": 1,
        "root": os.path.normpath(root),
        "tag_count": len(tags),
        "symbols": symbols,
        "build_warnings": warnings,
    }


def write_symbol_index(
    root: str,
    extra_exts: Iterable[str] | None = None,
    ignore_dirs: Iterable[str] | None = None,
) -> dict:
    """Build and persist ``symbol_index.json`` under ``sac-context/.sac/``."""
    index = build_symbol_index(root, extra_exts=extra_exts, ignore_dirs=ignore_dirs)
    out_path = symbol_index_path(root)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(
            {k: v for k, v in index.items() if k != "build_warnings"},
            fh,
            indent=1,
        )
        fh.write("\n")
    index["index_path"] = out_path
    return index


def check_symbol_index(
    root: str,
    extra_exts: Iterable[str] | None = None,
    ignore_dirs: Iterable[str] | None = None,
) -> dict:
    """Compare on-disk index to a fresh scan (no write).

    Returns a result dict with ``ok`` True only when the file exists, is valid,
    and ``tag_count`` + ``symbols`` match a fresh ``build_symbol_index``.
    """
    path = symbol_index_path(root)
    existing = load_symbol_index(root)
    if existing is None:
        return {
            "ok": False,
            "reason": "missing_or_invalid",
            "index_path": path,
            "expected_tag_count": None,
            "actual_tag_count": None,
        }

    fresh = build_symbol_index(root, extra_exts=extra_exts, ignore_dirs=ignore_dirs)
    expected_count = existing.get("tag_count")
    actual_count = fresh.get("tag_count")
    symbols_match = existing.get("symbols") == fresh.get("symbols")
    count_match = expected_count == actual_count
    ok = bool(symbols_match and count_match)
    return {
        "ok": ok,
        "reason": "fresh" if ok else "stale",
        "index_path": path,
        "expected_tag_count": expected_count,
        "actual_tag_count": actual_count,
        "build_warnings": list(fresh.get("build_warnings") or []),
    }


def _resolve_hop1_tags(
    root: str,
    matches: list[SacTag],
    file_tags: list[SacTag],
    extra_exts: Iterable[str] | None,
    ignore_dirs: Iterable[str] | None,
    warnings: list[str],
    hop1_scope_rels: list[str] | None = None,
) -> list[SacTag]:
    if not _needs_hop1_root_scan(matches):
        return file_tags

    index = load_symbol_index(root)
    if index is not None:
        tags = _tags_from_symbol_index(index)
        if hop1_scope_rels is not None:
            tags = _filter_tags_by_rel_scope(root, tags, hop1_scope_rels)
            warnings.append(f"{root}:0: hop1_via_symbol_index_scoped")
        else:
            warnings.append(f"{root}:0: hop1_via_symbol_index")
        return tags

    if hop1_scope_rels is not None:
        abs_paths = [
            os.path.normpath(os.path.join(root, rel)) for rel in hop1_scope_rels
        ]
        warnings.append(f"{root}:0: hop1_domain_scan_no_index")
        return scan_paths(abs_paths, warnings)

    warnings.append(f"{root}:0: hop1_full_scan_no_index")
    return scan(
        root,
        extra_exts=extra_exts,
        ignore_dirs=ignore_dirs,
        warnings=warnings,
    )


def _trim_warnings(
    warnings: list[str],
    cap: int | None,
) -> tuple[list[str], bool]:
    if cap is None or cap <= 0 or len(warnings) <= cap:
        return warnings, False
    return warnings[:cap], True


def lookup(
    symbol: str,
    root: str,
    filepath: str | None = None,
    extra_exts: Iterable[str] | None = None,
    ignore_dirs: Iterable[str] | None = None,
    trim_warnings_cap: int | None = None,
    hop1_scope_rels: list[str] | None = None,
) -> dict:
    """Look up SAC context for ``symbol`` under ``root``.

    When ``filepath`` is set, only that file is parsed for symbol matches.
    REGR hop1 prefers ``symbol_index.json`` filtered by ``hop1_scope_rels``
    (domain files:). Without scope, uses full index or announced full scan.
    Without ``filepath``, behavior is a full root scan (CLI/smoke only).

    Returns a JSON-serializable dict with all matches, 1-hop expansion,
    truncation flag, and warnings.
    """
    warnings: list[str] = []

    if filepath is not None:
        filepath = _normalize_filepath(root, filepath)
        file_tags = _scan_file(filepath, warnings)
        matches = _lookup_symbol(symbol, file_tags)
        all_tags = _resolve_hop1_tags(
            root,
            matches,
            file_tags,
            extra_exts,
            ignore_dirs,
            warnings,
            hop1_scope_rels=hop1_scope_rels,
        )
    else:
        all_tags = scan(
            root,
            extra_exts=extra_exts,
            ignore_dirs=ignore_dirs,
            warnings=warnings,
        )
        matches = _lookup_symbol(symbol, all_tags, filepath)

    trimmed_warnings, warnings_truncated = _trim_warnings(warnings, trim_warnings_cap)

    result = {
        "found": bool(matches),
        "matches": [],
        "truncated": False,
        "warnings": trimmed_warnings,
        "warnings_truncated": warnings_truncated,
    }

    from sac_domains import attach_gates_bypassed

    if not matches:
        return attach_gates_bypassed(result)

    any_truncated = False
    for tag in matches:
        hop1, truncated = _expand_hop1(tag, all_tags, warnings)
        if truncated:
            any_truncated = True
        match_dict = tag.to_dict()
        match_dict["hop1"] = hop1
        result["matches"].append(match_dict)

    result["truncated"] = any_truncated
    return attach_gates_bypassed(result)


_CANONICAL_WARNING_MARKERS = (
    "invalid_trigger",
    "invalid_verify_target",
    "arch_imperative_required",
    "regr_verify_required",
    "deprecated_replacement_required",
    "unsupported_sac_grammar",
)


def _context_byte_metrics(root: str, domain_id: str) -> tuple[int, int, str] | dict:
    """Return (payload_bytes, max_bytes, payload_status) or an error payload dict."""
    probe = build_domain_context(root, domain_id)
    if probe.get("code") == "context_payload_too_large":
        return (
            int(probe["source_payload_bytes"]),
            int(probe["max_payload_bytes"]),
            "OVER_BUDGET",
        )
    if probe.get("error"):
        return probe
    raw_limit = os.environ.get(
        "SAC_CONTEXT_MAX_BYTES", str(DEFAULT_CONTEXT_MAX_BYTES)
    )
    try:
        max_bytes = int(raw_limit)
    except ValueError:
        max_bytes = DEFAULT_CONTEXT_MAX_BYTES
    if max_bytes < 512:
        max_bytes = DEFAULT_CONTEXT_MAX_BYTES
    payload_bytes = len(
        json.dumps(probe, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    )
    status = "OK" if payload_bytes <= max_bytes else "OVER_BUDGET"
    return payload_bytes, max_bytes, status


def _slim_tag_card(root: str, tag: SacTag) -> dict:
    from sac_domains import relativize_under_root

    card = {
        "file": relativize_under_root(root, tag.file),
        "line": tag.line,
        "tag_type": tag.tag_type,
        "symbol": tag.symbol,
    }
    if tag.verify:
        card["verify"] = list(tag.verify)
    if tag.replacement is not None:
        card["replacement"] = tag.replacement
    return card


def _tag_has_contract_warning(tag: SacTag, file_warnings: list[str]) -> bool:
    if _tag_contract_warnings(tag):
        return True
    needle = f":{tag.line}:"
    for warning in file_warnings:
        if needle not in warning:
            continue
        if any(marker in warning for marker in _CANONICAL_WARNING_MARKERS):
            return True
    return False


# Closed structural fitness: scenario → required tag_type (no new SAC tags; 5-col claims).
_SCENARIO_REQUIRED_TAG_TYPE = {
    "SUMMARY": "ARCH",
    "EXTEND": "ARCH",
    "REGRESSION": "REGR",
    "MIGRATION": "ARCH",
}


def _context_selected_keys(
    root: str,
    tags: list[SacTag],
    anchor_symbols: list[str],
) -> set[tuple[str, str, str]]:
    """Keys (filepath_norm, symbol, tag_type) that get_sac_context would select."""
    from sac_domains import normalize_repo_path, relativize_under_root

    anchors = set(anchor_symbols)
    selected: set[tuple[str, str, str]] = set()
    for tag in tags:
        if tag.symbol in anchors or tag.tag_type in {"REGR", "DEPRECATED"}:
            rel = relativize_under_root(root, tag.file)
            selected.add((normalize_repo_path(rel), tag.symbol, tag.tag_type))
    return selected


def _evaluate_context_fitness(
    *,
    scenarios: list[str],
    declared_claims: list[dict],
    matched_claims: list[dict],
    context_selected: set[tuple[str, str, str]],
) -> dict[str, Any]:
    """Fitness axis B: domain usable for agent context assembly.

    Payload budget (axis C) is evaluated separately and must not force OVER_SELECT.
    """
    from sac_domains import normalize_repo_path

    uncovered_scenarios: list[str] = []
    missing_roles: list[str] = []
    context_unfit_claims: list[dict] = []

    # Prefer matched claims for role coverage; fall back to declared for TOO_THIN signal.
    pool = matched_claims if matched_claims else declared_claims
    for scenario in scenarios:
        required_type = _SCENARIO_REQUIRED_TAG_TYPE.get(scenario)
        if not required_type:
            continue
        role_key = f"{scenario}:{required_type}"
        if not any(
            c.get("scenario") == scenario and c.get("tag_type") == required_type
            for c in pool
        ):
            uncovered_scenarios.append(scenario)
            missing_roles.append(role_key)

    for claim in matched_claims:
        key = (
            normalize_repo_path(claim["filepath"]),
            claim["symbol"],
            claim["tag_type"],
        )
        if key not in context_selected:
            context_unfit_claims.append(dict(claim))

    contracted_in_context = 0
    for claim in matched_claims:
        key = (
            normalize_repo_path(claim["filepath"]),
            claim["symbol"],
            claim["tag_type"],
        )
        if key in context_selected:
            contracted_in_context += 1
    uncontracted_context_count = max(0, len(context_selected) - contracted_in_context)

    if uncovered_scenarios or missing_roles:
        fitness = "TOO_THIN"
    elif context_unfit_claims:
        fitness = "UNFIT"
    elif uncontracted_context_count > 0:
        # Selected Context tags beyond declared claims (surface beyond contract).
        # OVER_BUDGET is axis C only — does not force OVER_SELECT.
        fitness = "OVER_SELECT"
    else:
        fitness = "FIT"

    return {
        "fitness_status": fitness,
        "uncovered_scenarios": sorted(set(uncovered_scenarios)),
        "missing_roles": sorted(set(missing_roles)),
        "context_unfit_claims": sorted(
            context_unfit_claims,
            key=lambda c: (
                c.get("claim_id", ""),
                c.get("filepath", ""),
                c.get("symbol", ""),
                c.get("tag_type", ""),
            ),
        ),
        "uncontracted_context_tag_count": uncontracted_context_count,
        "context_selected_tag_count": len(context_selected),
    }


def assess_domain_capillarity(root: str, domain_id: str) -> dict:
    """On-demand capillarity: claim coverage (A) + context fitness (B) + payload (C)."""
    from sac_domains import (
        capillarity_contract_from_domain,
        domain_id_required_error,
        domain_not_found_error,
        find_domain,
        normalize_repo_path,
        parse_sac_domains,
        relativize_under_root,
        resolve_domains_manifest,
    )

    manifest_path, err = resolve_domains_manifest(root)
    if err is not None:
        return err

    wanted = (domain_id or "").strip()
    if not wanted:
        return domain_id_required_error()

    domains = parse_sac_domains(root)
    domain = find_domain(domains, wanted)
    if domain is None:
        return domain_not_found_error(domains, wanted, mode="capillarity")

    contract = capillarity_contract_from_domain(domain)
    metrics = _context_byte_metrics(root, wanted)
    if isinstance(metrics, dict):
        return metrics
    context_payload_bytes, max_payload_bytes, payload_status = metrics

    warnings: list[str] = []
    files_rel = [str(f).replace("\\", "/") for f in (domain.get("files") or [])]
    missing_files: list[str] = []
    abs_paths: list[str] = []
    for rel in files_rel:
        abs_path = os.path.normpath(os.path.join(root, rel))
        if not os.path.isfile(abs_path):
            missing_files.append(rel)
            continue
        abs_paths.append(abs_path)

    tags = scan_paths(abs_paths, warnings)
    anchors = [str(s) for s in (domain.get("anchor_symbols") or [])]
    context_selected = _context_selected_keys(root, tags, anchors)

    def _quality(status: str, fitness: str | None) -> str:
        # Axis C OVER_BUDGET is WARN-only when coverage (A) is SUFFICIENT and
        # fitness (B) is FIT. MUST NOT thin files:/tags/claims to chase PASS.
        if status == "SUFFICIENT" and fitness == "FIT":
            if payload_status in {"OK", "OVER_BUDGET"}:
                return "PASS"
        return "FAIL"

    payload_warn = "OVER_BUDGET" if payload_status == "OVER_BUDGET" else None

    def _base(status: str, *, coverage=None, required=0, minimum=0) -> dict:
        fitness_block = {
            "fitness_status": None,
            "uncovered_scenarios": [],
            "missing_roles": [],
            "context_unfit_claims": [],
            "uncontracted_context_tag_count": 0,
            "context_selected_tag_count": len(context_selected),
        }
        return {
            "mode": "capillarity",
            "domain_id": domain.get("domain_id"),
            "status": status,
            "quality_status": _quality(status, None),
            "context_scenarios": list(contract.get("context_scenarios") or []),
            "required_claim_count": required,
            "minimum_source_tag_lines": minimum,
            "matched_claim_count": 0,
            "matched_source_tag_lines": 0,
            "missing_source_tag_lines": 0,
            "claim_coverage_pct": coverage,
            "missing_claims": [],
            "invalid_claims": list(contract.get("invalid_claims") or []),
            "non_contract_tag_count": 0,
            "non_contract_tags": [],
            "files_listed": len(files_rel),
            "files_scanned": len(abs_paths),
            "missing_files": missing_files,
            "context_payload_bytes": context_payload_bytes,
            "max_payload_bytes": max_payload_bytes,
            "payload_status": payload_status,
            "payload_warn": payload_warn,
            "warnings": list(warnings),
            **fitness_block,
        }

    if contract["status"] == "UNRATED":
        non_contract = sorted(
            (_slim_tag_card(root, tag) for tag in tags),
            key=lambda c: (c["file"], c["symbol"], c["tag_type"], c["line"]),
        )
        payload = _base("UNRATED")
        payload["non_contract_tag_count"] = len(non_contract)
        payload["non_contract_tags"] = non_contract
        # Legado: sem contrato não há fitness avaliável; payload ainda reportado.
        return payload

    if contract["status"] == "INVALID_CONTRACT":
        return _base(
            "INVALID_CONTRACT",
            required=len(contract.get("coverage_claims") or []),
            minimum=int(contract.get("minimum_source_tag_lines") or 0),
        )

    claims = list(contract.get("coverage_claims") or [])
    required_tuples = list(contract.get("required_tag_tuples") or [])
    scenarios = list(contract.get("context_scenarios") or [])

    by_tuple: dict[tuple[str, str, str], list[SacTag]] = {}
    for tag in tags:
        rel = relativize_under_root(root, tag.file)
        key = (normalize_repo_path(rel), tag.symbol, tag.tag_type)
        by_tuple.setdefault(key, []).append(tag)

    matched_claims: list[dict] = []
    missing_claims: list[dict] = []
    matched_tuple_keys: set[tuple[str, str, str]] = set()
    extra_warnings: list[str] = []

    for claim in claims:
        key = (
            normalize_repo_path(claim["filepath"]),
            claim["symbol"],
            claim["tag_type"],
        )
        candidates = by_tuple.get(key) or []
        chosen: SacTag | None = None
        for tag in candidates:
            if not _tag_has_contract_warning(tag, warnings):
                chosen = tag
                break
        if chosen is None:
            for tag in candidates:
                for w in _tag_contract_warnings(tag):
                    extra_warnings.append(
                        f"{relativize_under_root(root, tag.file)}:{tag.line}: {w}"
                    )
            missing_claims.append(dict(claim))
            continue
        matched_claims.append(dict(claim))
        matched_tuple_keys.add(key)

    missing_tuple_count = 0
    for tup in required_tuples:
        key = (
            normalize_repo_path(tup["filepath"]),
            tup["symbol"],
            tup["tag_type"],
        )
        if key not in matched_tuple_keys:
            missing_tuple_count += 1

    declared_keys = {
        (
            normalize_repo_path(t["filepath"]),
            t["symbol"],
            t["tag_type"],
        )
        for t in required_tuples
    }
    non_contract = []
    for tag in tags:
        rel = relativize_under_root(root, tag.file)
        key = (normalize_repo_path(rel), tag.symbol, tag.tag_type)
        if key not in declared_keys:
            non_contract.append(_slim_tag_card(root, tag))
    non_contract.sort(
        key=lambda c: (c["file"], c["symbol"], c["tag_type"], c["line"])
    )

    required_claim_count = len(claims)
    matched_claim_count = len(matched_claims)
    coverage = (
        round(100.0 * matched_claim_count / required_claim_count, 4)
        if required_claim_count
        else None
    )

    status = "SUFFICIENT"
    if missing_claims or missing_tuple_count:
        status = "INSUFFICIENT"
    for tag in tags:
        rel = relativize_under_root(root, tag.file)
        key = (normalize_repo_path(rel), tag.symbol, tag.tag_type)
        if key in declared_keys and _tag_has_contract_warning(tag, warnings):
            status = "INSUFFICIENT"
            break

    fitness = _evaluate_context_fitness(
        scenarios=scenarios,
        declared_claims=claims,
        matched_claims=matched_claims,
        context_selected=context_selected,
    )

    missing_claims.sort(
        key=lambda c: (
            c.get("claim_id", ""),
            c.get("filepath", ""),
            c.get("symbol", ""),
            c.get("tag_type", ""),
        )
    )

    from sac_domains import attach_gates_bypassed

    return attach_gates_bypassed({
        "mode": "capillarity",
        "domain_id": domain.get("domain_id"),
        "status": status,
        "quality_status": _quality(status, fitness["fitness_status"]),
        "context_scenarios": scenarios,
        "required_claim_count": required_claim_count,
        "minimum_source_tag_lines": len(required_tuples),
        "matched_claim_count": matched_claim_count,
        "matched_source_tag_lines": len(matched_tuple_keys),
        "missing_source_tag_lines": missing_tuple_count,
        "claim_coverage_pct": coverage,
        "missing_claims": missing_claims,
        "invalid_claims": [],
        "non_contract_tag_count": len(non_contract),
        "non_contract_tags": non_contract,
        "files_listed": len(files_rel),
        "files_scanned": len(abs_paths),
        "missing_files": missing_files,
        "context_payload_bytes": context_payload_bytes,
        "max_payload_bytes": max_payload_bytes,
        "payload_status": payload_status,
        "payload_warn": payload_warn,
        "warnings": list(warnings) + extra_warnings,
        **fitness,
    })


def main() -> None:
    import sys

    args = sys.argv[1:]
    if len(args) < 2:
        print("usage: python sac_engine.py <command> <symbol> [root]", file=sys.stderr)
        sys.exit(2)
    command, symbol, *rest = args
    root = rest[0] if rest else os.getcwd()
    if command != "lookup":
        print(f"unknown command: {command}", file=sys.stderr)
        sys.exit(2)
    print(json.dumps(lookup(symbol, root), indent=1))


if __name__ == "__main__":
    main()
