---
name: project-directives
description: "Use primarily from planejamento-contratual-harness during planning, and before sensitive implementation/review when .context/DIRECTIVES.md exists, to qualify decisions that may become project paradigms: remote SSOT, offline-first, ID construction, sync strategy, API contract, persistence authority, permission authority, or repeated architectural rule. Qualify, read, propose, and enforce project directives without writing recorded context automatically."
---

# Project Directives

This skill governs semantic directives. It does not contain project directives.
Real directives live in the target repository at `.context/DIRECTIVES.md`.
Large projects may also keep `.context/directives_map.md` as an impact index.

## Boundary

- Context gate: architecture, known paths, recorded context targets.
- Directive gate: semantic rule that governs future implementation decisions.

Do not update `active_context`, `current_execution`, drawers, or recorded
context from this skill. If a durable memory update is needed, hand off to the
project's recorded-context/update skill with a known context path.

## Invocation Model

Primary invoker: `planejamento-contratual-harness`.

Use this skill during planning when a decision may define reusable semantics for
more than one implementation. Do not run it as a global hook for every edit.

Execution and review may consult this skill only when `.context/DIRECTIVES.md`
exists or when the task touches a sensitive layer covered by a known directive.

## Qualification

A decision is a directive only when it passes at least 2 of 3:

1. Broad scope: affects multiple modules, features, or future tasks.
2. Low reversibility: reverting requires broad refactor or migration.
3. Precedent: creates a pattern for analogous future decisions.

Also require one of these:

- The decision likely affects at least two future implementations.
- The decision protects a critical boundary: identity, persistence, sync,
  permission, validation authority, schema, API contract, or domain rule.

Examples that usually qualify:

- Remote SSOT vs offline-first.
- ID construction format for persisted/synced entities.
- Sync conflict strategy.
- Internal API/data contract authority.
- Validation or permission authority.

Do not register local style, naming, one-file behavior, list ordering, or cheap
reversible choices as directives. Those belong in the plan for that track, not
in `.context/DIRECTIVES.md`.

## Required Read Before Code

Before code implementation, refactor, or review:

1. Check only whether `.context/DIRECTIVES.md` exists at the target repo root.
2. If absent, state: `No project directives registered.`
3. If `.context/directives_map.md` exists and target diff paths are known, read
   the map first to identify candidate directive IDs.
4. Read only `.context/DIRECTIVES.md` rows for candidate IDs, or the compact
   full file when no map exists.
5. If an active directive conflicts with the task, stop and request explicit
   human decision.

Do not read `active_context`, drawers, or `current_execution` for this skill.
That is context-gate work.

## Directive Format

When creating or proposing `.context/DIRECTIVES.md`, include this compact
pointer before the table:

```markdown
impact_map: .context/directives_map.md
map_policy: index only; do not duplicate semantic rules
```

Use one markdown table row per directive:

```markdown
| ID | Status | Date | Applies_to | Rule | Forbidden | Validation | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D001 | active | 2026-07-04 | sync,persistence | Orders are remote SSOT; client writes only after server confirmation | Local optimistic persistence as source of truth | Repository write path confirms server response before durable local state | planning-report-2026-07-04 |
```

Field rules:

- `Applies_to`: concrete layer, module, or file group.
- `Rule`: semantic rule the implementation must obey.
- `Forbidden`: pattern that would violate the directive.
- `Validation`: signal proving the directive was obeyed.
- `Source`: report, PRD, issue, commit, or user decision.

Escape literal `|` inside cells as `\|`.

## Directives Impact Map

Use `.context/directives_map.md` only as an index from directive IDs to likely
diff targets. It belongs to recorded context, not to the semantic directive
itself.

Minimal format:

```markdown
source_of_truth: .context/DIRECTIVES.md
purpose: map directive_id to diff targets without duplicating semantic rules

| directive_id | applies_to | diff_targets | trigger_when | plan_action |
| --- | --- | --- | --- | --- |
| D001 | sync,persistence | lib/data/**; lib/sync/** | write/read/sync changes | add Rule to track requirements; add Forbidden to track forbidden list |
```

Rules:

- Do not duplicate `Rule`, `Forbidden`, rationale, history, or execution
  evidence in the map.
- Keep only `directive_id`, `applies_to`, `diff_targets`, `trigger_when`, and
  `plan_action`.
- If edited paths match `diff_targets`, read only the mapped directive rows from
  `.context/DIRECTIVES.md`.
- If the map is absent, fall back to `.context/DIRECTIVES.md`.
- If a new directive has reusable diff impact, propose a matching map row as a
  recorded-context update after the directive is accepted.

## Capture Flow

Never write automatically.

When the user says a decision is a directive, or the planner detects a decision
that appears to create a paradigm:

1. Apply the qualification test.
2. Check the proposed directive does not contradict active directives.
3. Propose one row for `.context/DIRECTIVES.md`.
4. If the directive has reusable diff impact, propose one row for
   `.context/directives_map.md`.
5. Write only after explicit human confirmation.

If it fails qualification, say it is not a directive and continue without
recording.

## Planning Integration

During contractual planning:

- Use `planejamento-contratual-harness` as the normal entrypoint for this skill.
- Treat accepted active directives as closed planning decisions.
- If a directive applies to a sensitive track, copy its `Rule` into the track
  requirements.
- Copy its `Forbidden` value into the track forbidden list when it names an
  implementation shortcut.
- Include its `Validation` signal in acceptance criteria or validation
  expectation.
- Put local or one-track-only decisions in the plan only; do not promote them
  to `.context/DIRECTIVES.md`.
- Use `.context/directives_map.md` to locate directive IDs by diff target; do
  not treat it as the directive source of truth.

If a new directive also requires durable project memory, use the recorded
context gate after the target path is known. Do not use FastContext to discover
where to write directives or context.

## Output

When this skill is used, report:

```text
Project directives:
- Invoked by: planejamento-contratual-harness|execution|review|manual
- File: present|absent
- Relevant active directives: [IDs or none]
- Conflicts: [none or directive ID + reason]
- Candidate directive: [none or proposed row awaiting confirmation]
- Candidate map row: [none or proposed directives_map row]
- Track promotion: [none or requirement/forbidden item]
```
