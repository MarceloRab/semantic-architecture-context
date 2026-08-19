---
name: validating-flutter-projects
description: Performs context-first technical validation for Flutter repositories with architectural grounding, severity-based findings, and minimal code probing. Triggers include 'validate Flutter project', 'auditar app Flutter', 'check Flutter architecture', and 'security/performance review'. Use when a user needs precise risks and actionable fixes without broad project scans.
version: 1.1.0
tags:
  [
    flutter,
    validation,
    architecture,
    context-first,
    security,
    performance,
    agnostic,
    scope:project-wide,
  ]
difficulty: advanced
estimated_time: 10-20min
---

# Validating Flutter Projects

## When to use this skill

- When the user asks to validate Flutter architecture, security, performance, maintainability, or scalability.
- When a release or refactor needs a technical gate with severity-ranked findings.
- When output must be audit-ready and grounded on existing project context.
- When token budget is constrained and broad scanning is undesirable.

## Prerequisites

- Access to the repository root being validated.
- Mandatory context artifacts readable.
- Ability to inspect targeted files when context evidence is insufficient.

## Dependencies

**Required:**

- Core artifacts: `.cursorrules`, `.antigravityignore`, `.context/active_context.md`, `.context/support/architecture_drawer_contract.md`.
- Optional but recommended: `.context/docs/pendentes/current_execution.md` for recent delivery state.

**Optional:**

- `rg`: targeted evidence probes when explicitly needed.
- Flutter SDK: only for build/release validation when requested.

## Workflow

- [ ] Read mandatory context gate in order (`.cursorrules` -> `.antigravityignore` -> `.context/active_context.md` -> `.context/support/architecture_drawer_contract.md` -> `.context/docs/pendentes/current_execution.md`).
- [ ] **Freshness check**: Verify `active_context.md` last-modified date. If older than 7 days, add a `S3_minor` finding: `"Restart snapshot may be stale — last updated {{date}}. Findings may not reflect recent changes."`.
- [ ] **Token budget**: If `.context/support/token_budget_policy.md` exists, read it and enforce output limits. If absent, default to compact report (max 3 findings per severity level).
- [ ] Load `.context/support/architecture_drawer_contract.md` and derive validation boundaries (mission, scope, contracts, risks).
- [ ] Build a hypothesis map from context before touching source files.
- [ ] Validate dimensions using context evidence first.
- [ ] If evidence is missing, request explicit authorization and probe only the affected modules.
- [ ] Emit technical report with severity-ordered findings and up to 3 priority actions.
- [ ] Apply early stop when `S0_blocker` exists (return blockers/criticals only).

## Instructions

### Core-context compatibility (mandatory)

- Context-first is not optional. Do not start with project-wide scan.
- Use `.context/support/architecture_drawer_contract.md` as the primary frame for:
  - expected layer boundaries
  - quality/safety rules
  - operational flow and high-risk surfaces
- Use `.context/active_context.md` only as a restart snapshot and `.context/docs/pendentes/current_execution.md` to prioritize current risk hotspots.
- If a mandatory context artifact is unavailable, stop and ask the user to restore access.

### Severity and effort

- `severity`: `S0_blocker | S1_critical | S2_major | S3_minor`
- `effort`: `XS | S | M | L`

### Operating modes

- `default`:
  - context-driven validation only
  - no broad code scan
  - max 6 reads (context + targeted files)
- `expanded`:
  - targeted code probes allowed only after explicit user confirmation
  - still avoid full-repository sweeps
  - focus only on modules tied to active findings

### Validation protocol

1. Build validation matrix from architecture skeleton:
   - Architecture integrity
   - Security posture
   - Performance hotspots
   - Maintainability and scalability
   - Testing and release readiness
2. For each potential issue, classify:
   - evidence type: `direct` or `inferred`
   - architectural contract impacted
   - severity and effort
3. If evidence is inferred, mark it clearly and request minimal targeted probe.

### Objective checks by dimension

- `security`: hardcoded secrets, sensitive logs, token storage, unsafe WebView, risky dependency overrides
- `build_release`: obfuscation/split-debug-info, Android shrink/minify/proguard, iOS ATS looseness
- `performance`: rebuild storms, non-virtualized large lists, blocking sync work on UI thread
- `maintainability`: god files, duplicated logic, unclear boundaries for routing/DI/state
- `scalability`: mixed state-management with no boundaries, weak feature modularization
- `testing`: missing tests or missing smoke path for critical behavior

### Stop conditions (gates)

If any `S0_blocker` is confirmed:

- stop normal flow
- return only `S0/S1` items and top 3 actions
- mark verdict as `BLOCKED`

Typical `S0_blocker`:

- secret hardcoded in code or config
- unsafe WebView runtime pattern with unvalidated dynamic input
- clearly insecure release hardening for production path
- systematic resource lifecycle leaks in critical runtime flows

### Output template (required)

```markdown
# Flutter Validation Report

**Mode:** {{default|expanded}}
**Scope:** {{context-only|context+targeted-probes}}
**Reads used:** {{N}}/6
**Verdict:** {{PASS WITH RISKS|REQUEST CHANGES|BLOCKED}}

## Findings (ordered by severity)

### {{S0_blocker|S1_critical|S2_major|S3_minor}} - {{title}}

- Where: `{{path:line or subsystem}}`
- Evidence: {{direct evidence or inferred note}}
- Contract impact: {{architecture/safety contract affected}}
- Recommended fix: {{short imperative}}
- Validation check: {{objective check}}

## Gaps and tradeoffs

- {{what is unknown and why}}
- {{what was intentionally not scanned}}

## Priority actions (max 3)

1. {{action}} - {{why}} - {{acceptance}}
2. {{action}} - {{why}} - {{acceptance}}
3. {{action}} - {{why}} - {{acceptance}}
```

## Success criteria

**Observable outcomes:**

- Findings are presented first, ordered by severity, with evidence and impact.
- Report stays within architectural boundaries defined in `.context/support/architecture_drawer_contract.md`.
- Unknowns are explicit (no hidden assumptions).
- Priority actions are objective and testable.

## Error handling

### Common issue: required context file is missing

**Symptom:** one of `.cursorrules`, `.antigravityignore`, `.context/active_context.md`, `.context/support/architecture_drawer_contract.md` cannot be read.
**Solution:** stop execution and ask the user to restore/access the missing file before scanning code.

### Common issue: context is insufficient for confident verdict

**Symptom:** key claim is only inferred and no direct evidence exists in context artifacts.
**Solution:** request explicit authorization for minimal targeted probes in affected modules only.

### Common issue: targeted probe reveals broader systemic risk

**Symptom:** single module check indicates repeated anti-pattern across boundaries.
**Solution:** propose expanded mode with bounded scope before continuing.

## Resources

- `.context/support/architecture_drawer_contract.md` - scope boundaries and validation contracts.
- `.context/active_context.md` - compact restart snapshot.
- `.context/docs/pendentes/current_execution.md` - current delivery status and pending risks.
- `.cursorrules` - mandatory execution gates.
- `.antigravityignore` - low-signal surfaces to skip.

## Related skills

- `briefing-structural-architecture` - refresh architecture map before deeper validation.
- `reviewing-code-changes` - perform surgical review on proposed fixes.
- `investigating-bugs` - run root-cause flow for critical runtime failures.

## Changelog

### v1.1.0 (2026-02-16)

- Aligned structure and output style to agnostic skills in this repository.
- Replaced JSON/command-centric flow with context-first architectural protocol.
- Added operating modes (`default` and `expanded`) with bounded probing rules.
- Enforced technical markdown report with severity-first findings.

### v1.0.0 (2026-02-16)

- Created agnostic Flutter validation skill from `flutter-validator-optimized_v2_1.md`.
- Added mandatory context-first gate and architecture-informed scoping.
- Kept severity gates, evidence model, and compact JSON output.
