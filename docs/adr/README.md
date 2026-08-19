# Architecture Decision Records (ADRs)

This directory contains the Architecture Decision Records (ADRs) for the Semantic Architecture Context (SAC) standard and tooling.

---

## What is an ADR?

An Architecture Decision Record (ADR) captures a significant architectural, semantic, or governance decision made for SAC, along with its context, considered alternatives, and consequences.

All proposed changes to tag grammar, MCP protocol interfaces, domain manifest specifications, or core execution pipeline stages must be documented via an ADR before implementation.

---

## ADR Lifecycle

```
Proposed ──> Accepted ──> [ Deprecated | Superseded ]
```

- **Proposed:** Under active discussion via GitHub Issue / PR.
- **Accepted:** Approved and implemented in the SAC codebase.
- **Deprecated:** No longer recommended, but maintained for backward compatibility.
- **Superseded:** Replaced by a newer ADR (must link to the successor ADR).

---

## ADR Template

When authoring a new ADR, create `docs/adr/ADR-XXX-<short-name>.md` using the following structure:

```markdown
# ADR-XXX: [Short Title of Decision]

- **Status:** Proposed | Accepted | Deprecated | Superseded
- **Date:** YYYY-MM-DD
- **Authors:** [Name / GitHub Handle]
- **Relevant Issue:** [Link to GitHub Issue]

## Context & Problem Statement
Describe the context, the limitation of the existing design, and why a decision is necessary. Provide concrete examples or reproduction steps where applicable.

## Decision Drivers
- Driver 1 (e.g., Contract safety, performance, language support)
- Driver 2

## Considered Options
1. Option 1: [Description, pros, cons]
2. Option 2: [Description, pros, cons]

## Decision Outcome
Chosen option: [Option X], because [rationale].

### Positive Consequences
- [Consequence 1]

### Negative Consequences / Trade-offs
- [Trade-off 1]

## Invariants & Constraints
Explicit rules that must hold permanently after this decision:
1. Invariant 1
2. Invariant 2

## Backward Compatibility & Recovery
Describe reachable legacy states and the deterministic recovery path for each.

## Verification & Definition of Done (DoD)
Deterministic verification criteria to prove compliance.
```

---

## Index of ADRs

| ADR | Title | Status | Date |
|---|---|---|---|
| *ADRs will be registered here as the standard evolves.* | | | |
