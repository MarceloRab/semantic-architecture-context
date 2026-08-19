# Track 05 — Registro de linguagens e dogfooding real

[governance]
1. Deliver the goal and DoD literally; do not invent observable behavior.
2. Follow the required approach; choose only mechanically equivalent details.
3. Read only causal dependencies and record mechanically necessary unexpected writes.
4. Replan on any DoD, strategy or authority gap; do not replace it with insight, heuristic or a merely functional result.
5. No silent fallback, masked error, weak critical heuristic, TODO/stub, optional improvement or self-certification.
[/governance]

## Goal

O `diff-check` roda em Python, JS/TS e Go além de Dart e PowerShell, e o repositório SAC passa a proteger a si mesmo: uma PR com REGR não coberta deixa a CI do próprio repositório vermelha.

## Context capsule

- Current flow: `_SYMBOL_REGISTRY: dict[str, list[re.Pattern]]` @ `src/sac_diff.py:36` tem exatamente duas entradas — `.dart` (classe/extension/enum/mixin e membros de topo por tipo de retorno) e `.ps1` (`function Foo`, `$foo =`). Cada entrada é uma lista de regex com grupo nomeado `symbol`.
- Current flow: extensão fora do registro **e** arquivo com tag SAC ⇒ `FAIL CLOSED` @ `src/sac_diff.py:392`.
- Consequência verificada: o engine do SAC é Python e o gate não roda em Python, logo o SAC não consegue proteger a si mesmo — o dogfooding não é trabalho pendente, é impossível no código atual. Para qualquer consumidor fora de Flutter/PowerShell o pilar 2 tem só dois estados: desligado (sem tags) ou bloqueando tudo (com tags).
- Evidência de campo (consumidores reais do SAC, verificada): `api_robot` escreve tags SAC em arquivos **`.py`** (`backend/app_v3/**`); `to_de_plantao` escreve em **`.dart`** e em **`.ts`** (`supabase/functions/**`). Das três linguagens realmente em uso, só `.dart` está registrada — `.py` e `.ts` produzem `FAIL CLOSED` hoje. Esses projetos **não** são tocados por esta track; a evidência serve apenas para justificar a lista escolhida.
- Contrato herdado: enforcement é lexical, stdlib-only, sem AST.
- Owner: `src/sac_diff.py`; a matriz de compatibilidade vive em `README.md`.

## Semantic authority

- Must: registrar `.py`, `.js`, `.jsx`, `.ts`, `.tsx`, `.go`, mantendo `.dart` e `.ps1` inalterados.
- Must: cada entrada nova segue a forma existente — lista de `re.Pattern` com grupo nomeado `symbol`, regex simples e lexical.
- Must: `FAIL CLOSED` para extensão não registrada com tag SAC é **preservado**.
- Must: publicar a lista de linguagens no `README.md` como dimensão de primeira classe da matriz de compatibilidade.
- Must: ligar o job `diff-check` na CI do próprio repositório, bloqueante.
- Must not: introduzir AST; usar parser de terceiros; tornar o job não-bloqueante; silenciar extensão não registrada; alterar `_is_covered` (é track_04); registrar linguagem sem fixture.
- Error behavior: extensão não registrada com tag SAC continua falhando fechado, nomeando o arquivo.

## Required approach

- Owner and boundary: `_SYMBOL_REGISTRY` é o dono único do reconhecimento de símbolo por linguagem.
- Data/control flow: extensão do arquivo → lista de regex → primeiro grupo `symbol` que casar na linha.
- Integration rule: cada linguagem entra acompanhada de duas fixtures — uma com declarações que **devem** casar e uma com linhas que **não** devem casar (chamada de função, comentário, string, import).
- Executor latitude: mechanically equivalent details only

## Focus

- Likely writes: `src/sac_diff.py`, `tests/test_symbol_registry.py`, `.github/workflows/ci.yml`, `README.md`
- Essential reads: `src/sac_diff.py:36,392`
- Forbidden work: alterar cobertura; tocar `sac_engine.py`; ampliar marcador de comentário (é track_08); tocar `api_robot`, `to_de_plantao` ou `rabelo-standards`
- Stop if: uma linguagem não puder ser reconhecida de forma lexical sem heurística
- Depends on: track_04

## DoD

1. Para cada uma das seis extensões novas, a fixture positiva tem todos os símbolos reconhecidos e a fixture negativa tem **zero** falsos positivos. | Proof: approved-test (`tests/test_symbol_registry.py`)
2. `.dart` e `.ps1` continuam com o comportamento de hoje. | Proof: approved-test
3. Arquivo em extensão fora do registro com tag SAC continua produzindo `FAIL CLOSED` com exit 1, nomeando o arquivo. | Proof: manual
4. Uma PR no próprio repositório com uma REGR não coberta deixa a CI **vermelha**. | Proof: manual (link da execução)
5. A mesma PR com o alvo `verify:` tocado deixa a CI verde. | Proof: manual
6. Nenhum job usa `continue-on-error`; o `diff-check` é bloqueante. | Proof: inspect
7. `README.md` lista as oito linguagens como dimensão da matriz de compatibilidade. | Proof: inspect

## Handoff

- File: .context/docs/pendentes/sac_public_extraction/bloco_02_melhoria_funcional/handoff.md
- Terminal: `EXECUTED`; review requires a separate manual trigger
