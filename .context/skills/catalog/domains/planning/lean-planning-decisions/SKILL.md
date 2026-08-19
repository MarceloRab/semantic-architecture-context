---
name: lean-planning-decisions
description: Compact planning and decision skill for medium-to-high impact technical tasks. Classifies complexity quickly and outputs only the minimum useful artifact with explicit checks for performance, security, maintainability, and scalability. Use when you need high-quality decisions with low token usage.
version: 1.0.0
tags: [planning, decision-making, architecture, performance, security, scalability, agnostic]
difficulty: beginner
estimated_time: 3-10min
---

# Lean Planning Decisions

## When to use

- When you need a fast technical decision before implementation.
- When there are 2+ plausible approaches and you need a recommendation.
- Before touching critical paths (latency, auth, data integrity, infra cost).
- When the user asks for a concise/low-token plan.

## Core principle

**Minimum artifact, maximum signal.**

- Classify quickly.
- Analyze only what changes the decision.
- Prefer reversible first steps.

## Workflow (token-efficient)

1. **Frame (30-60s):** objective, constraints, affected modules.
2. **Classify:** S1 / S2 / S3.
3. **Route output:** direct action, mini-plan, or options table.
4. **Quality gate:** performance + security + maintainability + scalability.
5. **Recommend first step + pivot condition.**

## Complexity routing

| Level | Typical scope | Output |
| --- | --- | --- |
| **S1 Quick** | 1 file, low risk, obvious change | 3-5 bullets + execute |
| **S2 Focused** | 1-5 files, some uncertainty | `MINI_PLAN` |
| **S3 Strategic** | multi-module, irreversible risk, architecture impact | `DECISION_NOTE` with 2-3 options |

If unclear between levels, choose the higher level.

## Output templates

### 1) MINI_PLAN (S2)

```markdown
# MINI_PLAN: [Task]

## Goal
[1 sentence]

## Scope
- Files/modules: [...]
- Constraints: [...]

## Steps
1. [Atomic action]
2. [Atomic action]
3. [Atomic validation]

## Quality Gate (must pass)
- Performance: [latency/throughput/memory expectation]
- Security: [authn/authz/input/data exposure]
- Maintainability: [readability, coupling, test impact]
- Scalability: [load growth, bottlenecks, limits]

## Go / Pivot
- Go if: [objective metric]
- Pivot if: [clear failure signal]
```

### 2) DECISION_NOTE (S3)

```markdown
# DECISION_NOTE: [Decision]

## Context
- Objective: [...]
- Non-negotiables: [...]

## Options (2-3, structurally different)
| Option | Upside | Risk | Reversibility | Best fit |
|---|---|---|---|---|
| A |  |  |  |  |
| B |  |  |  |  |

## Cross-check (required)
- Performance: [winner + why]
- Security: [winner + why]
- Maintainability: [winner + why]
- Scalability: [winner + why]

## Recommendation
- Choose: [A/B]
- First reversible step: [...]
- Validation metric: [...]
- Pivot condition: [...]
```

## Decision heuristics

- Prefer **simpler architecture** when gains are marginal.
- Prefer **reversible changes** when uncertainty is high.
- Prefer **local optimizations** before distributed complexity.
- Prefer **secure defaults** over compensating controls.

## Guardrails

- Do not generate long narrative blocks.
- Do not list generic risks; only decision-changing risks.
- Do not produce more than 3 options.
- Do not proceed without explicit metric for success.

## Success criteria

- Chosen route (S1/S2/S3) is explicit.
- Output is actionable in under 2 minutes of reading.
- Includes explicit checks for performance, security, maintainability, scalability.
- Includes go/pivot criteria.
