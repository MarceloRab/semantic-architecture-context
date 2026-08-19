# Architecture Router Contract

## Metadata

- Project: `semantic-architecture-context`
- Last updated: `2026-08-19`
- last_verified: `2026-08-19`
- owner: `TBD`
- source_of_truth: `.context/support/architecture_drawer_contract.md`
- expiry_days: `30`
- fill_status: `needs_project_fill`
- required_skill: `context-maintenance` (`bootstrap-fill`)

## Purpose

This contract serves as the primary architecture router for this project. It provides:
- Core architecture facts (mission, scope, system model)
- Drawer routing by intent
- Context governance integration

## Mission

- What this project delivers: `TBD`
- Who it serves: `TBD`
- Why it exists: `TBD`

## Scope

### In scope

- `TBD`

### Out of scope

- `TBD`

### Constraints

- `TBD`

## System model (CEP)

```text
Core (what assembles the system)
  ├── [TBD: DI composition root]
  ├── [TBD: Bootstrap/init order]
  └── [TBD: Core services]

Engines (what makes it work)
  ├── [TBD: Mechanism 1]
  ├── [TBD: Mechanism 2]
  └── [TBD: Mechanism 3]

Presentation (how it reaches the user)
  ├── [TBD: Routes]
  ├── [TBD: Controllers]
  └── [TBD: Views]
```

## Context governance integration

Core context read chain (mandatory):

1. `.cursorrules`
2. `.antigravityignore`
3. `.context/active_context.md`
4. `.context/support/architecture_drawer_contract.md` (this file)
5. `.context/docs/pendentes/current_execution.md` (compatibility pointer)

Policy overlay in `.context/support/`:

- `context_read_order.md`
- `token_budget_policy.md`
- `freshness_policy.md`
- `context_contract.md`
- `archive_policy.md`
- `bootstrap_fill_state.md` (project-specific fill lifecycle)

## Drawer set (fixed)

| Drawer | File | Intent |
| --- | --- | --- |
| 01 | `.context/docs/architecture_drawers/01_core_bootstrap.md` | Bootstrap, entrypoints, init order |
| 02 | `.context/docs/architecture_drawers/02_engines_mechanisms.md` | Mechanisms, systemic gates |
| 03 | `.context/docs/architecture_drawers/03_presentation_routes.md` | Routes, bindings, controllers |
| 04 | `.context/docs/architecture_drawers/04_data_sync_state.md` | Persistence, sync, migrations |
| 05 | `.context/docs/architecture_drawers/05_ops_risks_observability.md` | Risks, observability, release |

## Drawer readiness

| Drawer | File | Readiness | last_verified |
| --- | --- | --- | --- |
| 01 | `.context/docs/architecture_drawers/01_core_bootstrap.md` | `pending` | `TBD` |
| 02 | `.context/docs/architecture_drawers/02_engines_mechanisms.md` | `pending` | `TBD` |
| 03 | `.context/docs/architecture_drawers/03_presentation_routes.md` | `pending` | `TBD` |
| 04 | `.context/docs/architecture_drawers/04_data_sync_state.md` | `pending` | `TBD` |
| 05 | `.context/docs/architecture_drawers/05_ops_risks_observability.md` | `pending` | `TBD` |

## Quality and safety rules

- Keep artifacts factual and compact; avoid duplicated truth across files.
- Maintain drawer contract as the single architecture router.
- Update drawer files when structural facts change.
- Run `context-maintenance` when fill is complete.

## Success criteria

- Mandatory core context remains readable and coherent.
- Architecture decisions are traceable to real code flows.
- Planning can proceed from this file without deep re-discovery.

