---
name: investigating-bugs
description: Systematic bug investigation and surgical fixing using the Scientific Method. Enforces breakpoint-driven debugging, zero-fallback policy, and minimal-impact fixes. Triggers include 'investigar bug', 'debug this', 'fix error', 'caçar erro', 'root cause analysis', 'por que está quebrando'.
version: 3.0.0
tags:
  [
    debugging,
    stability,
    scientific-method,
    root-cause,
    surgical-fix,
    no-fallback,
  ]
difficulty: advanced
estimated_time: 10-25min
---

# Investigating Bugs (Scientific Protocol — Surgical Mode)

## 🚨 Mandatory Operational Rules (Hard Constraints)

- PROHIBITED:
  - Adding fallback logic to hide errors
  - Silent error handling (catch without action)
  - Guessing fixes without evidence
  - Modifying multiple files without explicit approval
  - Refactoring outside the bug scope

- REQUIRED:
  - Use breakpoints BEFORE forming hypotheses
  - Fix must be surgical (minimal change)
  - Root cause MUST be proven, not assumed
  - One file at a time unless justified

---

## 🧠 Core mindset

You are not allowed to "try fixes".

You must:

1. Observe (via debugger, not assumption)
2. Prove (with runtime evidence)
3. Fix (minimal and precise)

If you skip observation → you are guessing → FAIL.

---

## 🔧 Debug-first policy (CRITICAL)

Before ANY hypothesis:

- Use available debugging tools:
  - Breakpoints (preferred)
  - Step-through execution
  - Variable inspection
  - Call stack tracing

DO NOT proceed without runtime inspection if breakpoints are available.

Priority order:

1. Breakpoint
2. Step execution
3. Logs (only if debugger unavailable)

---

## When to use this skill

- When a bug reappears after a fix (regression/loop)
- When GPT/agent previously introduced the bug
- When fallback logic was added and masked the issue
- When behavior is inconsistent or unclear
- When previous attempts failed

---

## Workflow

- [ ] Debug with breakpoint (mandatory if possible)
- [ ] Define symptom
- [ ] Isolate and reproduce
- [ ] Formulate hypothesis
- [ ] Prove hypothesis (runtime evidence)
- [ ] Pre-fix report (approval gate)
- [ ] Surgical fix (minimal)
- [ ] Validate and regression check
- [ ] Circuit breaker if needed

---

## Step 0 - Debug (MANDATORY FIRST STEP)

Breakpoint location: [...]
Observed runtime values: [...]
Call stack: [...]
Unexpected behavior point: [...]

If breakpoint not used → explain why.

---

## Step 1 - Define symptom (max 3 lines)

Observed: [exact behavior/error]
Expected: [correct behavior]
Where: [file:line / screen / endpoint]

---

## Step 2 - Isolate and reproduce

Rule: if you cannot reproduce, you cannot fix.

- Deterministic steps only
- Explicit scope definition

Scope: [single file/module ideally]

---

## Step 3 and 4 - Hypothesis and proof

| Cause          | Confidence | Evidence (runtime) | Invalidation |
| -------------- | ---------- | ------------------ | ------------ |
| [Hypothesis A] | 90%        | [...]              | [...]        |
| [Hypothesis B] | 60%        | [...]              | [...]        |

Evidence MUST come from:

- breakpoint
- stack trace
- inspected variables

---

## Step 5 - Pre-fix report (HARD GATE)

# Diagnosis

Symptom: [...]
Root cause: [...]
Evidence: [...]
Since when: [...]

# Proposed fix (Surgical)

Action: [...]
Files: [ONE file preferred]
Lines affected: [...]
Why this fixes the root cause: [...]

# Risk analysis

Collateral risk: [none|low|medium]
Regression surface: [...]
Reversibility: [yes|no]

# Validation plan

Steps: [...]
Regression checks: [...]

If root cause is not proven → STOP.

---

## Step 6 - Implement fix (Surgical Mode)

- Modify ONLY what is necessary
- Do NOT:
  - add fallback
  - add defensive noise
  - “improve” unrelated code

Changed file(s): [...]
Diff summary: [...]

---

## Step 7 - Validation

- Re-run reproduction steps
- Re-run breakpoint if needed
- Confirm:
  - bug gone
  - no side effects

---

## Step 8 - Circuit breaker

If second attempt fails:

1. STOP immediately
2. Mark hypothesis as invalid
3. Return to debug phase
4. Do NOT escalate complexity

---

## 🧬 Anti-degradation detection

If the agent:

- suggests fallback
- avoids breakpoint/debug
- proposes broad changes
- cannot explain root cause clearly

ENTER DEGRADED MODE

Action:
STOP execution
Return to Step 0 (debug)
Reduce scope
Rebuild hypothesis

---

## Bug-type shortcuts

- Runtime crash → breakpoint at crash origin
- Logic error → inspect variable mutation chain
- UI bug → inspect state + render triggers
- Data inconsistency → trace input → transformations → output
- Heisenbug → focus on timing/state, not retries

---

## Tiebreaker questions

1. What changed since last working state?
2. Is this deterministic or timing-related?
3. Which variable first deviates from expected?

---

## Success criteria

- Root cause proven via runtime evidence
- Fix is minimal and localized
- No fallback introduced
- No regression introduced
- Debugger confirms corrected behavior

---

## Quality gates

- No breakpoint used (when available) → FAIL
- No hypothesis → FAIL
- No evidence → FAIL
- Fix before diagnosis → FAIL
- Multi-file change without justification → FAIL
- Fallback introduced → FAIL

---

## Error handling

Cannot reproduce:
Increase instrumentation → do not guess

Fix breaks another flow:
Immediate rollback → reassess scope

Fix does not resolve:
Invalidate hypothesis → return to debug

---

## Related skills

- reviewing-code-changes
- planning-and-deciding
- context-orchestrator

---

## Changelog

v3.0.0 (2026-04-09)

- Added breakpoint-first debugging policy
- Enforced surgical fix constraint
- Introduced zero-fallback rule
- Added anti-degradation detection
- Strengthened scope control (single-file bias)
- Added runtime-evidence requirement

v2.0.0 (2026-02-15)

- Added pre-fix report gate
- Expanded hypothesis validation

v1.0.0 (2026-02-15)

- Initial release
