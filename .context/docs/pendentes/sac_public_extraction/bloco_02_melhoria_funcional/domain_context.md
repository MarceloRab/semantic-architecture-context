# Domain Context — Bloco 02: melhoria funcional da feature

Cápsula factual reutilizável. Só fatos necessários ao Bloco 02, cada um citado. Caminhos relativos à raiz do repositório público após o Bloco 01.

## Focus

- Objective area: fazer os três pilares e os três princípios do SAC entregarem o que prometem, por caminho predominantemente subtrativo.
- Entry point: `src/sac_engine.py` (gramática, Route, Context, fitness) e `src/sac_diff.py` (gate de regressão).
- Out of focus: veículo de entrega (extração, licença, installer, CI de fork, superfície MCP, identidade de versão) — tudo no Bloco 01. Harness de benchmark — non-goal declarado.

## Current flow

### Gate de regressão (`diff-check`)

1. `git diff` lista arquivos alterados, **ordenados por caminho** @ `src/sac_diff.py`
2. Para cada arquivo, extensão é resolvida contra `_SYMBOL_REGISTRY` @ `src/sac_diff.py:36`
3. Extensão fora do registro **e** arquivo com tag SAC ⇒ `FAIL CLOSED` @ `src/sac_diff.py:392`
4. Para cada símbolo alterado: `changed_symbols.append(changed)` e, **no mesmo laço**, `lookup()` + avaliação de `verify:` contra `changed_symbols` @ `src/sac_diff.py:415-427`
5. `_is_covered(target, changed_symbols, changed_files)` @ `src/sac_diff.py:323`
6. Alvo não coberto e não presente em `SAC-ACK:` do corpo da PR ⇒ `Violation`

### Gramática da tag

1. `<marcador> SAC:<TAG>: <TRIGGER> - <Símbolo>: <Constraint>` @ `src/sac_engine.py:20`
2. Marcador exigido: `//` ou `#`
3. `_ALLOWED_TRIGGERS` @ `src/sac_engine.py:102-106`
4. `_ARCH_IMPERATIVE_RE = \b(?:MUST|NEVER|ONLY)\b` @ `src/sac_engine.py:107`
5. `_VERIFY_TERMINAL_RE = r".*\bverify:\s*(?P<targets>[^.]+)"` @ `src/sac_engine.py:43`, aplicado em @ `src/sac_engine.py:146`

### Fitness de capillarity

1. `_context_selected_keys`: seleciona tag se `symbol ∈ anchors` **ou** `tag_type ∈ {REGR, DEPRECATED}` @ `src/sac_engine.py:971-985`
2. `context_unfit_claims`: claim casada cujo alvo não está no selecionado ⇒ `UNFIT` @ `src/sac_engine.py:1019-1027`
3. `uncontracted_context_count = max(0, len(context_selected) − contracted_in_context)` ⇒ `OVER_SELECT` @ `src/sac_engine.py:1037`
4. `_SCENARIO_REQUIRED_TAG_TYPE = {SUMMARY:ARCH, EXTEND:ARCH, REGRESSION:REGR, MIGRATION:ARCH}` @ `src/sac_engine.py:964-969`
5. Cenário-base ausente ⇒ `INVALID_CONTRACT` @ `src/sac_domains.py:225`; papel ausente ⇒ `TOO_THIN` @ `src/sac_engine.py:1039`

### Payload

1. Adapter chama a CLI sempre com `--root <absoluto>`; o engine prefixa `file` com a string recebida
2. Orçamento medido com `separators=(",",":")` (compacto) @ `src/sac_engine.py:636`
3. CLI imprime com `indent=1`; adapter emite `JSON.stringify(obj, null, 1)` @ `mcp/server.mjs:266`
4. `_perf.payload_bytes` calculado sobre o payload **sem** `_perf` e **sem** indentação @ `mcp/server.mjs:291`

## Contracts and invariants

- Três tags e apenas três: `ARCH`, `REGR`, `DEPRECATED` @ `src/sac_engine.py:101`. Não criar tag nova.
- Vocabulário fechado é o padrão da casa: `_ALLOWED_TRIGGERS`, `_ALLOWED_SCENARIOS`, `_TAG_TYPES`.
- Parser dual para tags legadas já existe @ `src/sac_engine.py:32-34` — compatibilidade retroativa é o padrão estabelecido.
- Tag malformada continua parseável e emite warning, em vez de sumir. Preserva o agente cego mesmo com erro de sintaxe.
- Quatro warnings canônicos: `invalid_trigger`, `arch_imperative_required`, `regr_verify_required`, `deprecated_replacement_required`.
- `verify:` restrito a tokens `[A-Za-z_][A-Za-z0-9_.$-]*` (gramática declarada em `sac-evolution`), narrativa explicitamente rejeitada.
- `_HOP1_CAP = 10` @ `src/sac_engine.py:99`.
- Índice de símbolos é gerado, nunca versionado.

## Owners and dependents

- Owner da cobertura: `_is_covered` @ `src/sac_diff.py:323`; único chamador é o laço @ `src/sac_diff.py:415-427`
- Owner do registro de linguagens: `_SYMBOL_REGISTRY` @ `src/sac_diff.py:36`; dependente: o `FAIL CLOSED` @ `src/sac_diff.py:392`
- Owner do campo `trigger`: `_ALLOWED_TRIGGERS` @ `src/sac_engine.py:102`; dependentes: parser canônico @ `src/sac_engine.py:24`, parser legado @ `src/sac_engine.py:34`, warning `invalid_trigger`, skills `sac-context` e `sac-onboard`, `templates/domains.template.md`
- Owner do orçamento: `SAC_CONTEXT_MAX_BYTES` @ `src/sac_engine.py:15,620,919`
- Owner do fitness: `_evaluate_context_fitness` @ `src/sac_engine.py:988`

## Critical surfaces

- **Identity**: `verify:` aponta símbolos por nome; o gate compara nome exato de símbolo alterado ou basename de arquivo alterado. Não há ID estável — é lexical por construção (C4/DP-1, sem AST).
- **Persistence/compatibility**: a **gramática da tag é o formato persistido**. Toda tag já escrita em qualquer repositório é estado antigo alcançável. Mudança no campo `trigger` é mudança de formato persistido e exige a matriz do Contract Break Gate.
- **Security/permission**: não aplicável a este bloco. Os escapes de HALT são fechados no Bloco 01.
- **External boundary**: `verify:` e `on=` são lidos por agente humano e por agente sem MCP. O texto da linha é a interface pública.

### Defeitos reproduzidos (fatos, não hipóteses)

- **Ordenação**: alvo `verify:` definido em `test/pay_test.dart` ⇒ `uncovered`, exit 1; o mesmo alvo em `aaa/pay_test.dart` ⇒ exit 0. `git diff` ordena por caminho e `lib/` < `test/`, logo o alvo apontando para teste é sistematicamente marcado não coberto.
- **Truncamento**: `verify: Cache.key, Adapter` → `['Cache']`, `warnings=[]`. `[^.]+` para no primeiro ponto e descarta o resto em silêncio. A gramática declarada aceita ponto no token; o parser não.
- **`trigger` inerte**: `RULE` vs `CONSTRAINT` não é distinguido em lugar nenhum do engine; `WARNING` vs `CRITICAL` não altera comportamento — `diff_check` bloqueia qualquer REGR não coberta independentemente do trigger.
- **`_SYMBOL_REGISTRY` = 2 entradas**: `.dart`, `.ps1`. O engine do SAC é Python; o gate não roda em Python; o dogfooding é impossível no código atual.
- **Path absoluto = 16,1 % do payload**: mesma consulta, root relativo 1.599 bytes, root absoluto 1.857 bytes.
- **Unidade divergente**: compacto 1.599 bytes vs `indent=1` 1.942 bytes → 1,215×. `SAC_CONTEXT_MAX_BYTES=12288` autoriza ~14,9 KB reais.
- **`_perf.payload_bytes` sub-relata 23,9 %**: reporta 1.599, stdout escreve 2.101.
- **Taxa de densidade**: `context_selected` inclui automaticamente toda REGR e toda DEPRECATED; qualquer excedente sobre claims casadas ⇒ `OVER_SELECT`. Logo cada REGR nova exige uma claim nova, e o manifesto cresce linearmente com o número de tags.
- **Piso rígido de anchors**: toda claim ARCH obriga que seu símbolo seja anchor, senão `context_unfit_claims` ⇒ `UNFIT`. Minimizar anchors abaixo do conjunto de símbolos das claims ARCH é FAIL.
- **`AGENTS.md` não menciona SAC**. A única referência de raiz é `.cursorrules`, específico de host, e trata de governança de mirror.
- **Ergonomia das skills**: `sac-onboard` tem cadeia de 3 níveis (`prompt_resumido.md` → `PROMPT.md` → `SKILL.md`); `sac-execution-overlay` tem 2; `sac-context` e `sac-evolution` não têm entrada curta. `sac-execution-overlay/PROMPT.md` tem item `15.` duplicado e duas linhas `Pipeline:` divergentes. A tabela *frase do usuário → contrato derivado* existe só em `sac-onboard/prompt_resumido.md`.
- **Idioma imperativo**: `_ARCH_IMPERATIVE_RE` exige `MUST|NEVER|ONLY`; template e documentação escrevem constraints misturando português e inglês. Constraint em português dispara `arch_imperative_required` permanentemente.

## Unknowns

- none
