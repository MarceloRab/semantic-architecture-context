# SAC MCP Node — short runbook

Primary Cursor/stdio entry for SAC. Tags in source code are SSOT; the thin Node adapter delegates parsing and context assembly to the Python CLI.

## Requirements

- Node >= 18
- Python 3.12+ on PATH (or set `SAC_PYTHON`)

## Install

```powershell
cd sac-context/mcp
npm ci
```

## Run (stdio MCP)

```powershell
$env:SAC_ROOT = "C:\path\to\project"
# optional: $env:SAC_PYTHON = "C:\...\python.exe"
node server.mjs
```

Default `SAC_ROOT` when unset: repository root two levels above this folder (`sac-context/mcp` → project root).

## Cursor snippet (apply in Track 5 / host)

```json
{
  "mcpServers": {
    "sac": {
      "command": "node",
      "args": ["${workspaceFolder}/sac-context/mcp/server.mjs"],
      "env": {
        "SAC_ROOT": "${workspaceFolder}"
      }
    }
  }
}
```

## Runtime contract

`list_sac_domains` routes intent compactly; `get_sac_context(domain_id)` assembles anchors + all `REGR`/`DEPRECATED` + hop1 for one selected domain; `DEPRECATED` carries `replacement` and blocks new use; `get_sac_constraints` verifies a precise target; `discover_sac` is optional inventory; `assess_sac_capillarity(domain_id)` compares declared `coverage_claims` to physical tags and evaluates context fitness (**on-demand only** — never boot/L0). Axes: (A) `status` `UNRATED|INVALID_CONTRACT|INSUFFICIENT|SUFFICIENT`; (B) `fitness_status` `TOO_THIN|UNFIT|OVER_SELECT|FIT`; (C) `payload_status` `OK|OVER_BUDGET` + `payload_warn`. `quality_status=PASS` when `SUFFICIENT`+`FIT`+(`OK`|`OVER_BUDGET`); OVER_BUDGET is WARN-only — MUST NOT thin domain. Responses include `_perf.elapsed_ms` and `_perf.payload_bytes`. `SAC_CONTEXT_MAX_BYTES` defaults to **12288**; overflow returns explicit `context_payload_too_large` without constraints (MUST Discover→Verify).

## Smoke (no Cursor)

```powershell
cd sac-context/mcp
npm run smoke
```

Compares Node lookup/list-domains/discover JSON to CLI (COR-GATE-1).
Smoke: compact catalog; discover scoped; hop1 scoped; MCP≡CLI filepath_required;
membership; domain_id on Verify; parity with --path.
