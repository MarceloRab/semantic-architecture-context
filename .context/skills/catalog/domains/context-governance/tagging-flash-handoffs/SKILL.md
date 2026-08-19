---
name: tagging-flash-handoffs
description: Avalia tarefas em `.context/docs/pendentes/current_execution.md` por complexidade e seguranÃƒÂ§a e injeta blocos Flash Handoff nas elegÃƒÂ­veis. Triggers incluem 'marcar tarefas Flash safe', 'anotar handoffs para Flash', 'quais tarefas vÃƒÂ£o para o Flash'. Use apÃƒÂ³s rodar updating-project-status, quando o conjunto de tarefas estÃƒÂ¡ definido e o agente precisa decidir o que delega ao executor.
version: 1.0.0
tags:
  [
    agent-orchestration,
    flash,
    handoff,
    context-governance,
    token-economy,
    flutter,
  ]
difficulty: beginner
estimated_time: 5min
---

# Tagging Flash Handoffs

## When to use this skill

- ApÃƒÂ³s rodar `updating-project-status` e o backlog de tarefas estar definido.
- Quando o usuÃƒÂ¡rio pede: "marcar tarefas Flash safe", "anotar handoffs para Flash", "quais tarefas vÃƒÂ£o para o Flash".
- Antes de iniciar uma sessÃƒÂ£o de execuÃƒÂ§ÃƒÂ£o em que um agente executor (Flash/Gemini) serÃƒÂ¡ usado.
- Quando um conjunto de tarefas pendentes precisa ser triado por complexidade antes da execuÃƒÂ§ÃƒÂ£o.

## Prerequisites

- `.context/docs/pendentes/current_execution.md` atualizado com tarefas contendo os campos `AI Load` e `Complexity` (gerados por `updating-project-status`).
- Contexto arquitetural suficiente para julgar seguranÃƒÂ§a da delegaÃƒÂ§ÃƒÂ£o (interfaces definidas, padrÃƒÂ£o de estado estabelecido).

## Dependencies

**Required:**

- Skill `updating-project-status` executada antes Ã¢â‚¬â€ fornece os metadados `AI Load` e `Complexity` que esta skill consome.

## Workflow

- [ ] **1. Ler `.context/docs/pendentes/current_execution.md`** Ã¢â‚¬â€ coletar todas as tarefas em `Pending Queue` e `Current`.
- [ ] **2. Aplicar filtro de elegibilidade** Ã¢â‚¬â€ para cada tarefa, verificar critÃƒÂ©rios de complexidade e seguranÃƒÂ§a (ver tabela abaixo).
- [ ] **3. Para tarefas elegÃƒÂ­veis** Ã¢â‚¬â€ adicionar `flash-safe: true` no cabeÃƒÂ§alho de metadados da tarefa e injetar o bloco `Flash Handoff` abaixo da Execution Pack.
- [ ] **4. Para sub-passos elegÃƒÂ­veis de tarefas M** Ã¢â‚¬â€ anotar `<!-- flash-safe -->` no sub-passo especÃƒÂ­fico e injetar bloco handoff referenciando apenas aquele sub-passo.
- [ ] **5. Salvar `.context/docs/pendentes/current_execution.md`** com flags e blocos injetados.
- [ ] **6. Confirmar ao usuÃƒÂ¡rio** a lista de tarefas/sub-passos marcados e os que ficaram com o Sonnet.

## Instructions

### CritÃƒÂ©rio de Elegibilidade Flash

A delegaÃƒÂ§ÃƒÂ£o ao Flash ÃƒÂ© decidida por **complexidade + seguranÃƒÂ§a**, nunca por porcentagem.

#### Filtro primÃƒÂ¡rio Ã¢â‚¬â€ Complexidade

| Complexity | AI Load             | DecisÃƒÂ£o                                         |
| ---------- | ------------------- | -------------------------------------------------- |
| `S`        | `low`               | **Tarefa inteira Ã¢â€ â€™ Flash**                  |
| `M`        | `low`               | **Sub-passos isolados Ã¢â€ â€™ Flash parcial**     |
| `S`        | `medium`            | Avaliar checklist de seguranÃƒÂ§a antes de delegar |
| `L`        | qualquer            | **Sempre Sonnet** Ã¢â‚¬â€ sem exceÃƒÂ§ÃƒÂ£o        |
| qualquer   | `high` ou `extreme` | **Sempre Sonnet** Ã¢â‚¬â€ sem exceÃƒÂ§ÃƒÂ£o        |

#### Checklist de SeguranÃƒÂ§a (obrigatÃƒÂ³rio antes de marcar Flash safe)

Uma tarefa sÃƒÂ³ ÃƒÂ© Flash safe se **todas** as condiÃƒÂ§ÃƒÂµes abaixo forem verdadeiras:

- [ ] O contrato de entrada/saÃƒÂ­da estÃƒÂ¡ 100% definido (interface, tipos, assinatura)
- [ ] NÃƒÂ£o envolve decisÃƒÂ£o de arquitetura (estrutura de pastas, escolha de lib, padrÃƒÂ£o de estado)
- [ ] NÃƒÂ£o integra com serviÃƒÂ§o externo (Firebase, Supabase, REST autenticado)
- [ ] NÃƒÂ£o altera estado global da aplicaÃƒÂ§ÃƒÂ£o
- [ ] O output ÃƒÂ© verificÃƒÂ¡vel sem contexto amplo (flutter analyze + critÃƒÂ©rio objetivo)
- [ ] Uma ambiguidade no input nÃƒÂ£o forÃƒÂ§a o Flash a inventar Ã¢â‚¬â€ a especificaÃƒÂ§ÃƒÂ£o ÃƒÂ© completa

Se qualquer condiÃƒÂ§ÃƒÂ£o falhar Ã¢â€ â€™ **Sonnet executa**.

#### Tarefas Flutter tÃƒÂ­picas que passam no filtro

**Flash safe (complexidade + seguranÃƒÂ§a OK):**

- Models com `fromJson` / `toJson` a partir de JSON de exemplo fornecido
- DTOs, `copyWith`, `==`, `hashCode`, `toString`
- Constantes, asset paths, strings de app
- Widgets `StatelessWidget` com spec explÃƒÂ­cita e arquivo de referÃƒÂªncia de estilo
- VariaÃƒÂ§ÃƒÂµes de widget existente (estado vazio, loading, dark mode)
- Unit tests de funÃƒÂ§ÃƒÂµes puras com mocks jÃƒÂ¡ definidos
- Rotas estÃƒÂ¡ticas em GoRouter jÃƒÂ¡ estruturado

**Nunca Flash safe (independente de AI Load):**

- LÃƒÂ³gica de UseCases ou Services
- ConfiguraÃƒÂ§ÃƒÂ£o de gerenciamento de estado (Riverpod, Bloc)
- IntegraÃƒÂ§ÃƒÂ£o com Firebase / Supabase / REST com autenticaÃƒÂ§ÃƒÂ£o
- GoRouter com guards ou parÃƒÂ¢metros dinÃƒÂ¢micos
- Debugging de estado assÃƒÂ­ncrono
- Qualquer tarefa com spec ambÃƒÂ­gua

---

### Flag de tarefa Ã¢â‚¬â€ cabeÃƒÂ§alho de metadados

Para tarefas elegÃƒÂ­veis, adicione `flash-safe: true` inline nos metadados da tarefa, junto aos campos jÃƒÂ¡ existentes de `updating-project-status`. O flag ÃƒÂ© uma decisÃƒÂ£o assinada pelo arquiteto Ã¢â‚¬â€ o executor nÃƒÂ£o precisa re-avaliar.

**Formato para tarefa inteira (Complexity S):**

```markdown
- [ ] Gerar `ProductModel` com fromJson/toJson
      Impact: low | AI Load: low | Complexity: S | Budget: conserve | flash-safe: true
```

**Formato para sub-passo de tarefa M:**

```markdown
- [ ] Criar model `OrderModel` <!-- flash-safe -->
- [ ] Integrar ao repositÃƒÂ³rio <!-- sonnet -->
- [ ] Configurar cache <!-- sonnet -->
```

O flag `flash-safe: true` comunica ao executor:

> "O arquiteto jÃƒÂ¡ avaliou complexidade e seguranÃƒÂ§a. Siga o bloco Flash Handoff abaixo sem anÃƒÂ¡lise adicional."

---

### Template Flash Handoff

Injete este bloco dentro da tarefa elegÃƒÂ­vel em `.context/docs/pendentes/current_execution.md`, apÃƒÂ³s a Execution Pack:

```markdown
### Flash Handoff

agent: flash
flash-safe: true

---

TAREFA:
[objetivo em 1 linha Ã¢â‚¬â€ o que deve ser produzido]

CONTRATO:
Entrada:
[model / interface / typedef que o Flash recebe Ã¢â‚¬â€ cole o cÃƒÂ³digo]
SaÃƒÂ­da:
[arquivo .dart e assinatura esperada Ã¢â‚¬â€ seja exato]
ReferÃƒÂªncia de estilo:
[caminho de arquivo existente que Flash deve replicar o padrÃƒÂ£o]
Imports resolvidos:
[lista fechada de imports Ã¢â‚¬â€ Flash nÃƒÂ£o adiciona nenhum alÃƒÂ©m destes]

RESTRIÃƒâ€¡Ãƒâ€¢ES:

- NÃƒÂ£o introduzir nova dependÃƒÂªncia no pubspec
- NÃƒÂ£o alterar interfaces ou assinaturas existentes
- NÃƒÂ£o criar StatefulWidget (usar ConsumerWidget se precisar de estado)
- Se houver ambiguidade Ã¢â€ â€™ parar e retornar ao Sonnet com a dÃƒÂºvida explÃƒÂ­cita

ACEITO QUANDO:

- flutter analyze sem warnings no arquivo gerado
- [critÃƒÂ©rio especÃƒÂ­fico da tarefa Ã¢â‚¬â€ ex: aceita os mesmos params que WidgetX]
- Nenhum import alÃƒÂ©m dos listados acima
```

---

### Template Retorno Flash Ã¢â€ â€™ Sonnet

O executor deve retornar neste formato para facilitar a revisÃƒÂ£o do Sonnet:

```markdown
# RETORNO Ã¢â€ â€™ SONNET

STATUS: [concluÃƒÂ­do | bloqueado | dÃƒÂºvida]

ENTREGÃƒVEL:
[cÃƒÂ³digo gerado]

PONTOS DE ATENÃƒâ€¡ÃƒÆ’O:
[algo identificado mas fora do escopo de decisÃƒÂ£o do Flash]

DEPENDÃƒÅ NCIAS DETECTADAS:
[import ou padrÃƒÂ£o que pode estar faltando Ã¢â‚¬â€ nÃƒÂ£o adicionado]
```

---

### RevisÃƒÂ£o pelo Sonnet (foco mÃƒÂ­nimo)

Ao receber o retorno, o Sonnet verifica **apenas**:

1. Assinaturas de mÃƒÂ©todos e tipos batem com o contrato
2. Nenhum import nÃƒÂ£o autorizado foi introduzido
3. PadrÃƒÂ£o de estado nÃƒÂ£o foi violado
4. RestriÃƒÂ§ÃƒÂµes negativas foram cumpridas

NÃƒÂ£o ÃƒÂ© necessÃƒÂ¡rio reler linha a linha Ã¢â‚¬â€ os critÃƒÂ©rios acima cobrem 95% dos riscos.

---

### Para sub-passos de tarefas M

Quando uma tarefa `Complexity: M` tem sub-passos isolados delegÃƒÂ¡veis, anote apenas o sub-passo:

```markdown
- [ ] Gerar model `ProductModel` com fromJson/toJson <!-- flash-safe --> > Flash Handoff: ver bloco abaixo
- [ ] Conectar model ao repositÃƒÂ³rio <!-- sonnet -->
- [ ] Implementar lÃƒÂ³gica de cache <!-- sonnet -->
```

E inclua o bloco Flash Handoff referenciando apenas aquele sub-passo.

## Success Criteria

**Observable Outcomes:**

- `.context/docs/pendentes/current_execution.md` contÃƒÂ©m blocos `Flash Handoff` apenas em tarefas que passaram no filtro de complexidade + seguranÃƒÂ§a.
- Tarefas marcadas `flash-safe: true` tÃƒÂªm contrato completo (entrada, saÃƒÂ­da, referÃƒÂªncia, imports, critÃƒÂ©rio de aceitaÃƒÂ§ÃƒÂ£o).
- O usuÃƒÂ¡rio pode copiar o bloco e colar diretamente no Flash sem precisar adicionar contexto extra.
- Tarefas com decisÃƒÂ£o de arquitetura embutida **nÃƒÂ£o** foram marcadas Flash safe.

**ValidaÃƒÂ§ÃƒÂ£o manual:**

- Para cada tarefa marcada: confirmar que o checklist de seguranÃƒÂ§a foi cumprido.
- O bloco `ACEITO QUANDO` deve conter pelo menos um critÃƒÂ©rio verificÃƒÂ¡vel por comando (`flutter analyze`, `flutter test`).

## Error Handling

### Tarefa marcada Flash safe com spec incompleta

**Sintoma:** Flash retorna com `STATUS: dÃƒÂºvida` ou inventa padrÃƒÂ£o nÃƒÂ£o especificado.
**Causa:** Contrato de entrada/saÃƒÂ­da nÃƒÂ£o estava totalmente definido no momento do handoff.
**SoluÃƒÂ§ÃƒÂ£o:** Sonnet completa a spec (interface, tipos, arquivo de referÃƒÂªncia) e remonta o bloco Flash Handoff antes de reenviar.

### Flash altera interface existente

**Sintoma:** Retorno do Flash modifica assinatura de classe/mÃƒÂ©todo jÃƒÂ¡ definido.
**Causa:** RestriÃƒÂ§ÃƒÂ£o negativa ausente ou ambÃƒÂ­gua no bloco handoff.
**SoluÃƒÂ§ÃƒÂ£o:** Descartar o output, adicionar a restriÃƒÂ§ÃƒÂ£o explÃƒÂ­cita (`NÃƒÂ£o alterar [NomeClasse].[mÃƒÂ©todo]`) e reenviar.

### Tarefa M marcada inteiramente como Flash safe

**Sintoma:** Bloco Flash Handoff cobre a tarefa inteira, incluindo passos com decisÃƒÂ£o.
**Causa:** Complexidade `M` foi tratada como `S` sem verificar sub-passos individualmente.
**SoluÃƒÂ§ÃƒÂ£o:** Dividir a tarefa Ã¢â‚¬â€ anotar apenas os sub-passos que passam no checklist de seguranÃƒÂ§a.

## Related Skills

- [updating-project-status](../updating-project-status/SKILL.md) Ã¢â‚¬â€ prerequisito: gera os metadados `AI Load` e `Complexity` consumidos por esta skill.
- [context-orchestrator](../context-orchestrator/SKILL.md) Ã¢â‚¬â€ deve ser rodado antes de qualquer sessÃƒÂ£o de execuÃƒÂ§ÃƒÂ£o.

## Changelog

### v1.1.0 (2026-03-01)

- Adicionado flag `flash-safe: true` no cabeÃƒÂ§alho de metadados da tarefa Ã¢â‚¬â€ decisÃƒÂ£o assinada pelo arquiteto, executor nÃƒÂ£o re-avalia.
- Formato inline para tarefa inteira e para sub-passo de tarefa M.
- Workflow atualizado para refletir injeÃƒÂ§ÃƒÂ£o do flag antes do bloco handoff.

### v1.0.0 (2026-03-01)

- Initial release Ã¢â‚¬â€ integraÃƒÂ§ÃƒÂ£o com `updating-project-status`, filtro por complexidade + seguranÃƒÂ§a (nÃƒÂ£o por porcentagem), template Flash Handoff compacto para Flutter.
