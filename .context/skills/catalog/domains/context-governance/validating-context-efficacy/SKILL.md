---
name: validating-context-efficacy
description: Audits context quality for code anchoring, token discipline, and execution governance. Triggers include 'validar contexto', 'auditar contexto', 'context efficacy', 'meu contexto está funcionando?', 'avaliar qualidade do contexto'.
version: 1.0.0
tags: [context, audit, governance, token-economy, agnostic]
difficulty: advanced
estimated_time: 5-12min
---

# Validating Context Efficacy

## When to use this skill

- Periodically (biweekly or post-sprint) to verify context health.
- After running `context-maintenance`.
- When agents ask too many clarifying questions.
- When agents keep scanning files that should not be needed.
- When context drift is suspected.

## Prerequisites

Mandatory core:

1. `.cursorrules`
2. `.antigravityignore`
3. `.context/active_context.md`
4. `.context/support/architecture_drawer_contract.md`
5. `.context/docs/pendentes/current_execution.md`

Policy overlay:

1. `.context/support/context_read_order.md`
2. `.context/support/token_budget_policy.md`
3. `.context/support/freshness_policy.md`
4. `.context/support/context_contract.md`
5. `.context/support/archive_policy.md`

If mandatory core is missing, return `REJECTED` immediately.

## Workflow

- [ ] Phase 1: context surface mapping
- [ ] Phase 2: code anchoring validation (sampled claims)
- [ ] Phase 3: premise gate simulation
- [ ] Phase 4: token efficiency analysis
- [ ] Phase 5: decision influence test
- [ ] Output: strict verdict

## Constraints

- Default mode: follow project token policy (hard cap from `.context/support/token_budget_policy.md`).
- Use directed sampling (3 critical claims), never exhaustive scan.
- Read-only audit: do not edit files during this skill.
- If budget is insufficient for a reliable verdict, return `REJECTED` with corrective action: request explicit approval for extended audit.

## Phase rules

### Phase 1 - Context surface mapping

Classify context files as:

- `hot` (session-critical)
- `stable` (reference docs)
- `cold` (historical)
- `noise` (duplicated, stale, non-operational)

### Phase 2 - Code anchoring

For 3 critical claims from context:

1. extract claim
2. locate concrete evidence in code (path + symbol)
3. classify:
   - `VERIFIED`
   - `PARTIALLY_VERIFIED`
   - `NOT_FOUND`

If more than 20% of sampled claims are `NOT_FOUND`, return `REJECTED`.

### Phase 3 - Premise gate simulation

Simulate one risky task and verify if context alone can answer required premises.

If task could proceed with blind assumptions, return `REJECTED`.

### Phase 4 - Token efficiency

Check:

1. Is context loaded selectively (not full load every session)?
2. Is hot/warm/cold layering respected?
3. Is `.context/active_context.md` concise and operational?
4. Are historical items separated from operational context?

If layering is absent or non-operational load is high, return `REJECTED`.

### Phase 5 - Decision influence

Answer objectively:

1. Did context prevent at least one wrong assumption?
2. Did it reduce exploratory scanning?
3. Did it improve task routing (GO/NO-GO or skill selection)?
4. Did it reduce scope drift?

If 2 or more answers are `NO`, return `REJECTED`.

## Scoring gates

All must pass:

- Code anchoring >= 80% verified
- Premise enforcement present
- Token discipline enforced
- Decision influence demonstrable
- Redundancy controlled

## Output format (strict)

```text
Context Audit Result
- Claims verified: X/Y (Z%)
- Premise gate: YES/NO
- Layered context: YES/NO
- Redundancy: LOW/MEDIUM/HIGH
- Token discipline: PASS/FAIL

Verdict: APPROVED | REJECTED

Corrective actions (if REJECTED):
1. ...
2. ...
3. ...
```

## Non-negotiable rule

Context must govern execution behavior.
If it only documents but does not constrain decisions, verdict must be `REJECTED`.

## Related skills

- `context-orchestrator` (per-task GO/NO-GO gate)
- `context-maintenance` (structural hygiene and archival)

