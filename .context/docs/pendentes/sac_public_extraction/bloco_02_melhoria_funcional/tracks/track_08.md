# Track 08 — Marcadores de comentário e idioma imperativo

[governance]
1. Deliver the goal and DoD literally; do not invent observable behavior.
2. Follow the required approach; choose only mechanically equivalent details.
3. Read only causal dependencies and record mechanically necessary unexpected writes.
4. Replan on any DoD, strategy or authority gap; do not replace it with insight, heuristic or a merely functional result.
5. No silent fallback, masked error, weak critical heuristic, TODO/stub, optional improvement or approval without literal evidence for every DoD item.
[/governance]

## Goal

Uma tag SAC pode ser escrita em qualquer linguagem cujo comentário comece com um prefixo não-alfanumérico curto, e uma constraint escrita em português deixa de disparar warning permanente.

## Context capsule

- Current flow: a gramática exige `//` ou `#` como marcador @ `src/sac_engine.py:20,24`. A verificação barata é `"SAC:" not in line` @ `src/sac_engine.py:215` e `:237`, com `re.search(r"SAC:([A-Za-z0-9_]+):", line)` @ `src/sac_engine.py:245`.
- Consequência: linguagens com `--` (SQL, Lua, Haskell), `%` (Erlang, LaTeX), `;` (Lisp, assembly), `<!-- -->` (HTML, XML, Markdown), `/* */` e `"""` não conseguem sequer **portar** uma tag. Para essas linguagens o agente sem ferramenta não tem linha nenhuma para ler.
- Current flow: `_ARCH_IMPERATIVE_RE = re.compile(r"\b(?:MUST|NEVER|ONLY)\b")` @ `src/sac_engine.py:107`. O template e a documentação escrevem constraints misturando português e inglês, então toda constraint em português dispara `arch_imperative_required` **permanentemente**.
- Owner: `src/sac_engine.py`.
- Contrato herdado: tag malformada continua parseável e emite warning, em vez de sumir.

## Semantic authority

- Must: o marcador deixa de ser whitelist. Passa a ser qualquer prefixo de comentário não-alfanumérico de **até 4 caracteres**, imediatamente antes de `SAC:`, ancorado após o espaço inicial da linha. Cobre `//`, `#`, `--`, `%`, `;`, `<!--`, `/*`, `"""`.
- Must: delimitador de fechamento presente na mesma linha (`-->`, `*/`, `"""`) é removido do fim da constraint **antes** do parsing, para não contaminar `verify:` nem `replacement:`.
- Must: `_ARCH_IMPERATIVE_RE` aceita `MUST|NEVER|ONLY|DEVE|NUNCA|SOMENTE|APENAS`.
- Must not: reconhecer `SAC:` que apareça dentro de literal de string com prefixo alfanumérico ou com mais de 4 caracteres não-alfanuméricos antes; afrouxar a exigência de imperativo (ela continua valendo, só ganha um segundo idioma); criar tag nova; alterar `verify:` (track_01) ou `on=` (track_02).
- Error behavior: falso positivo é evitado por restrição de forma, não por heurística de contexto. Se a linha não casar a forma, ela simplesmente não é tag — sem warning, como hoje.

## Required approach

- Owner and boundary: `src/sac_engine.py` é o dono do reconhecimento de marcador e do vocabulário imperativo.
- Data/control flow: espaço inicial → até 4 caracteres não-alfanuméricos → `SAC:` → resto da gramática → remoção do delimitador de fechamento → parsing dos campos.
- Integration rule: substituir a whitelist, não estendê-la. O resultado é uma regra a menos, não mais entradas.
- Executor latitude: mechanically equivalent details only

## Focus

- Likely writes: `src/sac_engine.py`, `tests/test_markers.py`
- Essential reads: `src/sac_engine.py:20,24,107,215,237,245`
- Forbidden work: tocar `_SYMBOL_REGISTRY` (é track_05); alterar fitness; mexer em payload
- Stop if: a restrição de forma não bastar para evitar falso positivo em literal de string
- Depends on: track_07

## DoD

1. Tag reconhecida em fixture com `--`, `%`, `;`, `<!-- -->`, `/* */` e `"""`. | Proof: approved-test (`tests/test_markers.py`)
2. `// ` e `# ` continuam reconhecidos exatamente como hoje. | Proof: approved-test
3. Uma linha com `"SAC:ARCH: ..."` dentro de literal de string **não** é reconhecida como tag, e uma tag real na mesma fixture é. | Proof: approved-test
4. Em `<!-- SAC:REGR: ... verify: A, B -->`, os alvos são `['A','B']` e o `-->` não aparece em nenhum campo. | Proof: approved-test
5. Constraint em português com `DEVE` não dispara `arch_imperative_required`; constraint sem nenhum imperativo continua disparando. | Proof: approved-test
6. `mcp/smoke.mjs` verde. | Proof: manual

## Handoff

- File: .context/docs/pendentes/sac_public_extraction/bloco_02_melhoria_funcional/handoff.md
- Terminal: record `EXECUTED` + `APPROVED` after the executor checks every DoD item in this chat; then return the robust prompt for `track_09` in a new chat
