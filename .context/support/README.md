# Context Support

Central governance docs that keep agent context usage deterministic and low-cost.

## Files
- `context_read_order.md`: mandatory read order in any project.
- `context_contract.md`: minimal required context artifacts and ownership.
- `token_budget_policy.md`: hard caps to reduce token waste.
- `freshness_policy.md`: validity windows and verification strategy.
- `archive_policy.md`: what to archive and when.
- `architecture_drawer_contract.md`: local contract for drawerized architecture retrieval in large projects.
- `bootstrap_fill_state.md`: generated in target projects to track first project-specific fill.

Use these docs as policy, not as a place for task history.

Execution state belongs in the local planning report/handoff declared by the trail.
`.context/docs/pendentes/current_execution.md` is only a compatibility pointer, and `.context/active_context.md` stays as a restart snapshot.

Operating model:
- Default mode: solve with core context + minimal policy reads (target <= 6 reads).
- Expanded mode: only with explicit user confirmation when deeper policy validation is required.
