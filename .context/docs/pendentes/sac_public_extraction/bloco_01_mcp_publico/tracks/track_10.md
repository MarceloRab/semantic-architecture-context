# Track 10 — 0.1.0-rc e porta de release

[governance]
1. Deliver the goal and DoD literally; do not invent observable behavior.
2. Follow the required approach; choose only mechanically equivalent details.
3. Read only causal dependencies and record mechanically necessary unexpected writes.
4. Replan on any DoD, strategy or authority gap; do not replace it with insight, heuristic or a merely functional result.
5. No silent fallback, masked error, weak critical heuristic, TODO/stub, optional improvement or self-certification.
[/governance]

## Goal

O repositório está em `0.1.0-rc` com uma porta de release explícita: `RELEASE_GATE.md` enumera nominalmente o que falta para a tag pública `0.1.0`, e o README não promete o que o produto ainda não entrega.

## Context capsule

- Current flow: o `diff-check` define cobertura como "um símbolo alterado tem o nome do alvo, ou o basename de um arquivo alterado é o alvo" @ `src/sac_diff.py:323`. Isso é *você editou algo com esse nome* — não é "o teste existe", não é "o teste passou", não é "o teste cobre o símbolo".
- Current flow: `_SYMBOL_REGISTRY` @ `src/sac_diff.py:36` tem duas entradas, `.dart` e `.ps1`; extensão fora do registro com tag SAC ⇒ `FAIL CLOSED` @ `src/sac_diff.py:392`.
- Current flow: o veredicto do gate depende hoje da ordem alfabética dos caminhos (`src/sac_diff.py:415-427`), e `verify:` trunca no primeiro ponto (`src/sac_engine.py:43`).
- Owner: `RELEASE_GATE.md` na raiz é a porta única para a tag `0.1.0`.

## Semantic authority

- Must: `RELEASE_GATE.md` enumera nominalmente os itens do Bloco 02 que liberam `0.1.0`, cada um rastreável a uma track daquele bloco: truncamento de `verify:`; campo `on=`; porta de entrada em `AGENTS.md` e camada de atalho; ordenação em `_is_covered`; registro de linguagens e dogfooding; path relativo e unidade de bytes; numerador de `OVER_SELECT` e piso de anchors; marcadores e idioma imperativo; promessa honesta.
- Must: o README declara, sem eufemismo, que o gate é um **co-edit gate** — verifica que algo com o nome do alvo foi editado — e lista `.dart` e `.ps1` como as linguagens suportadas hoje, como limitação corrente conhecida.
- Must: `CHANGELOG.md` existe e registra a `0.1.0-rc`.
- Must: a tag criada é `0.1.0-rc`, anotada.
- Must not: criar a tag `0.1.0`. Ela é ato da última track do Bloco 02.
- Must not: descrever o gate como "prevenção de regressão", "prova de teste" ou equivalente.
- Error behavior: se algum item do gate não for rastreável a uma track do Bloco 02, parar e reportar.

## Required approach

- Owner and boundary: `RELEASE_GATE.md`, `README.md`, `CHANGELOG.md`. Nenhum código é tocado.
- Data/control flow: enumerar item → apontar a track do Bloco 02 que o resolve → declarar o critério de satisfação → tag `0.1.0-rc`.
- Integration rule: cada item do gate é uma linha com caixa de verificação vazia; o Bloco 02 as preenche com evidência citada.
- Executor latitude: mechanically equivalent details only

## Focus

- Likely writes: `RELEASE_GATE.md`, `README.md`, `CHANGELOG.md`
- Essential reads: `src/sac_diff.py:36,323,392`, `.context/docs/pendentes/sac_public_extraction/bloco_02_melhoria_funcional/tracks/`
- Forbidden work: corrigir qualquer defeito funcional; criar tag `0.1.0`; publicar em registry
- Stop if: um item do gate não tiver track correspondente no Bloco 02
- Depends on: track_09

## DoD

1. `RELEASE_GATE.md` lista os nove itens acima, cada um apontando a track do Bloco 02 que o resolve, com caixa de verificação vazia. | Proof: inspect
2. O README descreve o gate como co-edit gate e lista `.dart` e `.ps1` como limitação corrente. | Proof: inspect
3. O README não contém as expressões "prevenção de regressão", "prova de teste" ou equivalente aplicadas ao gate. | Proof: inspect
4. `git tag` lista `0.1.0-rc` e **não** lista `0.1.0`. | Proof: inspect
5. Nenhum arquivo de código foi alterado nesta track. | Proof: diff

## Handoff

- File: .context/docs/pendentes/sac_public_extraction/bloco_01_mcp_publico/handoff.md
- Terminal: `EXECUTED`; review requires a separate manual trigger
