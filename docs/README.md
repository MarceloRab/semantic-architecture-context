# SAC — arquitetura funcional (visão humana)

> Guia curto do **Semantic Architecture Context**. Contrato operacional detalhado: [`SAC_V2.md`](SAC_V2.md). Template de domínios: [`templates/domains.template.md`](../templates/domains.template.md).

## O que é

SAC anexa restrições arquiteturais **no código** (comentários de uma linha) e as expõe a agentes via MCP/CLI, com gate no CI.

Dois públicos:

| Público | Como recebe contexto |
|---------|----------------------|
| **Agente cego** (sem skill/MCP) | Lê o arquivo → vê a linha `// SAC:…` colada na assinatura (overlay passivo) |
| **Agente instrumentado** | Route → Context → Verify preciso; Discover opcional |

O pilar do cego **não** depende do MCP. O MCP só torna a busca cirúrgica e barata em tokens.

## Pipeline

```text
Route      list_sac_domains()              → 1 intent: auto-route; zero: bounded-unmapped; N>1: HALT
Context    get_sac_context(domain_id)       → anchors + todas REGR/DEPRECATED + hop1
Verify     get_sac_constraints(...)        → contrato preciso do símbolo
Discover   discover_sac(domain_id)          → inventário opcional e scoped
Gate       index-build / diff-check / CI   → regressão
```

### Papel de cada tool

| Tool | Camada | Serve para | Não serve para |
|------|--------|------------|----------------|
| `list_sac_domains` | Route | Direção inicial (`domain_id` + intent) | Montar overlay de restrições |
| `get_sac_context` | Context | Montar overlay do domínio em uma varredura | Escolher entre rotas ambíguas |
| `get_sac_constraints` | Verify | Confirmar contrato de um alvo preciso | Inventariar o domínio inteiro |
| `discover_sac` | Discover | Mapa opcional dos símbolos tagueados | Trazer o texto da constraint |

Fluxo mental:

```text
list = direção
context = overlay pragmático do módulo
verify = contrato do símbolo alvo
discover = inventário opcional
```

## Discover slim (economia de tokens)

`discover_sac` devolve **só** o inventário:

- `file`, `line`, `tag_type`, `symbol`
- `verify[]` apenas se for `REGR`

**Não** devolve `constraint` nem `trigger`. Isso vem no **Verify**, quando o agente já escolheu o símbolo.

No chat: ≤1 linha por símbolo; **proibido** colar JSON cru (skill `sac-execution-overlay`).

## Tags no código (pilar)

```text
// SAC:<TAG>: <TRIGGER> - <Symbol>: <constraint>
```

- Comentário interno (`//` / `#`), linha **imediatamente** acima da assinatura
- `ARCH` = invariante; `REGR` termina com `verify: a, b`; `DEPRECATED` termina com `replacement: símbolo|none` e bloqueia uso novo
- Agente cego: basta abrir o arquivo — a restrição já está no contexto local
- Onboard estrutural: o agente propõe linhas canônicas, o humano aprova o texto literal e só após injeção física + lookup `found=true` pode haver alteração de domínio/drawer/índice

## Índice de domínio

`.sac/domains.md` registra módulos onboardados (`domain_id`, `intent`, `files:`, anchors) sob posse exclusiva do projeto (`owned`).

- Schema, manual COR-3 e template managed residem em `templates/domains.template.md`
- Catalog Route **não** lista `files:` nem mantém `tag_count` manual (anti-dump/drift)
- Context / Discover / membership usam `files:` como limite de busca, nunca como fila de leitura; só arquivos relacionados à task são abertos
- Updates de tooling nunca sobrescrevem o `.sac/domains.md` do consumidor

## Skills (quando usar)

| Momento | Skill |
|---------|--------|
| Entender gramática | `sac-context` |
| Qualquer tarefa de código/arquitetura | `sac-execution-overlay` |
| Injetar tags / propor delta contextual | `sac-onboard` (aprovação humana) |
| Mudar o padrão no repositório pai | `sac-evolution` (não espelhada) |

## O que evitar

- Tratar `list_sac_domains()` como inventário de paths
- Usar `discover_sac` sem `domain_id` (chutar módulo)
- Esperar constraint no Discover
- `rg SAC:` no repo inteiro quando o MCP está disponível
- Inventar ou reformular `// SAC:` sem aprovação literal humana, inclusive dentro de `sac-onboard`
- Usar `lookup --pre-onboard` fora da validação bounded de arquivo novo no onboard
- Mexer na gramática/âncora das tags “para economizar tokens” (prejudica o agente cego)

## Referências

- [`SAC_V2.md`](SAC_V2.md) — contrato completo (CLI, MCP, CI, gramática)
- [`.sac/domains.md`](../.sac/domains.md) — manifesto owned do projeto
- [`templates/domains.template.md`](../templates/domains.template.md) — schema + template managed do índice
- [`SAC_BOOTSTRAP.md`](SAC_BOOTSTRAP.md) — ativar MCP no projeto filho
