# Track 09 — CI pública para PR de fork

[governance]
1. Deliver the goal and DoD literally; do not invent observable behavior.
2. Follow the required approach; choose only mechanically equivalent details.
3. Read only causal dependencies and record mechanically necessary unexpected writes.
4. Replan on any DoD, strategy or authority gap; do not replace it with insight, heuristic or a merely functional result.
5. No silent fallback, masked error, weak critical heuristic, TODO/stub, optional improvement or self-certification.
[/governance]

## Goal

Uma PR aberta de um fork por uma pessoa desconhecida completa a CI verde, sem acesso a segredo, sem execução de conteúdo hostil como código, e com limite de tempo determinístico.

## Context capsule

- Current flow: `ci/sac_guard.yml` roda em `pull_request`, executa `index-build` e `validate` sobre a árvore da PR, e injeta `SAC_PR_BODY: ${{ github.event.pull_request.body }}`. Enquanto o repositório é privado, o autor da PR é o dono; publicado, é qualquer pessoa da internet.
- Current flow: o engine aplica regex linha a linha, incluindo padrões `.*?` e `[^.]+`, sobre a árvore da PR.
- Owner: `.github/workflows/ci.yml` passa a ser o workflow público; `ci/sac_guard.yml` é a lógica reutilizada.
- Dependency: `mcp/smoke.mjs` exige `npm install` em `mcp/` antes de rodar, **inclusive** para as checagens puramente CLI.

## Semantic authority

- Must: gatilho `pull_request`. Nunca `pull_request_target`.
- Must: `permissions: contents: read` declarado explicitamente no workflow. Nenhum segredo referenciado.
- Must: `timeout-minutes` declarado no job — é o limite determinístico contra ReDoS sobre conteúdo hostil.
- Must: o corpo da PR é entregue ao processo por `env:` em passo intermediário, nunca por interpolação de expressão dentro de `run:`.
- Must: matriz OS × Python (3.11, 3.12, 3.13) × Node (22, 24).
- Must: jobs = higiene (track_02), `validate`, `index-build`, `smoke`.
- Must not: adicionar job de `diff-check`. Ele entra no Bloco 02, junto com a correção de ordenação e o registro de linguagens. Um job de gate **não-bloqueante** também é proibido.
- Must not: inventar cap de bytes por arquivo ou qualquer limite numérico não derivado de medição.
- Error behavior: falha de job é dura e nomeada. Nenhum job com `continue-on-error`.

## Required approach

- Owner and boundary: `.github/workflows/ci.yml` é o dono; `ci/sac_guard.yml` fornece a lógica de validate/index-build.
- Data/control flow: checkout → setup Python/Node da matriz → `npm install` em `mcp/` → higiene → validate → index-build → smoke.
- Integration rule: nenhum passo escreve no repositório; a CI é somente leitura.
- Executor latitude: mechanically equivalent details only

## Focus

- Likely writes: `.github/workflows/ci.yml`, `ci/sac_guard.yml`
- Essential reads: `ci/sac_guard.yml`, `mcp/smoke.mjs` (requisito de `npm install`)
- Forbidden work: ligar `diff-check`; adicionar cap numérico ao engine; endurecer regex; publicar em registry
- Stop if: algum job exigir segredo ou permissão de escrita
- Depends on: track_08

## DoD

1. Uma PR real aberta de um fork completa a CI verde. | Proof: manual (link da execução)
2. O workflow não contém `pull_request_target` nem interpolação `${{ }}` dentro de qualquer bloco `run:`. | Proof: inspect
3. `permissions: contents: read` e `timeout-minutes` estão declarados. | Proof: inspect
4. Nenhum job usa `continue-on-error` e nenhum job de `diff-check` existe. | Proof: inspect
5. A matriz cobre Python 3.11/3.12/3.13 e Node 22/24, e todas as combinações passam. | Proof: manual
6. O gate de higiene roda também sobre o histórico na CI. | Proof: manual

## Handoff

- File: .context/docs/pendentes/sac_public_extraction/bloco_01_mcp_publico/handoff.md
- Terminal: `EXECUTED`; review requires a separate manual trigger
