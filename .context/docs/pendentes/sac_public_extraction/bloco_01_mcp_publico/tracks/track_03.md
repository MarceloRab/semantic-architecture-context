# Track 03 — Transplante verbatim do código

[governance]
1. Deliver the goal and DoD literally; do not invent observable behavior.
2. Follow the required approach; choose only mechanically equivalent details.
3. Read only causal dependencies and record mechanically necessary unexpected writes.
4. Replan on any DoD, strategy or authority gap; do not replace it with insight, heuristic or a merely functional result.
5. No silent fallback, masked error, weak critical heuristic, TODO/stub, optional improvement or self-certification.
[/governance]

## Goal

O código do SAC existe em `semantic-architecture-context` com comportamento **idêntico** ao de origem, provado por `mcp/smoke.mjs` verde com o mesmo veredicto nos dois repositórios.

## Context capsule

- Current flow: origem é `C:\Users\Rabelo\projects\rabelo-standards\sac-context\`, com `src/` (6 módulos Python), `mcp/` (`server.mjs` 564 linhas, `smoke.mjs` 873 linhas, `package.json`, `package-lock.json`, `README.md`), `ci/` (`sac_ci_guard.ps1`, `sac_guard.yml`), `docs/` (8 arquivos), `scripts/smoke_sac_mcp_node.ps1`.
- Owner: `mcp/smoke.mjs` é o único instrumento de equivalência comportamental existente — não há teste unitário Python (`test_*.py` sob `sac-context/`: zero). Ele já cobre paridade CLI≡MCP por fixture, forma do catalog, slimness do discover, PAUSE negativo, membership, hop1 scoped e overflow de contexto.
- Dependency: `smoke.mjs` importa `server.mjs`, que importa o SDK MCP. Sem `npm install` o smoke não roda **nem** para as checagens puramente CLI.

## Semantic authority

- Must: copiar `src/` (exceto adapter Python legado e exceto `__pycache__/`), `mcp/`, `ci/`, `docs/` para a raiz do repositório de destino, preservando a estrutura de diretórios relativa.
- Must: **zero** alteração de comportamento nesta track. O diff é movimentação de arquivos e as duas exclusões declaradas, nada mais.
- Must not: renomear símbolo, corrigir defeito conhecido, atualizar versão, mexer em caminho hardcoded, formatar código, remover código morto, ou compartilhar commit com qualquer outra track.
- Must not: copiar `src/__pycache__/` (4 `.pyc` rastreados contendo `C:\Users\Rabelo\projects\rabelo-standards\...`) nem adapter Python legado.
- Error behavior: se o smoke falhar no destino, a causa é investigada e corrigida como problema de transplante (caminho, encoding, permissão), nunca como ajuste de comportamento do engine. Se a causa for comportamental, parar.

## Required approach

- Owner and boundary: a árvore copiada é `managed`. Nenhum arquivo `owned` é criado nesta track.
- Data/control flow: `npm install` em `mcp/` → executar `smoke.mjs` na origem, registrar veredicto → copiar → `npm install` no destino → executar `smoke.mjs` no destino → comparar veredictos.
- Integration rule: a arquitetura de camadas é preservada integralmente — semântica só em Python, `server.mjs` fino, paridade CLI≡MCP.
- Executor latitude: mechanically equivalent details only

## Focus

- Likely writes: `src/`, `mcp/`, `ci/`, `docs/`
- Essential reads: `C:\Users\Rabelo\projects\rabelo-standards\sac-context\` (origem)
- Forbidden work: qualquer correção de defeito; atualizar `package.json`; tocar `sac_domains.py:14`; criar `.sac/`; escrever installer
- Stop if: o smoke divergir entre origem e destino por causa comportamental
- Depends on: track_02

## DoD

1. `mcp/smoke.mjs` executado na origem e no destino produz o mesmo veredicto. | Proof: manual (saídas das duas execuções, comparadas)
2. Adapter Python legado e `src/__pycache__/` não existem no destino. | Proof: inspect
3. O diff da track contém apenas adição de arquivos copiados; nenhuma linha de conteúdo difere da origem para os arquivos copiados. | Proof: diff
4. O workflow de higiene de track_02 passa sobre a árvore copiada. | Proof: manual
5. Nenhum commit desta track contém alteração de outra track. | Proof: diff

## Handoff

- File: .context/docs/pendentes/sac_public_extraction/bloco_01_mcp_publico/handoff.md
- Terminal: `EXECUTED`; review requires a separate manual trigger
