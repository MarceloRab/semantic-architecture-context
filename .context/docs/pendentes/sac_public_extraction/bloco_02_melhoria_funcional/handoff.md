# Handoff — Bloco 02: melhoria funcional da feature

## Plan

- Design: .context/docs/pendentes/sac_public_extraction/bloco_02_melhoria_funcional/design.md
- Approved by: usuário, 2026-08-19 — autorização explícita para ativar o builder
- Current: track_08

## Tracks

| Track | Goal | Depends on | Status | Attempt |
| --- | --- | --- | --- | --- |
| track_01 | verify: termina em `;` ou fim de linha; nenhum alvo descartado em silêncio | none | APPROVED | 1 |
| track_02 | Campo `on=` com vocabulário fechado para ARCH e parser dual para tags legadas | track_01 | APPROVED | 1 |
| track_03 | AGENTS.md como porta de entrada e camada de atalho de dois níveis nas três skills | track_02 | APPROVED | 1 |
| track_04 | `_is_covered` avalia contra o conjunto completo; veredicto independente da ordem de caminhos | track_03 | APPROVED | 1 |
| track_05 | Registro de linguagens com Python, JS/TS e Go, e dogfooding bloqueante na CI | track_04 | APPROVED | 2 |
| track_06 | file relativo, `_perf.sac_root` removido, orçamento e payload_bytes na unidade emitida | track_05 | APPROVED | 1 |
| track_07 | OVER_SELECT deixa de contar tags auto-incluídas; piso de anchors reportado pelo assess | track_06 | APPROVED | 1 |
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

### track_02 — Attempt 1 — 2026-08-20 — EXECUTED + APPROVED

- Outcome: a forma canônica agora usa `on=<condition>`; ARCH valida o vocabulário fechado `ssot|boundary|ordering|state|exclusive|ownership`, REGR/DEPRECATED validam `[a-z][a-z0-9_]{2,47}`, valores inválidos continuam visíveis com `invalid_trigger`, e o parser dual preserva as formas legadas com condição vazia e `legacy_trigger`. ADR, template, três skills públicas, documentação causal e smoke foram atualizados sem alterar o parsing de `verify:` da Track 01.
- DoD 1: `python3 -m unittest tests/test_trigger_on.py -v` passou; `test_complete_legacy_matrix` reproduziu RULE e CONSTRAINT de ARCH, WARNING e CRITICAL de REGR e WARNING e CRITICAL de DEPRECATED, comprovando condição vazia, `legacy_trigger`, símbolo/constraint/verify/replacement preservados; `test_legacy_deprecated_still_requires_replacement` comprovou `deprecated_replacement_required`; `test_legacy_regr_if_modifying_form_remains_visible` comprovou a forma REGR legada adicional.
- DoD 2: o mesmo comando passou; `test_legacy_and_new_tags_coexist_without_loss` escaneou uma fixture única com tag legada e tag `on=`, obteve os dois símbolos na ordem, condição `['', 'ssot']` e exatamente um warning `legacy_trigger`.
- DoD 3: o mesmo comando passou; `test_arch_ssot_is_accepted` aceitou `on=ssot` sem warning, e `test_invalid_arch_condition_lists_exact_closed_vocabulary` manteve a tag e comparou literalmente `allowed=ssot|boundary|ordering|state|exclusive|ownership` e a tupla completa permitida.
- DoD 4: o mesmo comando passou; `test_regr_snake_case_condition_is_accepted` aceitou `on=normalization_order`, e `test_invalid_regr_condition_keeps_tag` preservou símbolo, condição e verify de `on=X` com o warning literal do padrão `[a-z][a-z0-9_]{2,47}`.
- DoD 5: `python3 - <<'PY' ...` comparou as linhas equivalentes `# SAC:ARCH: CONSTRAINT - Sym: MUST preserve behavior` e `# SAC:ARCH: on=ssot - Sym: MUST preserve behavior`, imprimiu `legacy=52 new=49 new_not_longer=True` e fez assert da desigualdade; `test_new_line_is_not_longer_than_legacy_equivalent` repetiu a prova no teste aprovado.
- DoD 6: `git diff -U0 -- src | rg '^[+-][^+-].*(_KNOWN_TAGS|_BASE_SCENARIOS|_OPTIONAL_SCENARIOS)'` não encontrou qualquer linha adicionada/removida e o gate imprimiu `forbidden_constant_diff=empty`.
- DoD 7: `rg -n 'Decisão|ssot.*boundary.*ordering.*state.*exclusive.*ownership|Compatibilidade|legacy_trigger' docs/adr/0001-sac-on-condition.md` comprovou a ADR, a decisão, o vocabulário fechado completo e a política de compatibilidade.
- Regressão e gates: `python3 -m unittest tests/test_verify_parse.py -v`, `node mcp/smoke.mjs`, `python3 .github/scripts/check_hygiene.py` e `git diff --check` passaram. Inspeção programática comparando `HEAD:src/sac_engine.py` ao worktree imprimiu `track_01_verify_regex_and_parser_diff=empty` para `_VERIFY_TERMINAL_RE`, `_VERIFY_TARGET_RE` e `_parse_verify`.
- Terminal: `EXECUTED` após implementação e execução das provas; `APPROVED` após checagem literal, neste mesmo chat, dos sete itens numerados acima.

### track_03 — Attempt 1 — 2026-08-20 — EXECUTED + APPROVED

- Outcome: `AGENTS.md` agora é a porta tool-neutral para o manifesto, a gramática em três linhas, o limite de busca de `files:`, a CLI sem MCP e os três atalhos disjuntos. Cada skill tem um `PROMPT.md` curto que aponta diretamente ao `SKILL.md`, traz no topo o bloco sem MCP e contém a tabela frase→contrato; o conteúdo exclusivo de `prompt_resumido.md` foi absorvido antes de sua remoção. A overlay ficou com numeração única e apenas o pipeline completo.
- DoD 1: a leitura dirigida `sed -n '1,120p' AGENTS.md` indicou `.sac/domains.md`; `sed -n '1,120p' .sac/domains.md` identificou `sac_core`; e o comando publicado `python3 src/sac_scan.py context --root . --domain sac_core --json`, validado por Python, imprimiu `manual_route=PASS domain=sac_core constraints_field=present selected_count=0`, comprovando o caminho completo sem MCP a partir somente da porta.
- DoD 2: `rg -n 'files:.*limite de busca, não fila de leitura' AGENTS.md` encontrou literalmente a afirmação na linha 11.
- DoD 3: `test ! -e skills/sac-onboard/prompt_resumido.md` passou; uma comparação de cada linha não vazia de `git show HEAD:skills/sac-onboard/prompt_resumido.md` contra o novo `skills/sac-onboard/PROMPT.md` imprimiu `absorbed_nonempty_lines=19 missing=0`; `git diff -- skills/sac-onboard` mostrou a remoção e a absorção no atalho.
- DoD 4: a inspeção em loop dos três paths `skills/{sac-context,sac-onboard,sac-execution-overlay}/PROMPT.md` comprovou `prompt=present no_mcp=top phrase_contract=present` para cada skill.
- DoD 5: inspeção Python de `skills/sac-execution-overlay/PROMPT.md` imprimiu `numbering=unique numbers=['1', '2', '3', '4'] pipeline_count=1 pipeline=complete` e comparou literalmente `boot → Route → Context ou bounded-unmapped → Verify/Discover → Capillarity(on-demand) → Gate`.
- DoD 6: inspeção dos três prompts e de `AGENTS.md` confirmou três literais e três destinos distintos (`SAC`, `SAC ONBOARD <id>`, `SAC TAG`), nenhum Write autorizado por atalho, e apenas `APROVAR SAC REGISTER <id>` / `APROVAR SAC TAG_DELTA <id>` como autorizações condicionadas ao contrato.
- Regressão e gates: `python3 -m unittest tests/test_trigger_on.py -v`, `python3 -m unittest tests/test_verify_parse.py -v`, `node mcp/smoke.mjs`, `python3 .github/scripts/check_hygiene.py` e `git diff --check` passaram. `test -z "$(git diff -- src)"` imprimiu `engine_diff_empty`, comprovando nenhuma alteração no parsing de `verify:`, em `on=`, no vocabulário fechado, nas validações ou na compatibilidade legada.
- Terminal: `EXECUTED` após implementação e execução das provas; `APPROVED` após checagem literal, neste mesmo chat, dos seis itens numerados acima.

### track_04 — Attempt 1 — 2026-08-20 — EXECUTED + APPROVED

- Outcome: `diff-check` agora conclui a coleta de símbolos de todos os arquivos alterados antes de executar `lookup()`, filtrar REGR e avaliar `verify:`. `_is_covered`, as duas regras de cobertura e o mecanismo `SAC-ACK` permaneceram byte a byte inalterados; o `CHANGELOG` registra a mudança de veredicto como breaking do gate.
- DoD 1: `python3 -m unittest tests/test_is_covered.py -v` passou; `test_test_and_aaa_path_orders_have_identical_verdicts` executou o mesmo alvo em `test/pay_test.dart` e `aaa/pay_test.dart` e comparou literalmente os veredictos `[0, 0]`.
- DoD 2: a fixture Git manual (`tmp=$(mktemp -d); git -C "$tmp" init -q; ...; python3 src/sac_diff.py --root "$tmp" --base HEAD^`) criou fonte alterada em `lib/pay.dart` e teste alterado em `test/pay_test.dart`; a saída registrou `SAC diff-check: exit 0`, os símbolos `lib/pay.dart:charge` e `test/pay_test.dart:testChargeIdem`, e `manual_fixture_exit=0`.
- DoD 3: o approved-test `test_untouched_verify_target_remains_a_violation` comprovou alvo `testNotChanged` não tocado, `uncovered == ["testNotChanged"]` e exit 1.
- DoD 4: o approved-test `test_ack_releases_exactly_the_named_symbol` forneceu `SAC-ACK: charge`, comprovou ACK reconhecido exatamente como `["charge"]` e manteve somente a violação de `refund`, com exit 1.
- DoD 5: inspeção AST entre `HEAD:src/sac_diff.py` e o worktree imprimiu `_is_covered_diff=empty`; `git diff -U0 HEAD -- src/sac_diff.py` mostrou hunks somente no laço de `diff_check`, sem qualquer mudança nas regras (a) e (b). A mesma inspeção imprimiu `_extract_acks_diff=empty` e `_gather_acks_diff=empty`.
- DoD 6: inspeção literal de `CHANGELOG.md` confirmou a seção `Breaking` e o registro de que a avaliação após o conjunto completo muda o comportamento do gate, podendo expor violações reais antes ocultas pela ordem.
- Regressão e gates: `python3 -m unittest discover -s tests -v`, `python3 -m unittest tests/test_verify_parse.py -v`, `python3 -m unittest tests/test_trigger_on.py -v`, `node mcp/smoke.mjs`, `python3 .github/scripts/check_hygiene.py`, `python3 .github/scripts/check_version.py`, `python3 src/sac_scan.py validate --root .`, `python3 src/sac_scan.py index-build --root .` e `git diff --check` passaram. O smoke completo terminou com `[OK] smoke exit 0`.
- Terminal: `EXECUTED` após implementação e execução das provas; `APPROVED` após checagem literal, neste mesmo chat, dos seis itens numerados acima.

### track_05 — Attempt 1 — 2026-08-20 — EXECUTED + CHANGES_REQUIRED

- Outcome: o registro lexical agora inclui `.py`, `.js`, `.jsx`, `.ts`, `.tsx` e `.go` sem alterar `.dart` ou `.ps1`; a matriz no README publica as oito extensões e a CI contém um job de PR bloqueante para o `diff-check`. O ambiente desta execução não possui remote Git nem cria uma execução real do GitHub Actions; por isso os links de execução exigidos pelos itens 4 e 5 não puderam ser produzidos e a track não foi aprovada.
- DoD 1: `python3 -m unittest tests/test_symbol_registry.py -v` passou; `test_positive_fixtures_recognize_every_declared_symbol` percorreu as seis fixtures positivas e `test_negative_fixtures_have_zero_false_positives` comprovou zero casamento para chamada, comentário, string e import em cada extensão.
- DoD 2: o mesmo approved-test passou; `test_existing_dart_and_powershell_behavior` comprovou os reconhecimentos preexistentes de classe/função Dart e função/variável PowerShell, e o diff manteve literalmente as entradas `.dart` e `.ps1`.
- DoD 3: a fixture manual Python criou `guard.rb` com tag SAC, executou `diff_check`, obteve `exit=1 file=guard.rb` e confirmou o nome do arquivo em `unknown_language_files`.
- DoD 4: a fixture manual Python comprovou localmente `uncovered_exit=1 uncovered=['engine_test']`, e a inspeção confirmou o job de PR; faltou, porém, o link de uma execução real vermelha solicitado pelo item.
- DoD 5: a mesma fixture adicionou a declaração de `engine_test`, obteve `covered_exit=0 changed=['engine', 'engine_test']` e comprovou localmente o veredicto verde; faltou, porém, o link de uma execução real verde solicitado pelo item.
- DoD 6: `rg -n 'continue-on-error' .github/workflows` não encontrou ocorrências e imprimiu `continue-on-error=absent`; a inspeção de `.github/workflows/ci.yml` confirmou que `Run blocking SAC diff-check` propaga diretamente o exit do comando, sem mascaramento.
- DoD 7: a inspeção de `README.md` confirmou a tabela de primeira classe com Python, JavaScript, JavaScript com JSX, TypeScript, TypeScript com JSX, Go, Dart e PowerShell e suas oito extensões registradas.
- Regressão e gates: `python3 -m unittest discover -s tests -v`, `node mcp/smoke.mjs`, `python3 .github/scripts/check_hygiene.py`, `python3 .github/scripts/check_version.py`, `python3 src/sac_scan.py validate --root .`, `python3 src/sac_scan.py index-build --root .` e `git diff --check` passaram. A inspeção AST contra `HEAD` imprimiu `_is_covered_unchanged=True`, `_extract_acks_unchanged=True`, `_gather_acks_unchanged=True` e `diff_check_unchanged=True`; `git diff -- AGENTS.md skills src/sac_engine.py` ficou vazio.
- Terminal: `EXECUTED` após implementação e checagem literal dos sete itens; `CHANGES_REQUIRED` porque os itens 4 e 5 exigem links de execuções reais da CI que este ambiente sem remote não pode gerar. `Current` permanece em `track_05`.

### track_05 — Attempt 2 — 2026-08-20 — EXECUTED + APPROVED

- Outcome: as provas remotas que faltavam foram executadas na mesma PR #6. A REGR de dogfooding sem o alvo coeditado bloqueou o job real; o commit seguinte tocou exatamente `track05DogfoodTest`, sem `SAC-ACK`, e o mesmo job passou. A asserção histórica do Bloco 01 foi ajustada somente na dependência causal que proibia o gate antes do Bloco 02: continua proibindo `continue-on-error` e agora exige o `diff-check` bloqueante estabelecido por esta track.
- DoD 1: `python3 -m unittest tests/test_symbol_registry.py -v` passou; as fixtures positivas reconheceram todos os símbolos das seis extensões e as negativas tiveram zero falsos positivos para chamada, comentário, string e import.
- DoD 2: o mesmo approved-test passou em `test_existing_dart_and_powershell_behavior`; as entradas `.dart` e `.ps1` permaneceram literalmente inalteradas.
- DoD 3: a fixture manual de `guard.rb` com tag SAC imprimiu `fail_closed_exit=1 file=guard.rb`, comprovando falha fechada e arquivo nomeado.
- DoD 4: a execução real vermelha `https://github.com/MarceloRab/semantic-architecture-context/actions/runs/87779759659`, job `CI / SAC Diff Check (pull_request)`, imprimiu `SAC diff-check: exit 1`, `track05Dogfood [NOT ACKED]` e `uncovered: track05DogfoodTest`.
- DoD 5: na mesma PR #6, o alvo exato `track05DogfoodTest` foi coeditado sem ACK; a execução real verde `https://github.com/MarceloRab/semantic-architecture-context/actions/runs/32381711142`, job `https://github.com/MarceloRab/semantic-architecture-context/actions/runs/32381711142/job/96466269069`, imprimiu `SAC diff-check: exit 0` e `No SAC violations found`.
- DoD 6: `rg -n 'continue-on-error' .github/workflows` não encontrou ocorrências; `python3 ci/test_track_09_dod.py` passou e comprovou o comando bloqueante no workflow. O check de `push` é deliberadamente skipped pela condição `github.event_name == 'pull_request'`; o check bloqueante de `pull_request` passou na execução verde acima.
- DoD 7: inspeção de `README.md` confirmou a matriz de primeira classe com Python, JavaScript, JavaScript com JSX, TypeScript, TypeScript com JSX, Go, Dart e PowerShell.
- Regressão e gates: `python3 -m unittest discover -s tests -v`, `node mcp/smoke.mjs`, `python3 .github/scripts/check_hygiene.py`, `python3 .github/scripts/check_version.py`, `python3 src/sac_scan.py validate --root .`, `python3 src/sac_scan.py index-build --root .` e `git diff --check` passaram. A inspeção AST contra a base da Track 05 imprimiu `_is_covered_unchanged=True`, `_extract_acks_unchanged=True`, `_gather_acks_unchanged=True` e `diff_check_unchanged=True`; `git diff 23111df -- AGENTS.md skills src/sac_engine.py` ficou vazio; o diff-check local contra a base completa da PR imprimiu `exit 0`.
- Terminal: `EXECUTED` após produzir e reunir as provas solicitadas; `APPROVED` após checagem literal, neste mesmo chat, dos sete itens numerados. `Current` avança para `track_06`.

### track_06 — Attempt 1 — 2026-08-20 — EXECUTED + APPROVED

- Outcome: o engine agora relativiza `file` e caminhos em warnings pela função compartilhada `relativize_under_root`; o orçamento mede a serialização indentada efetivamente emitida pela CLI; o envelope MCP removeu `_perf.sac_root` e calcula `_perf.payload_bytes` por ponto fixo sobre o payload completo, incluindo `_perf` e indentação. O smoke compara stdout bruto para a mesma consulta com root relativo e absoluto, sem normalização.
- DoD 1: `node mcp/smoke.mjs` passou e imprimiu `[OK] relative/absolute --root byte parity bytes=2389`; o caso executa duas vezes `context --domain smoke_domain`, uma com root relativo e outra com root absoluto, e compara diretamente os buffers de stdout com `Buffer.equals`, sem parse, normalização ou reordenação.
- DoD 2: a inspeção recursiva do JSON produzido por `python3 src/sac_scan.py context --root "$PWD" --domain sac_core --json` imprimiu `absolute_paths=absent sac_root=absent`; a inspeção do diff confirmou a remoção de `_perf.sac_root` e a relativização no Python, sem reescrita de path no Node.
- DoD 3: a medição independente `Buffer.byteLength(result.content[0].text, "utf8")` sobre `jsonToolResult(withPerf(...))` imprimiu `reported=113 actual=113`, incluindo `_perf` e a indentação no texto efetivamente entregue para escrita.
- DoD 4: a prova manual mediu 1.238 bytes no stdout irrestrito (excluído somente o newline acrescentado por `print`), executou novamente com limite 1.237 e obteve `emitted_bytes=1238 budget_measured=1238 ratio=1.000`.
- DoD 5: a mesma execução manual de overflow imprimiu `code=context_payload_too_large exit=1 message=Context exceeds the configured token budget; no constraints were returned.`, preservando literalmente código, mensagem, exit code e ausência de truncamento.
- DoD 6: a regressão plantada substituiu temporariamente, no engine, a relativização do `file` de contexto por `tag.file`; `node mcp/smoke.mjs` falhou no novo caso com `[FAIL] relative/absolute --root byte parity` e `planted_root_leak_exit=1`; o arquivo original foi restaurado antes dos gates e do commit.
- Regressão e gates: `python3 -m unittest discover -s tests -v`, os quatro módulos dirigidos das Tracks 01, 02, 04 e 05, `python3 ci/test_track_09_dod.py`, `node mcp/smoke.mjs`, hygiene, version, validate, index-build e `git diff --check` passaram. A inspeção do diff confirmou ausência de alterações em gramática, `_is_covered`, SAC-ACK, registro lexical, fixtures da Track 05, workflow, README, AGENTS.md e skills.
- Terminal: `EXECUTED` após implementação e execução das provas; `APPROVED` após checagem literal, neste mesmo chat, dos seis itens numerados acima. `Current` avança para `track_07`.

### track_07 — Attempt 1 — 2026-08-20 — EXECUTED + APPROVED

- Outcome: `_context_selected_keys` agora devolve separadamente o conjunto completo selecionado e o subconjunto selecionado por anchor; somente esse subconjunto participa do numerador de `uncontracted_context_tag_count`. O conjunto completo continua governando `context_unfit_claims` e claims contratadas. `assess` publica `anchor_floor_symbols`, derivado exclusivamente dos símbolos das claims ARCH, e `anchor_excess_symbols`, enquanto o template explica que reduzir anchors exige reduzir antes claims ARCH.
- DoD 1: `python3 -m unittest tests/test_fitness.py -v` passou; `test_policy_selected_regr_without_claim_keeps_fit` adicionou `Extra` como REGR auto-incluída sem claim ao domínio base FIT e comprovou `fitness_status == "FIT"` e `uncontracted_context_tag_count == 0`.
- DoD 2: o mesmo approved-test passou; `test_unclaimed_arch_selected_by_anchor_remains_over_select` adicionou a ARCH `ExtraArch` aos anchors sem claim e comprovou `fitness_status == "OVER_SELECT"` e excedente igual a 1.
- DoD 3: o mesmo approved-test passou; `test_missing_regression_role_claim_remains_too_thin` manteve uma claim no cenário REGRESSION com papel ARCH, portanto sem a claim de papel exata `REGRESSION:REGR`, e comprovou `fitness_status == "TOO_THIN"` e `REGRESSION:REGR` em `missing_roles`.
- DoD 4: o mesmo approved-test passou; `test_arch_claim_whose_symbol_is_not_anchor_remains_unfit` removeu `Core` dos anchors, manteve suas duas claims ARCH e comprovou `fitness_status == "UNFIT"` e as duas claims em `context_unfit_claims`.
- DoD 5: a fixture manual `/tmp/track07_assess_fixture` foi avaliada com `python3 src/sac_scan.py capillarity --root /tmp/track07_assess_fixture --domain fixture --json`; a inspeção imprimiu `anchor_floor_symbols=['Core']`, `anchor_excess_symbols=['Surplus']`, `arch_claim_symbols=['Core']` e `floor_equals_arch_claim_symbols=True`.
- DoD 6: a fixture imutável `/tmp/track07_context_fixture` foi consultada por `getSacContextPayload` no worktree detached do baseline `5885ea3` e no worktree implementado, sem normalização. `diff -u` terminou 0 e ambos os payloads tiveram SHA-256 literal `8ad4be212d00333cc1cb3bbff692662e8b93c2310c3b3079b756b4502244e786`.
- DoD 7: antes e depois, o único domínio do manifesto do repositório, `sac_core`, foi executado com `python3 src/sac_scan.py capillarity --root . --domain sac_core --json`; a comparação imprimiu `before_status=UNRATED after_status=UNRATED before_fitness=None after_fitness=None before_quality=FAIL after_quality=FAIL` e `repository_domains_worsened=0 checked=1`.
- Regressão e gates: os dois comandos de unittest geral/dirigido da Track 07, os quatro módulos dirigidos das Tracks 01, 02, 04 e 05, `python3 ci/test_track_09_dod.py`, `node mcp/smoke.mjs`, hygiene, version, validate, index-build e `git diff --check` passaram. A inspeção do diff confirmou writes somente no owner de fitness, no approved-test, no template causal e neste handoff, sem mudanças em parsing, gramática, cenários, `_is_covered`, SAC-ACK, registro lexical, Context, MCP, workflow, README, AGENTS.md ou skills das Tracks 01–06.
- Terminal: `EXECUTED` após implementação e produção das sete provas; `APPROVED` após checagem literal, neste mesmo chat, de cada item numerado. `Current` avança para `track_08`.

## Pré-condição do bloco

Este bloco inicia somente após `track_10` do Bloco 01 estar `APPROVED`. A ordem interna é ditada por princípio, não por custo: as quatro primeiras tracks são as únicas de toda a coleção de relatórios que **aumentam** o benefício ao agente cego; as demais defendem os outros dois pilares.

## Fora de escopo, posterior ao bloco

Nenhum consumidor existente é migrado por este bloco. `api_robot` e `to_de_plantao` continuam rodando suas cópias congeladas de `sac-context/`, e `rabelo-standards` — base propagadora, não consumidora — não é tocado. A transferência para esses projetos é decisão do usuário, posterior a testes estáveis pós-Bloco 02.
