---
name: briefing-architecture-drawers
description: Generates and normalizes architecture drawer files for large projects while keeping architecture_drawer_contract.md compact as a router artifact. Triggers include 'architecture drawers', 'gavetas de arquitetura', 'drawerized architecture', and 'split project architecture context'. Use when architecture context is too large for efficient default retrieval.
version: 2.0.0
tags: [architecture, drawers, context, token-economy, agnostic]
difficulty: advanced
estimated_time: 15-25min
---

# Briefing Architecture Drawers

## When to use this skill

- When `architecture_drawer_contract.md` is too large for default task retrieval.
- When architecture details need compartmentalization with stable contracts.
- When the team wants selective reads by intent (core + one drawer).
- After bootstrap/sync when drawer scaffold exists but remains unfilled.

## Prerequisites

Read core mandatory set first:

1. `.cursorrules`
2. `.antigravityignore`
3. `.context/active_context.md`
4. `.context/support/architecture_drawer_contract.md`
5. `project_status.md`

Then confirm drawer contract:

1. `.context/support/architecture_drawer_contract.md` (already in core)
2. `.context/docs/context_index.md`

If the contract is missing, stop and request scaffold initialization via bootstrap/sync.

## Scope

This skill manages only drawerized architecture artifacts:

- `.context/docs/architecture_drawers/01_core_bootstrap.md`
- `.context/docs/architecture_drawers/02_engines_mechanisms.md`
- `.context/docs/architecture_drawers/03_presentation_routes.md`
- `.context/docs/architecture_drawers/04_data_sync_state.md`
- `.context/docs/architecture_drawers/05_ops_risks_observability.md`

Do not replace `briefing-structural-architecture`. Keep it as the canonical compact briefing skill.

## Workflow

- [ ] Validate drawer contract and scaffold presence.
- [ ] Keep `architecture_drawer_contract.md` compact; use it as router, not as deep dump.
- [ ] Fill/update each drawer with objective evidence only.
- [ ] Remove duplicated facts between router and drawers.
- [ ] Ensure intent routing exists in `.context/docs/context_index.md`.
- [ ] Mark drawer readiness in `architecture_drawer_contract.md`.
- [ ] Emit concise report with updated drawers and remaining gaps.

## Drawer schema (required)

Each drawer must include:

1. metadata (`last_verified`, `owner`, `source_of_truth`, `expiry_days`)
2. scope boundaries
3. factual tables and flow map
4. known gaps
5. pointers to canonical files

## Router rules (architecture_drawer_contract.md)

- Must remain compact and planning-friendly.
- Must expose system model and contracts.
- Must route deep requests to drawer files by intent.
- Must not duplicate full tables already present in drawers.

## Read budget policy

- default retrieval: core + 1 drawer
- second drawer only with technical justification
- expanded mode required for reading more than 2 drawers

## Output format

```text
Drawerized Architecture Report
Router status: compact | oversized
Drawers updated: [list]
Drawer readiness: [01..05 status]
Duplicates removed: [summary]
Open gaps: [list]
Next action: [context-maintenance | context-orchestrator | targeted drawer fill]
```

## Success criteria

- `architecture_drawer_contract.md` remains compact and navigable.
- All 5 drawer files exist with required metadata.
- Intent-to-drawer routing is explicit in `context_index.md`.
- No critical contradiction between router and drawer content.

## Related skills

- `briefing-structural-architecture` (compact architecture artifact generation)
- `context-orchestrator` (gate and selective retrieval)
- `context-maintenance` (bootstrap-fill and hygiene lifecycle)

## Changelog

### v2.0.0 (2026-03-24)

- **BREAKING:** Replaced `PROJECT_ARCHITECTURE.md` with `architecture_drawer_contract.md` as primary router.
- Removed all references to PROJECT_ARCHITECTURE.md.
- Router is now `.context/support/architecture_drawer_contract.md`.
- Updated workflow to reflect new architecture model.

### v1.0.0 (2026-02-16)

- Initial release for drawerized architecture context normalization.