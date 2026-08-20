# Track 09 — Promessa honesta, política de vetos e release 0.1.0

[governance]
1. Deliver the goal and DoD literally; do not invent observable behavior.
2. Follow the required approach; choose only mechanically equivalent details.
3. Read only causal dependencies and record mechanically necessary unexpected writes.
4. Replan on any DoD, strategy or authority gap; do not replace it with insight, heuristic or a merely functional result.
5. No silent fallback, masked error, weak critical heuristic, TODO/stub, optional improvement or approval without literal evidence for every DoD item.
[/governance]

## Goal

O material público descreve exatamente o que o produto faz, a lista de vetos vira política publicada, e a tag `0.1.0` existe com `RELEASE_GATE.md` integralmente satisfeito.

## Context capsule

- Current flow: `_is_covered` @ `src/sac_diff.py:323` define cobertura como "um símbolo alterado tem o nome do alvo, ou o basename de um arquivo alterado é o alvo". Isso é *você editou algo com esse nome* — renomear uma variável dentro de `testChargeIdem` satisfaz o gate; escrever o teste certo com outro nome não satisfaz. Não é "o teste existe", não é "o teste passou", não é "o teste cobre o símbolo". É uma escolha defensável (lexical, stdlib-only, sem AST) que precisa ser **declarada como o que é**.
- Current flow: `_BASE_SCENARIOS = {"SUMMARY","EXTEND","REGRESSION"}` e `_OPTIONAL_SCENARIOS = {"MIGRATION"}` @ `src/sac_domains.py:36-38`; domínio sem cenário-base ⇒ `INVALID_CONTRACT` @ `src/sac_domains.py:225`. `_SCENARIO_REQUIRED_TAG_TYPE` @ `src/sac_engine.py:964-969` só pode mapear um cenário novo para `ARCH`, e criar tag de diagnóstico é vetado — logo uma claim de diagnóstico seria satisfeita pelas mesmas tags que já satisfazem `SUMMARY` e `EXTEND`: uma linha de manifesto a mais e zero requisito estrutural novo.
- Current flow: `RELEASE_GATE.md` foi criado no Bloco 01 com nove itens de caixa vazia, cada um apontando uma track deste bloco.
- Owner: `README.md`, `CHANGELOG.md`, `RELEASE_GATE.md`, `docs/`.

## Semantic authority

- Must: o README declara o gate como **co-edit gate**, dizendo explicitamente o que ele verifica (algo com o nome do alvo foi editado) e o que **não** verifica (existência do teste, execução do teste, cobertura do símbolo).
- Must: `DIAGNOSE` é documentado em `docs/` **apenas** como cenário de benchmark, com a justificativa de por que fica fora do schema. `_BASE_SCENARIOS` e `_OPTIONAL_SCENARIOS` não são tocados.
- Must: publicar a lista "Não implementar" como política do projeto, literalmente: code graph, AST como requisito, geração dinâmica de contexto pelo MCP, provenance no hot path, documentação causal paralela — acrescentando a permissão explícita de provenance **fora** do hot path (campo opcional fora do payload de Context, ou sinal derivado), que continua não implementada mas deixa de ser vetada.
- Must: `CHANGELOG.md` registra as mudanças de veredicto introduzidas pelo bloco — ordenação em `_is_covered` (track_04), alvos de `verify:` antes perdidos (track_01), e arquivos antes em `FAIL CLOSED` que passam a ser avaliados (track_05).
- Must: preencher cada item de `RELEASE_GATE.md` com a evidência citada da track que o resolveu.
- Must: criar a tag anotada `0.1.0`.
- Must not: criar a tag com qualquer item do gate pendente; usar "prevenção de regressão" ou "prova de teste" para descrever o gate; promover `DIAGNOSE` a cenário; implementar a harness de benchmark.
- Error behavior: item do gate sem evidência citada bloqueia a tag. Sem exceção.

## Required approach

- Owner and boundary: apenas documentação e tag. Nenhum arquivo de código é alterado nesta track.
- Data/control flow: verificar item a item do gate contra a evidência da track correspondente → preencher → escrever README/CHANGELOG/política → taguear.
- Integration rule: cada item preenchido do gate cita a track e o meio de prova que a track registrou no handoff.
- Executor latitude: mechanically equivalent details only

## Focus

- Likely writes: `README.md`, `CHANGELOG.md`, `RELEASE_GATE.md`, `docs/`
- Essential reads: `RELEASE_GATE.md`, `.context/docs/pendentes/sac_public_extraction/bloco_02_melhoria_funcional/handoff.md`, `src/sac_diff.py:323`, `src/sac_domains.py:36-38`
- Forbidden work: alterar código; implementar benchmark; publicar em registry; tocar cenários
- Stop if: algum item do gate não tiver evidência registrada no handoff
- Depends on: track_08

## DoD

1. Cada um dos nove itens de `RELEASE_GATE.md` está marcado com evidência citada, nomeando a track e o meio de prova. | Proof: inspect
2. O README descreve o gate como co-edit gate, com o que verifica e o que não verifica, e não contém "prevenção de regressão" nem "prova de teste" aplicados a ele. | Proof: inspect
3. `_BASE_SCENARIOS` e `_OPTIONAL_SCENARIOS` têm diff vazio em todo o bloco. | Proof: diff
4. `DIAGNOSE` aparece em `docs/` apenas como cenário de benchmark, e em nenhum ponto do código. | Proof: inspect
5. A lista "Não implementar" está publicada como política, com a permissão de provenance fora do hot path declarada. | Proof: inspect
6. `CHANGELOG.md` registra as três mudanças de veredicto. | Proof: inspect
7. `git tag` lista `0.1.0`, anotada, e nenhum item do gate está pendente. | Proof: inspect
8. Nenhum arquivo de código foi alterado nesta track. | Proof: diff

## Handoff

- File: .context/docs/pendentes/sac_public_extraction/bloco_02_melhoria_funcional/handoff.md
- Terminal: record `EXECUTED` + `APPROVED` after the executor checks every DoD item in this chat; then return the explicit release/tag operational handoff required by the DoD
