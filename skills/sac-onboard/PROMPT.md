# Prompt canônico — SAC Onboard

Este arquivo é o harness completo apontado por `prompt_resumido.md`. Ler também o `SKILL.md` irmão antes de qualquer ação.

## Contrato de boot

```text
Ative sac-onboard.

MODE é obrigatório para Write:
- mode=ASSESS: read-only; é o default quando mode estiver ausente.
- mode=REGISTER: index-only; exige comando literal APROVAR SAC REGISTER <domain_id>.
- mode=TAG_DELTA: ADD/REPLACE/REMOVE de tags; exige comando literal APROVAR SAC TAG_DELTA <domain_id> e tabela literal aprovada.

"Novo domain", "atualizar domain", "use sac-onboard", conhecimento deste harness, "ok" ou "pode aplicar" não autorizam criação/alteração/remoção de tags.
Não criar relatório, auditoria, handoff ou arquivo auxiliar. Handoff somente no chat, salvo path pedido literalmente pelo humano.
```

## Input contratual

```text
mode: ASSESS | REGISTER | TAG_DELTA
requested_domains: <IDs exatos>
intent_by_domain: <uma linha por ID>
candidate_scope: <paths/símbolos explícitos ou um domain_id existente>
approval_command: <literal ou none>
```

Regras:

1. Se `mode` faltar, usar `ASSESS`.
2. Se quantidade/IDs divergirem — por exemplo `02` e `92` — retornar `HALT_AMBIGUOUS_INPUT`.
3. Se `candidate_scope` faltar e não houver exatamente um domínio existente para derivá-lo, retornar `HALT_MISSING_SCOPE`; não fazer scan global.
4. Se dois domínios propostos compartilharem anchor, retornar `HALT_OVERLAPPING_ANCHOR`.
5. Se compartilharem arquivo, exigir aprovação literal do overlap e regra humana de roteamento; não inventar precedência.
6. Processar somente os IDs literais do input/aprovação.

## mode=ASSESS — zero Write

Executar:

1. `list_sac_domains()` uma vez.
2. Para domínio existente único, carregar `get_sac_context(domain_id)`; usar Discover/Verify somente quando necessário.
3. Para domínio novo, inspecionar somente `candidate_scope`. Tags existentes fora do índice podem ser verificadas por CLI `lookup --pre-onboard --path <arquivo>`.
4. Verificar cobertura existente, warnings, anchors e sobreposição.
5. Classificar:
   - `REGISTER_READY`: tags existentes já cobrem o domínio;
   - `TAG_DELTA_REQUIRED`: existe add/replace/remove comprovado;
   - `NO_OP`;
   - `HALT`.
6. Capillarity aplicável → `assess_sac_capillarity({domain_id})` ou CLI `capillarity --domain <id> --json` **uma vez após Discover**; nunca no boot; **nunca** para reverter tags já escritas. Interpretar eixos A/B/C; `quality_status=PASS` ≠ onboard completo se `files_listed > files_tagged`.
7. Gate `files_listed` vs `files_tagged` vs `claims_listed`: mismatch → `TAG_DELTA_REQUIRED`; `REGISTER_READY` proibido até alinhar.
8. Entregar `coverage_strategy: full | representative | phased | none` — humano escolhe em correção/update.
9. Entregar **tabela literal de claims** (executor nunca inventa após aprovação):

```text
context_scenarios: SUMMARY, EXTEND, REGRESSION[, MIGRATION]
coverage_claims:
  <claim_id>|SUMMARY|ARCH|<symbol>|<filepath>
  ...
```

- Claim sem tag física → `TAG_DELTA_REQUIRED` + tabela TAG_DELTA literal integral.
- Metadata-only (tags ok; falta índice/capillarity) → `REGISTER_READY`; write = somente `.sac/domains.md`.
8. Não editar nenhum arquivo.

Saída obrigatória:

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
- proposed_coverage_claims: <tabela literal ou none>
- proposed_write_set: .sac/domains.md only | exact TAG_DELTA table | none
- persistent_artifacts: none
- approval_required: APROVAR SAC REGISTER <id> | APROVAR SAC TAG_DELTA <id> | none
```

**Congelamento:** após aprovação literal, scenarios/claims/operações congelados; divergência na execução → HALT. **Anti-thrashing:** zero Write em ASSESS; proibido write→capillarity→revert.

**PARE.** ASSESS nunca continua para Write no mesmo turno sem o comando literal exigido.

## Correção de domínio existente (update)

Quando `domain_id` já onboardado com drift (`files:` > tags ou claims desalinhados):

1. `mode=ASSESS` obrigatório — não tratar como criação greenfield.
2. Inventário via expand + discover + contagem tags físicas.
3. Propor `coverage_strategy` + TAG_DELTA e/ou ajuste de `files:` — **PAUSE**.
4. Executar **um** ciclo após `APROVAR SAC TAG_DELTA` / `APROVAR SAC REGISTER` literal.

## DoD (binário — colar no chat)

```text
Hot path: list_sac_domains → get_sac_context(missing=[]) → responder/editar. Capillarity proibido.
Onboard: ASSESS diff=∅ → PAUSE → APROVAR → 1 TAG_DELTA → O5 files==tagged==claims. Revert=FAIL.
```

## mode=REGISTER — somente índice

Pré-condição: proposta `REGISTER_READY` + `APROVAR SAC REGISTER <domain_id>` literal. Scenarios/claims aprovados congelados; divergência → HALT.

Write autorizado: somente `.sac/domains.md`.

Bloco contém `intent`, `onboarded`, referências de drawer já existentes/confirmadas, `anchor_symbols`, `files`, `on_edit`, `known_gaps` e — se aprovados na proposta ASSESS — `context_scenarios` + `coverage_claims` literais. Metadata-only: diff persistente = **somente** `.sac/domains.md`. Não escrever `tag_count`: Discover deriva essa métrica.

Proibido:

- criar, alterar, mover ou remover tags;
- editar drawer;
- criar relatório/auditoria/handoff em arquivo;
- versionar symbol index;
- fechar com warning, orphan ou anchor ausente.

DoD literal:

1. Diff persistente = somente `.sac/domains.md`.
2. Catalog encontra o ID/intent sem `files`/`tag_count`.
3. Expand retorna somente os `files` aprovados.
4. Context retorna `missing_anchors=[]` e `warnings=[]`.
5. Discover fica scoped; sua contagem não é copiada ao manifesto.
6. Validate não retorna orphan/`UNMAPPED_ANCHOR_SYMBOL` no recorte.
7. Handoff apenas no chat.

## mode=TAG_DELTA — atualização completa de linhas

Pré-condição: proposta literal + `APROVAR SAC TAG_DELTA <domain_id>`. Tabela/operações congeladas após aprovação; divergência → HALT.

Tabela obrigatória:

| Operação | Arquivo | Assinatura real | Linha atual literal | Linha nova literal | Justificativa |
|---|---|---|---|---|---|
| `ADD` | path | assinatura | `none` | linha completa | evidência |
| `REPLACE` | path | assinatura | linha completa | linha completa | mudança comprovada |
| `REMOVE` | path | assinatura | linha completa | `none` | remoção aprovada |

Sem tabela integralmente aprovada → HALT. O executor não completa campos, escolhe operação nem reformula linha.

### Normalização fechada

```text
// SAC:ARCH: RULE|CONSTRAINT - <Symbol>: <constraint com MUST|NEVER|ONLY>
// SAC:REGR: WARNING|CRITICAL - <Symbol>: <obrigação>; MUST verify: <symbol_or_basename>[, ...]
// SAC:DEPRECATED: WARNING|CRITICAL - <Symbol>: <constraint>; replacement: <symbol|none>
```

Regras de linha:

- Somente `ARCH`, `REGR`, `DEPRECATED` e triggers acima.
- Símbolo = nome exato da assinatura seguinte.
- Bloco contíguo imediatamente acima da assinatura: `ARCH → REGR → DEPRECATED`.
- `REGR verify:` = lista separada por vírgula de tokens sem espaço que casem `[A-Za-z_][A-Za-z0-9_.$-]*`; frase narrativa é proibida.
- `REPLACE` preserva todas as obrigações existentes, salvo remoção semântica literal aprovada.
- `REMOVE` remove somente a linha atual aprovada.
- Nenhuma tag “útil”, densidade adicional ou linha fora da tabela.

Aplicação:

- `ADD`: inserir literalmente.
- `REPLACE`: substituir a linha atual literal pela nova literal.
- `REMOVE`: remover a linha atual literal.

Gate antes de `.sac/domains.md`:

1. `ADD/REPLACE`: lookup `found=true`, texto equivalente e zero warnings.
2. `REPLACE/REMOVE`: linha antiga ausente.
3. Bloco remanescente canônico e espacialmente válido.
4. Validate sem orphan/`UNMAPPED_ANCHOR_SYMBOL` causado pelo delta.
5. Contagem executada por operação = contagem aprovada.

Somente após `tag_delta_gate: PASS`, atualizar `.sac/domains.md` se necessário. Drawer e relatório continuam proibidos sem autorização literal separada.

DoD literal:

1. Diff de fonte contém exatamente ADD/REPLACE/REMOVE aprovados.
2. Nenhuma linha adicional foi criada, reformulada ou movida.
3. Cada operação possui evidência.
4. Context/Discover não retornam warnings canônicos.
5. `.sac/domains.md` só muda quando anchors/files/intent/gaps exigirem.
6. Nenhum relatório, auditoria, drawer ou arquivo auxiliar foi criado.
7. Handoff somente no chat.

## Handoff único

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

## Autoridade

- Runtime/docs: `src/`, `mcp/`, `docs/`.
- Skill canônica: `./SKILL.md`.
