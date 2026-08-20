# Track 01 — `verify:` deixa de truncar no ponto

[governance]
1. Deliver the goal and DoD literally; do not invent observable behavior.
2. Follow the required approach; choose only mechanically equivalent details.
3. Read only causal dependencies and record mechanically necessary unexpected writes.
4. Replan on any DoD, strategy or authority gap; do not replace it with insight, heuristic or a merely functional result.
5. No silent fallback, masked error, weak critical heuristic, TODO/stub, optional improvement or approval without literal evidence for every DoD item.
[/governance]

## Goal

`verify: Cache.key, Adapter` devolve `['Cache.key', 'Adapter']`. Nenhum alvo de `verify:` é descartado em silêncio, e o agente que chama o MCP nunca recebe menos alvos do que o agente que lê a linha crua.

## Context capsule

- Current flow: `_VERIFY_TERMINAL_RE = re.compile(r".*\bverify:\s*(?P<targets>[^.]+)")` @ `src/sac_engine.py:43`, aplicado em @ `src/sac_engine.py:146`. A classe `[^.]+` para no primeiro ponto e descarta o resto sem warning.
- Reproduzido: `verify: Cache.key, Adapter` → `['Cache']`, `warnings=[]`. `verify: CacheKey, Adapter.` → `['CacheKey','Adapter']` (ponto final funciona). `Se mudar X, entao Y. MUST verify: CacheKey` → `['CacheKey']` (ponto no meio da constraint funciona).
- Contrato declarado: a gramática normativa do SAC define alvos de `verify:` como tokens `[A-Za-z_][A-Za-z0-9_.$-]*` — **com** ponto. Parser e gramática declarada se contradizem, e hoje quem perde é o parser, em silêncio.
- Owner: `src/sac_engine.py`. Warnings canônicos hoje: `invalid_trigger`, `arch_imperative_required`, `regr_verify_required`, `deprecated_replacement_required`.
- Blast radius: `Cache.key`, `user.service`, `Order.validate`, métodos em JS/Dart/Kotlin, testes versionados (`test_charge.v2`).

## Semantic authority

- Must: a lista de alvos de `verify:` termina em `;` ou no fim da linha. Nunca no primeiro ponto.
- Must: cada alvo é validado individualmente contra `[A-Za-z_][A-Za-z0-9_.$-]*`.
- Must: alvo que não casa o token vira o warning canônico novo `invalid_verify_target`, nomeando o token rejeitado. Ele não entra na lista de alvos e **não** desaparece do resultado.
- Must: alvos válidos são preservados mesmo quando um alvo inválido está presente na mesma tag.
- Must not: aceitar narrativa como alvo; alterar a semântica de `verify:` (continua obrigação de revisão, não prova de teste); tocar `_is_covered` (é track_04); mudar o campo `trigger` (é track_02).
- Error behavior: nada é descartado em silêncio. Todo alvo lido da linha ou entra na lista, ou aparece como warning nomeado.

## Required approach

- Owner and boundary: `src/sac_engine.py` é o dono único do parsing de `verify:`. `sac_diff.py` consome a lista já parseada e não é tocado.
- Data/control flow: casar o prefixo `verify:` → capturar até `;` ou fim de linha → dividir por vírgula → normalizar espaço → validar token a token → alvos válidos na lista, inválidos em warning.
- Integration rule: `invalid_verify_target` segue a forma dos quatro warnings canônicos existentes.
- Executor latitude: mechanically equivalent details only

## Focus

- Likely writes: `src/sac_engine.py`, `tests/test_verify_parse.py`, `mcp/smoke.mjs`
- Essential reads: `src/sac_engine.py:43,146`
- Forbidden work: alterar `trigger`; tocar `sac_diff.py`; mudar serialização; endurecer outras regex
- Stop if: existir alvo alcançável que não caiba nem na lista nem no warning
- Depends on: none (primeira track do bloco; o Bloco 01 já está executado)

## DoD

1. `verify: Cache.key, Adapter` devolve `['Cache.key','Adapter']` e `warnings` vazio. | Proof: approved-test (`tests/test_verify_parse.py`)
2. `verify: CacheKey, Adapter.` e `Se mudar X, entao Y. MUST verify: CacheKey` continuam com o comportamento correto de hoje. | Proof: approved-test
3. `verify: 9bad, Good` devolve `['Good']` e um warning `invalid_verify_target` nomeando `9bad`. | Proof: approved-test
4. `verify: A; texto depois` devolve `['A']`. | Proof: approved-test
5. Para uma fixture com ponto no alvo, os alvos lidos da linha crua e os alvos do payload MCP são idênticos. | Proof: manual (caso novo em `mcp/smoke.mjs`)
6. Nenhuma tag existente deixa de ser parseada. | Proof: manual (`mcp/smoke.mjs` verde)

## Handoff

- File: .context/docs/pendentes/sac_public_extraction/bloco_02_melhoria_funcional/handoff.md
- Terminal: record `EXECUTED` + `APPROVED` after the executor checks every DoD item in this chat; then return the robust prompt for `track_02` in a new chat
