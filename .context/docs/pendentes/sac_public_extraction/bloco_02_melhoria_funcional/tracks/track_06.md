# Track 06 — Path relativo e unidade de bytes única

[governance]
1. Deliver the goal and DoD literally; do not invent observable behavior.
2. Follow the required approach; choose only mechanically equivalent details.
3. Read only causal dependencies and record mechanically necessary unexpected writes.
4. Replan on any DoD, strategy or authority gap; do not replace it with insight, heuristic or a merely functional result.
5. No silent fallback, masked error, weak critical heuristic, TODO/stub, optional improvement or approval without literal evidence for every DoD item.
[/governance]

## Goal

Nenhum byte de payload é caminho absoluto de máquina, o orçamento semântico governa a mesma serialização que o sistema emite, e `_perf.payload_bytes` reporta os bytes efetivamente escritos.

## Context capsule

- Current flow: o adapter sempre passa `--root <absoluto>` e o engine prefixa `file` com a string de root recebida. Medido, mesma consulta: root relativo 1.599 bytes, root absoluto 1.857 bytes → **+16,1 %**. Em fixture rasa; com `C:\Users\<nome>\projects\<app>\` cresce.
- Current flow: `--root fx` → `"file": "fx/lib/a.py"`; `--root $PWD/fx` → `"file": "/tmp/.../fx/lib/a.py"`. A paridade CLI ≡ MCP é hoje **condicional à forma do root**, e o smoke não detecta porque chama a CLI com a mesma string de root do adapter.
- Current flow: o orçamento mede com `separators=(",",":")` @ `src/sac_engine.py:636`; a CLI imprime com `indent=1` e o adapter emite `JSON.stringify(obj, null, 1)` @ `mcp/server.mjs:266`. Razão medida: **1,215×**. `SAC_CONTEXT_MAX_BYTES=12288` autoriza ~14,9 KB reais.
- Current flow: `withPerf` calcula `Buffer.byteLength(JSON.stringify(payload))` @ `mcp/server.mjs:291` — payload **sem** `_perf` e **sem** indentação; `jsonToolResult` emite **com** os dois. Medido: reporta 1.599, escreve 2.101 → sub-relato de **23,9 %**.
- Current flow: `_perf.sac_root` @ `mcp/server.mjs:292` carrega o caminho absoluto da máquina do usuário para dentro do contexto do LLM.
- Owner: `src/sac_engine.py` (orçamento e montagem de `file`), `src/sac_scan.py` (emissão), `mcp/server.mjs` (`withPerf`, `jsonToolResult`).

## Semantic authority

- Must: `file` é sempre relativo à raiz, qualquer que seja a forma de `--root`. Vale para `matches` e para warnings.
- Must: `_perf.sac_root` é removido do payload.
- Must: o orçamento (`SAC_CONTEXT_MAX_BYTES`) passa a medir a **mesma serialização emitida**.
- Must: `_perf.payload_bytes` passa a medir os bytes efetivamente escritos em stdout, incluindo `_perf` e indentação.
- Must: adicionar ao `mcp/smoke.mjs` um caso que compara a mesma consulta lógica com `--root` relativo e com `--root` absoluto, **sem normalizar** path, separador ou ordenação antes da comparação.
- Must not: normalizar path nesse caso de corpus — normalizar ali suprimiria exatamente o sinal que esta track corrige.
- Must not: alterar o valor padrão do orçamento por heurística; comprimir payload; remover campo que não seja `sac_root`; tocar gramática ou gate.
- Error behavior: `context_payload_too_large` permanece explícito, com a mesma semântica e o mesmo exit code de hoje. Nunca truncamento silencioso.

## Required approach

- Owner and boundary: a relativização acontece no Python, onde `file` é montado. O Node não reescreve path.
- Data/control flow: engine monta `file` relativo → serializa na unidade emitida → mede o orçamento sobre essa serialização → adapter mede `payload_bytes` sobre o que efetivamente escreve.
- Integration rule: o mecanismo de relativização já existe (`relativize_under_root` em `src/sac_domains.py`) e deve ser reutilizado, não reimplementado.
- Executor latitude: mechanically equivalent details only

## Focus

- Likely writes: `src/sac_engine.py`, `src/sac_scan.py`, `mcp/server.mjs`, `mcp/smoke.mjs`
- Essential reads: `src/sac_engine.py:636`, `mcp/server.mjs:266,291,292`, `src/sac_domains.py` (`relativize_under_root`)
- Forbidden work: mudar o default de `SAC_CONTEXT_MAX_BYTES`; alterar fitness; tocar gramática
- Stop if: a relativização não puder ser determinística para algum root alcançável
- Depends on: track_05

## DoD

1. A mesma consulta lógica com `--root .` e com `--root <absoluto>` produz payload **idêntico byte a byte**. | Proof: manual (caso não-normalizado em `mcp/smoke.mjs`)
2. Nenhum campo do payload contém caminho absoluto; `_perf.sac_root` não existe mais. | Proof: inspect
3. `_perf.payload_bytes` é igual aos bytes efetivamente escritos em stdout, medidos independentemente. | Proof: manual (medição direta)
4. O orçamento e a emissão usam a mesma serialização; a razão medida entre elas é 1,000. | Proof: manual
5. `context_payload_too_large` mantém mensagem, código e exit code de hoje. | Proof: manual
6. O caso novo de smoke falha se `--root` voltar a vazar para dentro de `file`. | Proof: manual (regressão plantada)

## Handoff

- File: .context/docs/pendentes/sac_public_extraction/bloco_02_melhoria_funcional/handoff.md
- Terminal: record `EXECUTED` + `APPROVED` after the executor checks every DoD item in this chat; then return the robust prompt for `track_07` in a new chat
