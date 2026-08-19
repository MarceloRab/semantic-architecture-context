---
name: briefing-structural-architecture
description: Generates a complete yet concise structural architecture brief for any project. Covers Core (DI, boot), Engines (mechanisms), and Presentation (routes, bindings, views). Triggers include 'architecture brief', 'structural brief', 'CEP audit', 'explain project architecture', 'gerar briefing arquitetural'. Use when a human or AI needs a non-verbose, non-omissive map of a codebase's mechanisms, layers, flows, and integrations.
version: 3.0.0
tags: [architecture, documentation, briefing, visual, agnostic, audit, CEP]
difficulty: intermediate
estimated_time: 20min
---

# Briefing Structural Architecture (CEP Model)

> **CEP = Core → Engines → Presentation**
> A mental navigation model: how the system is **assembled** (Core), what **makes it work** (Engines), and how it **reaches the user** (Presentation).

## When to use this skill

- When a human needs to **study or onboard** onto a large/medium project quickly.
- When an AI agent needs a **complete architectural snapshot** without reading hundreds of files.
- When planning a refactoring or migration and need to **map all mechanisms** first.
- When auditing a system end-to-end: from DI composition root to UI rendering.
- When someone asks: "explain this project's architecture", "generate a structural brief", "CEP audit".

## Prerequisites

- Access to the project's source code (file tree + key files).
- At least one structural source: `project_status.md`, architecture docs, `README.md`, codebase map, or similar.
- Minimal context: **project name + tech stack** (1 line).

## Core-context compatibility (mandatory)

- Run `context-orchestrator` in `default` mode before generating artifacts.
- Do not emit a giant architecture file as the mandatory core artifact.
- Always generate/update `architecture_drawer_contract.md` first as the compact router for planning and gating.
- If deep audit is needed, generate drawer files (01-05) outside the core mandatory set.

## Context organicity contract (mandatory)

- Treat `architecture_drawer_contract.md` as the canonical architecture router, not as isolated output.
- Never rebuild architecture docs from zero when a project already has a drawer contract.
- Always ingest and preserve existing semantic truth blocks before editing.
- Synchronize architecture facts across:
  - `architecture_drawer_contract.md`
  - `project_status.md`
  - `.context/active_context.md`
  - `.context/docs/architecture_drawers/*` (when present)
- If any mechanism/flow is changed in the router or drawers, update affected files in the same task.
- If conflict exists between files, resolve using evidence and mark unresolved points as `INFERRED` in gaps.

## Output strategy (required)

1. **Artifact A (mandatory):** `architecture_drawer_contract.md` compact, high-signal, gate-friendly, and audit-ready.
2. **Artifact B (optional):** drawer files (01-05) with deep architecture details.

`context-orchestrator`, planning, and execution skills should consume Artifact A by default.

## Operating modes

- `default`: produce/update Artifact A only, respecting default read budget.
- `expanded`: produce Artifact A + Artifact B (drawers) with deeper evidence collection, only after explicit user confirmation.
- In both modes, preserve existing architecture data and merge deltas instead of replacing content blindly.

Read budget alignment:

- `default`: up to 6 reads total
- `expanded`: up to 10 reads total

## Workflow

- [ ] **1. Gather Sources** — Read mandatory core context first, then only the minimum structural files required by active mode.
- [ ] **2. Ingest Existing Architecture** — Parse current `architecture_drawer_contract.md` and keep valid semantic blocks.
- [ ] **3. Build Artifact A** — Update `architecture_drawer_contract.md` in compact format first (merge-first, not rewrite-first).
- [ ] **4. Map Core** — Document DI composition root and boot pipeline.
- [ ] **5. Extract Engines** — Catalog every systemic behavior ("what makes the project work").
- [ ] **6. Map Presentation** — Document routes, bindings, and view construction.
- [ ] **7. Build Visual Maps** — Create high-level diagrams with arrows.
- [ ] **8. Fill Tables** — Populate all required tables (mechanisms, state, integrations, modules).
- [ ] **9. Trace Critical Flows** — Document up to 6 essential flows.
- [ ] **10. Sync Drawers** — Update `.context/docs/architecture_drawers/*` impacted by changed facts.
- [ ] **11. Cross-Context Reconciliation** — Align deltas with `project_status.md` and `.context/active_context.md`.
- [ ] **12. Compress + Validate** — Enforce line limits and run Validation Checklist before delivering.

---

## Artifact A Contract (architecture_drawer_contract.md)

The compact architecture router must:

- stay concise for mandatory planning reads (target <= 100 lines)
- expose freshness/ownership metadata required by context policies
- remain factual (no narrative history)
- keep stable sectioning for fast retrieval
- remain semantically consistent with drawers and active context

Mandatory metadata fields:

- `Last updated` (ISO date)
- `last_verified` (ISO date)
- `owner`
- `source_of_truth` = `.context/support/architecture_drawer_contract.md`
- `expiry_days` = `30`

Minimum section skeleton:

1. Metadata
2. Purpose
3. Mission
4. Scope (in/out)
5. System model (CEP diagram)
6. Context governance integration
7. Drawer set (fixed)
8. Drawer readiness
9. Source-of-truth map
10. Propagation rules
11. Quality and safety rules
12. Success criteria

Important:

- `architecture_drawer_contract.md` is the index/router of architecture truth.
- Drawer files hold deep architecture details and must be kept in sync when structural facts change.

---

## Artifact B Reference

For `expanded` mode (Artifact B — drawer files), follow this drawer schema:

Each drawer must include:

1. metadata (`last_verified`, `owner`, `source_of_truth`, `expiry_days`)
2. scope boundaries
3. factual tables and flow map
4. known gaps
5. pointers to canonical files

Drawer set (fixed):

1. `.context/docs/architecture_drawers/01_core_bootstrap.md` — Bootstrap, entrypoints, init order
2. `.context/docs/architecture_drawers/02_engines_mechanisms.md` — Mechanisms, systemic gates
3. `.context/docs/architecture_drawers/03_presentation_routes.md` — Operator/docs/skill interaction
4. `.context/docs/architecture_drawers/04_data_sync_state.md` — Sync matrix, persistence contracts
5. `.context/docs/architecture_drawers/05_ops_risks_observability.md` — Risks, observability, escalation

---

## Validation Checklist (agent self-check before delivery)

```text
□ Mechanism Catalog covers everything in the diagrams, flows, and module table
□ Every mechanism has a stable ID (MECH-NNN)
□ Every mechanism has "Where", "Trigger", and "SSOT" filled OR is in Gaps
□ No section exceeds its line limit
□ ≥ 3 ASCII/Unicode diagrams with arrows present (Boot, High-Level, Topology)
□ ≥ 6 tables with headers present
□ Every table row has a Status indicator (🟢🟡🔴⚪)
□ Every flow uses arrow notation (→ ──▶)
□ Routes/Bindings/Views are mapped (§7) OR in Gaps
□ Module boundaries are documented (§6)
□ Text is operational (no narrative, no storytelling)
□ Pointers cover ≥80% of Mechanism Catalog entries (using MECH-IDs)
□ Gaps section exists if any unknowns remain
□ Assertions without evidence are marked as INFERRED
□ Existing `architecture_drawer_contract.md` facts were merged/preserved when still valid
□ Drawer files were updated for every changed semantic block
□ No contradiction between `architecture_drawer_contract.md`, `project_status.md`, and `.context/active_context.md`
□ Router section points to the fixed drawer set when drawerized mode is present
```

**If any check fails → fix and re-emit.**

---

## Success Criteria

**Observable Outcomes:**

- Output document has **≥ 3 diagrams** with arrows and box-drawing characters.
- Output has **≥ 6 tables** with status indicators in every row.
- **100% of detected mechanisms** appear in the Mechanism Catalog with stable IDs.
- **DI composition root** is fully mapped.
- **Boot pipeline** is documented.
- **Routes → Bindings → Views** chain is traceable.
- No section exceeds its stated line limit.
- A human can answer "where does X live?" for any mechanism by reading the brief.

**Quality Gate:**

- If the output looks like a "wall of text" → **FAIL**. Must be visually scannable.
- If any mechanism is missing from the catalog → **FAIL**. Must be non-omissive.
- If routes/views are not mapped → **FAIL**. Presentation layer must be auditable.
- If assertions lack evidence or INFERRED marking → **FAIL**. Must be honest.

---

## Related Skills

- [context-orchestrator](../context-governance/context-orchestrator/SKILL.md) — Per-task GO/NO-GO gate (must run before generating artifacts)
- [planning-and-deciding](../planning/planning-and-deciding/SKILL.md) — Planning skill that benefits from having this brief available

## Changelog

### v3.0.0 (2026-03-24)

- **BREAKING:** Replaced `PROJECT_ARCHITECTURE.md` with `architecture_drawer_contract.md` as primary router.
- Removed PROJECT_ARCHITECTURE.md from all references.
- Architecture router is now `.context/support/architecture_drawer_contract.md`.
- Updated mandatory core context sequence.
- Simplified Artifact A to focus on router + metadata + drawer routing table.

### v2.3.0 (2026-02-18)

- Added mandatory context-organicity contract (merge-first architecture updates)
- Added explicit requirement to preserve existing `PROJECT_ARCHITECTURE.md` semantic blocks
- Added mandatory drawer synchronization when architecture facts change
- Added cross-context reconciliation with `project_status.md` and `.context/active_context.md`
- Expanded validation checklist with anti-contradiction checks
- Clarified that `PROJECT_ARCHITECTURE.md` is router/index and drawers are deep structure

### v2.2.0 (2026-02-16)

- Split skill into compact `SKILL.md` + `CEP_REFERENCE.md` for token economy
- `SKILL.md` covers Artifact A (default mode) without loading 600 lines
- `CEP_REFERENCE.md` loaded only in expanded mode for Artifact B
- No content removed — all sections preserved in reference file

### v2.1.0 (2026-02-16)

- Added mandatory compatibility layer with `context-orchestrator`
- Introduced dual-artifact strategy (Artifact A compact + Artifact B detailed)
- Added `default` vs `expanded` operating modes with read-budget alignment
- Added explicit metadata contract for `PROJECT_ARCHITECTURE.md`

### v2.0.0 (2026-02-15)

- Merged with CEP Architecture Audit File — unified into single skill
- Added CEP model (Core → Engines → Presentation) as organizing principle