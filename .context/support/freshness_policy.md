# Freshness Policy

Each stable context document should include:
- `last_verified`
- `owner`
- `source_of_truth`
- `expiry_days`

If any field is missing, treat the document as potentially stale until verified.

## Expiry guidance
- Active operational docs: 7 to 14 days
- Architecture docs: 30 days
- Process/playbooks: 60 to 90 days

## Core defaults
- `.context/active_context.md`: `expiry_days: 7`
- `.context/docs/pendentes/current_execution.md`: `expiry_days: 7`
- `.context/support/architecture_drawer_contract.md`: `expiry_days: 30`

When expired:
1. Mark as stale.
2. Revalidate against code and current project state.
3. Archive old versions in `.context/archive/` when needed.
