---
name: mobile-planning
description: Generates a compact Project Mind document for mobile AI planning sessions.
version: 1.1.0
tags: [planning, mobile, context, documentation]
difficulty: beginner
estimated_time: 5min
---

# Mobile Planning

## When to use this skill

- User needs to continue planning from smartphone.
- User asks for "project mind", "status compacto", or "mobile snapshot".
- Before leaving desktop, to preserve high-signal context.
- When async planning with team members in chat tools.

## Prerequisites

- `.cursorrules`
- `.antigravityignore`
- `.context/active_context.md`
- `PROJECT_ARCHITECTURE.md`
- `project_status.md`
- Optional policy overlay when needed: `.context/support/context_read_order.md`

## Core-context alignment (mandatory)

- Run `context-orchestrator` in `default` mode before generating the mobile snapshot.
- Continue only if gate result is `GO`.
- Keep retrieval compact; do not exceed policy read limits without explicit confirmation.

## Workflow

- [ ] Read mandatory core prerequisites.
- [ ] Extract only current objective, blockers, and next step.
- [ ] Build a concise "Project Mind" document.
- [ ] Save in `.context/docs/mobile_project_mind.md` (create `.context/docs/` if missing).
- [ ] Ensure the document can be consumed in less than 2 minutes.

## Generation rules

1. Keep each bullet to 1 to 2 lines.
2. Prefer facts over narrative.
3. Include only one immediate next action.
4. Include only critical links (repo, board, docs).
5. Include timestamp in header.

## Output template

```markdown
# Project Mind - [Project Name] ([YYYY-MM-DD])

## 1. 30-second view
- [What it is, for whom, and why]

## 2. Architecture snapshot
- Frontend: [...]
- Backend: [...]
- Data: [...]
- Integrations: [...]

## 3. Critical flows
- [Flow A] - [status]
- [Flow B] - [status]
- Common failure point: [...]

## 4. Locked decisions
- [Decision] -> [reason]

## 5. Current state
- Working: [...]
- Unstable: [...]
- Tried and failed: [...]

## 6. Next action
- [ ] [single concrete action + ETA]

## 7. Blockers
- [...]

## 8. Open questions
- [ ] [...]

## 9. Quick links
- [Repo](#) | [Board](#) | [Docs](#)
```

## Success criteria

- All 9 sections are filled.
- Entire file is short enough for mobile reading.
- No outdated or contradictory status information.

## Error handling

### Output too long

Symptom: file becomes hard to scan on mobile.
Solution: keep only active context, move history to `project_status.md`.

### Missing key context

Symptom: AI asks basic clarifying questions.
Solution: improve sections 4, 5, and 7 with objective facts.

