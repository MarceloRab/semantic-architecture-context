# Bootstrap Fill State

## Metadata
- project: `semantic-architecture-context`
- generated_on: `2026-08-19`
- fill_status: `needs_project_fill`
- required_skill: `context-maintenance`
- mode: `bootstrap-fill`

## Automation behavior
- If `fill_status` is `needs_project_fill`, `context-orchestrator` may auto-trigger `context-maintenance bootstrap-fill`.
- `context-maintenance update` may also auto-trigger `bootstrap-fill` in the same cycle.
- Goal state after auto or manual run: `fill_status: ready_for_execution`.

## Required fill targets (project-specific)
- [ ] `.context/active_context.md`
- [ ] `.context/support/architecture_drawer_contract.md`
- [ ] `.context/docs/context_index.md`
- [ ] `.context/docs/pendentes/current_execution.md`
- [ ] `.context/docs/architecture_drawers/01_core_bootstrap.md`
- [ ] `.context/docs/architecture_drawers/02_engines_mechanisms.md`
- [ ] `.context/docs/architecture_drawers/03_presentation_routes.md`
- [ ] `.context/docs/architecture_drawers/04_data_sync_state.md`
- [ ] `.context/docs/architecture_drawers/05_ops_risks_observability.md`
- [ ] `.context/support/context_read_order.md`
- [ ] `.context/support/token_budget_policy.md`
- [ ] `.context/support/freshness_policy.md`
- [ ] `.context/support/context_contract.md`
- [ ] `.context/support/archive_policy.md`
- [ ] `.context/support/architecture_drawer_contract.md`

## Completion criteria
- [ ] Core docs have factual project data in critical fields.
- [ ] Core metadata fields are verified (`last_verified`, `owner`, `source_of_truth`, `expiry_days`).
- [ ] `fill_status` is changed to `ready_for_execution` by `context-maintenance` after completion.
