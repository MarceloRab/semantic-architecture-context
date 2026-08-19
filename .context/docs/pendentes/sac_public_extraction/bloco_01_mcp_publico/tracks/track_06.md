# Track 06 — Atestação de gates e terceira classe de erro

[governance]
1. Deliver the goal and DoD literally; do not invent observable behavior.
2. Follow the required approach; choose only mechanically equivalent details.
3. Read only causal dependencies and record mechanically necessary unexpected writes.
4. Replan on any DoD, strategy or authority gap; do not replace it with insight, heuristic or a merely functional result.
5. No silent fallback, masked error, weak critical heuristic, TODO/stub, optional improvement or self-certification.
[/governance]

## Goal

Uma resposta que operou com HALT relaxado é distinguível de uma resposta gated, e uma falha de uso ou de ambiente chega ao agente como erro de ambiente, não como falha de lookup.

## Context capsule

- Current flow: `runCliJson` monta `{ ...process.env, ...(opts.env || {}) }` @ `mcp/server.mjs:78`, então o subprocesso herda o ambiente do host e os três escapes são configuráveis pelo bloco `env` do arquivo de config do host MCP, valendo para todas as chamadas.
- Current flow: os três escapes são `SAC_ALLOW_UNSCOPED` @ `src/sac_scan.py:354`, `SAC_ALLOW_FILEPATH_OUTSIDE_DOMAINS` @ `src/sac_domains.py:478`, `SAC_ALLOW_HOP1_FULL_SCAN` @ `src/sac_domains.py:537`. Verificado: com o escape ligado o payload devolve `found: true` com matches fora do domínio, e é **indistinguível** do payload gated — nenhum campo, nenhum warning.
- Current flow: `src/sac_scan.py` usa exit 2 em 8 pontos (root não é diretório, erro de uso do argparse), escrevendo **só em stderr**, stdout vazio. O adapter cai no ramo "empty stdout" e devolve `Error` genérico, convertido pelo handler em `lookup_failed` / `context_failed`.
- Owner: `src/sac_scan.py` monta o payload final da CLI; `mcp/server.mjs` o envelopa.

## Semantic authority

- Must: toda resposta que operou com ao menos um escape ativo inclui `gates_bypassed: [<nome do env var>, …]` e um warning correspondente, em CLI e em MCP identicamente.
- Must: quando nenhum escape está ativo, o campo `gates_bypassed` é **omitido** do payload. Custo zero de bytes no caminho normal.
- Must: todo caminho que hoje sai com exit 2 passa a emitir JSON estruturado em **stdout** com `code` da família `sac.environment.*` (mínimo: root inexistente, root não é diretório, uso inválido de argumento, interpretador Python ausente), mantendo o exit code 2.
- Must: `mcp/server.mjs` mapeia esses payloads para `sac.environment_error`, distinto de `lookup_failed` e de `context_failed`.
- Must not: remover os escapes; alterar o que os escapes fazem; introduzir campo quando não há bypass; usar exit code para transportar semântica que o payload deveria carregar.
- Error behavior: erro de ambiente é explícito e nomeado. Nunca é convertido em erro semântico nem mascarado em erro de transporte.

## Required approach

- Owner and boundary: a detecção de escape ativo pertence ao Python (é lá que os escapes são lidos). O Node apenas propaga e mapeia.
- Data/control flow: leitura do env no Python → coleta dos escapes ativos → campo no payload quando não vazio → adapter propaga sem reinterpretar.
- Integration rule: paridade CLI ≡ MCP vale para os campos novos; nenhum campo existe em um adapter e não no outro.
- Executor latitude: mechanically equivalent details only

## Focus

- Likely writes: `src/sac_scan.py`, `src/sac_domains.py`, `mcp/server.mjs`, `mcp/smoke.mjs`
- Essential reads: `mcp/server.mjs:78`, `src/sac_scan.py:354`, `src/sac_domains.py:478,537`
- Forbidden work: tocar caminho do manifesto; alterar serialização ou unidade de bytes; tornar `file` relativo (é Bloco 02)
- Stop if: algum escape não puder ser detectado no ponto onde é lido
- Depends on: track_05

## DoD

1. Para cada um dos três escapes: payload contém `gates_bypassed` com o nome correto quando ligado, e **não contém o campo** quando desligado. | Proof: manual (seis execuções)
2. Cada payload com `gates_bypassed` traz também o warning correspondente. | Proof: manual
3. Root inexistente devolve JSON em stdout com `code` `sac.environment.*` e o adapter reporta `sac.environment_error`, não `lookup_failed`. | Proof: manual (CLI e MCP)
4. Argumento inválido devolve `sac.environment.*`, não erro de transporte. | Proof: manual
5. `mcp/smoke.mjs` cobre cada escape ligado e desligado, e a classe de erro de ambiente. | Proof: manual
6. Paridade CLI ≡ MCP preservada para todos os campos novos. | Proof: manual

## Handoff

- File: .context/docs/pendentes/sac_public_extraction/bloco_01_mcp_publico/handoff.md
- Terminal: `EXECUTED`; review requires a separate manual trigger
