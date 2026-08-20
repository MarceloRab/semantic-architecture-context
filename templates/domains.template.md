# SAC Domain Index

> Registro compacto de **módulos/redes de escopo** com cobertura SAC física. Atualizado somente por `sac-onboard mode=REGISTER` ou após `mode=TAG_DELTA` com gate PASS.
>
> **Route L0 (catalog):** `list_sac_domains()` → `domain_id` + `intent` + `files_count` (sem dump de files).
> **Context fast path:** `get_sac_context({domain_id})` → anchors + todas `REGR`/`DEPRECATED` + hop1 em um overlay de um único domínio.
> **Discover L1:** `discover_sac({domain_id})` → inventário slim (`file/line/type/symbol` [+ `verify`/`replacement`]); sem constraint.
> **Verify:** `get_sac_constraints` — `filepath` explícito ∈ `files:` (+ `domain_id` opcional).
> **Capillarity (on-demand):** `context_scenarios` + `coverage_claims` no domain; ausentes ⇒ `UNRATED`. Nunca entram no catalog L0 nem no expand. Assessor: `capillarity --domain` / `assess_sac_capillarity` (T2/T3). Três eixos: (A) `status` claims vs tags; (B) `fitness_status` papéis estruturais + seleção Context (`ARCH` ∈ `anchor_symbols`); (C) `payload_status` + `payload_warn`. `quality_status=PASS` com `SUFFICIENT`+`FIT`+(`OK`|`OVER_BUDGET`); `OVER_BUDGET` é WARN — **MUST NOT** thin `files:`/tags/claims.

## Como usar

1. **Toda intenção de código/arquitetura:** `list_sac_domains()` antes de ler código.
2. **Route:** exatamente um `intent` compatível → auto-selecionar; zero → bounded-unmapped; múltiplos → perguntar / NO-GO.
3. **Contexto:** `get_sac_context({domain_id})` monta anchors + `REGR`/`DEPRECATED` + hop1 em uma chamada; nunca carregar todos os domínios.
4. **Alvo concreto:** `get_sac_constraints(<symbol>, filepath=<path ∈ files:>, domain_id)`.
5. **Sem ferramenta:** filtrar primeiro por condição com `rg 'SAC:.*on=<condition>' <files:>`; ARCH usa `ssot|boundary|ordering|state|exclusive|ownership`, e REGR/DEPRECATED usam `[a-z][a-z0-9_]{2,47}`.
6. **Inspeção detalhada:** `files:` é limite de busca, não fila de leitura; abrir o alvo primário e somente dependências objetivas da task. `discover_sac({domain_id})`; fallback `rg` scoped.
7. **Novo domínio:** `sac-onboard mode=ASSESS`; `REGISTER` só indexa tags existentes; `TAG_DELTA` é o único modo que altera tags.
8. **Capilaridade:** opcional; base `SUMMARY, EXTEND, REGRESSION`; claims = `claim_id|scenario|tag_type|symbol|filepath` (5 colunas). Papéis estruturais: `SUMMARY`→ARCH, `EXTEND`→ARCH, `REGRESSION`→REGR; `ARCH` para Context deve constar em `anchor_symbols`. Sem claims ⇒ não declarar suficiência.
   O piso de anchors é exatamente o conjunto de símbolos das claims ARCH: para minimizar `anchor_symbols`, minimize antes as claims ARCH sem violar os papéis estruturais.
9. **Saída:** handoff somente no chat; não criar relatório persistente. Registrar `sac_scope`, limite real, warnings e `domain_index_status`.

### COR-3 — resolução de domínio (fechada)

| Overlap diff/intent ↔ `files:` | Ação |
|--------------------------------|------|
| **Exatamente 1** domínio por intent ou overlap | Auto-selecionar e montar contexto |
| **0** domínios compatíveis | `sac_scope: unmapped`; busca bounded com `fd`/`rg`/`bat`; sem diretório objetivo → HALT |
| **N>1** | Perguntar / NO-GO — **proibido** chutar |

---

## _template

<!-- Copie este bloco somente após REGISTER ou TAG_DELTA com gate PASS; remova comentários HTML. Não adicione tag_count. Capillarity opcional: declare context_scenarios + coverage_claims juntos, ou omita ambos. -->

## example_domain
- intent: One-line semantic summary of this module / context network
- onboarded: YYYY-MM-DD
- drawer_file: .context/docs/architecture_drawers/02_engines_mechanisms.md
- drawer_refs: MECH-XXX, CriticalFlowExample
- anchor_symbols: PrimaryOrchestrator, SecondaryFacade
- files:
  - path/to/backend.ts
  - path/to/frontend.dart
- context_scenarios: SUMMARY, EXTEND, REGRESSION
- coverage_claims:
  - EX_SUMMARY_ORCH | SUMMARY | ARCH | PrimaryOrchestrator | path/to/backend.ts
  - EX_EXTEND_ORCH | EXTEND | ARCH | PrimaryOrchestrator | path/to/backend.ts
  - EX_REGR_FACADE | REGRESSION | REGR | SecondaryFacade | path/to/frontend.dart
- on_edit: sac-execution-overlay + get_sac_context + get_sac_constraints
- known_gaps:

---

<!-- Domínios reais de projetos residem em .sac/domains.md. Este arquivo mantém schema, manual COR-3 e _template managed. -->
