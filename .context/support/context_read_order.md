# Context Read Order

Apply this sequence at the start of each task:

1. `<repo>/.cursorrules`
2. `<repo>/.antigravityignore`
3. `<repo>/.context/active_context.md`
4. `<repo>/.context/support/architecture_drawer_contract.md`
5. `<repo>/.context/docs/pendentes/current_execution.md` (compatibility pointer)

## Default mode

- Keep the task inside 6 total reads whenever possible.
- Decide with the core sequence first (`GO/NO-GO`) before opening more files.
- Treat `.context/active_context.md` as a lightweight restart snapshot, not as an execution handoff.
- Treat `.context/docs/pendentes/current_execution.md` as a pointer to the local planning report/handoff, not execution truth.
- Read a local report/handoff only when the active task is a sequential trail and a path is explicitly declared.
- If a sequential trail lacks a report/handoff path, ask the user to choose or confirm one before continuing that trail.
- Do not ask for a handoff file for non-sequential tasks, context maintenance, one-shot evaluations, or punctual fixes.
- If architecture is drawerized, prefer reading exactly one drawer by intent:
  - `<repo>/.context/docs/architecture_drawers/01_core_bootstrap.md`
  - `<repo>/.context/docs/architecture_drawers/02_engines_mechanisms.md`
  - `<repo>/.context/docs/architecture_drawers/03_presentation_routes.md`
  - `<repo>/.context/docs/architecture_drawers/04_data_sync_state.md`
  - `<repo>/.context/docs/architecture_drawers/05_ops_risks_observability.md`

## Initialization mode

- Start from the same core sequence (items 1-5).
- If architecture is drawerized, prioritize:
  1. `<repo>/.context/support/architecture_drawer_contract.md` (already in core)
  2. one drawer file by task intent.
- Keep initialization runs inside 8 total reads whenever possible.
- If source 9 or 10 is required, request explicit user confirmation before reading.
- If clarity is still insufficient after 10 reads, return `NO-GO` and escalate.

## Expanded mode

Only enter expanded mode with explicit user confirmation.

Suggested policy read order in expanded mode:

1. `<repo>/.context/support/token_budget_policy.md`
2. `<repo>/.context/support/freshness_policy.md`
3. `<repo>/.context/support/context_contract.md`
4. `<repo>/.context/support/archive_policy.md`

Only read additional files when required data is missing from core + applicable policies.
