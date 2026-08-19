---
name: context-scout
description: Explores recorded context and current code with bounded, read-only, evidence-first probes before planning or execution. Use when Codex must cheaply locate likely architecture flow, business-rule location, bug diff target, context/code divergence, or decide whether a sequential execution trail needs a local handoff before involving a stronger agent.
version: 1.0.0
tags: [context-governance, exploration, evidence, token-economy, handoff, no-guessing]
difficulty: advanced
estimated_time: 5-15min
---

# context-scout

## Purpose

Produce a compact **Context Exploration Report** before planning, delegation, or implementation.

This skill is read-only. It scouts; it does not fix.

## Hard constraints

- Do not edit, create, delete, format, patch, build, test, or install.
- Do not update `.context/active_context.md` or any handoff file.
- Do not treat recorded context as proof of current code state.
- Do not treat current code as proof of canonical business rule.
- Do not infer when evidence is missing; report a gap.
- Do not ask for a handoff file unless the task is an explicit sequential trail and no `handoff_file` is declared.

## Inputs

Require or infer:

- `intent`: `architecture | business_rule | bug_diff`
- `context_mode`: `none | minimal | canonical | compare`
- `user_target`: problem, feature, rule, bug, stack trace, or symbol
- optional: `known_files`, `known_symbols`, `domain_terms`, `max_radius`

## Context modes

- `none`: symbol/file/stack-trace lookup only; no canonical conclusion.
- `minimal`: read the project core chain only.
- `canonical`: read core chain plus one routed drawer or domain doc.
- `compare`: explicitly compare recorded context against current code evidence.

When context was already read by the parent agent, reuse the extracted premises and do not reopen files unless new evidence is required.

## Sequential handoff rule

Decide and report:

```yaml
sequential: true | false
handoff_required: true | false
handoff_file: path | ASK_USER | none
```

Use `sequential: true` only when work is multi-step, delegated to a weak executor, expected to resume later, or requires local operational memory.

If `sequential: true` and no `handoff_file` exists, stop before delegation and ask the user to choose or confirm one.

If `sequential: false`, set `handoff_file: none` and do not ask.

## Radius protocol

- Radius 0: user-mentioned files, stack trace files, exact symbols, exact error text.
- Radius 1: direct imports, direct references, direct callers/callees.
- Radius 2: related controllers, services, repositories, usecases, routes, bindings, DI.
- Radius 3: only after a declared critical gap; record why radius 2 failed.

Always record max radius reached, why it stopped, and what evidence supports the boundary.

## Intent protocols

### architecture

Find entrypoints and structural flow without deep internal implementation.

Include evidence for: `main`, app root, routes, bindings, DI, providers, root controllers, modules, services, repositories, external adapters, Firebase config, Drift/local database config, and layer boundaries.

If logic is mixed into widgets/controllers, report the coupling as evidence. Do not assume the ideal architecture.

### business_rule

Find where a rule is validated, calculated, blocked, permitted, synchronized, charged, notified, or persisted.

Allowed evidence:

- domain term occurrence
- file/class/method names
- imports and direct calls
- cross references
- throws/exceptions
- conditionals tied to the investigated term
- related tests, if already in scope

Forbidden evidence:

- “seems like”
- many `if/switch/throw` without domain linkage
- generic names without cross-reference
- ideal architecture assumptions
- rule inference from absent or incomplete code

### bug_diff

Order:

1. Parse symptom, stack trace, file, symbol, line, message, and domain terms.
2. Locate direct occurrence.
3. Locate direct callers/references.
4. Walk outward by radius only while evidence remains connected.
5. Treat `git diff` and `git log` as signals, never proof.
6. Cross-check minimal recorded context.
7. List primary target, secondary targets, do-not-edit paths, confidence, and gaps.

## Evidence rules

Every primary or secondary target must include:

- file path
- symbol or line reference when available
- evidence text or command result summary
- reason for relevance
- confidence impact

If evidence is insufficient, say:

- what was searched
- what was not found
- what data is missing
- what controlled search is needed next

## Output format

```markdown
# Context Exploration Report

## Intent
architecture | business_rule | bug_diff

## Target
...

## Sequential Decision
- sequential: true|false
- handoff_required: true|false
- handoff_file: path|ASK_USER|none
- reason:

## Context Mode
none | minimal | canonical | compare

## Stored Context Used
| file | reason | premise | freshness risk |

## Project Signals
- language/framework:
- relevant folders:
- entrypoints:
- tools available:
- ignored/generated surfaces:

## Search Strategy
- terms:
- commands:
- inclusion criteria:
- exclusion criteria:
- max radius:
- stop reason:

## Evidence Table
| file | symbol/line | evidence | relevance | type |

## Flow Map
entry → route/binding → controller/provider → service/usecase → repository/adapter → storage/external

## Stored Context vs Current Code
Required for `canonical` and `compare`.

## Primary Target
- file:
- symbol:
- evidence:
- confidence:

## Secondary Targets
- ...

## Do Not Edit
- path: reason

## Confidence
High | Medium | Low

## Gaps / Blocking Points
- ...

## Handoff Prompt for Stronger Agent
Compact prompt with objective, targets, evidence, divergences, risks, validations, do-not-edit paths, and pending questions.
```

## Quality gates

Fail the scout if:

- a conclusion lacks evidence;
- max radius is missing;
- commands/search terms are missing;
- `canonical` or `compare` omits context-vs-code comparison;
- `sequential: true` lacks `handoff_file` or `ASK_USER`;
- `sequential: false` asks for a handoff.
