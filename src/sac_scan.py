#!/usr/bin/env python3
"""SAC scanner CLI.

Stateless command-line surface for the SAC engine. Pure Python 3.12 stdlib.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

# Make the script runnable both as `python sac-context/src/sac_scan.py` and from the
# project root, without requiring `tools` to be a Python package.
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from sac_engine import (  # noqa: E402
    assess_domain_capillarity,
    build_domain_context,
    check_symbol_index,
    discover_domain,
    lookup,
    symbol_index_path,
    write_symbol_index,
)
from sac_domains import (  # noqa: E402
    attach_gates_bypassed,
    filepath_membership_error,
    filepath_required_error,
    list_sac_domains_payload,
    relativize_under_root,
    resolve_hop1_scope_rels,
)
from sac_diff import run_diff_check  # noqa: E402
from sac_validate import validate, render_orphans, Orphan  # noqa: E402


class SacArgumentParser(argparse.ArgumentParser):
    """Custom ArgumentParser emitting structured JSON on usage errors with exit code 2."""

    def error(self, message: str) -> None:
        payload = {
            "error": True,
            "code": "sac.environment.invalid_arguments",
            "message": message,
            "remediation": "Check command-line syntax.",
        }
        print(json.dumps(payload, indent=1))
        sys.exit(2)


def validate_root(root: str) -> dict[str, Any] | None:
    """Validate that root path exists and is a directory."""
    if not os.path.exists(root):
        return {
            "error": True,
            "code": "sac.environment.root_not_found",
            "message": f"Root directory does not exist: {root}",
            "root": root,
            "remediation": "Ensure the specified --root path exists.",
        }
    if not os.path.isdir(root):
        return {
            "error": True,
            "code": "sac.environment.root_not_directory",
            "message": f"Root path is not a directory: {root}",
            "root": root,
            "remediation": "Specify a valid directory path for --root.",
        }
    return None


def resolve_package_version() -> str:
    """Resolve project version from mcp/package.json (SSOT).

    Fails explicitly with a descriptive error and exit != 0 if unreadable or invalid.
    Never falls back to a default version.
    """
    pkg_path = Path(__file__).resolve().parent.parent / "mcp" / "package.json"
    try:
        with open(pkg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        version = data.get("version")
        if not version or not isinstance(version, str) or not version.strip():
            raise ValueError(f"Invalid or missing 'version' field in {pkg_path}")
        return version.strip()
    except Exception as exc:
        print(f"error: failed to read project version from {pkg_path}: {exc}", file=sys.stderr)
        sys.exit(1)


def _build_parser() -> SacArgumentParser:
    version = resolve_package_version()
    parser = SacArgumentParser(
        prog="sac_scan",
        description="Semantic Architecture Context (SAC) scanner.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=version,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    lookup_parser = subparsers.add_parser(
        "lookup",
        help="Look up SAC context for a symbol.",
    )
    lookup_parser.add_argument(
        "symbol",
        help="Symbol name to look up.",
    )
    lookup_parser.add_argument(
        "--root",
        default=os.getcwd(),
        help="Root directory to scan (default: current working directory).",
    )
    lookup_parser.add_argument(
        "--path",
        dest="filepath",
        default=None,
        help=(
            "Required for execution lookups (relative or absolute file). "
            "Without --path, exit 1 unless SAC_ALLOW_UNSCOPED=1 (CI/debug only). "
            "Hop1 scopes to domain files: when domains exist; else index/full scan."
        ),
    )
    lookup_parser.add_argument(
        "--pre-onboard",
        action="store_true",
        help=(
            "Verify a human-approved physical tag before its path is added to "
            "SAC_domains.md. Requires --path, forbids --domain, and scans only "
            "that explicit repo-local file."
        ),
    )
    lookup_parser.add_argument(
        "--domain",
        dest="domain_id",
        default=None,
        help=(
            "Optional domain_id: membership must be in that domain's files:; "
            "hop1 scopes to that domain."
        ),
    )
    lookup_parser.add_argument(
        "--trim-warnings",
        type=int,
        default=None,
        metavar="N",
        help="Cap warnings in JSON output (default: no cap; MCP uses SAC_TRIM_WARNINGS).",
    )
    lookup_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit raw engine JSON to stdout.",
    )

    diff_parser = subparsers.add_parser(
        "diff-check",
        help="Check a diff for SAC:REGR violations.",
    )
    diff_parser.add_argument(
        "--patch",
        default=None,
        help="Path to a unified diff patch file (mutually exclusive with --base).",
    )
    diff_parser.add_argument(
        "--base",
        default=None,
        help="Git base ref to diff against (mutually exclusive with --patch).",
    )
    diff_parser.add_argument(
        "--root",
        default=os.getcwd(),
        help="Project root (default: current working directory).",
    )
    diff_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit structured JSON report to stdout.",
    )

    validate_parser = subparsers.add_parser(
        "validate",
        help="Detect orphan SAC:ARCH/SAC:REGR/SAC:DEPRECATED tags via AST.",
    )
    validate_parser.add_argument(
        "--root",
        default=os.getcwd(),
        help="Root directory to scan (default: current working directory).",
    )
    validate_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit structured JSON report to stdout.",
    )
    validate_parser.add_argument(
        "--warning-only",
        action="store_true",
        dest="warning_only",
        help="Exit 0 even if orphan tags are detected (warning mode).",
    )

    index_parser = subparsers.add_parser(
        "index-build",
        help="Build .sac/symbol_index.json for hop1 lookups.",
    )
    index_parser.add_argument(
        "--root",
        default=os.getcwd(),
        help="Project root (default: current working directory).",
    )
    index_parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "Do not write. Exit 0 if on-disk index matches a fresh scan; "
            "exit 1 if missing, invalid, or stale."
        ),
    )
    index_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit build/check summary JSON to stdout.",
    )

    domains_parser = subparsers.add_parser(
        "list-domains",
        help=(
            "Route catalog from SAC_domains.md (compact modules). "
            "Pass --domain to expand files/anchors for one module."
        ),
    )
    domains_parser.add_argument(
        "--root",
        default=os.getcwd(),
        help="Project root (default: current working directory).",
    )
    domains_parser.add_argument(
        "--domain",
        dest="domain_id",
        default=None,
        help="Expand one domain_id (files + anchors). Omit for compact catalog.",
    )
    domains_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON payload (default for agents; always structured).",
    )

    discover_parser = subparsers.add_parser(
        "discover",
        help=(
            "Discover SAC tags only under one domain's files: "
            "(no full-repo walk)."
        ),
    )
    discover_parser.add_argument(
        "--domain",
        dest="domain_id",
        required=True,
        help="domain_id to discover (required).",
    )
    discover_parser.add_argument(
        "--root",
        default=os.getcwd(),
        help="Project root (default: current working directory).",
    )
    discover_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON payload (always structured for agents).",
    )

    context_parser = subparsers.add_parser(
        "context",
        help="Build a compact domain overlay from anchors and REGR/DEPRECATED tags.",
    )
    context_parser.add_argument(
        "--domain",
        dest="domain_id",
        required=True,
        help="domain_id to assemble (required).",
    )
    context_parser.add_argument(
        "--root",
        default=os.getcwd(),
        help="Project root (default: current working directory).",
    )
    context_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON payload (always structured for agents).",
    )

    capillarity_parser = subparsers.add_parser(
        "capillarity",
        help=(
            "On-demand capillarity assessor for one domain "
            "(claims vs physical SAC tags; never part of boot)."
        ),
    )
    capillarity_parser.add_argument(
        "--domain",
        dest="domain_id",
        required=True,
        help="domain_id to assess (required).",
    )
    capillarity_parser.add_argument(
        "--root",
        default=os.getcwd(),
        help="Project root (default: current working directory).",
    )
    capillarity_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON payload (always structured for agents).",
    )

    return parser


def _render_hop1(hop1: list[dict]) -> list[str]:
    lines: list[str] = []
    for entry in hop1:
        symbol = entry.get("symbol", "?")
        found = entry.get("found", False)
        if not found:
            lines.append(f"    ? {symbol} (untagged / not found)")
            continue
        match = entry.get("match", {})
        file_path = match.get("file", "?")
        line_no = match.get("line", 0)
        tag_type = match.get("tag_type", "?")
        constraint = match.get("constraint", "")
        lines.append(
            f"    -> {file_path}:{line_no} [{tag_type}] {symbol}"
        )
        if constraint:
            lines.append(f"       {constraint}")
    return lines


def _render_lookup(result: dict) -> str:
    lines: list[str] = []
    if not result.get("found"):
        lines.append("SAC: symbol not found.")
        lines.append(f"matches: {len(result.get('matches', []))}")
        lines.append(f"truncated: {result.get('truncated', False)}")
        lines.append(f"warnings: {len(result.get('warnings', []))}")
    else:
        lines.append("SAC context:")
        for match in result.get("matches", []):
            file_path = match.get("file", "?")
            line_no = match.get("line", 0)
            tag_type = match.get("tag_type", "?")
            symbol = match.get("symbol", "?")
            trigger = match.get("trigger", "?")
            constraint = match.get("constraint", "")
            verify = match.get("verify", [])
            hop1 = match.get("hop1", [])

            lines.append(
                f"\n{file_path}:{line_no} [{tag_type}/{trigger}] {symbol}"
            )
            if constraint:
                lines.append(f"  constraint: {constraint}")
            if verify:
                lines.append(f"  verify: {', '.join(verify)}")
            if hop1:
                lines.append("  hop1:")
                lines.extend(_render_hop1(hop1))

    warnings = result.get("warnings", [])
    if warnings:
        lines.append("\nwarnings:")
        for warning in warnings:
            lines.append(f"  - {warning}")

    if result.get("truncated"):
        lines.append("\nnote: hop1 expansion truncated (limit 10).")

    return "\n".join(lines)


def _resolve_trim_cap(explicit: int | None) -> int | None:
    if explicit is not None:
        return explicit
    raw = os.environ.get("SAC_TRIM_WARNINGS", "").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def _cmd_lookup(args: argparse.Namespace) -> int:
    root_err = validate_root(args.root)
    if root_err is not None:
        print(json.dumps(root_err, indent=1))
        return 2

    filepath = (args.filepath or "").strip() or None
    domain_id = (getattr(args, "domain_id", None) or "").strip() or None
    pre_onboard = bool(getattr(args, "pre_onboard", False))
    if pre_onboard and filepath is None:
        payload = filepath_required_error()
        print(json.dumps(payload, indent=1))
        return 1
    if filepath is None:
        allow = (os.environ.get("SAC_ALLOW_UNSCOPED") or "").strip() == "1"
        if not allow:
            payload = filepath_required_error()
            print(json.dumps(payload, indent=1))
            return 1
    elif pre_onboard:
        if domain_id is not None:
            payload = {
                "error": True,
                "code": "pre_onboard_domain_forbidden",
                "message": "--pre-onboard verifies an explicit path before domain membership; omit --domain.",
            }
            print(json.dumps(payload, indent=1))
            return 1
        root_abs = os.path.abspath(args.root)
        path_abs = os.path.abspath(
            filepath if os.path.isabs(filepath) else os.path.join(root_abs, filepath)
        )
        try:
            inside_root = os.path.commonpath([root_abs, path_abs]) == root_abs
        except ValueError:
            inside_root = False
        if not inside_root:
            payload = {
                "error": True,
                "code": "pre_onboard_path_outside_root",
                "message": "--pre-onboard path must remain inside --root.",
                "filepath": filepath,
            }
            print(json.dumps(payload, indent=1))
            return 1
    else:
        membership = filepath_membership_error(
            args.root, filepath, domain_id=domain_id
        )
        if membership is not None:
            print(json.dumps(membership, indent=1))
            return 1

    if pre_onboard:
        hop1_scope = [relativize_under_root(args.root, filepath)]
        scope_err = None
    else:
        hop1_scope, scope_err = resolve_hop1_scope_rels(
            args.root, filepath=filepath, domain_id=domain_id
        )
    if scope_err is not None:
        print(json.dumps(scope_err, indent=1))
        return 1

    result = lookup(
        symbol=args.symbol,
        root=args.root,
        filepath=filepath,
        trim_warnings_cap=_resolve_trim_cap(args.trim_warnings),
        hop1_scope_rels=hop1_scope,
    )
    result = attach_gates_bypassed(result)

    if args.json:
        print(json.dumps(result, indent=1))
    else:
        print(_render_lookup(result))

    return 0


def _cmd_list_domains(args: argparse.Namespace) -> int:
    root_err = validate_root(args.root)
    if root_err is not None:
        print(json.dumps(root_err, indent=1))
        return 2
    payload = list_sac_domains_payload(args.root, domain_id=args.domain_id)
    payload = attach_gates_bypassed(payload)
    print(json.dumps(payload, indent=1))
    return 1 if payload.get("error") else 0


def _cmd_discover(args: argparse.Namespace) -> int:
    root_err = validate_root(args.root)
    if root_err is not None:
        print(json.dumps(root_err, indent=1))
        return 2
    payload = discover_domain(args.root, args.domain_id)
    payload = attach_gates_bypassed(payload)
    print(json.dumps(payload, indent=1))
    return 1 if payload.get("error") else 0


def _cmd_context(args: argparse.Namespace) -> int:
    root_err = validate_root(args.root)
    if root_err is not None:
        print(json.dumps(root_err, indent=1))
        return 2
    payload = build_domain_context(args.root, args.domain_id)
    payload = attach_gates_bypassed(payload)
    print(json.dumps(payload, indent=1))
    return 1 if payload.get("error") else 0


def _cmd_capillarity(args: argparse.Namespace) -> int:
    root_err = validate_root(args.root)
    if root_err is not None:
        print(json.dumps(root_err, indent=1))
        return 2
    payload = assess_domain_capillarity(args.root, args.domain_id)
    payload = attach_gates_bypassed(payload)
    print(json.dumps(payload, indent=1))
    if payload.get("error"):
        return 1
    return 0 if payload.get("quality_status") == "PASS" else 1


def _cmd_diff_check(args: argparse.Namespace) -> int:
    root_err = validate_root(args.root)
    if root_err is not None:
        print(json.dumps(root_err, indent=1))
        return 2
    if args.patch is None and args.base is None:
        payload = {
            "error": True,
            "code": "sac.environment.invalid_arguments",
            "message": "diff-check requires --patch or --base",
            "remediation": "Provide either --patch <file> or --base <ref>.",
        }
        print(json.dumps(payload, indent=1))
        return 2
    if args.patch is not None and args.base is not None:
        payload = {
            "error": True,
            "code": "sac.environment.invalid_arguments",
            "message": "use --patch or --base, not both",
            "remediation": "Provide either --patch <file> or --base <ref>, but not both.",
        }
        print(json.dumps(payload, indent=1))
        return 2

    try:
        exit_code, output = run_diff_check(
            patch=args.patch,
            base=args.base,
            root=args.root,
            pr_body=os.environ.get("SAC_PR_BODY"),
            json_output=args.json,
        )
    except (ValueError, RuntimeError) as exc:
        payload = {
            "error": True,
            "code": "sac.environment.diff_check_failed",
            "message": str(exc),
            "remediation": "Check git repository state and diff arguments.",
        }
        print(json.dumps(payload, indent=1))
        return 2

    print(output)
    return exit_code


def _cmd_validate(args: argparse.Namespace) -> int:
    root_err = validate_root(args.root)
    if root_err is not None:
        print(json.dumps(root_err, indent=1))
        return 2

    orphans, warnings = validate(root=args.root)

    if args.json:
        report = {
            "orphans": [o.to_dict() for o in orphans],
            "warnings": warnings,
            "count": len(orphans),
        }
        report = attach_gates_bypassed(report)
        print(json.dumps(report, indent=1))
    else:
        if warnings:
            for w in warnings:
                print(f"warning: {w}", file=sys.stderr)
        print(render_orphans(orphans))

    if args.warning_only:
        return 0
    return 1 if orphans else 0


def _cmd_index_build(args: argparse.Namespace) -> int:
    root_err = validate_root(args.root)
    if root_err is not None:
        print(json.dumps(root_err, indent=1))
        return 2

    if args.check:
        result = check_symbol_index(root=args.root)
        result = attach_gates_bypassed(result)
        if args.json:
            print(json.dumps(result, indent=1))
        else:
            status = "fresh" if result.get("ok") else result.get("reason", "stale")
            print(
                f"symbol index check: {status}\n"
                f"index_path: {result.get('index_path', symbol_index_path(args.root))}\n"
                f"expected_tag_count: {result.get('expected_tag_count')}\n"
                f"actual_tag_count: {result.get('actual_tag_count')}"
            )
        return 0 if result.get("ok") else 1

    summary = write_symbol_index(root=args.root)
    summary = attach_gates_bypassed(summary)
    if args.json:
        print(json.dumps(summary, indent=1))
    else:
        print(
            f"symbol index written: {summary.get('index_path', symbol_index_path(args.root))}\n"
            f"tag_count: {summary.get('tag_count', 0)}"
        )
        build_warnings = summary.get("build_warnings") or []
        if build_warnings:
            print(f"build_warnings: {len(build_warnings)}", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2

    if args.command == "lookup":
        return _cmd_lookup(args)
    if args.command == "diff-check":
        return _cmd_diff_check(args)
    if args.command == "validate":
        return _cmd_validate(args)
    if args.command == "index-build":
        return _cmd_index_build(args)
    if args.command == "list-domains":
        return _cmd_list_domains(args)
    if args.command == "discover":
        return _cmd_discover(args)
    if args.command == "context":
        return _cmd_context(args)
    if args.command == "capillarity":
        return _cmd_capillarity(args)

    payload = {
        "error": True,
        "code": "sac.environment.invalid_arguments",
        "message": f"unknown command: {args.command}",
        "remediation": "Check command-line syntax.",
    }
    print(json.dumps(payload, indent=1))
    return 2


if __name__ == "__main__":
    sys.exit(main())
