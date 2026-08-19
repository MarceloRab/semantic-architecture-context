---
name: validating-task-blocks
description: Validates local task batches for immediate execution using minimal context. Focuses on clarity, completeness, and risk within the current sprint/status, avoiding full project architectural scans to save tokens. Triggers include 'validate task block', 'check this plan', 'can I execute these tasks?'. Use before Plan->Execute transitions.
version: 1.2.0
tags: [planning, validation, local-scope, efficiency, agnostic]
difficulty: intermediate
estimated_time: 2-5min
---

# Validating Task Blocks (Local Scope)

## When to use this skill

- When a user asks to validate a specific list of tasks (e.g., "Check this plan").
- When you need to ensure a generated plan is executable _now_.
- During the `Plan -> Execute` transition in a sprint.
- When avoiding token-heavy architectural audits is a priority.

## Prerequisites

- A concrete task block (ordered list, checklist, or batch plan).
- Access to `.context/docs/pendentes/current_execution.md` (to check alignment with valid tasks).
- Access to `.context/active_context.md` as a compact restart snapshot only.
- Access to the declared local `handoff_file` only when the task block is a sequential trail.

## Dependencies

**Required (Minimal):**

- `.context/docs/pendentes/current_execution.md`
- `.context/active_context.md`

**Explicitly Excluded (Token Savings):**

- `PROJECT_ARCHITECTURE.md` (Assume validated at project (re)planning)
- `.cursorrules` (Assume generic rules apply)
- Full codebase scans

## Workflow

- [ ] **Load Context**: Read only `.context/docs/pendentes/current_execution.md` and `.context/active_context.md`.
- [ ] **Sequential Check**: If the task block is sequential and declares `handoff_file`, read that handoff. If sequential and missing `handoff_file`, ask the user. If non-sequential, do not ask for a handoff.
- [ ] **Normalize**: Ensure the task block has clear `Action -> Target -> Outcome` structure.
- [ ] **Validate**: Check against _immediate_ context (e.g., is this file actually the one we are working on?).
- [ ] **Risk Check**: Identify high-risk operations (deletes, overwrites) that might need a backup step.
- [ ] **Report**: Emit a concise `PASS`, `PASS_WITH_NOTES`, or `FAIL` verdict.

## Instructions

### 1. Minimal Context Strategy

- **Do NOT** read the full architecture or multiple source files unless a specific task is ambiguous.
- Treat `active_context.md` as a restart snapshot, not the source of detailed execution truth.
- Trust `.context/docs/pendentes/current_execution.md` for active tasks and delivery state.
- Trust a local handoff only when the task is explicitly sequential and the handoff path is declared.

### 2. Validation Dimensions (with examples)

- **Clarity**: Does every task have a specific target file/component?
  - ✅ PASS: `"Edit lib/services/auth_service.dart to add token refresh"`
  - ❌ FAIL: `"Refactor authentication"` (no target, no scope)
- **Atomicity**: Is the task small enough to be executed in one step?
  - ✅ PASS: `"Add validation to email field in AddPatientController"`
  - ❌ FAIL: `"Implement entire patient module"` (needs decomposition)
- **Safety**: Are there destructive operations without a backup/rollback step?
  - ✅ PASS: `"Delete unused test fixtures in test/old/"` (low-risk, recoverable via git)
  - ❌ FAIL: `"Drop and recreate database schema"` (no backup step listed)
- **Sequence**: Do dependencies come before dependents?
  - ✅ PASS: `T1: Create model -> T2: Create service using model -> T3: Create view using service`
  - ❌ FAIL: `T1: Create view -> T2: Create the model it depends on`

### 3. Outcome Routing

- **PASS**: Tasks are clear, safe, and aligned with active context.
- **PASS_WITH_NOTES**: Minor clarifications needed (e.g., "Remember to run tests after T3"), but executable.
- **FAIL**:
  - **Ambiguous targets** ("Refactor code").
  - **Missing dependencies** (Using a file that hasn't been created).
  - **High risk** (Deleting DB without backup) -> **Action**: Request specific safety step.

### Output Template (mandatory format)

```markdown
# Local Task Validation

**Verdict:** {{PASS|PASS_WITH_NOTES|FAIL}}
**Tasks evaluated:** {{N}}
**Source:** current_execution.md + active_context.md + declared handoff_file when sequential

## Findings (one per issue, ordered by impact)

### {{Clarity|Atomicity|Safety|Sequence}} - {{short title}}

- **Task:** {{T# - task text}}
- **Evidence:** {{quote from task or context that proves the issue}}
- **Impact:** {{what goes wrong if executed as-is}}
- **Fix:** {{minimal correction}}

## Validated Plan (if PASS or PASS_WITH_NOTES)

1. {{T1 - validated task}}
2. {{T2 - validated task}}
   ...
```

## Related Skills

- `validating-flutter-projects` (Use for FULL project/architecture validation).
- `planning-and-deciding` (Use to generate the initial plan).
