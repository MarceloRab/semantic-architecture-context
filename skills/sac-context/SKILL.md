---
name: sac-context
description: "Gramática, regras e sintaxe de escrita e atualização de tags SAC (ARCH, REGR, DEPRECATED). Define o formato canônico de comentários in-code, triggers válidos, regras espaciais anti-chunking e contratos de integridade semântica."
---

# SAC Context

Camada semântica (In-Code RAG) para reduzir regressões e alinhar agentes. Injeta restrições no espaço de atenção local do LLM. Não é documentação humana; é contrato verificável + indexação estática.

**SSOT operacional do pipeline:** `docs/SAC_V2.md` (§ Pipeline + § Como o agente usa).
**Edição em código tagueado:** skill `sac-execution-overlay`.
**Avaliar/registrar domínio ou ADD/REPLACE/REMOVE de tags:** skill `sac-onboard` (`ASSESS|REGISTER|TAG_DELTA`).
**Evoluir o padrão:** consulte `GOVERNANCE.md` e `docs/adr/`.

## Pipeline (L0–L4) — não inventar atalho

| Modo | Quem | Ação | MCP? |
|------|------|------|------|
| L0 Route | skill / `list_sac_domains` | Catalog mínimo; 1 intent → auto-rota; zero → bounded-unmapped; múltiplos → HALT | `list_sac_domains` |
| Fast Context | MCP/CLI | Anchors + todas `REGR`/`DEPRECATED` de um domínio + hop1 | `get_sac_context` |
| L1 Discover | MCP/CLI | Inventário slim para inspeção detalhada | `discover_sac` |
| L2 Verify | MCP/CLI | Constraint precisa por símbolo/path | `get_sac_constraints` |
| L3 Hop1 | engine | índice **scoped** aos `files:` do domínio; senão scan só desses files | Se preciso |
| L4 Gate | CI | `index-build` + `diff-check` / `validate` | Não |
| Capillarity | MCP/CLI **on-demand** | (A) claims vs tags, (B) context fitness, (C) payload em `files:` | `assess_sac_capillarity` |

**Capillarity não entra no boot nem no L0.** Chamar somente em pedido explícito de auditoria/onboard, `domain_index_status=suspected_stale` ou `context_payload_too_large` — nunca em Route→Context normal.

### Modos de ativação (READ + EXECUTE)

| Modo | Quando | Pipeline |
|------|--------|----------|
| **READ** | Qualquer pergunta de código/arquitetura em projeto SAC-enabled | L0 → Context antes de Read; Verify quando houver alvo |
| **EXECUTE** | Planejamento/review/edição de código em projeto SAC-enabled | L0 → Context antes de Read; Verify + L4 no alvo |

**Proibido** em ambos: `rg` global; `Read` amplo do repo; chutar `domain_id`/filepath antes do Route.

### Session boot (1ª intenção de código/arquitetura na sessão)

1. Antes de ler código, chamar `list_sac_domains()` uma vez e cachear o catalog.
2. Exatamente 1 intent compatível → auto-selecionar + `get_sac_context(domain_id)`; `context_payload_too_large` entrega zero constraints e exige Discover/Verify focado.
3. Zero intents → bounded-unmapped; múltiplos → PAUSE / NO-GO; nunca chutar.
4. **MCP error/unavailable** → anunciar CLI (`list-domains` / `context` / `lookup --path`).
5. MCP **e** CLI down em alvo tagueado → **NO-GO**.
6. Reportar `_perf.elapsed_ms` + `payload_bytes` em uma linha; não dump JSON.

### DoD operacional (hot path)

| PASS | FAIL |
|------|------|
| D2 `get_sac_context` → `missing=[]` **ou** overflow explícito + Discover→Verify | Context thin / thin domain → rg/read amplo |
| D4 resposta ≤15 linhas com constraints do slice | Dump JSON; capillarity no READ/EXECUTE |

Capillarity = **cold path** (auditoria, onboard ASSESS). Não substitui entrega de Context.

Pedido vago “usar MCP SAC” → **PAUSE** (máquina + humano):

```text
Qual o filepath, ou gostaria de chamar list_sac_domains?
```

`get_sac_constraints` sem path → JSON `filepath_required` (≡ CLI), **zero matches** — não erro Zod opaco. Agente **não** chuta path.

**Pilar (agente cego a skill/MCP):** tags `SAC:` no fonte continuam overlay passivo na leitura do código. MCP/skills só tornam Route/Discover/Verify cirúrgicos.

## O Padrão (Template Obrigatório)

    <comment-marker> SAC:<TAG>: on=<condition> - <Symbol>: <Imperative Constraint>

- `<comment-marker>`: Comentário INTERNO (`//`, `#`). NUNCA `///` / `/**`.
- `<TAG>`: `ARCH`, `REGR` ou `DEPRECATED`.
- `on=<condition>`: para ARCH, exatamente `ssot|boundary|ordering|state|exclusive|ownership`; para REGR/DEPRECATED, `[a-z][a-z0-9_]{2,47}`.
- `<Symbol>`: Nome exato do símbolo. Nunca número de linha.
- `<Imperative Constraint>`: Texto plano em inglês. **Proibido** JSON, crases markdown, `[]`/`{}` de array/objeto.

### 1. SAC:ARCH

- **Condições:** `on=ssot`, `on=boundary`, `on=ordering`, `on=state`, `on=exclusive`, `on=ownership`.
- **Conteúdo:** `MUST` / `NEVER` / `ONLY`.
- **Exemplo:**

  // SAC:ARCH: on=ownership - ViewTransform: MUST own all viewport coordinate transforms. DO NOT delegate.
  class ViewTransform { ... }

### 2. SAC:REGR

- **Condição:** `on=<condition>` em snake_case, conforme `[a-z][a-z0-9_]{2,47}`.
- **Formato:** `- <Symbol>: <condicional>. MUST verify: <alvo1>, <alvo2>, ...`
- **Contrato:** lista `verify:` terminal até EOL com tokens separados por vírgula que casem `[A-Za-z_][A-Za-z0-9_.$-]*`. Frase narrativa/regra não é alvo hop1 e é proibida em linha nova ou substituída.
- **Exemplo canônico:**

  // SAC:REGR: on=dose_change - calculateDose: If modifying this method, you MUST verify: pediatric_module, ui_graph
  double calculateDose() { ... }

  > Parser também aceita forma legada; **código novo = forma canônica `- <Symbol>:`**.

### 3. SAC:DEPRECATED

- **Condição:** `on=<condition>` em snake_case, conforme `[a-z][a-z0-9_]{2,47}`.
- **Contrato:** identifica símbolo inseguro/obsoleto e termina com `replacement: <símbolo|none>`.
- **Gate:** uso novo ou nova dependência é proibido. Leitura, diagnóstico, remoção ou migração explicitamente pedidos podem usar a tag para alcançar a substituição.
- `replacement` ausente gera `deprecated_replacement_required` e HALT; risco nunca é ocultado.
- **Exemplo:**

  // SAC:DEPRECATED: on=new_dependency - legacyStream: MUST NOT be used by new code; replacement: RealtimeStream
  Stream legacyStream() { ... }

---

## Regras de Ouro Espaciais (CRÍTICO)

1. **Anti-Chunking:** uma tag fica imediatamente acima da assinatura; múltiplas tags formam bloco contíguo sem linha em branco, na ordem `ARCH` → `REGR` → `DEPRECATED` → assinatura.
2. **Âncora local:** proibido agrupar tags no topo do arquivo / abaixo dos imports.
3. **WRITE vs EXECUTE:**
   - **WRITE** só via `sac-onboard`: `REGISTER` altera apenas `.sac/domains.md`; `TAG_DELTA` aplica somente ADD/REPLACE/REMOVE e texto literal aprovados. Novo domínio ou aprovação genérica não autoriza tag.
   - **EXECUTE:** sem `SAC:` no alvo → no-op de tags. Path tagueado + MCP e CLI down → **NO-GO**.
   - Símbolo crítico sem tag → `known_gaps` / bloqueio; não inventar comentário.

---

## Ferramental do SAC

| Peça | Papel |
|------|--------|
| `src/sac_engine.py` | Parse + lookup + hop1 scoped + discover + symbol index (stdlib-only) |
| `src/sac_scan.py` | CLI: `lookup`, `discover`, `diff-check`, `validate`, `index-build` / `--check` |
| `src/sac_diff.py` | Guard REGR em PR |
| `mcp/server.mjs` | MCP Node: Route + Context + Discover + Verify; `_perf` inclui tempo e bytes |
| `src/sac_domains.py` | Parse `.sac/domains.md` + membership + hop1 scope + pause_hint |
| `docs/SAC_V2.md` | Contrato canônico (gramática, pipeline, MCP, CI) |
| `.sac/domains.md` | Manifesto de domínios (lido por `list_sac_domains` / skill; não por Verify) |
| `docs/INSTALL.md` | Guia de instalação e configuração do MCP |
| `.sac/symbol_index.json` | Artefato **gerado** (não commit); hop1 rápido scoped |

### Comandos agent-facing

```powershell
# Route — locais possíveis (sem scan de tags)
python src/sac_scan.py list-domains --root .

# Context — anchors + todas REGR/DEPRECATED + hop1
python src/sac_scan.py context --domain <domain_id> --root . --json

# Discover detalhado — tags só nos files: do domínio
python src/sac_scan.py discover --domain <domain_id> --root . --json

# Verify (filepath obrigatório; --domain opcional para membership/hop1 scoped)
python src/sac_scan.py lookup <symbol> --root . --path <file> --json
python src/sac_scan.py lookup <symbol> --root . --path <file> --domain <id> --json

# Pré-onboard: somente dentro de sac-onboard, em scope explícito; CLI-only e bounded ao path
python src/sac_scan.py lookup <symbol> --root . --path <file> --pre-onboard --json

# Índice hop1
python src/sac_scan.py index-build --root .
python src/sac_scan.py index-build --check --root .

# Gate
python src/sac_scan.py diff-check --base origin/main
python src/sac_scan.py validate --root . --warning-only

# Capillarity — on-demand; nunca no boot
python src/sac_scan.py capillarity --domain <domain_id> --root . --json
```

Escapes (debug only): `SAC_ALLOW_UNSCOPED=1`, `SAC_ALLOW_FILEPATH_OUTSIDE_DOMAINS=1`, `SAC_ALLOW_HOP1_FULL_SCAN=1`.

## Manifesto de domínios (`.sac/domains.md`)

Após `sac-onboard REGISTER` ou `TAG_DELTA` com gate PASS. `REGISTER` é index-only; `TAG_DELTA` é o único modo que altera tags; nenhum modo cria relatório persistente por padrão. Agentes:

- **Boot:** toda intenção de código/arquitetura chama `list_sac_domains()` antes de Read.
- **COR-3:** exatamente 1 intent/overlap → auto-rota; zero → bounded-unmapped; múltiplos → ask/NO-GO.
- **Context:** `get_sac_context({domain_id})` uma vez para o único domínio selecionado, antes de ler código.
- **Recorte:** `domain.files` é limite de busca, não fila de leitura; abrir apenas o alvo primário e arquivos adicionais com relação objetiva (`verify`/hop1, import/chamada direta ou staleness).
- **Precisão:** Discover/Verify somente quando houver necessidade ou alvo concreto; nunca carregar todos os domínios.

Cada bloco: `anchor_symbols`, `files`, `drawer_refs`, `known_gaps`.

**Capillarity (opcional, on-demand):** `context_scenarios` + `coverage_claims` no bloco do domínio; ausentes ⇒ assessor `UNRATED`. Não entram no catalog L0 nem no expand. Linhas de claim: `claim_id|scenario|tag_type|symbol|filepath` (`tag_type` ∈ `ARCH|REGR|DEPRECATED` — CAP-01: sem tipos novos). Cenários base: `SUMMARY`, `EXTEND`, `REGRESSION` (+ `MIGRATION` opcional). Assessor: `capillarity --domain` / `assess_sac_capillarity({domain_id})`. **Três eixos:** (A) `status` claims vs tags físicas; (B) `fitness_status` papéis estruturais + seleção Context; (C) `payload_status` `OK|OVER_BUDGET` + `payload_warn`. `quality_status=PASS` com `SUFFICIENT` + `fitness_status=FIT` + (`payload_status=OK` \| `OVER_BUDGET`). `OVER_BUDGET` é WARN — **MUST** Discover→Verify; **MUST NOT** thin domain. `non_contract_tags` informativo; não autoriza remoção automática. **PASS capillarity ≠ domínio onboard completo:** se `files:` listar paths sem tag física, domínio permanece incompleto até TAG_DELTA ou redução aprovada de `files:` (`coverage_strategy: representative`). Corrigir via `sac-onboard mode=ASSESS` — update, não criação.

## Auditoria de suficiência (qualidade, não densidade)

- Quantidade de arquivos/tags é telemetria, nunca mínimo ou máximo de qualidade.
- `files_scanned` pelo MCP não significa arquivos abertos/lidos pelo agente; reportar ambos separadamente.
- `anchor_symbols` é seleção do fast Context, não inventário total. Tag válida fora de anchors = `non_anchor_tag`, não orphan.
- `orphan` só pode ser afirmado por `sac_scan.py validate`/AST; auditoria MCP-only registra `orphans: not_measured`.
- Tag parseada não prova gramática canônica: validar `on=` (`ARCH=ssot|boundary|ordering|state|exclusive|ownership`; `REGR/DEPRECATED=[a-z][a-z0-9_]{2,47}`) e campos terminais (`verify`, `replacement`).
- Warnings canônicos do engine são bloqueantes para suficiência: `invalid_trigger`, `arch_imperative_required`, `regr_verify_required` e `deprecated_replacement_required`. A tag pode continuar visível no lookup, mas não é canônica.
- Qualquer warning canônico em risco crítico força `INSUFFICIENT`; nunca “gap não bloqueante”.
- `duplicate_constraints=0` só é comprovado se todas as constraints forem verificadas; Discover slim sozinho não prova.
- Métricas devem declarar origem: `MCP-measured`, `CLI-validated` ou `inferred`. Inferência nunca fecha DoD.
