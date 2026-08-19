# Intent Signals - Quando a Master Skill e Invocada

## Triggers Principais

| Padrao | Intencao | Acao Típica |
|--------|----------|-------------|
| "implementar", "criar", "fazer" | Execucao | Avaliar abordagem e executar |
| "resolver", "corrigir", "consertar" | Debug/Fix | Investigar causa raiz |
| "preciso de", "quero", "gostaria de" | Request | Entender problema real |
| "como fazer", "melhor jeito de" | Guidance | Analisar opcoes |
| "avaliar", "decidir", "escolher" | Decision | Apresentar trade-offs |

## Triggers Secundarios

| Padrao | Intencao | Contexto |
|--------|----------|----------|
| "feature", "funcionalidade", "modulo" | Feature creation | Novo codigo |
| "bug", "erro", "problema" | Debugging | Correcao |
| "melhorar", "refatorar", "limpar" | Refactoring | Qualidade |
| "planejar", "analisar", "arquitetura" | Planning | Estrutura |
| "otimizar", "performance", "rápido" | Optimization | Performance |

## Anti-Triggers (NAO usar master-skill)

| Padrao | Motivo | Alternativa |
|--------|--------|-------------|
| Pedido simples e direto | Escopo claro, sem decisao | Skill especifica |
| "apenas", "somente", "só" | Escopo restrito | Execucao direta |
| Comando direto de script | Automacao conhecida | Script/execucao |
| Pergunta especifica de conhecimento | Nenhuma execucao | Resposta direta |
| "listar", "mostrar", "qual" | Consulta | Resposta informativa |

## Pontuacao de Relevancia

Quando multiplos triggers sao encontrados, pontue:

```
Score = (triggers_principais * 3) + (triggers_secundarios * 1) - (anti_triggers * 5)

Score >= 3  → Usar master-skill
Score < 3   → Usar skill especifica ou resposta direta
```

### Exemplo de Calculo

**Input**: "Implementar feature de login no Flutter"

```
triggers_principais = ["implementar", "feature"] = 2 * 3 = 6
triggers_secundarios = ["Flutter"] = 1 * 1 = 1
anti_triggers = [] = 0

Score = 6 + 1 - 0 = 7

Score >= 3 → Usar master-skill
```

**Input**: "Qual a sintaxe do forEach em Dart?"

```
triggers_principais = [] = 0
triggers_secundarios = ["Dart"] = 1 * 1 = 1
anti_triggers = ["Qual", "sintaxe"] = 2 * 5 = 10

Score = 0 + 1 - 10 = -9

Score < 3 → Resposta direta, nao usar master-skill
```

## Matriz de Decisao Rapida

```
┌─────────────────────────────────────────────────────────────┐
│                  PEDIDO DO USUARIO                          │
│                                                             │
│   ┌─────────────┐                                          │
│   │  Simplex    │──→ Escopo claro, sem decisao             │
│   │  (direto)   │    → Skill especifica OU execucao direta │
│   └─────────────┘                                          │
│                                                             │
│   ┌─────────────┐                                          │
│   │  Complex    │──-> Multiplas abordagens possiveis       │
│   │  (decisao)  │     → master-skill: avaliar + escolher   │
│   └─────────────┘                                          │
│                                                             │
│   ┌─────────────┐                                          │
│   │  Vago       │──→ Ambiguo, mal definido                 │
│   │  (clarify)  │    → master-skill: questionar + definir  │
│   └─────────────┘                                          │
│                                                             │
│   ┌─────────────┐                                          │
│   │  Over-      │──→ Usuario pediu X mas precisa de Y      │
│   │  engineered  │    → master-skill: simplificar + propor │
│   └─────────────┘                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Exemplos de Classificacao

### Exemplo 1: Simples (NAO usar master-skill)

**Input**: "Adicionar parametro `timeout` no metodo `fetchData`"

**Analise**:
- Escopo: claro e restrito
- Decisao: nenhuma necessaria
- Complexidade: baixa

**Acao**: Execucao direta ou skill especifica (clean-code-flutter)

---

### Exemplo 2: Complexo (USAR master-skill)

**Input**: "Implementar sistema de notificacoes push"

**Analise**:
- Escopo: amplo, multiplas opcoes
- Decisao: Firebase vs OneSignal vs proprietary?
- Complexidade: alta
- Impacto: arquitetural

**Acao**: master-skill: avaliar abordagens + questionar requisitos

---

### Exemplo 3: Vago (USAR master-skill)

**Input**: "Melhorar a performance do app"

**Analise**:
- Escopo: ambiguo
- Decisao: o que priorizar?
- Complexidade: variavel

**Acao**: master-skill: questionar: "Qual metrica? Onde esta lento?"

---

### Exemplo 4: Over-engineered (USAR master-skill)

**Input**: "Criar sistema distribuindo com microservicos para um app de lista de tarefas"

**Analise**:
- Escopo: excessivo para o problema
- Decisao: precisa mesmo?
- Complexidade: desnecessaria

**Acao**: master-skill: simplificar: "Realmente precisa? MVP primeiro?"

---

## Trigger Phrases por Dominio

### Flutter/Platform

| Trigger | Contexto |
|---------|----------|
| "implementar feature Flutter" | Geracao de codigo |
| "GetX controller/view" | Arquitetura Flutter |
| "state management" | Decisao arquitetural |
| "offline first" | Integracao complexa |

### Context/Governance

| Trigger | Contexto |
|---------|----------|
| "contexto desatualizado" | Manutencao de contexto |
| "validar antes de executar" | Gate GO/NO-GO |
| "bootstrap do contexto" | Inicializacao |

### Planning

| Trigger | Contexto |
|---------|----------|
| "planejar feature" | Analise pre-implementacao |
| "avaliar trade-offs" | Decisao tecnica |
| "analisar opcoes" | Multiple approaches |

### Debugging

| Trigger | Contexto |
|---------|----------|
| "investigar bug" | Root cause analysis |
| "adicionar logs" | Instrumentacao |
| "erro recurrente" | Debug estruturado |