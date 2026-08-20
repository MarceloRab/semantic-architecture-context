---
name: sac-execution-overlay
description: "Gate obrigatório de execução cirúrgica, verificação de rotas Route e constraints antes de tocar no código. Orquestra a resolução de domínio único via MCP (list_sac_domains / get_sac_context), overlay de restrições e verificação pontual (Verify) antes de qualquer leitura ou edição."
---

# SAC Execution Overlay

Skill operacional para carregar restrições SAC como overlay **antes** de editar código tagueado. Não substitui `sac-context` (gramática); não faz onboard (`sac-onboard`).

**Papéis (fechados):**

| Quem | Papel |
|------|--------|
| **MCP** | Cérebro de busca (`list_sac_domains`, `get_sac_context`, Discover, Verify); tags são SSOT |
| **Esta skill** | Orquestra L0–L4 e traduz códigos MCP → ação humana / overlay |
| **CLI** | Fallback anunciado se MCP down — **mesmo JSON** |

**Pipeline:** L0 Route → Context fast path → Verify preciso → Capillarity (on-demand) → L4 Gate.

**Capillarity = cold path.** Proibido em READ/EXECUTE boot. Permitido: auditoria explícita; encaminhar `sac-onboard mode=ASSESS`. **Nunca** reverter tags por capillarity; **nunca** entre ADDs da mesma tabela TAG_DELTA.

## Contrato de fidelidade MCP (COR-GATE)

**Resposta ao user sobre SAC = só o que o MCP devolveu neste turno** (PAUSE ou overlay). Nenhuma ferramenta supera o MCP para fidelidade ao contrato.

| Estado MCP | Agente **deve** | **Proibido** |
|------------|-----------------|--------------|
| `list_sac_domains` OK | 1 intent → auto-rota; zero → bounded-unmapped; múltiplos → PAUSE | Chutar, expandir múltiplos, listar files |
| `get_sac_context` OK | Montar overlay de anchors + todas `REGR`/`DEPRECATED` + hop1 de **um** domínio | Reconsultar anchors; carregar outros domínios; abrir todos os `files:` |
| `discover_sac` OK | ≤1 linha/símbolo (`file:line TYPE symbol`); **sem** constraint; depois Verify | Dump JSON; esperar constraint no Discover; rg global |
| `filepath_required` | ≤2 linhas: `pause_hint`; oferecer catalog | Chutar path; retry; dump JSON; constraints |
| `filepath_not_in_sac_domains` / `filepath_not_in_domain` | Pause + `domains_hint` | Lookup “mesmo assim” |
| VERIFY `found: true` | Overlay ≤15 linhas/símbolo | Colar JSON cru |
| VERIFY `found: false` (scoped) | no-op tags | Inventar `SAC:` |
| MCP down / session boot fail | CLI anunciado (`lookup --path` / `list-domains` / `discover`) | Fingir MCP OK; rg global; continuar sem anunciar |
| MCP OK + `_perf` | 1 linha: `sac_perf: <tool> <elapsed_ms>ms` (agregar se N calls) | Dump `_perf` ou JSON cru |

**Hierarquia de ferramentas:**

```text
1º MCP  list_sac_domains / discover_sac / get_sac_constraints
2º CLI  list-domains / discover --domain / lookup --path   (só se MCP down; anunciar)
3º rg   só em files: do domínio         (fallback Discover — nunca Verify)
Nunca: lookup sem path · `lookup --pre-onboard` em READ/EXECUTE · rg global · path inventado · hop1 full-root sem escape
```

**pause_hint canônico:**

```text
Qual domain_id expandir, ou informe filepath direto?
```

**Auto-route (COR-GATE-9/10):** após catalog, exatamente 1 intent compatível autoriza `get_sac_context(domain_id)`; zero → bounded-unmapped; múltiplos → PAUSE. Proibido expandir múltiplos ou listar `files:` no chat.

Schema: `filepath` **optional** no Zod; omitido → PAUSE JSON ≡ CLI (**zero** `matches`/`hop1`/`found: true`).

## Quando ativar

Ative quando **qualquer** condição for verdadeira:

1. **EXECUTE:** qualquer plano, review, refactor ou implementação de código/arquitetura.
2. **READ:** qualquer pergunta sobre código ou arquitetura no projeto.
3. Pré-condição: `.sac/domains.md` (ou `SAC_domains.md` legado) existe.

**Session boot (obrigatório na 1ª intenção de código/arquitetura):**

| Estado | Ação |
|--------|------|
| MCP `list_sac_domains` OK | Continuar L0; registrar `_perf.elapsed_ms` (1 linha) |
| MCP error / tool ausente | Anunciar CLI fallback; **não** rg global |
| MCP + CLI down + alvo tagueado | **NO-GO** |

**Não ative** para: arquivos sem SAC e sem intent de domínio; onboard (`sac-onboard`); arquitetura de alto nível genérica (`briefing-architecture-drawers`).

## Pré-condições

- **MCP (obrigatório para fidelidade):** Node `mcp/server.mjs` com tools `list_sac_domains` + `get_sac_context` + `get_sac_constraints` + `discover_sac` (`filepath` optional no schema).
- Smoke verde: `node mcp/smoke.mjs` (inclui discover + hop1 scoped + paridade negativa MCP≡CLI).
- Após mudar MCP: **recarregar** servidor na IDE.
- **CLI (fallback):** `python src/sac_scan.py lookup|list-domains|discover`.

**Anti-inventário:**

- Alvo **sem** `SAC:` → manter gate ativo, registrar gap/unmapped e não inventar tags.
- Alvo tagueado + MCP **e** CLI down → **NO-GO**.
- Host sem smoke → BLOQUEIO + CLI anunciado; nunca inventar tags.

## Workflow de overlay

### 0. Route (L0) — preferir MCP

1. Antes de qualquer Read de código → `list_sac_domains()` uma vez por sessão.
2. Exatamente 1 intent compatível → auto-selecionar e chamar `get_sac_context(domain_id)` **uma vez**; nunca carregar todos os domínios.
3. Zero intents compatíveis → declarar `sac_scope: unmapped` e usar busca local bounded; se não houver diretório objetivo, HALT.
4. Mais de 1 intent compatível → HALT por ambiguidade.
5. Cachear catalog + overlay durante a sessão; path conhecido pode seguir para Verify preciso.
6. Proibido: chutar domínio/path, expandir múltiplos, dump de files, scan global.

### 1. Context fast path

`get_sac_context(domain_id)` retorna intent, constraints dos anchors, todas `REGR` e `DEPRECATED`, hop1, missing anchors, gaps e warnings. A forma canônica usa `on=<condition>`: ARCH aceita somente `ssot|boundary|ordering|state|exclusive|ownership`; REGR/DEPRECATED aceitam `[a-z][a-z0-9_]{2,47}`. Tags com o vocabulário antigo continuam visíveis com condição vazia e `legacy_trigger`. `invalid_trigger`, `arch_imperative_required`, `regr_verify_required` ou `deprecated_replacement_required` tornam a constraint visível porém não canônica e bloqueiam suficiência. `REGR verify` com item fora de `[A-Za-z_][A-Za-z0-9_.$-]*` (por exemplo frase narrativa) também bloqueia. Se retornar `context_payload_too_large`, nenhuma constraint foi entregue: registrar `source_payload_bytes`, **MUST** `discover_sac(domain_id)` + `get_sac_constraints(symbol, filepath∈files:)`, **MUST NOT** remover `files:`/tags/claims para caber na métrica. O limite padrão é **12288 bytes** (`SAC_CONTEXT_MAX_BYTES`); nunca truncar silenciosamente. Domínio completo é SSOT; Context compacto é otimização.

### 2. Recortar a task antes de abrir código

`domain.files` é **limite de busca**, nunca fila de leitura. O Context é overlay semântico; não autoriza abrir cada arquivo listado.

1. Começar com zero arquivos de código abertos após o overlay.
2. Abrir o alvo explícito da task ou, se não houver, um único arquivo primário encontrado por `fd`/`rg` scoped.
3. Cada arquivo adicional exige uma relação objetiva: alvo explícito, `verify`/hop1, import/chamada direta do primário ou evidência de índice stale.
4. Sem relação objetiva ou com dúvida sobre o domínio/alvo → HALT; não compensar lendo o domínio inteiro.
5. Registrar no report cada arquivo aberto e o motivo.

Arquivos do diff devem pertencer a `files:` do domínio resolvido.

### 3. Discover (L1) — somente se o overlay não localizar o alvo

Preferir MCP **`discover_sac({domain_id})`** (tags só em `files:`).  
Fallback anunciado: `rg "SAC:(ARCH|REGR|DEPRECATED):"` **somente** no recorte objetivo dentro de `files:`.
`rg` scoped é permitido e preferido; bloqueio de busca ampla não autoriza trocar por `Get-ChildItem -Recurse`, `Select-String` ou script PowerShell equivalente. Discover é opcional após Context; Verify pode seguir direto quando o alvo já é conhecido.

### 4. Verify (L2) — MCP

Para cada símbolo tagueado **com** `filepath` ∈ `files:`:

```json
{
  "name": "get_sac_constraints",
  "arguments": {
    "symbol_name": "<symbol>",
    "filepath": "<path relativo ∈ files:>",
    "domain_id": "<domain_id>"
  }
}
```

`domain_id` opcional mas **recomendado** após Route (membership + hop1 scoped).

SE retorno `filepath_required` | `filepath_not_in_sac_domains` | `filepath_not_in_domain` → aplicar COR-GATE (tabela acima).

**CLI fallback (anunciar):**

```bash
python src/sac_scan.py lookup <symbol> --root . --path <file> --domain <id> --json
```

**Token economy:** cache `(symbol, filepath)`; sem lookup de símbolo não tagueado; sem JSON cru no chat.

### 5. Hop1 (L3) — só REGR

1. Usar `hop1` do Verify (índice **scoped** ou `hop1_domain_scan_no_index` anunciado).
2. Lookup extra só com `filepath` do match hop1 (+ mesmo `domain_id`).
3. Cap 10; sem recursão.
4. Índice stale → sugerir `index-build` / `--check` (não rebuild a cada lookup).
5. **Proibido** depender de `hop1_full_scan_no_index` no EXECUTE quando há domínio (escape só debug).
### 6. Overlay compacto

```text
SAC OVERLAY (mandatório)
=======================
<file>:<line> [<tag_type>/<trigger>] <symbol>
  constraint: <constraint>
  verify: [<target1>, ...]  (somente REGR)
  replacement: <symbol|none>  (somente DEPRECATED)
  hop1:
    - <target1> -> <file>:<line> [...]
    - <target2> -> untagged
=======================
```

Só após VERIFY_OK. ≤15 linhas/símbolo.

### 7. Executar respeitando overlay (EXECUTE) ou responder (READ)

- **EXECUTE — ARCH:** restrição inegociável.
- **EXECUTE — REGR:** validar `verify:` antes de alterar.
- **DEPRECATED:** uso novo ou nova dependência → HALT. Leitura, diagnóstico, remoção ou migração explicitamente pedidos podem prosseguir usando `replacement`. `deprecated_replacement_required` → risco bloqueante/HALT.
- **READ (Q&A):** resumo ≤15 linhas: intent do domínio + constraints relevantes à task; **sem** colar JSON; incluir `sac_perf` agregado se `_perf` presente.
- Toda resposta final registra `sac_scope: domain=<id>|unmapped`, `context_domains_loaded: 1|0`, limite real da busca, arquivos abertos com motivo, `deprecated_risk: none|present|blocking` e `domain_index_status: current|suspected_stale|not_applicable`.
- Auditoria/report: `files_scanned` ≠ arquivos abertos; tag fora de anchors = `non_anchor_tag`, não orphan; orphan só via validate AST; métricas rotuladas `MCP-measured|CLI-validated|inferred`.
- Tag parseada não basta: warnings `invalid_trigger`, `arch_imperative_required`, `regr_verify_required` e `deprecated_replacement_required` → `INSUFFICIENT`/HALT em risco crítico, nunca cobertura aprovada.
- Evidência de staleness: missing file/anchor, alvo necessário fora de `files:`, ou resultado relevante encontrado apenas no fallback bounded. Não atualizar automaticamente; encaminhar `sac-onboard mode=ASSESS`. Somente REGISTER/TAG_DELTA literalmente aprovados escrevem. EXECUTE material fora do domínio → HALT.
- **Capillarity on-demand:** encaminhar `sac-onboard mode=ASSESS` se stale; **não** reverter tags; PASS capillarity ≠ domínio completo se `files:` > tagged.
- Risco de regressão → pause + decisão humana.

### DoD sessão (hot path)

D1 MCP Ready → D2 catalog → D3 `get_sac_context` `missing=[]` **ou** overflow + Discover→Verify (sem thin) → D4 responder/editar. Sem capillarity; sem auditoria de agente em turno 2.

## Exemplo

Diff: `lib/dose_calculator.dart` com REGR em `calculateDose`.

1. Route/domínio ok → Discover no arquivo.
2. `get_sac_constraints(symbol_name="calculateDose", filepath="lib/dose_calculator.dart")`.
3. Overlay ≤15 linhas a partir do JSON (não colar JSON).
4. Editar só se consistente com hop1/`verify:`.

## Fallbacks

| Situação | Ação |
|---|---|
| MCP down | CLI anunciado (`list-domains` / `context --domain` / `discover --domain` / `lookup --path`) |
| Sem domínio compatível | `sac_scope: unmapped`; `fd` bounded para paths, `rg` scoped para texto, `bat` para intervalos; sem diretório objetivo → HALT |
| CLI down, arquivo tem `SAC:` | `rg` **só** no arquivo-alvo (ler tags) |
| MCP **e** CLI down em path tagueado | **NO-GO** |
| Path sem `SAC:` | no-op |
| `found=false` scoped | continuar sem escrever `SAC:`; encaminhar `sac-onboard mode=ASSESS` se o índice estiver stale |
| Tentativa de `lookup --pre-onboard` em READ/EXECUTE | HALT; esse modo é exclusivo dos modos fechados do `sac-onboard` com scope explícito |
| Warning canônico (`invalid_trigger`, `arch_imperative_required`, `regr_verify_required`, `deprecated_replacement_required`) | `INSUFFICIENT`/HALT em risco crítico + `sac-context`; não inventar tag |

## Campos MCP (VERIFY_OK)

`found`, `matches[].file|line|tag_type|trigger|constraint|verify|replacement|hop1[]`, `warnings`.

## Integração

- `sac-context` — gramática.
- `sac-onboard` — ASSESS read-only; REGISTER index-only; TAG_DELTA é o único WRITE de tags.
- `context-orchestrator` — pode exigir overlay antes de editar código tagueado.

## Invariantes

1. MCP = fidelidade; skill = orquestração.
2. Nunca ignorar overlay sem motivo registrado.
3. Nunca além de 1-hop.
4. Nunca full-scan / path chutado / dump JSON; busca blocked não pode reaparecer por PowerShell equivalente.
5. Cache por sessão `(symbol, filepath)`.
6. Nunca inventar `SAC:`.
7. WRITE de tags só via `sac-onboard TAG_DELTA` literal; REGISTER só indexa; `--pre-onboard` é proibido nesta skill.

## Modos L0–L4

| Modo | Ação | MCP |
|------|------|-----|
| L0 Route | `list_sac_domains` (preferir); COR-3; pause_hint | `list_sac_domains` |
| L1 Discover | `discover_sac(domain_id)` (preferir); rg só em `files:` como fallback | Sim |
| L2 Verify | `get_sac_constraints(symbol, filepath?, domain_id?)` | Sim |
| L3 Hop1 | `verify:` / índice **scoped** ao domínio | Se necessário |
| L4 Gate | `index-build` + `diff-check` / `validate` | Não |

---

## Prompt resumido (copiar/colar)

Use no chat para ativar o contrato sem reler a skill inteira:

```text
Ative sac-execution-overlay. Contrato COR-GATE (tags = SSOT; MCP = cérebro de busca):

1. Toda intenção de código/arquitetura → list_sac_domains() antes de Read.
2. Exatamente 1 intent compatível → auto-rota + get_sac_context(domain_id).
3. Zero intents → `sac_scope: unmapped` + fd/rg/bat bounded; sem diretório objetivo → HALT.
4. Mais de 1 intent → HALT; nunca chutar ou expandir múltiplos.
5. Cachear catalog + contexto; `context_payload_too_large` / `payload_warn=OVER_BUDGET` → MUST Discover→Verify; MUST NOT thin files:/tags/claims; sem truncar.
6. Discover só para detalhe; rg scoped permitido, rg global proibido.
7. Verify preciso quando símbolo/path forem conhecidos; `filepath_*` → PARAR sem chute/dump.
8. Busca ampla bloqueada não pode ser refeita por PowerShell equivalente.
9. MCP down → CLI+jq anunciado; nunca fingir MCP OK.
10. READ/EXECUTE respeitam ARCH/REGR/DEPRECATED e hop1 scoped; uso novo de DEPRECATED → HALT.
11. `domain.files` é limite de busca, não fila; abrir só arquivos com relação objetiva à task.
12. Reportar `sac_scope`, `context_domains_loaded` (`1|0`), `search_scope`, `files_scanned` separado de arquivos abertos+motivo, `deprecated_risk`, `domain_index_status`, evidência de staleness e `sac_perf`; non-anchor ≠ orphan e inferência ≠ evidência.
13. Índice suspeito → encaminhar `sac-onboard mode=ASSESS`; REGISTER/TAG_DELTA exigem aprovação literal; EXECUTE material fora do domínio → HALT.
14. Capillarity **nunca** no boot; assessor só em pedido explícito, `suspected_stale` ou `context_payload_too_large`.
15. `domain.files` ≠ fila de leitura; proibido abrir todos os arquivos listados.

Pipeline: boot → Route → Context ou bounded-unmapped → Verify/Discover → Capillarity(on-demand) → Gate.
```

### Handoff curto (após overlay montado)

```text
SAC OVERLAY READY | SAC QUERY READY
- mode: EXECUTE | READ
- sac_scope: domain=<domain_id> | unmapped
- context_domains_loaded: 1 | 0
- search_scope: files=<n> | dirs=<csv>
- opened_files: <path=objective reason; ...>
- deprecated_risk: none | present | blocking
- domain_index_status: current | suspected_stale | not_applicable
- scope_evidence: <none | missing anchor/file | outside-domain target | bounded fallback result>
- symbols verified: <csv>
- sac_perf: <elapsed_ms>ms (aggregate)
- pause/codes: <none | filepath_*>
- mcp: list_sac_domains / get_sac_context / get_sac_constraints
- next: edit under ARCH/REGR/DEPRECATED gate | answer from task-scoped constraints
```

## Onde esta skill vive

`skills/sac-execution-overlay/SKILL.md` no repositório do SAC ou `.context/skills/` em projetos consumidores.
