# Context Contract

Every new project must contain:

- `.cursorrules` (project guardrails and execution rules)
- `.antigravityignore` (low-value scan exclusions)
- `.context/support/architecture_drawer_contract.md` (architecture router and drawer governance)
- `.context/active_context.md` (lightweight restart snapshot)
- `.context/docs/pendentes/current_execution.md` (compatibility pointer to local report/handoff)

## Optional but recommended

- `.context/docs/README.md` (index of stable docs)
- `.context/docs/architecture_drawers/*` (deep architecture drawers for large projects)
- `.context/handoffs/` (local handoff files for sequential execution trails)
- `.context/archive/` (cold memory for stale docs/logs)
- `.context/skills/` (task-specific skill packs)

## Ownership

- Architecture truth: `.context/support/architecture_drawer_contract.md` + drawers
- Restart snapshot: `.context/active_context.md`
- Execution truth: local planning report/handoff declared by the trail
- Compatibility pointer: `.context/docs/pendentes/current_execution.md`
- Sequential handoff truth: explicit `handoff_file` declared in the plan or current execution item

## Freshness minimum

- `architecture_drawer_contract.md`, `.context/docs/pendentes/current_execution.md`, and `.context/active_context.md` should expose:
  - `last_verified`
  - `owner`
  - `source_of_truth`
  - `expiry_days`

Avoid duplicating the same information across these files.

## Handoff and execution memory policy

- `.context/active_context.md` is a compact restart pointer/snapshot updated at pauses, chat transitions, or end-of-cycle maintenance.
- `.context/active_context.md` is not the default execution handoff for sequential work.
- Sequential execution trails must declare a local planning report/handoff file; `.context/docs/pendentes/current_execution.md` may point to it for compatibility.
- If a sequential trail has no declared `handoff_file`, the agent must ask the user to choose or confirm one before delegating or continuing the trail.
- Non-sequential tasks, context maintenance, one-shot evaluations, and punctual fixes must not ask for a handoff file.
- Local handoffs are working execution memory only; `active_context.md` may point to them, but must not duplicate their execution detail.
- Promote durable decisions to architecture/context docs through an explicit context update.

## Context governance lifecycle

```text
bootstrap ──► core files + policies copied to project
     │
     ▼
context-orchestrator (gate)
     │
  GO ┤ NO-GO
     │    │
     │    ├─► context-maintenance (pontual)
     │    │        └──► re-run orchestrator
     │    │
     │    └─► validating-context-efficacy (sistêmico)
     │              └──► corrective actions ──► re-run orchestrator
     │
     ▼
execution skills (briefing-structural-architecture, updating-project-status, etc.)
     └──► architecture_drawer_contract.md, drawers, local planning report/handoff, optional compatibility pointer in `.context/docs/pendentes/current_execution.md`
           └──► briefing-architecture-drawers (when deep architecture update is needed)
```
