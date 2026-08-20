# Track 04 — `_is_covered` avalia contra o conjunto completo

[governance]
1. Deliver the goal and DoD literally; do not invent observable behavior.
2. Follow the required approach; choose only mechanically equivalent details.
3. Read only causal dependencies and record mechanically necessary unexpected writes.
4. Replan on any DoD, strategy or authority gap; do not replace it with insight, heuristic or a merely functional result.
5. No silent fallback, masked error, weak critical heuristic, TODO/stub, optional improvement or approval without literal evidence for every DoD item.
[/governance]

## Goal

O veredicto do `diff-check` é idêntico para mudanças logicamente idênticas, independentemente da ordem alfabética dos caminhos alterados.

## Context capsule

- Current flow: `_is_covered(target, changed_symbols, changed_files)` @ `src/sac_diff.py:323` — cobertura ocorre quando (a) um símbolo alterado tem exatamente o nome do alvo, ou (b) o basename sem extensão de um arquivo alterado é o alvo.
- Current flow: no laço @ `src/sac_diff.py:415-427`, `changed_symbols.append(changed)` acontece **dentro do mesmo laço** que em seguida chama `lookup()` e avalia `verify:` contra `changed_symbols`. Logo símbolos de arquivos processados depois ainda não existem quando o alvo é verificado. `changed_files` é completo desde o início; `changed_symbols` não é.
- Reproduzido: alvo `testChargeIdem` definido em `test/pay_test.dart` ⇒ exit 1, `uncovered: testChargeIdem`, **mesmo com o símbolo presente na lista impressa**. O mesmo alvo movido para `aaa/pay_test.dart` ⇒ exit 0.
- Causa: `git diff` ordena por caminho; fonte fica em `lib/`, `src/`, `app/` e teste em `test/`, `tests/`, então a fonte é sempre processada antes. Para o layout convencional, o alvo `verify:` que aponta para um teste é **sistematicamente** marcado não coberto — e `verify:` existe justamente para apontar testes.
- Efeito comportamental: a única saída é `SAC-ACK: <symbol>` no corpo da PR, ou seja, o gate ensina o desenvolvedor a escrever o bypass em toda PR.
- Owner: `src/sac_diff.py`.

## Semantic authority

- Must: separar o laço único em dois — primeiro montar `changed_symbols` e `changed_files` **completos** para todos os arquivos alterados, depois avaliar violações.
- Must: `_is_covered` mantém exatamente a mesma definição de cobertura (a) e (b). Nenhuma regra nova.
- Must: o mecanismo `SAC-ACK` permanece intacto como saída explícita e auditável.
- Must: registrar no `CHANGELOG` que o veredicto do gate muda — PRs que passavam por alvo não visto podem passar a falhar. Isso é o comportamento correto e desejado.
- Must not: alterar a definição de cobertura; introduzir AST; introduzir ordenação artificial de arquivos; suprimir violação recém-exposta; tocar `verify:` (track_01) ou `_SYMBOL_REGISTRY` (track_05).
- Error behavior: violação real recém-exposta é reportada, nunca suprimida nem convertida em warning.

## Required approach

- Owner and boundary: `src/sac_diff.py` é o dono. `sac_engine.lookup` é consumido sem alteração.
- Data/control flow: laço 1 — para cada arquivo alterado, extrair símbolos e acumular em `changed_symbols` e `changed_files`. Laço 2 — para cada arquivo alterado, `lookup()`, filtrar REGR, avaliar cada alvo `verify:` contra os conjuntos já completos, aplicar ACK, acumular violações.
- Integration rule: a chamada a `lookup()` e a filtragem por `tag_type != "REGR"` permanecem como estão.
- Executor latitude: mechanically equivalent details only

## Focus

- Likely writes: `src/sac_diff.py`, `tests/test_is_covered.py`
- Essential reads: `src/sac_diff.py:323,415-427`
- Forbidden work: mexer em `_SYMBOL_REGISTRY`; alterar `FAIL CLOSED`; tocar `_is_covered` na definição; alterar `sac_engine.py`
- Stop if: a separação em dois laços exigir mudar a semântica de cobertura
- Depends on: track_03

## DoD

1. Alvo definido em `test/pay_test.dart` e o mesmo alvo em `aaa/pay_test.dart` produzem veredicto **idêntico**. | Proof: approved-test (`tests/test_is_covered.py`)
2. O caso original reproduzido (fonte em `lib/`, teste em `test/`, ambos alterados na mesma mudança) passa a sair com exit 0. | Proof: manual (fixture git, saída registrada)
3. Uma REGR cujo alvo `verify:` **não** foi tocado continua sendo violação com exit 1. | Proof: approved-test
4. `SAC-ACK: <symbol>` continua liberando exatamente o símbolo nomeado. | Proof: approved-test
5. A definição de cobertura em `_is_covered` tem diff vazio nas regras (a) e (b). | Proof: diff
6. `CHANGELOG.md` registra a mudança de veredicto como breaking de comportamento do gate. | Proof: inspect

## Handoff

- File: .context/docs/pendentes/sac_public_extraction/bloco_02_melhoria_funcional/handoff.md
- Terminal: record `EXECUTED` + `APPROVED` after the executor checks every DoD item in this chat; then return the robust prompt for `track_05` in a new chat
