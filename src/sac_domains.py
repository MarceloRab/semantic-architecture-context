"""Parse sac-context/docs/SAC_domains.md (Route index). Stdlib-only.

L0 catalog is compact (module/intent only). Expand with domain_id returns
files/anchors for Discover/Verify. Membership uses files: lists.
Discover/Hop1 scope resolves to domain files: (not full-repo).
"""

from __future__ import annotations

import os
import re
from typing import Any

_DOMAINS_REL = os.path.join("sac-context", "docs", "SAC_domains.md")

PAUSE_HINT = (
    "Qual domain_id expandir, ou informe filepath direto?"
)

DISCOVER_HINT = (
    "Use discover_sac(domain_id), then get_sac_constraints(symbol, filepath)."
)

_SKIP_DOMAIN_IDS = frozenset(
    {
        "como usar",
        "_template",
        "example_domain",
    }
)

_HEADER_RE = re.compile(r"^##\s+(.+?)\s*$")
_FIELD_RE = re.compile(r"^- ([a-z_]+):\s*(.*)\s*$")
_FILE_ITEM_RE = re.compile(r"^  - (.+?)\s*$")

_BASE_SCENARIOS = frozenset({"SUMMARY", "EXTEND", "REGRESSION"})
_OPTIONAL_SCENARIOS = frozenset({"MIGRATION"})
_ALLOWED_SCENARIOS = _BASE_SCENARIOS | _OPTIONAL_SCENARIOS
_TAG_TYPES = frozenset({"ARCH", "REGR", "DEPRECATED"})
_CLAIM_ID_RE = re.compile(r"^[A-Z][A-Z0-9_]{2,63}$")
_SYMBOL_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.$-]*$")


def sac_domains_path(root: str) -> str:
    return os.path.normpath(os.path.join(root, _DOMAINS_REL))


def normalize_repo_path(path: str) -> str:
    """Normalize for membership compare (posix-ish, lower on Windows)."""
    p = path.strip().replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    if os.name == "nt":
        return p.lower()
    return p


def parse_sac_domains(root: str) -> list[dict[str, Any]]:
    """Return onboarded domain blocks (excludes template / howto sections)."""
    path = sac_domains_path(root)
    if not os.path.isfile(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError:
        return []

    domains: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    in_files = False
    in_coverage_claims = False

    def _flush() -> None:
        nonlocal current, in_files, in_coverage_claims
        if current is None:
            return
        domain_id = str(current.get("domain_id", "")).strip()
        if domain_id and domain_id.lower() not in _SKIP_DOMAIN_IDS:
            current.setdefault("files", [])
            current.setdefault("anchor_symbols", [])
            current.setdefault("coverage_claims_raw", [])
            current.setdefault("_fields_seen", set())
            domains.append(current)
        current = None
        in_files = False
        in_coverage_claims = False

    for raw in lines:
        header = _HEADER_RE.match(raw)
        if header:
            _flush()
            domain_id = header.group(1).strip()
            current = {
                "domain_id": domain_id,
                "files": [],
                "anchor_symbols": [],
                "coverage_claims_raw": [],
                "_fields_seen": set(),
            }
            in_files = False
            in_coverage_claims = False
            continue

        if current is None:
            continue

        if in_files:
            file_item = _FILE_ITEM_RE.match(raw)
            if file_item:
                current["files"].append(file_item.group(1).strip().replace("\\", "/"))
                continue
            if raw.startswith("  - "):
                continue
            in_files = False

        if in_coverage_claims:
            claim_item = _FILE_ITEM_RE.match(raw)
            if claim_item:
                current["coverage_claims_raw"].append(claim_item.group(1).strip())
                continue
            if raw.startswith("  - "):
                continue
            in_coverage_claims = False

        field = _FIELD_RE.match(raw)
        if not field:
            continue
        key, value = field.group(1), field.group(2).strip()
        current["_fields_seen"].add(key)
        if key == "files":
            in_files = True
            in_coverage_claims = False
            continue
        if key == "coverage_claims":
            in_coverage_claims = True
            in_files = False
            continue
        if key == "anchor_symbols":
            if value:
                current["anchor_symbols"] = [
                    p.strip() for p in value.split(",") if p.strip()
                ]
            continue
        if key == "context_scenarios":
            current["context_scenarios_raw"] = value
            continue
        if key in {
            "intent",
            "summary",
            "onboarded",
            "drawer_file",
            "drawer_refs",
            "tag_count",
            "on_edit",
            "known_gaps",
        }:
            current[key] = value

    _flush()
    return domains


def _parse_scenario_csv(raw: str) -> list[str]:
    items: list[str] = []
    seen: set[str] = set()
    for part in (raw or "").split(","):
        token = part.strip().upper()
        if not token or token in seen:
            continue
        seen.add(token)
        items.append(token)
    return items


def _claim_sort_key(claim: dict[str, str]) -> tuple[str, str, str, str]:
    return (
        claim.get("claim_id", ""),
        claim.get("filepath", ""),
        claim.get("symbol", ""),
        claim.get("tag_type", ""),
    )


def capillarity_contract_from_domain(domain: dict[str, Any]) -> dict[str, Any]:
    """Normalize/validate optional capillarity metadata for one domain.

    Does not match source tags (T2). L0 catalog/expand never include this payload.
    """
    seen = domain.get("_fields_seen") or set()
    has_scenarios = "context_scenarios" in seen
    has_claims = "coverage_claims" in seen
    files = [str(f).replace("\\", "/") for f in (domain.get("files") or [])]
    files_norm = {normalize_repo_path(f) for f in files}

    base: dict[str, Any] = {
        "domain_id": domain.get("domain_id"),
        "context_scenarios": [],
        "coverage_claims": [],
        "invalid_claims": [],
        "required_tag_tuples": [],
        "minimum_source_tag_lines": 0,
        "contract_errors": [],
    }

    if not has_scenarios and not has_claims:
        base["status"] = "UNRATED"
        return base

    if has_scenarios != has_claims:
        base["status"] = "INVALID_CONTRACT"
        base["contract_errors"].append("partial_fields")
        return base

    scenarios = _parse_scenario_csv(str(domain.get("context_scenarios_raw") or ""))
    base["context_scenarios"] = scenarios
    errors: list[str] = []

    if not scenarios:
        errors.append("scenarios_empty")
    unknown = [s for s in scenarios if s not in _ALLOWED_SCENARIOS]
    if unknown:
        errors.append("scenarios_unknown:" + ",".join(unknown))
    missing_base = sorted(_BASE_SCENARIOS - set(scenarios))
    if missing_base:
        errors.append("scenarios_base_missing:" + ",".join(missing_base))

    claim_ids: set[str] = set()
    claims: list[dict[str, str]] = []
    invalid_claims: list[dict[str, Any]] = []
    scenario_set = set(scenarios)

    for raw_line in domain.get("coverage_claims_raw") or []:
        parts = [p.strip() for p in raw_line.split("|")]
        entry: dict[str, Any] = {"raw": raw_line}
        if len(parts) != 5:
            entry["error"] = "column_count"
            invalid_claims.append(entry)
            continue
        claim_id, scenario, tag_type, symbol, filepath = parts
        filepath = filepath.replace("\\", "/")
        entry.update(
            {
                "claim_id": claim_id,
                "scenario": scenario,
                "tag_type": tag_type,
                "symbol": symbol,
                "filepath": filepath,
            }
        )
        row_errors: list[str] = []
        if not _CLAIM_ID_RE.fullmatch(claim_id):
            row_errors.append("claim_id")
        elif claim_id in claim_ids:
            row_errors.append("claim_id_duplicate")
        if scenario not in _ALLOWED_SCENARIOS:
            row_errors.append("scenario_unknown")
        elif scenario not in scenario_set:
            row_errors.append("scenario_undeclared")
        if tag_type not in _TAG_TYPES:
            row_errors.append("tag_type")
        if not _SYMBOL_RE.fullmatch(symbol):
            row_errors.append("symbol")
        if "|" in claim_id or "|" in scenario or "|" in tag_type or "|" in symbol:
            row_errors.append("embedded_pipe")
        if normalize_repo_path(filepath) not in files_norm:
            row_errors.append("filepath_not_in_files")
        if row_errors:
            entry["error"] = ",".join(row_errors)
            invalid_claims.append(entry)
            continue
        claim_ids.add(claim_id)
        claims.append(
            {
                "claim_id": claim_id,
                "scenario": scenario,
                "tag_type": tag_type,
                "symbol": symbol,
                "filepath": filepath,
            }
        )

    claims.sort(key=_claim_sort_key)
    invalid_claims.sort(
        key=lambda c: (
            str(c.get("claim_id") or ""),
            str(c.get("filepath") or ""),
            str(c.get("symbol") or ""),
            str(c.get("tag_type") or ""),
            str(c.get("raw") or ""),
        )
    )

    if not claims and not invalid_claims:
        errors.append("claims_empty")

    covered_scenarios = {c["scenario"] for c in claims}
    for sc in scenarios:
        if sc not in covered_scenarios:
            errors.append(f"scenario_without_claim:{sc}")

    tuples: list[dict[str, str]] = []
    seen_tuples: set[tuple[str, str, str]] = set()
    for claim in claims:
        key = (
            normalize_repo_path(claim["filepath"]),
            claim["symbol"],
            claim["tag_type"],
        )
        if key in seen_tuples:
            continue
        seen_tuples.add(key)
        tuples.append(
            {
                "filepath": claim["filepath"],
                "symbol": claim["symbol"],
                "tag_type": claim["tag_type"],
            }
        )
    tuples.sort(
        key=lambda t: (t["filepath"], t["symbol"], t["tag_type"])
    )

    base["coverage_claims"] = claims
    base["invalid_claims"] = invalid_claims
    base["required_tag_tuples"] = tuples
    base["minimum_source_tag_lines"] = len(tuples)
    base["contract_errors"] = errors

    if errors or invalid_claims:
        base["status"] = "INVALID_CONTRACT"
    else:
        base["status"] = "VALID"
    return base


def _intent_of(domain: dict[str, Any]) -> str:
    return str(domain.get("intent") or domain.get("summary") or "").strip()


def _compact_domain(domain: dict[str, Any]) -> dict[str, Any]:
    """L0 catalog card — minimum fields only (COR-GATE-8)."""
    files = list(domain.get("files") or [])
    return {
        "domain_id": domain.get("domain_id"),
        "summary": _intent_of(domain),
        "files_count": len(files),
    }


def _expanded_domain(domain: dict[str, Any]) -> dict[str, Any]:
    """L0b expand — full module surface for Discover/Verify."""
    files = list(domain.get("files") or [])
    anchors = list(domain.get("anchor_symbols") or [])
    return {
        "domain_id": domain.get("domain_id"),
        "summary": _intent_of(domain),
        "files_count": len(files),
        "drawer_file": domain.get("drawer_file") or "",
        "drawer_refs": domain.get("drawer_refs") or "",
        "on_edit": domain.get("on_edit")
        or "sac-execution-overlay + discover_sac + get_sac_constraints",
        "onboarded": domain.get("onboarded") or "",
        "known_gaps": domain.get("known_gaps") or "",
        "files": files,
        "anchor_symbols": anchors,
    }


def find_domain(
    domains: list[dict[str, Any]], domain_id: str
) -> dict[str, Any] | None:
    wanted = (domain_id or "").strip().lower()
    if not wanted:
        return None
    return next(
        (
            d
            for d in domains
            if str(d.get("domain_id", "")).lower() == wanted
        ),
        None,
    )


def domain_not_found_error(
    domains: list[dict[str, Any]], domain_id: str, *, mode: str
) -> dict[str, Any]:
    return {
        "error": True,
        "code": "domain_not_found",
        "message": f"domain_id not found in SAC_domains.md: {domain_id}",
        "domain_id": domain_id,
        "index": "sac-context/docs/SAC_domains.md",
        "available": [d.get("domain_id") for d in domains],
        "pause_hint": PAUSE_HINT,
        "mode": mode,
    }


def relativize_under_root(root: str, filepath: str) -> str:
    """Return repo-relative path for filepath (posix-ish separators)."""
    candidate = filepath
    root_norm = os.path.normpath(root)
    abs_candidate = os.path.normpath(
        filepath if os.path.isabs(filepath) else os.path.join(root, filepath)
    )
    try:
        rel = os.path.relpath(abs_candidate, root_norm)
        if not rel.startswith(".."):
            candidate = rel
    except ValueError:
        candidate = filepath
    return candidate.replace("\\", "/")


def list_sac_domains_payload(
    root: str, domain_id: str | None = None
) -> dict[str, Any]:
    """Catalog (compact) or expand one domain.

    Default: module cards only — no files[] / full anchors (token economy).
    With domain_id: full files + anchors for that module only.
    """
    domains = parse_sac_domains(root)
    wanted = (domain_id or "").strip()

    if wanted:
        match = find_domain(domains, wanted)
        if match is None:
            return domain_not_found_error(domains, wanted, mode="expand")
        return {
            "index": "sac-context/docs/SAC_domains.md",
            "mode": "expand",
            "count": 1,
            "domains": [_expanded_domain(match)],
            "pause_hint": (
                "Chame discover_sac(domain_id) ou escolha filepath ∈ files:, "
                "depois get_sac_constraints(symbol, filepath)."
            ),
        }

    compact = [_compact_domain(d) for d in domains]
    return {
        "index": "sac-context/docs/SAC_domains.md",
        "mode": "catalog",
        "count": len(compact),
        "domains": compact,
        "pause_hint": PAUSE_HINT,
    }


def domains_covering_filepath(
    domains: list[dict[str, Any]], filepath: str
) -> list[str]:
    target = normalize_repo_path(filepath)
    hits: list[str] = []
    for d in domains:
        for f in d.get("files") or []:
            if normalize_repo_path(str(f)) == target:
                hits.append(str(d.get("domain_id")))
                break
    return hits


def filepath_membership_error(
    root: str,
    filepath: str,
    domain_id: str | None = None,
) -> dict[str, Any] | None:
    """If domains exist and filepath is out of scope, return error payload.

    With domain_id: path must be in that domain's files: (P2).
    Without domain_id: path must be in the union of all domain files:.
    Escape: SAC_ALLOW_FILEPATH_OUTSIDE_DOMAINS=1
    """
    if (os.environ.get("SAC_ALLOW_FILEPATH_OUTSIDE_DOMAINS") or "").strip() == "1":
        return None
    domains = parse_sac_domains(root)
    if not domains:
        return None

    candidate = relativize_under_root(root, filepath)
    wanted = (domain_id or "").strip()

    if wanted:
        match = find_domain(domains, wanted)
        if match is None:
            return domain_not_found_error(domains, wanted, mode="verify")
        allowed = {
            normalize_repo_path(str(f)) for f in (match.get("files") or [])
        }
        if normalize_repo_path(candidate) in allowed:
            return None
        return {
            "error": True,
            "code": "filepath_not_in_domain",
            "message": (
                f"filepath is not listed under domain_id={wanted} files: "
                "in SAC_domains.md."
            ),
            "filepath": candidate,
            "domain_id": wanted,
            "domains_hint": [d.get("domain_id") for d in domains],
            "pause_hint": PAUSE_HINT,
            "hint_tool": "list_sac_domains",
        }

    hits = domains_covering_filepath(domains, candidate)
    if hits:
        return None
    return {
        "error": True,
        "code": "filepath_not_in_sac_domains",
        "message": (
            "filepath is not listed under any domain files: in SAC_domains.md. "
            "Pick a module via list_sac_domains, discover_sac, or onboard."
        ),
        "filepath": candidate,
        "domains_hint": [d.get("domain_id") for d in domains],
        "pause_hint": PAUSE_HINT,
        "hint_tool": "list_sac_domains",
    }


def resolve_hop1_scope_rels(
    root: str,
    filepath: str | None = None,
    domain_id: str | None = None,
) -> tuple[list[str] | None, dict[str, Any] | None]:
    """Relative files for hop1 scope, or None for unscoped full index/scan.

    Returns (scope_rels, error_payload).
    Escape: SAC_ALLOW_HOP1_FULL_SCAN=1 → (None, None) full scan allowed.
    """
    if (os.environ.get("SAC_ALLOW_HOP1_FULL_SCAN") or "").strip() == "1":
        return None, None

    domains = parse_sac_domains(root)
    if not domains:
        return None, None

    wanted = (domain_id or "").strip()
    if wanted:
        match = find_domain(domains, wanted)
        if match is None:
            return None, domain_not_found_error(domains, wanted, mode="hop1")
        return [str(f).replace("\\", "/") for f in (match.get("files") or [])], None

    if not filepath:
        return None, None

    candidate = relativize_under_root(root, filepath)
    hits = domains_covering_filepath(domains, candidate)
    if not hits:
        return None, None

    scope: list[str] = []
    seen: set[str] = set()
    for domain_name in hits:
        match = find_domain(domains, domain_name)
        if match is None:
            continue
        for f in match.get("files") or []:
            rel = str(f).replace("\\", "/")
            key = normalize_repo_path(rel)
            if key in seen:
                continue
            seen.add(key)
            scope.append(rel)
    return scope, None


def filepath_required_error() -> dict[str, Any]:
    return {
        "error": True,
        "code": "filepath_required",
        "message": (
            "Lookup requires filepath. Do not full-scan. "
            "Call list_sac_domains, discover_sac(domain_id), "
            "then get_sac_constraints(symbol, filepath)."
        ),
        "pause_hint": PAUSE_HINT,
        "hint_tool": "list_sac_domains",
    }


def domain_id_required_error() -> dict[str, Any]:
    return {
        "error": True,
        "code": "domain_id_required",
        "message": (
            "discover_sac requires domain_id. "
            "Call list_sac_domains() first, then discover_sac(domain_id)."
        ),
        "pause_hint": PAUSE_HINT,
        "hint_tool": "list_sac_domains",
    }
