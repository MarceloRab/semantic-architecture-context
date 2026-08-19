---
name: quality-standards
description: Structured technical analysis framework (Sections A-H) for pre-implementation planning. Covers problem context, diagnostic analysis, approach spectrum, technical specification, impact assessment, risk evaluation, validation strategy, and implementation readiness. Use before implementing any non-trivial solution.
phases: [P, R]
version: 3.1.0
tags: [planning, analysis, pre-execution, quality, agnostic]
difficulty: advanced
estimated_time: 15-25min
---

# 📐 Quality Standards - Planning Framework

Metodologia de análise técnica estruturada para planejamento pré-implementação.

---

## 🎯 Workflow de Análise

**Objetivo:** Produzir análise técnica completa ANTES de implementar qualquer solução.

**Modo de operação:**

- Análise detalhada do problema
- Mapeamento de abordagens possíveis
- Avaliação de riscos e trade-offs
- Plano de execução estruturado

**Importante:** Este é um framework de PLANEJAMENTO. Não execute código nesta fase.

---

## 📋 Template de Análise Técnica

Use esta estrutura para toda análise de problemas técnicos:

---

### SECTION A: Problem Context

**Informações do problema:**

- [Liste todos constraints, requisitos e informações fornecidas]

**Decisões técnicas relevantes:**

- [Se houver contexto prévio da sessão, liste aqui]
- [Se primeira interação, declare: "Nenhum contexto prévio"]

**Suposições necessárias:**

- [Se precisar assumir algo não explicitado, liste com justificativa]

---

### SECTION B: Diagnostic Analysis

**Identificação do problema central:**
[Descreva o problema real, não apenas sintomas]

**Possíveis causas (priorize por probabilidade × impacto × custo):**

1. **[Causa A]**
   - Probabilidade: [Alta/Média/Baixa]
   - Impacto se confirmada: [Alto/Médio/Baixo]
   - Custo de investigação: [Alto/Médio/Baixo]
   - Justificativa: [Por que esta probabilidade/impacto]

2. **[Causa B]**
   [mesma estrutura]

3. **[Causa C]**
   [mesma estrutura]

**Critério de priorização usado:**
[Explique por que ordenou desta forma]

---

### SECTION C: Approach Spectrum

Apresente 3 níveis de solução:

#### Approach 1: Minimal Intervention

**Descrição:** [Solução mais simples possível]
**Escopo:** [Arquivos/componentes afetados]
**Estimativa:** [Linhas de código / tempo]
**Vantagens:**

- [Pro 1]
- [Pro 2]
  **Desvantagens:**
- [Con 1]
- [Con 2]

#### Approach 2: Balanced Solution

**Descrição:** [Solução equilibrada]
[mesma estrutura de A1]

#### Approach 3: Comprehensive Solution

**Descrição:** [Solução completa/robusta]
[mesma estrutura de A1]

**Recomendação:** [A1/A2/A3]
**Justificativa:** [Por que esta escolha dado o contexto]

---

### SECTION D: Technical Specification

Para a abordagem recomendada, detalhe:

**Arquitetura:**

```
Componentes modificados:
- [Componente X]: [tipo de mudança]
- [Componente Y]: [tipo de mudança]

Fluxo de dados:
[Input] → [Processo] → [Output]
```

**Lógica crítica (pseudo-código):**

```
// Principais passos da solução
Step 1: [Ação]
Step 2: [Ação]
Step 3: [Ação]
```

**Casos especiais a tratar:**

1. [Edge case 1]: [Como será tratado]
2. [Edge case 2]: [Como será tratado]
3. [Edge case 3]: [Como será tratado]

---

### SECTION E: Impact Assessment

**Complexity evaluation:**

```
Complexidade do problema: [Simples/Média/Alta]
Complexidade da solução: [Simples/Média/Alta]
Relação: [Proporcional/Desproporcional]

Se desproporcional: [Justifique por que é necessário]
```

**Scope check:**

- [ ] Requer modificar 3+ arquivos? [SIM/NÃO - se SIM, justifique]
- [ ] Envolve mudança arquitetural? [SIM/NÃO - se SIM, justifique]
- [ ] Pode introduzir novos bugs? [SIM/NÃO - se SIM, liste riscos]

**Threshold validation:**

- Bug visual → esperado 1-5 linhas
- Bug de timing → esperado ajuste de parâmetros
- Bug de lógica → esperado correção pontual

[Sua solução está dentro desses thresholds? Comente]

---

### SECTION F: Risk Evaluation

| Risco Identificado | Probabilidade | Impacto | Mitigação Proposta |
| ------------------ | ------------- | ------- | ------------------ |
| [Risco 1]          | [A/M/B]       | [A/M/B] | [Ação preventiva]  |
| [Risco 2]          | [A/M/B]       | [A/M/B] | [Ação preventiva]  |
| [Risco 3]          | [A/M/B]       | [A/M/B] | [Ação preventiva]  |

---

### SECTION G: Validation Strategy

**Testes necessários para validar solução:**

1. [Teste tipo 1]: [O que valida]
2. [Teste tipo 2]: [O que valida]
3. [Teste tipo 3]: [O que valida]

**Critérios de aceitação:**

- ✓ [Critério 1]
- ✓ [Critério 2]
- ✓ [Critério 3]

---

### SECTION H: Implementation Readiness

**Completeness check:**

Análise de contexto: [Mapeou todas informações? SIM/NÃO]
Diagnóstico de causas: [Priorizou 3 causas? SIM/NÃO]
Diversidade de abordagens: [Apresentou 3 níveis? SIM/NÃO]
Especificação técnica: [Detalhou pseudo-código? SIM/NÃO]
Avaliação de riscos: [Identificou 3+ riscos? SIM/NÃO]

**Confidence level:**
[Parágrafo explicando: Esta análise está completa o suficiente para
implementação? O que poderia ser aprimorado? Há gaps de informação?]

**Recommendation:**
[Prosseguir com implementação / Coletar mais informações / Revisar abordagem]

---

## 📚 Design Principles

**P1 - Simplicity First:** Preferir solução simples que resolve vs solução elegante que over-engineers

**P2 - Context Awareness:** Referenciar decisões e constraints já estabelecidos na sessão

**P3 - Trade-off Transparency:** Explicitar vantagens/desvantagens de cada escolha técnica

**P4 - Specificity:** Soluções devem ser contextuais ao problema específico, não genéricas

**P5 - Adaptability:** Se contestado ou surgir nova informação, revisar análise sem defensividade

**P6 - Option Diversity:** Apresentar spectrum de abordagens (minimal -> comprehensive)

---

## 🚨 Quality Gates

**Red flags que indicam análise inadequada:**

- Propor refatoração arquitetural para bug comportamental simples
- Solução requer modificar 4+ arquivos sem justificativa clara
- Complexidade da solução muito superior à do problema
- Menos de 2 abordagens alternativas consideradas
- Edge cases não identificados
- Riscos não mapeados

**Se sua análise contém algum red flag acima, revisite Section C (Approach Spectrum)
buscando abordagens mais simples.**

---

## 🎯 Usage Example

```
User: [Descreve problema técnico]
      /quality-standards

Agent: [Produz análise seguindo Sections A-H]

User: [Revisa SECTION H - Implementation Readiness]
      [Decide se prossegue ou ajusta]
```

---

## 📖 Philosophy

Esta metodologia garante que toda implementação seja precedida de análise estruturada,
reduzindo loops de correção e over-engineering.

Baseado em: Cascade error prevention analysis (Session 2026-01-24)
