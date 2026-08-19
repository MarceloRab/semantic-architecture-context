---
name: reviewing-code-changes
description: Conducts surgical code reviews focusing on correctness, security, performance, breaking changes, and architecture. Triggers include 'review this', 'code review', 'analisar mudança', 'validar código', 'PR review', 'before commit'. Use before confirming any significant edit or merging changes.
version: 2.0.0
tags: [review, quality, security, performance, architecture, agnostic]
difficulty: intermediate
estimated_time: 5-15min
---

# Reviewing Code Changes

## When to use this skill

- Before the user accepts a suggested change (Human-Validation).
- When the agent has generated complex code and needs self-correction (Agent-Validation).
- When the user asks: "review this", "code review", "analisar mudança", "está bom?", "PR review".
- Before every significant commit or PR merge.
- When integrating a new library or pattern.
- After changes in critical files (controllers, repositories, sync, auth).

## Prerequisites

- Access to the modified files (diff or full content).
- Knowledge of the project's style guide and architecture (if available).
- **Mental Mode**: You are the "Grumpy Senior Reviewer." Be strict, not nice.

---

## Workflow

- [ ] **1. Context Check** — Does this change align with the task goal?
- [ ] **2. Bug Scan** — Does it actually work? (Logic bugs, race conditions, edge cases).
- [ ] **3. Security Scan** — Injection, secrets, permissions, data leaks.
- [ ] **4. Performance Check** — Loops, memory leaks, unnecessary re-renders, DB hits.
- [ ] **5. Breaking Changes** — Contract violations, schema changes, API incompatibility.
- [ ] **6. Architecture Check** — Layer violations, DI abuse, complexity.
- [ ] **7. Clean Code** — Naming, structure, dead code.
- [ ] **8. Regression Risk** — What could this break elsewhere?
- [ ] **9. Final Verdict** — ✅ APPROVED / ⚠️ REQUEST CHANGES / 🛑 BLOCKED.

---

## Instructions

### Review Checklist (5 Categories)

Go through these points one by one. Only signal **material issues** that affect correctness, security, or performance. **Ignore aesthetic style preferences** unless they violate project linting rules.

---

#### 1. 🐞 Correctness (The "Does it Work?" Test)

- [ ] Does the code solve the _asserted_ problem?
- [ ] Are null/undefined cases handled? (e.g., `user?.name` vs `user!.name`)
- [ ] Are error states caught and logged? (try/catch blocks)
- [ ] Are asynchronous operations properly awaited? (race conditions)
- [ ] Are resources released? (streams closed, listeners cancelled)
- [ ] Are business rules respected? (invariants from architecture docs)

---

#### 2. 🔒 Security (The "Hacker" Test)

- [ ] **Secrets in code**: API keys, tokens, passwords hardcoded? (**FAIL immediately**)
- [ ] **Injection**: SQL injection? XSS? Command injection?
- [ ] **Auth**: Is the user ID validated? Can User A see User B's data?
- [ ] **Data Leak**: Sensitive info logged to console?
- [ ] **Crypto**: Weak algorithms? (MD5, hardcoded keys)

---

#### 3. 🚀 Performance (The "Scale" Test)

- [ ] **Loops in loops**: O(N²) complexity where O(N) is possible.
- [ ] **Unnecessary I/O**: Reading file/DB multiple times inside a loop.
- [ ] **Memory**: Large objects held in memory? Streams not closed?
- [ ] **Queries**: N+1 patterns? Missing indexes on large tables?

---

#### 4. 💥 Breaking Changes (The "Contract" Test)

- [ ] API signatures altered without versioning?
- [ ] DB schema changed without migration?
- [ ] Public methods removed that are used externally?
- [ ] Serialization format incompatible with existing data?

---

#### 5. 🏗️ Architecture & Maintainability (The "Future" Test)

- [ ] Layer boundaries respected? (UI → Controller → Repository)
- [ ] Dependencies injected correctly? (no `Get.put` in Views, etc.)
- [ ] Functions > 50 lines? Should be split.
- [ ] Naming reveals intent? (`x` vs `userIndex`)
- [ ] Comments explain "Why", not "What".
- [ ] Dead code removed? (unused imports, variables, functions)

---

### Stack-Specific Addons (Optional)

If reviewing **Flutter/Dart + GetX** code, also check:

| Check           | Rule                                                          |
| --------------- | ------------------------------------------------------------- |
| `Obx` scope     | Must wrap the **smallest possible widget**, not entire lists  |
| `setState`      | Should NOT appear in GetxController code                      |
| Theme tokens    | Use `MyThemeApp.*` and `AppColors.*`, not hardcoded styles    |
| `withOpacity()` | **Deprecated**. Use `withValues(alpha: X)` instead            |
| `const` widgets | Applied to all static widgets (`SizedBox`, `Divider`, `Icon`) |
| `onClose()`     | Workers, subscriptions, and streams cancelled                 |

### What NOT to Signal

```text
❌ Aesthetic style preferences (unless violates linter)
❌ Feature requests or "nice to haves"
❌ Vague compliments or padding
❌ Variable names (unless they cause real confusion)
```

---

## Output Template (The Review Report)

Generate this structured feedback:

````markdown
# 🔍 Code Review Report

**Date:** {{ISO_DATE}}
**Scope:** {{FILES_REVIEWED}}
**Verdict:** [✅ APPROVED / ⚠️ REQUEST CHANGES / 🛑 BLOCKED]

---

## 🟢 Good Points

- [Strong point 1]
- [Strong point 2]

## 🔴 Critical Issues

### {{FILE}}:{{LINE}}

**Severity:** {{Critical | High}}
**Category:** {{Correctness | Security | Performance | Breaking | Architecture}}
**Issue:** {{concise_technical_description}}
**Impact:** {{what_breaks_or_degrades}}

**Suggested Fix:**

\```language
{{minimal_fix_code}}
\```

## 🟡 Improvements (Optional/Nitpicks)

- **[Style]** at `line X`: [suggestion]
- **[Perf]** at `line Y`: [suggestion]

## 🔗 Action Items

1. Fix Critical Issue #1 immediately.
2. [Other actions]

## 📊 Summary

| Metric          | Count |
| --------------- | ----- |
| Files Reviewed  | {{N}} |
| Critical Issues | {{N}} |
| High Issues     | {{N}} |
| Improvements    | {{N}} |

## ✅ Pre-Commit Validation

- [ ] All Futures awaited
- [ ] Resources released (streams, listeners, workers)
- [ ] No secrets hardcoded
- [ ] No N+1 queries
- [ ] Architecture layers respected
- [ ] Linter passes on modified files
````

---

## Success Criteria

**Observable Outcomes:**

- **Blocked**: If critical issue (Security/Logic) found.
- **Request Changes**: If style/perf nits found but logic is sound.
- **Approved**: Only if all 5 categories pass.

**Quality Gates:**

- If Agent approves code with hardcoded secrets → **FAIL** (Severe).
- If Agent approves code that breaks compilation → **FAIL**.
- If Agent misses obvious null pointer possibility → **FAIL**.
- If Agent provides "LGTM!" without detailed analysis → **FAIL**.

---

## Anti-Patterns

| ❌ Don't                                       | ✅ Do Instead                                 |
| ---------------------------------------------- | --------------------------------------------- |
| "LGTM!" (without reading)                      | Read line by line. Provide specific feedback. |
| "Looks good, but maybe..."                     | Be decisive: Approve or Request Changes.      |
| Reviewing only style                           | Focus on logic & security first. Style last.  |
| Ignoring missing tests                         | Ask: "Where are the tests for this?"          |
| Reviewing auto-generated files (.g.dart, etc.) | Skip them. Focus on handwritten code.         |

---

## Portability Notes

- **Antigravity**: Use `view_file` to read the diff/file first.
- **Claude/ChatGPT**: Paste the code snippet + this Skill.
- **Human**: Use as a PR review checklist.

## Related Skills

- [investigating-bugs](../investigating-bugs/SKILL.md) — If review finds a bug, use that skill to fix it.
- [briefing-structural-architecture](../briefing-structural-architecture/SKILL.md) — To check architectural compliance.
- [planning-and-deciding](../planning-and-deciding/SKILL.md) — If review reveals architectural issues needing planning.

## Changelog

### v2.0.0 (2026-02-15)

- MERGED from `code-review` v1.0 + `reviewing-code-changes` v1.0
- Added 5th category: Breaking Changes (from code-review)
- Added Architecture category (from code-review)
- Added Stack-Specific Addons (Flutter/GetX) as optional section
- Added Pre-Commit Validation checklist (from code-review)
- Added Summary table to Report template
- Made 100% agnostic (project-specific examples are optional addons)

### v1.0.0 (2026-02-15)

- Initial release: agnostic checklist + report template.
