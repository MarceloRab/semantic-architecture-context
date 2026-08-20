---
name: sac-onboard
description: "Avaliar, registrar ou atualizar domínios SAC com três modos fechados: ASSESS read-only, REGISTER index-only e TAG_DELTA para adicionar, substituir ou remover tags após aprovação literal. Use em pedido de novo domínio, atualização de domínio ou manutenção de linhas SAC; novo domínio nunca autoriza escrita ou criação de tags."
---

# SAC Onboard

Operar o índice de domínios e as tags SAC sem heurística. Tags no fonte são SSOT; `.sac/domains.md` é apenas índice de escopo.

## Boot obrigatório

1. Usar o `PROMPT.md` irmão como entrada única **antes de qualquer análise ou ferramenta**; ele aponta diretamente para esta skill.
2. Ler esta skill antes de propor ou executar Write.
3. Fixar um modo: `ASSESS`, `REGISTER` ou `TAG_DELTA`.
4. Se o modo não estiver literal no pedido, usar `ASSESS`.

**Nunca inferir autorização:** “novo domain”, “atualizar domain”, “pode avaliar”, “use sac-onboard”, conhecimento do harness ou aprovação genérica não autorizam Write nem criação de linhas.

**Saída persistente proibida:** não criar relatório, auditoria, handoff ou arquivo auxiliar. Handoff existe somente na resposta do chat, salvo path solicitado explicitamente pelo humano.

## Modos fechados

| Modo | Finalidade | Escrita autorizada |
|---|---|---|
| `ASSESS` | Avaliar domínio novo/existente e produzir proposta | Nenhuma |
| `REGISTER` | Registrar domínio usando tags físicas já válidas | Somente `.sac/domains.md` |
| `TAG_DELTA` | Adicionar, substituir ou remover linhas SAC aprovadas | Somente linhas aprovadas; depois `.sac/domains.md` se necessário |

Transições autorizadas:

```text
ASSESS → REGISTER  somente com: APROVAR SAC REGISTER <domain_id>
ASSESS → TAG_DELTA somente com: APROVAR SAC TAG_DELTA <domain_id>
```

Aprovar um modo não aprova o outro. Para vários domínios, listar todos os IDs no comando literal; qualquer diferença entre IDs propostos e aprovados exige HALT.

## Ferramentas e limites

| Situação | Ferramenta |
|---|---|
| Catalogar domínios | MCP `list_sac_domains()` |
| Domínio existente e único | MCP `get_sac_context(domain_id)`; Discover/Verify só quando necessário |
| Novo domínio com tags existentes fora do índice | CLI `lookup --pre-onboard --path <arquivo>` limitado aos paths e símbolos explícitos |
| Validar domínio registrado | `list-domains --domain`, `context --domain`, `discover --domain` |
| Validar tags alteradas | MCP `get_sac_constraints` se path já mapeado; CLI `lookup --pre-onboard --path` antes do registro |
| Validar estrutura | `sac_scan.py validate`; warnings canônicos bloqueiam fechamento |
| Índice hop1 | `index-build` + `--check`; artefato gerado, nunca report/versionamento |

Proibir scan global, path/domínio inventado e leitura de todos os `files:`. Sem recorte objetivo, retornar `HALT_MISSING_SCOPE`. Engine capillarity lê somente `files:` do domínio; `files_scanned` ≠ arquivos abertos pelo agente.

### Capillarity (on-demand em ASSESS)

- Assessor: MCP `assess_sac_capillarity({domain_id})` ou CLI `capillarity --domain <id> --json`.
- **Nunca** no boot Route→Context; somente dentro de `ASSESS` ou quando o humano pedir auditoria explícita.
- **Eixos:** (A) `status` claims vs tags; (B) `fitness_status` papéis estruturais + seleção Context; (C) `payload_status` + `payload_warn`. `quality_status=PASS` com `SUFFICIENT` + `fitness_status=FIT` + (`payload_status=OK` \| `OVER_BUDGET`). `OVER_BUDGET` é WARN — **MUST NOT** thin `files:`/tags/claims.
- Claims propostos **devem** cobrir papéis `SUMMARY`+`EXTEND`+`REGRESSION` com evidência Discover; `ARCH` para Context **deve** estar em `anchor_symbols` (ou `TAG_DELTA`/`REGISTER` adiciona anchors). Nunca inventar quantidade; nunca PASS sem `FIT`. Discover sem evidência dos três papéis → HALT.
- Proposta literal obrigatória — o executor **nunca** inventa claim, scenario ou tag após aprovação.
- **`quality_status=PASS` ≠ onboard completo:** PASS só valida contrato capillarity (A∧B∧C); não autoriza fechar domínio com `files:` untagged, reduzir escopo silenciosamente ou estratégia “amostra representativa” sem aprovação humana.

## Anti-thrashing (hard)

| Proibido | Ação correta |
|---|---|
| WRITE (tag ou `.sac/domains.md`) durante `ASSESS` | ASSESS read-only; PAUSE + proposta |
| Escrever tags antes de `APROVAR SAC TAG_DELTA` | Tabela TAG_DELTA literal → aprovação → um único apply |
| Revert/undo de tags por resultado capillarity | Capillarity informa ASSESS; **não** autoriza revert. Divergência → `HALT` |
| Escrever N arquivos → capillarity → desfazer para M<N | Um write-set congelado; retrabalho = falha de processo |
| “Mesmo padrão” / amostra representativa sem aprovação | `coverage_strategy` explícito na proposta ASSESS |

## Gate `files:` vs tags físicas

1. Após Discover/Context, calcular: `files_listed` (manifesto), `files_tagged` (paths com ≥1 tag SAC), `claims_listed`.
2. Se `files_listed > files_tagged` **ou** claim sem tag física → **`TAG_DELTA_REQUIRED`** (nunca `REGISTER_READY`).
3. Se `files_listed > files_tagged` e humano escolhe escopo mínimo → `coverage_strategy: representative`; proposta deve **reduzir `files:`** ao subconjunto tagueado (ou listar fase 2 em `known_gaps` **fora** de `files:`).
4. `REGISTER_READY` só quando `files_listed == files_tagged` **e** cada claim tem tag canônica **e** zero warning canônico no recorte.

## Correção de domínio existente (update, não criação)

Quando `domain_id` já existe com drift conhecido (ex.: manifesto 14 `files:`, 4 tags):

1. **Sempre** iniciar `mode=ASSESS` — tratar como correção, não onboard greenfield.
2. Inventariar estado: expand → discover → diff tags vs `files:` vs `coverage_claims`.
3. Classificar + `coverage_strategy: full | representative | phased` (**humano escolhe**).
4. **Zero Write** até `APROVAR SAC TAG_DELTA` e/ou `APROVAR SAC REGISTER` conforme proposta.
5. Um único ciclo TAG_DELTA; proibido write→assess→revert.

### DoD onboard (binário)

| # | PASS |
|---|------|
| O1 | ASSESS: zero diff persistente |
| O3 | PAUSE até `APROVAR SAC TAG_DELTA\|REGISTER` literal |
| O4 | TAG_DELTA: 1 apply; diff ⊆ tabela; **proibido revert** |
| O5 | `files_listed == files_tagged == claims_listed` ou `coverage_strategy` aprovado |

Capillarity **antes** de TAG_DELTA: só em ASSESS (informa proposta). **Depois** de TAG_DELTA: verificação only; FAIL → HALT report; **nunca** desfazer tags.

## ASSESS — sempre read-only

### Entradas mínimas

- `domain_id` ou quantidade/nome dos domínios propostos;
- `intent` de uma linha por domínio;
- paths/símbolos candidatos explícitos **ou** exatamente um domínio existente do qual derivar o recorte.

Conflito como “02” versus “92”, IDs divergentes, múltiplos domínios compatíveis ou scope ausente exige HALT. Não corrigir typo por conta própria.

### Avaliação determinística

1. Chamar `list_sac_domains()`; não expandir domínios não relacionados.
2. Com domínio existente único, carregar Context uma vez. Para novo domínio, usar apenas os paths/símbolos explícitos.
3. Comparar cada anchor candidato com tags físicas existentes.
4. Verificar sobreposição:
   - anchor compartilhado entre domínios propostos → `HALT_OVERLAPPING_ANCHOR`;
   - arquivo compartilhado → exigir aprovação humana literal e regra de roteamento; o agente não inventa precedência;
   - intent que casa mais de um domínio → `HALT_AMBIGUOUS_ROUTE`.
5. Classificar exatamente um resultado:
   - `REGISTER_READY`: cobertura existente, canônica e suficiente;
   - `TAG_DELTA_REQUIRED`: falta, mudança ou remoção comprovada de tag;
   - `NO_OP`: domínio e cobertura já atuais;
   - `HALT`: input, rota, warning ou evidência insuficiente.
6. Quando capillarity aplicável, chamar assessor uma vez; classificar `capillarity_status` (`UNRATED|INVALID_CONTRACT|INSUFFICIENT|SUFFICIENT`) e `capillarity_fitness` (`TOO_THIN|UNFIT|OVER_SELECT|FIT|N/A`); `quality_status=PASS` com `SUFFICIENT` + `fitness_status=FIT` + (`payload_status=OK` \| `OVER_BUDGET`); `payload_warn=OVER_BUDGET` ⇒ Discover→Verify, sem thin.
7. Entregar **tabela literal de claims** (não inventar após aprovação):

```text
context_scenarios: SUMMARY, EXTEND, REGRESSION[, MIGRATION]
coverage_claims:
  <claim_id>|SUMMARY|ARCH|<symbol>|<filepath>
  <claim_id>|EXTEND|REGR|<symbol>|<filepath>
  ...
```

- Claim declarado sem tag física correspondente → `TAG_DELTA_REQUIRED` + tabela TAG_DELTA literal (não completar campos).
- Metadata-only (tags já existem; falta só índice/capillarity) → `REGISTER_READY`; `proposed_write_set: .sac/domains.md only`.
- Não escrever nada.

### Saída ASSESS

```text
SAC ASSESS
- mode: ASSESS
- domain_id: <id>
- intent: <linha>
- result: REGISTER_READY | TAG_DELTA_REQUIRED | NO_OP | HALT
- capillarity_status: UNRATED | INVALID_CONTRACT | INSUFFICIENT | SUFFICIENT | N/A
- capillarity_fitness: TOO_THIN | UNFIT | OVER_SELECT | FIT | N/A
- capillarity_quality: PASS | FAIL | N/A
- existing_coverage: <symbols>
- files_listed: <n>
- files_tagged: <n>
- claims_listed: <n>
- coverage_strategy: full | representative | phased | none
- overlap: none | HALT_<code>
- proposed_context_scenarios: <csv literal ou none>
- proposed_coverage_claims: <tabela literal claim_id|scenario|tag_type|symbol|filepath ou none>
- proposed_write_set: .sac/domains.md only | exact TAG_DELTA table | none
- persistent_artifacts: none
- approval_required: APROVAR SAC REGISTER <id> | APROVAR SAC TAG_DELTA <id> | none
```

**Congelamento (AC4.4):** após `APROVAR SAC REGISTER` ou `APROVAR SAC TAG_DELTA`, scenarios, claims e operações aprovados ficam congelados. Qualquer divergência na execução → HALT; não reformular linha, claim ou operação.

## REGISTER — index-only

Executar somente após `APROVAR SAC REGISTER <domain_id>` corresponder a uma proposta `REGISTER_READY` desta conversa. Scenarios/claims aprovados congelados; divergência → HALT.

### Pré-condições

- Todas as tags/anchors já existem fisicamente e são canônicas.
- Nenhum `invalid_trigger`, `arch_imperative_required`, `regr_verify_required`, `deprecated_replacement_required`, `unsupported_sac_grammar`, orphan ou `UNMAPPED_ANCHOR_SYMBOL` no recorte.
- `REGR verify:` contém somente símbolos ou basenames exatos que casem `[A-Za-z_][A-Za-z0-9_.$-]*`, separados por vírgula; frase narrativa não é alvo.
- Sobreposição já foi resolvida pelo humano.

### Write permitido

Atualizar somente `.sac/domains.md` com:

- `intent`;
- `onboarded`;
- `drawer_file` e `drawer_refs` já existentes/confirmados, sem editar drawer;
- `anchor_symbols`;
- `files`;
- `on_edit`;
- `known_gaps` objetivos;
- `context_scenarios` e `coverage_claims` **somente** se constarem literalmente na proposta ASSESS aprovada (metadata-only).

Não gravar `tag_count`: é métrica derivada por Discover e fica stale quando arquivos se sobrepõem. **Metadata-only fecha via REGISTER → diff persistente = somente `.sac/domains.md`.**

### Proibido em REGISTER

- criar, substituir ou remover `// SAC:`;
- editar drawer;
- criar relatório/auditoria/handoff em arquivo;
- versionar `symbol_index.json`;
- transformar warning preexistente em “não bloqueante”.

### DoD REGISTER

1. Diff persistente contém somente `.sac/domains.md`.
2. Catalog retorna exatamente o novo `domain_id` e `intent` sem `files`/`tag_count`.
3. Expand retorna os `files` aprovados.
4. Context retorna `missing_anchors=[]` e zero warnings.
5. Discover fica scoped aos `files` e sua contagem não é copiada ao manifesto.
6. `validate` não retorna orphan nem `UNMAPPED_ANCHOR_SYMBOL` no recorte.
7. Resposta do chat contém handoff compacto; nenhum relatório foi criado.

Qualquer item sem evidência → não declarar COMPLETE.

## TAG_DELTA — add, replace e remove

Executar somente após `APROVAR SAC TAG_DELTA <domain_id>` e aprovação literal da tabela inteira. Scenarios/claims/operações aprovados ficam congelados; qualquer divergência na execução → HALT.

### Tabela obrigatória

| Operação | Arquivo | Assinatura real | Linha atual literal | Linha nova literal | Justificativa |
|---|---|---|---|---|---|
| `ADD` | path | assinatura | `none` | `// SAC:...` | evidência |
| `REPLACE` | path | assinatura | `// SAC:...` | `// SAC:...` | mudança comprovada |
| `REMOVE` | path | assinatura | `// SAC:...` | `none` | obrigação removida por decisão humana |

Sem linha atual exata em `REPLACE/REMOVE`, sem assinatura comprovada ou com qualquer reformulação após aprovação → HALT.

### Normalização fechada

```text
// SAC:ARCH: on=<ssot|boundary|ordering|state|exclusive|ownership> - <Symbol>: <constraint com MUST|NEVER|ONLY>
// SAC:REGR: on=<snake_case_condition> - <Symbol>: <obrigação>; MUST verify: <symbol_or_basename>[, ...]
// SAC:DEPRECATED: on=<snake_case_condition> - <Symbol>: <constraint>; replacement: <symbol|none>
```

- Usar somente `ARCH`, `REGR`, `DEPRECATED` e condições `on=` acima.
- Usar o nome exato da assinatura seguinte.
- Colocar bloco contíguo imediatamente acima da assinatura, na ordem `ARCH → REGR → DEPRECATED`.
- Em `REGR verify`, aceitar somente tokens sem espaço que casem `[A-Za-z_][A-Za-z0-9_.$-]*`; proibir frases, regras ou sentenças.
- Preservar todas as obrigações da linha atual em `REPLACE`; enfraquecimento exige aprovação humana literal da remoção semântica.
- Nunca nivelar densidade, completar tags “úteis” ou criar linha não listada.

### Aplicação literal

- `ADD`: inserir exatamente a linha aprovada.
- `REPLACE`: substituir exatamente a linha atual pela nova.
- `REMOVE`: remover exatamente a linha aprovada, sem criar substituta.
- Não tocar em símbolo/arquivo ausente da tabela.

### Gate antes do domínio

1. `ADD/REPLACE`: lookup retorna `found=true`, texto literal equivalente e zero warnings.
2. `REPLACE/REMOVE`: linha atual literal não existe mais.
3. `REMOVE`: bloco remanescente continua canônico e espacialmente válido.
4. `validate`: zero orphan/`UNMAPPED_ANCHOR_SYMBOL` causado pelo delta.
5. Contagens físicas executadas = contagens aprovadas por operação.

Somente após `tag_delta_gate: PASS`, atualizar `.sac/domains.md` se anchors/files/intent/gaps mudaram. Drawer continua fora do escopo salvo autorização literal separada.

### DoD TAG_DELTA

1. Diff de fonte contém exatamente as operações aprovadas.
2. Nenhuma linha SAC adicional foi criada, reformulada ou movida.
3. Gate de add/replace/remove passou com evidência por linha.
4. Context/Discover do domínio não retornam warnings canônicos.
5. `.sac/domains.md` mudou somente se o delta exige atualização do índice.
6. Nenhum relatório, auditoria, drawer ou arquivo auxiliar foi criado.
7. Handoff foi emitido somente no chat.
8. Capillarity pós-apply (opcional): FAIL → HALT + report; **proibido** REMOVE/revert por capillarity.

## Handoff único no chat

```text
SAC COMPLETE | NO_OP | HALT
- mode: ASSESS | REGISTER | TAG_DELTA
- domain_id: <id>
- approved_command: <literal | none>
- operations: add=<n> replace=<n> remove=<n>
- persistent_diff: <paths>
- domain_gate: PASS | N/A | HALT
- tag_delta_gate: PASS | N/A | HALT
- warnings: none | <codes>
- validation: <evidência compacta>
- persistent_report: none
```

## Autoridade e propagação

- Runtime/docs: `src/`, `mcp/`, `docs/`.
- Skills: `skills/sac-context`, `skills/sac-onboard`, `skills/sac-execution-overlay`.
