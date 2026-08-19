# Templates for `updating-project-status`

Use these blocks only when needed. Keep values concrete and short.

## Template 1 — `CURRENT` with Execution Pack (M/L)

```md
## CURRENT
- Task: <single active task>
- Progress: <0-100%>
- Blocker: <none|short blocker>
- Impact: <high|medium|low>
- AI Load: <low|medium|high|extreme>
- Budget Hint: <conserve|normal|spend>
- Next Action: <one immediate action>

### Execution Pack
- Complexity: <S|M|L>
- Goal: <single sentence>
- Scope:
  - In: <what is included>
  - Out: <what is excluded>
- Do:
  1. <step 1>
  2. <step 2>
  3. <step 3>
- Files:
  - `<path/to/fileA>` (<why>)
  - `<path/to/fileB>` (<why>)
- Checks:
  - `<command 1>`  # expects: <short expected result>
  - `<command 2>`  # expects: <short expected result>
- Done when:
  - [ ] <acceptance criterion 1>
  - [ ] <acceptance criterion 2>
- Pitfalls:
  - <risk 1 + mitigation>
- Rollback:
  - <how to revert safely>
```

## Template 2 — `.context/active_context.md` minimal execution-ready block

```md
## Current Objective
<Must mirror CURRENT task in project_status.md>

## Implementation Map
- `<path/module>`: <responsibility>
- `<path/module>`: <responsibility>

## Execution Constraints
- Must: <rule>
- Must not: <rule>
- Architecture boundary: <constraint>

## Code Anchors
- `<file>:<symbol/signature>`
  - `<short snippet or signature>`

## Validation Plan
- `<command>` -> <expected>
- `<command>` -> <expected>

## Open Questions / Assumptions
- Q: <question>
  - Assumption: <temporary assumption>
```

## Template 3 — Adaptive line-budget justification

```md
### Budget Justification
- Complexity Tier: <S|M|L>
- Expected size target: <200|260|320>
- Why extra detail is needed now:
  - <reason 1>
  - <reason 2>
- Compression strategy after execution:
  - Move history to `.context/archive/`
  - Keep only durable execution signals in status
```
