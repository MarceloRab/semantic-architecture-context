# SAC ONBOARD <id> — atalho

## Sem MCP

```bash
python3 src/sac_scan.py list-domains --root . --json
python3 src/sac_scan.py context --root . --domain <id> --json
```

Use `SAC ONBOARD <id>` — ou simplesmente peça para criar/atualizar um domínio ao apontar esta skill — para ativar `sac-onboard` em `mode=ASSESS`, read-only por default. Leia agora o [`SKILL.md`](./SKILL.md) irmão, que contém o contrato; se o caminho relativo não resolver, pare e reporte.

Os atalhos são estáveis e disjuntos: `SAC` → `sac-execution-overlay`; `SAC ONBOARD <id>` → `sac-onboard`; `SAC TAG` → `sac-context`. Nenhum deles autoriza Write; somente `APROVAR SAC REGISTER <id>` e `APROVAR SAC TAG_DELTA <id>` podem autorizá-lo nos limites do contrato.


## Gatilho natural (1 linha do usuário → contrato)

Interpretar a mensagem do usuário **antes** de Write:

| Frase (exemplos) | Derivar automaticamente |
|---|---|
| Só apontar este `PROMPT.md` (sem intenção nem `domain_id`) | **PAUSE imediato** — perguntar literalmente: **«Criar um novo domínio ou atualizar um existente?»**; zero ASSESS, zero Write, zero scan até resposta |
| Resposta «criar novo» / «novo domain» (ainda sem `domain_id`) | **PAUSE** — pedir `domain_id` + escopo mínimo; zero Write |
| Resposta «atualizar» / «existente» (ainda sem `domain_id`) | **PAUSE** — listar IDs via `list_sac_domains` (MCP) e pedir qual(is); zero Write |
| `Atualizar domínio <id>` / `Atualizar domínios <id>, <id>` | `mode=ASSESS`; `requested_domains` = IDs exatos; derivar `candidate_scope` dos domínios existentes; `approval_command=none` |
| `Criar domínio <id> em <escopo>` / `Novo domain <id> em <escopo>` | `mode=ASSESS`; ID e `candidate_scope` explícitos; avaliar sem Write |
| `Criar domínio <id>` / `Novo domain <id>` / `Onboard <id>` sem escopo | `mode=ASSESS`; ID explícito; **PAUSE** somente para pedir o escopo mínimo ausente |
| `Implementar <mudança>` / `Corrigir bug <descrição>` | Encaminhar para `sac-execution-overlay`; não executar onboard nem escrever tags |
| `APROVAR SAC REGISTER <id>` / `APROVAR SAC TAG_DELTA <id>` | modo correspondente **somente** se literal; senão permanece ASSESS |

**N>1 domínios:** entregar **um bloco `SAC ASSESS` por `domain_id`**, depois PAUSE único. Overlap de `files:`/anchors entre domínios → regra da skill (HALT ou aprovação humana); não inventar precedência.

`novo domain`, `atualizar domain(s)`, conhecimento deste harness, `ok` ou `pode aplicar` **nunca** autorizam Write nem criação de linhas.

Não pedir ao usuário `mode`, `requested_domains`, `candidate_scope` ou `approval_command` quando esses campos já forem derivados literalmente da frase. Perguntar somente pelo ID ou escopo mínimo realmente ausente.

## Modos (resumo)

Se `mode` não estiver literal, execute somente `mode=ASSESS` read-only.

`REGISTER` exige `APROVAR SAC REGISTER <domain_id>` e altera somente `.sac/domains.md`. `TAG_DELTA` exige `APROVAR SAC TAG_DELTA <domain_id>` + tabela literal `ADD|REPLACE|REMOVE` — único caminho para criar/substituir/remover tags.

ASSESS: tabela literal `claim_id|scenario|tag_type|symbol|filepath`; claim sem tag → `TAG_DELTA_REQUIRED`; claims cobrem SUMMARY+EXTEND+REGRESSION (Discover); ARCH para Context ∈ `anchor_symbols`; `files_listed == files_tagged == claims_listed` ou `coverage_strategy` aprovado; diff persistente = ∅.

Capillarity: `assess_sac_capillarity` / `capillarity --domain` **somente em ASSESS** ou pedido explícito — **cold path**; nunca boot READ/EXECUTE; **proibido revert** por capillarity.

DoD cristalino: ASSESS sem diff → PAUSE → `APROVAR` → 1 TAG_DELTA/REGISTER. Sem turno 2 de auditoria de agente.

Proibido abrir todos os `files:`. Conflito de IDs, overlap não resolvido, warning ou decisão não literal → HALT. **`domain_id` ausente ≠ HALT** — usar PAUSE + pergunta acima. Nunca criar relatório/auditoria/handoff em arquivo; handoff somente no chat.
