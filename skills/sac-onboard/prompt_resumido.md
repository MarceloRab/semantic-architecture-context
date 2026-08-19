Antes de qualquer ação, resolva o harness sem heurística: leia integralmente o arquivo irmão ./PROMPT.md. Depois leia o ./SKILL.md irmão.

## Gatilho natural (1 linha do usuário → contrato)

Interpretar a mensagem do usuário **antes** de Write:

| Frase (exemplos) | Derivar automaticamente |
|---|---|
| Só `Ler …/prompt_resumido.md` (sem `domain_id`) | **PAUSE imediato** — perguntar literalmente: **«Criar um novo domain ou atualizar um existente?»**; zero ASSESS, zero Write, zero scan até resposta |
| Resposta «criar novo» / «novo domain» (ainda sem `domain_id`) | **PAUSE** — pedir `domain_id` + escopo mínimo; zero Write |
| Resposta «atualizar» / «existente» (ainda sem `domain_id`) | **PAUSE** — listar IDs via `list_sac_domains` (MCP) e pedir qual(is); zero Write |
| `Atualizar domain <id>` / `Atualizar domains <id>, <id>` | `mode=ASSESS`; `requested_domains` = IDs exatos; `candidate_scope` = mesmos IDs; `approval_command=none` |
| `Novo domain <id>` / `Onboard <id>` | `mode=ASSESS`; `requested_domains` = ID explícito; scope ausente → **PAUSE** pedindo escopo |
| `APROVAR SAC REGISTER <id>` / `APROVAR SAC TAG_DELTA <id>` | modo correspondente **somente** se literal; senão permanece ASSESS |

**N>1 domínios:** entregar **um bloco `SAC ASSESS` por `domain_id`**, depois PAUSE único. Overlap de `files:`/anchors entre domínios → regra da skill (HALT ou aprovação humana); não inventar precedência.

`novo domain`, `atualizar domain(s)`, conhecimento deste harness, `ok` ou `pode aplicar` **nunca** autorizam Write nem criação de linhas.

## Modos (resumo)

Se `mode` não estiver literal, execute somente `mode=ASSESS` read-only.

`REGISTER` exige `APROVAR SAC REGISTER <domain_id>` e altera somente `.sac/domains.md`. `TAG_DELTA` exige `APROVAR SAC TAG_DELTA <domain_id>` + tabela literal `ADD|REPLACE|REMOVE` — único caminho para criar/substituir/remover tags.

ASSESS: tabela literal `claim_id|scenario|tag_type|symbol|filepath`; claim sem tag → `TAG_DELTA_REQUIRED`; claims cobrem SUMMARY+EXTEND+REGRESSION (Discover); ARCH para Context ∈ `anchor_symbols`; `files_listed == files_tagged == claims_listed` ou `coverage_strategy` aprovado; diff persistente = ∅.

Capillarity: `assess_sac_capillarity` / `capillarity --domain` **somente em ASSESS** ou pedido explícito — **cold path**; nunca boot READ/EXECUTE; **proibido revert** por capillarity.

DoD cristalino: ASSESS sem diff → PAUSE → `APROVAR` → 1 TAG_DELTA/REGISTER. Sem turno 2 de auditoria de agente.

Proibido abrir todos os `files:`. Conflito de IDs, overlap não resolvido, warning ou decisão não literal → HALT. **`domain_id` ausente ≠ HALT** — usar PAUSE + pergunta acima. Nunca criar relatório/auditoria/handoff em arquivo; handoff somente no chat.
