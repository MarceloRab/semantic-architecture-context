# Token Budget Policy

## Primary objective
Keep context retrieval cheap while preserving correctness.

## Rules
- Read only the mandatory sequence first.
- Default (`update`) cap: 6 total reads.
- Initialization target: 8 total reads.
- Initialization hard cap: 10 total reads only after explicit user confirmation.
- Expanded cap: 10 total reads only after explicit user confirmation.
- In drawerized architecture projects, default to core + one drawer by intent.
- Never reopen the same file in the same task unless new data is expected.
- Prefer delta updates in `.context/active_context.md` only for pause/end-of-cycle restart snapshots.
- Keep sequential execution details in an explicitly declared local `handoff_file`; do not store them in `.context/active_context.md`.
- Move long historical details to `.context/archive/`.
- If expansion is requested, record the reason before reading extra files.

## Practical checks
- If a file does not influence the current decision, skip it.
- If no sequential trail is active, do not search for or ask about local handoffs.
- If a section is stale, mark and ignore it until verified.
- In initialization mode, if clarity is not reached inside 8 reads, request explicit confirmation before reads 9-10.
- If clarity is not reached inside the active hard cap, return `NO-GO` or request explicit expansion.
