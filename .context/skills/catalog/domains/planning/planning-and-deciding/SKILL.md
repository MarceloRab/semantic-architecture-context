---
name: planning-and-deciding
description: Unified planning skill that triages task complexity and routes to the right depth of analysis. Combines complexity triage (classify → route → act), strategic trade-off analysis (compare options, hidden risks, pivot conditions), and structured pre-implementation framework. Triggers include 'modo arquiteto', 'planejar tarefa', 'analisar opções', 'avaliar trade-offs', 'flash plan', 'plan this'. Use before any non-trivial task.
version: 1.1.0
tags:
  [
    planning,
    architecture,
    triage,
    strategy,
    decision-making,
    trade-offs,
    agnostic,
  ]
difficulty: intermediate
estimated_time: 5-25min
---

# Planning & Deciding

## When to use this skill

- Before **any task** where complexity is uncertain — this skill decides the approach.
- When starting a new feature, refactoring, or bug fix and you need to **triage first**.
- When deciding between **technical approaches** for a structural problem.
- Before changes with **architectural impact** or **low reversibility**.
- When there are **non-obvious trade-offs** between options.
- When the user says: "modo arquiteto", "plan this", "analisar opções", "flash plan", "avaliar trade-offs".
- Before committing significant time (>2h) in one technical direction.

## Prerequisites

- `.cursorrules`
- `.antigravityignore`
- `.context/active_context.md`
- `.context/support/architecture_drawer_contract.md`
- `project_status.md`
- Access to the project's source code.
- Understanding of project constraints (deadline, budget, team).
- Optional: any local workflow tracker for progress visibility.

## Core-context alignment (mandatory)

- Run `context-orchestrator` in `default` mode first.
- Proceed with planning only when the gate returns `GO`.
- Keep read budget aligned with context policies (`default` 6, `expanded` 10 with explicit confirmation).

---

## Core Mindset

> **Act as a Senior Tech Lead.**
> Your job is NOT to code immediately — it's to **classify, plan, and hand off**.
>
> - If it's simple → **do it**.
> - If it's medium → **plan it, then do it**.
> - If it's complex → **decompose it, don't touch it**.
> - If there are trade-offs → **analyze them before choosing**.

---

## Workflow

- [ ] **1. Gate Context** — Run `context-orchestrator` and validate `GO`.
- [ ] **2. Gather Context** — Read mandatory core context and identify affected files/modules.
- [ ] **3. Classify Complexity** — Use the Triage Matrix.
- [ ] **4. Route to Flow** — 🟢 Green / 🟡 Yellow / 🔴 Red.
- [ ] **5. Execute Flow** — Generate appropriate output.
- [ ] **6. Analyze Trade-offs** — If YELLOW/RED, evaluate options deeply.
- [ ] **7. Confirm with User** — Present result and wait for authorization.

---

## Instructions

### Phase 1 — Gather Context

Before classifying, collect minimum context:

```text
┌─ Context Checklist
│  □ What is the task? (1 sentence)
│  □ Which files/modules are affected?
│  □ Are there architectural constraints or invariants?
│  □ Does it touch external integrations? (APIs, DB, auth)
│  □ Is there a risk of regression?
└─
```

**Sources** (in priority order):

1. `.context/active_context.md`
2. `.context/support/architecture_drawer_contract.md`
3. `project_status.md`
4. Relevant agent profiles (`.context/agents/*.md`) only if still needed

> **🔌 Tooling Optional**: If workflow automation is available, use it only as a support layer.

---

### Phase 2 — Triage Matrix

```text
┌──────────────────────────────────────────────────────────────────┐
│                    COMPLEXITY TRIAGE MATRIX                      │
├──────────┬──────────────┬────────────────────────────────────────┤
│  Scale   │  Color Code  │  Criteria                             │
├──────────┼──────────────┼────────────────────────────────────────┤
│  QUICK   │  🟢 GREEN    │  1 file, no architecture impact,      │
│          │              │  < 5 min, typo/config/style fix        │
├──────────┼──────────────┼────────────────────────────────────────┤
│  SMALL   │  🟡 YELLOW   │  1-3 files, simple feature,           │
│          │              │  no new patterns, ~15 min              │
├──────────┼──────────────┼────────────────────────────────────────┤
│  MEDIUM  │  🟡 YELLOW   │  3-8 files, design decisions needed,  │
│          │              │  may touch integrations, ~30 min       │
├──────────┼──────────────┼────────────────────────────────────────┤
│  LARGE   │  🔴 RED      │  8+ files, new patterns/architecture, │
│          │              │  multi-layer, security/compliance,     │
│          │              │  risk of hallucination, ~1+ hour       │
└──────────┴──────────────┴────────────────────────────────────────┘
```

**Decision Table:**

| Scale     | Action                                                        | Output Artifact              |
| --------- | ------------------------------------------------------------- | ---------------------------- |
| 🟢 QUICK  | **Execute directly.** No planning.                            | Code changes + 1-line report |
| 🟡 SMALL  | **Create FLASH_PLAN.** Single phase.                          | `FLASH_PLAN.md` (compact)    |
| 🟡 MEDIUM | **Create FLASH_PLAN** + **Trade-off Analysis** if ≥2 options. | `FLASH_PLAN.md` (detailed)   |
| 🔴 LARGE  | **STOP & DECOMPOSE.** Do NOT code.                            | Sub-tasks in status tracker  |

---

### Phase 3 — Execute the Appropriate Flow

#### 🟢 GREEN Flow (QUICK)

```text
┌─ Flow: Direct Execution
│  1. List steps in chat (3-5 bullets)
│  2. Execute code changes immediately
│  3. Report: "✅ Simple task completed: [summary]"
└─ No artifact generated.
```

**Rules:**

- No plan file needed.
- Confirm with user only if change is destructive.

---

#### 🟡 YELLOW Flow (SMALL / MEDIUM)

> **Rule**: You do NOT execute code yet. You create the "Treasure Map" for execution.

```text
┌─ Flow: Structured Planning
│  1. Identify all affected files
│  2. Read relevant agent profiles (if available)
│  3. If MEDIUM and ≥2 viable approaches → do Trade-off Analysis (Phase 4)
│  4. Write FLASH_PLAN.md using template below
│  5. Include REAL code in the plan
│  6. Ask: "Plan saved. Authorize execution?"
└─ Artifact: FLASH_PLAN.md
```

**FLASH_PLAN Template:**

```markdown
# 🎯 FLASH PLAN: [Task Name]

## 📊 Dashboard

| Field                | Value                                 |
| -------------------- | ------------------------------------- |
| **Objective**        | [Clear 1-line summary]                |
| **Scale**            | 🟡 [SMALL/MEDIUM]                     |
| **Estimated effort** | ~[X] min                              |
| **Files affected**   | [count]                               |
| **Risk level**       | [Low/Med/High]                        |
| **Constraints**      | [architectural invariants to respect] |

## ⚡ Phase 1: Execution

### ✅ Step 1.1: [Action description]

**File**: `path/to/file.ext`
**Action**: `CREATE` | `MODIFY (Lines X-Y)` | `DELETE`

**Ready-to-paste code:**

\`\`\`language
// REAL CODE HERE. Executor should paste, not think.
\`\`\`

### ✅ Step 1.2: [Next action]

[Same structure...]

---

## 🔍 Validation

- [ ] Lint/analyze passes on modified files
- [ ] Core flow tested (manual or automated)
- [ ] No invariant broken

## 🚀 Handoff

> "Follow this plan step by step."
```

**Key Rules:**

- **Code must be REAL** — no pseudocode, no placeholders, no `// TODO`.
- **Each step must be atomic** — one file, one action, one code block.
- **Specify exact lines** when modifying existing files.

---

#### 🔴 RED Flow (LARGE)

> **Rule**: Task too large for single-shot. Risk of hallucination or token overflow.

```text
┌─ Flow: Decompose & Stop
│  1. Analyze task → identify 2+ sub-components
│  2. Classify each sub-component (most should be YELLOW)
│  3. Add sub-tasks to project status tracker
│  4. Report: "COMPLEX task decomposed into [N] sub-tasks."
│  5. Ask user to select first sub-task to begin
└─ Artifact: Updated status tracker (no code generated)
```

**Decomposition Template:**

```text
🔴 COMPLEX TASK: [Original Task Name]
├── 🟡 Sub-task 1: [Name] — [1-line scope]
├── 🟡 Sub-task 2: [Name] — [1-line scope]
├── 🟡 Sub-task 3: [Name] — [1-line scope]
└── 🟢 Sub-task 4: [Name] — [1-line scope]

Recommended order: 1 → 2 → 3 → 4
Dependencies: Sub-task 2 depends on 1.
```

**Rules:**

- **Do NOT generate code** for RED tasks.
- **Do NOT create a single giant plan**.
- Each sub-task should fit into YELLOW or GREEN when taken alone.
- Maximum 5 top-level sub-tasks. Use nesting for details.

---

### Phase 4 — Trade-off Analysis (When ≥2 Viable Approaches)

> Use this when you have a MEDIUM or large decision with structurally different options.
> Skip for QUICK/SMALL when the path is obvious.

#### 4.1 Problem Definition (max 5 lines)

- What is being decided?
- Main objective?
- Critical constraints?
- Relevant implicit assumptions?

#### 4.2 Viable Options (min 2, max 3)

For each option:

> **Option A — [Direct Technical Name]**
>
> - **Approach:** [How it works]
> - **Key Advantages:** [2-3 bullets]
> - **Concrete Risks (obvious + hidden):** [2-3 bullets]
> - **Complexity:** (Low / Medium / High)
> - **Reversibility:** (Easy / Medium / Hard / Irreversible)
> - **Key Validation Test:** What proves this works? How hard to test? (Easy/Med/Hard)
> - **Best Use Case:** When is this the ideal choice?

Repeat for B and C if needed.

**Rule:** Options must be **structurally different**, not cosmetic variations.

#### 4.3 Comparison Table

```markdown
| Criterion            | A   | B   | C   |
| -------------------- | --- | --- | --- |
| Complexity           |     |     |     |
| Technical Risk       |     |     |     |
| Testability          |     |     |     |
| Reversibility        |     |     |     |
| Implementation Speed |     |     |     |
```

Add **cost** or **scalability** only if decisive in this context.

#### 4.4 Realistic Scenarios (max 8 lines)

- **Safe Path:** Lowest structural risk and highest predictability.
- **Optimized Path:** Highest potential gain, higher risk exposure.
- **How it can fail:** Main failure vector + early warning signal.

#### 4.5 Hidden Risks (Top 3)

Only risks **specific to this situation**, not generic ones:

| Risk | Trigger/Signal | Practical Mitigation |
| ---- | -------------- | -------------------- |
|      |                |                      |

#### 4.6 Validation & Go/No-Go

**Reversible Initial Experiment:** Smallest step that generates reliable signal.

**Validation Metric:** Objective success indicator + clear failure criterion.

- **Go if:** [condition]
- **No-Go if:** [condition]

#### 4.7 Final Recommendation

- Recommended option
- Objective justification
- First concrete step
- Explicit pivot condition

---

### Critical Questions (Use at least 3)

Select the most relevant to context:

1. Are we solving the root cause or just the symptom?
2. If we wanted to fail, what decision would we make?
3. At what point does this decision become irreversible?
4. What would an external expert question immediately?
5. What is the opportunity cost of this choice?
6. If we needed to be 10x better, would this approach still work?

---

## Visual Decision Flowchart

```text
                    ┌─────────────────┐
                    │  New Task Arrives│
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Gather Context  │
                    │  (5 checkboxes)  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Classify Scale   │
                    │ (Triage Matrix)  │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼───┐  ┌──────▼──────┐  ┌────▼────────┐
     │ 🟢 GREEN   │  │ 🟡 YELLOW   │  │ 🔴 RED      │
     │ Execute    │  │ Plan First  │  │ Decompose   │
     │ Directly   │  │ Then Execute│  │ Then Select  │
     └────────┬───┘  └──────┬──────┘  └────┬────────┘
              │              │              │
     ┌────────▼───┐  ┌──────▼──────┐  ┌────▼────────┐
     │ Code +     │  │ FLASH_PLAN  │  │ Sub-tasks   │
     │ Report     │  │ + Approval  │  │ in Tracker  │
     └────────────┘  └──────┬──────┘  └─────────────┘
                            │
                   ┌────────▼────────┐
                   │ ≥2 approaches?  │
                   └────┬───────┬────┘
                   No   │       │ Yes
                   ┌────▼──┐ ┌──▼────────────┐
                   │Execute│ │Trade-off       │
                   │ Plan  │ │Analysis (§4)   │
                   └───────┘ │→ Recommendation│
                             └────────────────┘
```

---

## Success Criteria

**Per Scale:**

| Scale     | Success Looks Like                                                            |
| --------- | ----------------------------------------------------------------------------- |
| 🟢 GREEN  | Code change done + 1-line report. No plan artifact.                           |
| 🟡 YELLOW | `FLASH_PLAN.md` with real code, ready for blind execution. User approved.     |
| 🟡+Trade  | Trade-off analysis with ≥1 hidden risk identified. Go/No-Go defined.          |
| 🔴 RED    | Task decomposed into ≤5 sub-tasks. No code generated. Status tracker updated. |

**Trade-off Analysis Quality:**

- ✓ Identifies at least 1 hidden risk not obvious at first glance
- ✓ Explains clearly how to test before committing
- ✓ Maintains conscious reversibility
- ✓ Defines explicit pivot condition
- ✓ Delivers actionable next step

**Quality Gates:**

- If a YELLOW plan contains pseudocode or `// TODO` → **FAIL**. Code must be real.
- If a RED task is attempted in one shot → **FAIL**. Must decompose first.
- If a GREEN task generates a plan file → **FAIL**. Over-engineering.
- If trade-off options are just cosmetic variations → **FAIL**.
- If analysis is >2 pages without converging → **FAIL**. Apply brevity rules.

---

## Anti-Patterns

| ❌ Don't                           | ✅ Do Instead                              |
| ---------------------------------- | ------------------------------------------ |
| Generate code for RED tasks        | Decompose into sub-tasks first             |
| Create plans for GREEN tasks       | Execute directly, report in chat           |
| Write pseudocode in FLASH_PLAN     | Write real, paste-ready code               |
| Make one giant step with 200 lines | Split into atomic steps (1 file, 1 action) |
| Start coding without classifying   | Always triage first (30 seconds)           |
| Present cosmetic option variations | Only structurally different approaches     |
| Over-analyze when path is obvious  | Skip trade-off if only 1 viable approach   |
| Produce generic risk lists         | Only risks specific to this context        |

---

## Error Handling

### Issue: Misclassification (harder than expected)

**Symptom:** Execution hits unexpected files or patterns mid-task.
**Solution:** Stop. Reclassify upward (GREEN→YELLOW or YELLOW→RED). Generate appropriate artifact.

### Issue: Paralysis by analysis

**Symptom:** Analysis grows beyond 2 pages without converging to recommendation.
**Solution:** Apply "max 5 lines" rule per section. Focus on the reversible initial experiment.

### Issue: Options are superficial

**Symptom:** All options look like variants of the same approach.
**Solution:** Force at least one option using a different stack/paradigm. Ask: "If this technology didn't exist, how would we solve it?"

### Issue: FLASH_PLAN has stale line numbers

**Symptom:** Line references don't match current file.
**Solution:** Re-read target file before writing plan. Include 3+ surrounding lines of context.

---

## Relationship with `quality-standards`

This skill and `quality-standards` are **complementary at different depths**:

```text
planning-and-deciding         quality-standards
┌─────────────────────┐       ┌────────────────────────┐
│ "What to do?"       │  ──→  │ "How to do it well?"   │
│ Classify + Route    │       │ Sections A-H Detail    │
│ Trade-off Analysis  │       │ Full Technical Spec    │
│ 5-25 min            │       │ 15-25 min              │
└─────────────────────┘       └────────────────────────┘
```

- Use **this skill first** to classify and decide the approach.
- Use **quality-standards** when you need a **full technical specification** (Sections A-H) before implementing the chosen approach.

---

## Portability Notes

| Feature               | With automation support            | Without automation             |
| --------------------- | ---------------------------------- | ------------------------------ |
| Triage classification | Semi-assisted by local tooling     | Manual via Triage Matrix       |
| Workflow tracking     | Tracked by workflow helper         | Manual checklist in chat       |
| Agent profiles        | `.context/agents/*.md`             | Skip or use any docs available |
| Plan storage          | Helper tooling + file              | Just create the file           |
| Phase gates           | Enforced by process checks         | Enforced by user approval      |

> **Bottom line**: MCP tools are a bonus, not a requirement. The core logic (classify → route → act) works everywhere.

## Communication Protocol (Socratic Gate)

### Quando Acionar o Gate

| Padrão do Request | Ação |
|-------------------|------|
| "build", "create", "implement" sem detalhes | 🛑 ASK 3 perguntas estratégicas |
| Feature complexa ou decisão arquitetural | 🛑 Clarificar antes de implementar |
| Vago ou ambíguo | Perguntar Propósito, Usuários, Escopo |
| Usuário dá lista de requisitos | ASK sobre trade-offs ou edge cases |

### Protocolo de Progresso

Durante tarefas longas, comunicar status usando este formato:

| Ícone | Significado |
|-------|-------------|
| 🔍 Analisando... | Lendo código/contexto |
| 📝 Planejando... | Criando FLASH_PLAN |
| ⚡ Executando... | Implementando mudanças |
| ✅ Concluído | Tarefa finalizada |
| ⚠️ Bloqueado | Precisa de input do usuário |
| 🔄 Reclassificando | Complexidade maior do que esperado |

### Categorias de Erro

| Tipo | Mensagem | Próximo Passo |
|------|----------|---------------|
| Contexto insuficiente | "Preciso de mais informações sobre X antes de prosseguir" | Fazer 1-2 perguntas específicas |
| Tarefa muito grande | "Esta tarefa é LARGE (🔴). Vou decompor em sub-tarefas" | Mostrar decomposição |
| Ambiguidade técnica | "Encontrei 2 abordagens viáveis. Análise de trade-offs:" | Trade-off Analysis |
| Bloqueio parcial | "Concluí partes X e Y. Bloqueado em Z por: [razão]" | Solicitar decisão pontual |

### FluttterFlash-Plan Validation Commands

Após plano aprovado, confirmar com scripts de validação:

```powershell
# Lint + análise (sempre executar após implementação)
.\scripts\flutter_lint_runner.ps1 -ProjectPath <projeto>

# Audit GetX (quando mudanças em controllers/views)
.\scripts\getx_audit.ps1 -ProjectPath <projeto>

# Arquitetura (quando mudanças estruturais)
.\scripts\flutter_arch_check.ps1 -ProjectPath <projeto>
```

---

## Related Skills

- [quality-standards](../quality-standards/SKILL.md) — Full technical analysis framework (Sections A-H) for chosen approach.
- [briefing-structural-architecture](../briefing-structural-architecture/SKILL.md) — Generate architecture overview this skill may reference.
- [investigating-bugs](../investigating-bugs/SKILL.md) — Specialized triage for bug investigation.
- [breaking-loops](../breaking-loops/SKILL.md) — Circuit Breaker safety net.

## Changelog

### v1.1.0 (2026-02-16)

- Added mandatory context gate with `context-orchestrator` before planning
- Updated prerequisites to mandatory core context set
- Aligned source priority with core context files used by execution gate

### v1.0.0 (2026-02-15)

- MERGED from 3 skills:
  - `planning-as-architect` v1.0 (complexity triage, FLASH_PLAN, decomposition)
  - `strategic-planning` v1.0 (trade-off analysis, critical questions, scenarios)
  - `quality-standards` patterns integration
- Unified workflow: Triage → Route → (Trade-offs if needed) → Plan/Decompose
- Added extended Decision Flowchart with trade-off branch
- Added explicit relationship diagram with `quality-standards`
- Added Critical Questions (from strategic-planning)
- 100% agnostic design with MCP portability table
