# Handoff — Bloco 02: melhoria funcional da feature

## Plan

- Design: .context/docs/pendentes/sac_public_extraction/bloco_02_melhoria_funcional/design.md
- Approved by: usuário, 2026-08-19 — autorização explícita para ativar o builder
- Current: track_02

## Tracks

| Track | Goal | Depends on | Status | Attempt |
| --- | --- | --- | --- | --- |
| track_01 | verify: termina em `;` ou fim de linha; nenhum alvo descartado em silêncio | none | APPROVED | 1 |
| track_02 | Campo `on=` com vocabulário fechado para ARCH e parser dual para tags legadas | track_01 | PENDING | 0 |
| track_03 | AGENTS.md como porta de entrada e camada de atalho de dois níveis nas três skills | track_02 | PENDING | 0 |
| track_04 | `_is_covered` avalia contra o conjunto completo; veredicto independente da ordem de caminhos | track_03 | PENDING | 0 |
| track_05 | Registro de linguagens com Python, JS/TS e Go, e dogfooding bloqueante na CI | track_04 | PENDING | 0 |
| track_06 | file relativo, `_perf.sac_root` removido, orçamento e payload_bytes na unidade emitida | track_05 | PENDING | 0 |
| track_07 | OVER_SELECT deixa de contar tags auto-incluídas; piso de anchors reportado pelo assess | track_06 | PENDING | 0 |
| track_08 | Marcador de comentário sem whitelist e vocabulário imperativo PT+EN | track_07 | PENDING | 0 |
| track_09 | Promessa honesta, política de vetos publicada, RELEASE_GATE satisfeito e tag 0.1.0 | track_08 | PENDING | 0 |

Status: `PENDING` -> `EXECUTED` -> `APPROVED` | `FAILED` | `REPLAN` | `CHANGES_REQUIRED`.
The executor performs the literal DoD check in the same chat. When every item has evidence, it records both `EXECUTED` and `APPROVED` in the attempt, updates its own row and attempt number, and moves `Current` to the next track. If any item lacks evidence, it must record the truthful non-approved terminal instead. Nobody edits another row.

## Correção de rota — 2026-08-20

- Authority: usuário.
- Review is no longer a separate manual trigger. It is a literal DoD check performed by the same agent that executes the track.
- Approval is not inferred from implementation or green tests alone: every numbered DoD item must have its requested proof recorded in the attempt.
- A successful attempt records the sequence `EXECUTED` + `APPROVED` in the same history entry and leaves the track row as `APPROVED`.
- At completion, the agent must return a robust, self-contained prompt for executing **only the next track in a new chat**. The prompt must name the track and dependency already approved; require reading its track file, this handoff and only causal dependencies; require literal Goal, Semantic authority, Required approach and DoD; require tests and requested proof; require commit and PR; require the same-chat DoD check; and require updating this handoff plus returning the following track's prompt. For `track_09`, replace the following-track prompt with the explicit release/tag operational handoff required by its DoD.

## Attempts

Append entries; never rewrite history.

### track_01 — Attempt 1 — 2026-08-20 — EXECUTED + APPROVED

- Outcome: o parser de `verify:` agora captura até `;` ou fim da linha, preserva pontos dentro de tokens, valida cada alvo contra `[A-Za-z_][A-Za-z0-9_.$-]*`, mantém todos os alvos válidos e emite `invalid_verify_target target=<token>` para cada alvo inválido. O mesmo parsing é usado pelas formas canônica e REGR legada; `_is_covered`, `trigger` e consumidores não foram alterados.
- DoD 1: `python3 -m unittest tests/test_verify_parse.py` passou; `test_dotted_target_and_second_target_are_preserved` provou `verify: Cache.key, Adapter` → `['Cache.key', 'Adapter']` e warnings `[]`.
- DoD 2: o mesmo comando passou; `test_terminal_period_preserves_existing_behavior` provou `verify: CacheKey, Adapter.` → `['CacheKey', 'Adapter']`, e `test_narrative_before_verify_preserves_existing_behavior` provou a narrativa anterior seguida de `MUST verify: CacheKey` → `['CacheKey']`, ambos sem warnings.
- DoD 3: o mesmo comando passou; `test_invalid_target_is_named_without_dropping_valid_target` provou `verify: 9bad, Good` → `['Good']` e warning exato `invalid_verify_target target=9bad`.
- DoD 4: o mesmo comando passou; `test_semicolon_ends_verify_list` provou `verify: A; texto depois` → `['A']` sem warnings.
- DoD 5: `node mcp/smoke.mjs` passou e imprimiu `[OK] dotted verify raw-line≡MCP targets=SmokeHop.method,SmokeHop`, comparando literalmente a lista declarada na linha crua da fixture com `matches[0].verify` retornado por `runLookup`.
- DoD 6: `node mcp/smoke.mjs` completo terminou com `[OK] smoke exit 0`; todas as fixtures/tag forms anteriores continuaram parseáveis, além do novo caso pontuado. O gate adicional `python3 .github/scripts/check_hygiene.py` passou e `git diff --check` não encontrou erros.
- Terminal: `EXECUTED` após implementação e execução das provas; `APPROVED` após checagem literal, neste mesmo chat, dos seis itens numerados acima.

## Pré-condição do bloco

Este bloco inicia somente após `track_10` do Bloco 01 estar `APPROVED`. A ordem interna é ditada por princípio, não por custo: as quatro primeiras tracks são as únicas de toda a coleção de relatórios que **aumentam** o benefício ao agente cego; as demais defendem os outros dois pilares.

## Fora de escopo, posterior ao bloco

Nenhum consumidor existente é migrado por este bloco. `api_robot` e `to_de_plantao` continuam rodando suas cópias congeladas de `sac-context/`, e `rabelo-standards` — base propagadora, não consumidora — não é tocado. A transferência para esses projetos é decisão do usuário, posterior a testes estáveis pós-Bloco 02.
