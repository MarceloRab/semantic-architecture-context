# Track 01 — Auditoria de estado real consolidada

[governance]
1. Deliver the goal and DoD literally; do not invent observable behavior.
2. Follow the required approach; choose only mechanically equivalent details.
3. Read only causal dependencies and record mechanically necessary unexpected writes.
4. Replan on any DoD, strategy or authority gap; do not replace it with insight, heuristic or a merely functional result.
5. No silent fallback, masked error, weak critical heuristic, TODO/stub, optional improvement or self-certification.
[/governance]

## Goal

`AUDIT.md` existe na raiz de `semantic-architecture-context` registrando cada defeito conhecido do SAC com arquivo:linha, reprodução e classificação em exatamente uma de três categorias: `corrigir antes da extração`, `corrigir antes da 0.1.0`, `aceitar e documentar`.

## Context capsule

- Current flow: os defeitos já foram levantados e reproduzidos nos três relatórios em `.context/docs/pendentes/sac_public_extraction/AVALIACAO_ADVERSARIAL_V3.md`, `AVALIACAO_FUNCIONAL_V4.md`, `AVALIACAO_ADVERSARIAL_V5_REPORT_EXTERNO.md`. Nenhum está classificado nem consolidado.
- Owner: nenhum arquivo de código é tocado nesta track. O produto é documental.
- Dependency: nenhuma.

## Semantic authority

- Must: registrar no mínimo os seguintes achados, cada um com anchor e classificação — manifesto `owned` dentro da árvore `managed` (`src/sac_domains.py:14`); segunda superfície MCP (adapter Python legado); Layer A de testes = 0 (`test_*.py` sob `sac-context/`: zero); `_perf.payload_bytes` sub-relata 23,9 % (`mcp/server.mjs:291` vs `:266`); unidade de orçamento 1,215× divergente (`src/sac_engine.py:636` vs `indent=1`); vazamento de path absoluto no payload = 16,1 %; três escapes `SAC_ALLOW_*` não atestados (`mcp/server.mjs:78`, `src/sac_scan.py:354`, `src/sac_domains.py:478`, `src/sac_domains.py:537`); 4 `.pyc` rastreados com caminho do autor; identidade de versão tripla (`mcp/package.json` 1.0.0, `mcp/server.mjs:327` 1.6.0, gate D4 de `sac-evolution`); terceira classe de erro apagada (exit 2 só em stderr, `src/sac_scan.py`); `_SYMBOL_REGISTRY` com duas entradas (`src/sac_diff.py:36`); ordenação em `_is_covered` (`src/sac_diff.py:415-427`); truncamento de `verify:` no ponto (`src/sac_engine.py:43`); campo `trigger` inerte (`src/sac_engine.py:102-106`); `AGENTS.md` sem menção a SAC; caminho absoluto em `skills/.../sac-onboard/prompt_resumido.md`; colisão de gatilho no frontmatter de `sac-context` e `sac-execution-overlay`; CI executando parsing sobre corpo de PR de fork (`ci/sac_guard.yml`).
- Must: registrar o inventário de superfícies MCP (duas), de cobertura de teste por camada (Layer A = 0, smoke = Layer B+C) e o eixo linguagem como dimensão ausente da matriz de compatibilidade.
- Must not: propor correção, alterar código, ou deixar achado sem classificação.
- Error behavior: se um achado não puder ser reproduzido a partir do anchor citado, registrá-lo como `NÃO REPRODUZIDO` com o motivo. Nunca omitir e nunca presumir.

## Required approach

- Owner and boundary: um único arquivo `AUDIT.md` na raiz do repositório de destino. Nenhum código é lido para alterar; leitura é apenas para confirmar anchor.
- Data/control flow: para cada achado — identificador estável (`A01`, `A02`, …) → anchor arquivo:linha → sintoma observável → passo de reprodução → classificação → track do Bloco 01 ou 02 que o resolve, ou `aceitar e documentar`.
- Integration rule: tabela markdown, uma linha por achado, legível sem ferramenta.
- Executor latitude: mechanically equivalent details only

## Focus

- Likely writes: `AUDIT.md`
- Essential reads: os três relatórios em `.context/docs/pendentes/sac_public_extraction/`; para confirmar anchor, `C:\Users\Rabelo\projects\rabelo-standards\sac-context\src\` e `mcp\`
- Forbidden work: corrigir qualquer defeito; criar `.git`; copiar código; escrever README, LICENSE ou workflow
- Stop if: um achado exigir decisão de classificação que os relatórios não sustentem
- Depends on: none

## DoD

1. `AUDIT.md` contém todos os achados listados em Semantic authority, cada um com identificador, anchor arquivo:linha e passo de reprodução. | Proof: inspect
2. Cada achado tem exatamente uma classificação entre as três categorias, e nenhuma linha está vazia na coluna. | Proof: inspect
3. Cada achado classificado como `corrigir antes da extração` ou `corrigir antes da 0.1.0` aponta a track que o resolve. | Proof: inspect
4. Nenhum arquivo além de `AUDIT.md` foi criado ou alterado. | Proof: diff

## Handoff

- File: .context/docs/pendentes/sac_public_extraction/bloco_01_mcp_publico/handoff.md
- Terminal: `EXECUTED`; review requires a separate manual trigger
