# Track 07 — Fim da taxa de densidade e piso de anchors visível

[governance]
1. Deliver the goal and DoD literally; do not invent observable behavior.
2. Follow the required approach; choose only mechanically equivalent details.
3. Read only causal dependencies and record mechanically necessary unexpected writes.
4. Replan on any DoD, strategy or authority gap; do not replace it with insight, heuristic or a merely functional result.
5. No silent fallback, masked error, weak critical heuristic, TODO/stub, optional improvement or self-certification.
[/governance]

## Goal

Adicionar uma REGR a um domínio deixa de exigir uma claim nova para ele permanecer `FIT`, e o piso rígido de anchors passa a ser visível em vez de descoberto por FAIL.

## Context capsule

- Current flow: `_context_selected_keys` @ `src/sac_engine.py:971-985` seleciona uma tag se `tag.symbol in anchors` **ou** `tag.tag_type in {"REGR","DEPRECATED"}` — ou seja, toda REGR e toda DEPRECATED entram **automaticamente**, por política, não por escolha do anchor.
- Current flow: `uncontracted_context_count = max(0, len(context_selected) - contracted_in_context)` @ `src/sac_engine.py:1037`; qualquer excedente ⇒ `OVER_SELECT`. Combinado com a inclusão automática, **cada REGR nova exige uma claim nova** para o domínio não sair de `FIT`, e o manifesto cresce linearmente com o número de tags. O contrato de capillarity taxa a densidade semântica.
- Current flow: `context_unfit_claims` @ `src/sac_engine.py:1019-1027` — claim casada cujo alvo não está em `context_selected` ⇒ `UNFIT`. Combinado com a seleção por anchor, **toda claim ARCH obriga que seu símbolo seja anchor**. Não é recomendação: é condição de PASS. O menor conjunto possível de anchors tem, portanto, um piso rígido — o conjunto de símbolos das claims ARCH.
- Current flow: `missing_roles` / `uncovered_scenarios` ⇒ `TOO_THIN` @ `src/sac_engine.py:1039`, calculado sobre `_SCENARIO_REQUIRED_TAG_TYPE` @ `src/sac_engine.py:964-969`.
- Owner: `_evaluate_context_fitness` @ `src/sac_engine.py:988`.

## Semantic authority

- Must: `uncontracted_context_count` passa a contar **apenas** tags que entraram em `context_selected` por `symbol ∈ anchors`. Tags incluídas pela política `tag_type ∈ {REGR, DEPRECATED}` saem do numerador.
- Must: uma tag ARCH arrastada por anchor **sem** claim correspondente continua contando e continua produzindo `OVER_SELECT`.
- Must: a exigência de claim de papel `REGRESSION:REGR` permanece intacta; domínio sem ela continua `TOO_THIN`.
- Must: `context_unfit_claims` e `UNFIT` permanecem com a semântica de hoje.
- Must: `assess` passa a reportar o **piso de anchors** — o conjunto de símbolos das claims ARCH — junto com o excedente atual.
- Must: `templates/domains.template.md` documenta o piso: minimizar anchors exige minimizar antes as claims ARCH.
- Must not: alterar `_SCENARIO_REQUIRED_TAG_TYPE`; adicionar cenário; mudar o schema de claims de 5 colunas; permitir claim multi-símbolo; afrouxar `TOO_THIN` ou `UNFIT`.
- Error behavior: nenhum domínio existente pode piorar de veredicto por causa desta track.

## Required approach

- Owner and boundary: `_context_selected_keys` passa a distinguir a **origem** da seleção (anchor vs política); `_evaluate_context_fitness` consome essa distinção apenas no numerador de `uncontracted_context_count`.
- Data/control flow: seleção com origem → `context_unfit_claims` sobre o conjunto completo (inalterado) → `contracted_in_context` sobre o conjunto completo (inalterado) → numerador restrito às tags de origem anchor.
- Integration rule: o conjunto `context_selected` que o Context monta e entrega ao agente **não muda**. Muda apenas como o fitness o pontua.
- Executor latitude: mechanically equivalent details only

## Focus

- Likely writes: `src/sac_engine.py`, `tests/test_fitness.py`, `templates/domains.template.md`
- Essential reads: `src/sac_engine.py:964-969,971-985,988,1019-1027,1037,1039`
- Forbidden work: tocar `_BASE_SCENARIOS`/`_OPTIONAL_SCENARIOS`; alterar o payload do Context; mexer em gramática ou gate
- Stop if: a origem da seleção não puder ser determinada sem ambiguidade para alguma tag
- Depends on: track_06

## DoD

1. Adicionar uma REGR a um domínio `FIT`, sem adicionar claim, mantém o domínio `FIT`. | Proof: approved-test (`tests/test_fitness.py`)
2. Uma tag ARCH arrastada por anchor sem claim continua produzindo `OVER_SELECT`. | Proof: approved-test
3. Domínio sem claim de papel `REGRESSION:REGR` continua `TOO_THIN`. | Proof: approved-test
4. Claim ARCH cujo símbolo não é anchor continua produzindo `UNFIT`. | Proof: approved-test
5. `assess` reporta o piso de anchors e o excedente, e o piso corresponde aos símbolos das claims ARCH do domínio. | Proof: manual
6. O payload entregue por `get_sac_context` tem diff vazio para uma fixture inalterada. | Proof: manual
7. Nenhum domínio do próprio repositório piorou de veredicto. | Proof: manual (assess antes/depois)

## Handoff

- File: .context/docs/pendentes/sac_public_extraction/bloco_02_melhoria_funcional/handoff.md
- Terminal: `EXECUTED`; review requires a separate manual trigger
