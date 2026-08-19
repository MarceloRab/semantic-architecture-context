# Design — Bloco 02: melhoria funcional da feature

## Objective

Os três pilares e os três princípios do SAC passam a entregar o que prometem, e a tag `0.1.0` pública é liberada.

Estado observável final:

1. Uma PR que altera `lib/pay.dart` e o teste que `verify:` aponta em `test/pay_test.dart` passa no `diff-check`, independentemente da ordem alfabética dos caminhos.
2. `verify: Cache.key, Adapter` devolve `['Cache.key', 'Adapter']`. Nenhum alvo é descartado em silêncio; token inválido vira warning, não desaparecimento.
3. O agente que lê a linha crua e o agente que chama o MCP recebem a mesma informação. Nunca menos pela ferramenta.
4. O campo `trigger` carrega condição de aplicação (`on=…`), permitindo ao agente sem ferramenta **filtrar** constraints por `grep` antes de ler o texto.
5. `diff-check` roda em Python, JS/TS e Go, além de Dart e PowerShell; o repositório SAC valida a si mesmo no CI.
6. Nenhum byte de payload é caminho absoluto de máquina; o orçamento governa a mesma serialização que o sistema emite; `_perf.payload_bytes` reporta os bytes efetivamente escritos.
7. `AGENTS.md` na raiz descreve SAC, o manifesto, a gramática e o caminho degradado sem MCP.
8. Uma REGR nova deixa de exigir uma claim nova para o domínio permanecer `FIT`.
9. `RELEASE_GATE.md` está integralmente satisfeito e a tag `0.1.0` existe.

## Non-goals

- **Harness de benchmark** (Blind-Agent Utility, Regression Recall, Context Compression Effectiveness, tarefas rotuladas, ground truth, N execuções com variância, anotação manual). Declarado non-goal com custo reconhecido: é trabalho de eval com LLM, o segundo maior item de custo do plano original, e nenhuma decisão deste bloco depende dele. `DIAGNOSE` entra **apenas** como cenário de benchmark documentado — zero schema, zero código.
- **Layer A completa** sobre as ~3.400 linhas de Python. Autorizada apenas a Layer A mínima (D14).
- **AST**, code graph, geração dinâmica de contexto pelo MCP, provenance no hot path, documentação causal paralela. Vetos herdados literalmente da lista "Não implementar" do report externo, que passa a ser política pública.
- Criar qualquer tag SAC nova. Três tags é o número certo.
- Tornar `DIAGNOSE` cenário-base.
- Migração MCP SDK v2, HTTP streamable, worker persistente, cap de concorrência, ceilings físicos de stdout/stderr.
- Qualquer item do Bloco 01 (licença, installer, CI de fork, superfície MCP, versão, relocação de manifesto).

## Closed decisions

- **D1 — `_is_covered` avalia contra o conjunto completo.** O laço único vira dois: primeiro monta `changed_symbols` e `changed_files` inteiros, depois avalia violações. | Why: `changed_symbols` é construído incrementalmente dentro do próprio laço que o consulta, então símbolos de arquivos processados depois não existem quando o alvo é verificado; como `git diff` ordena por caminho e fonte (`lib/`, `src/`, `app/`) vem antes de teste (`test/`, `tests/`), o alvo que aponta para um teste é sistematicamente não coberto. Não é edge case: é o caso principal, porque `verify:` existe para apontar testes. A única saída hoje é `SAC-ACK` no corpo da PR, ou seja, o gate ensina o bypass. Maior razão benefício/custo do plano inteiro.

- **D2 — `verify:` termina em `;` ou fim de linha, não no primeiro ponto.** `_VERIFY_TERMINAL_RE` deixa de usar `[^.]+`. Cada alvo é validado contra `[A-Za-z_][A-Za-z0-9_.$-]*`; token que não casa vira warning `invalid_verify_target` e **não** é descartado em silêncio. | Why: a gramática declarada aceita ponto no token e o parser a contradiz, perdendo `Cache.key`, `user.service`, métodos em JS/Dart/Kotlin e testes versionados. É o único defeito conhecido em que o MCP entrega **menos** do que a leitura crua da linha — inversão exata do contrato do produto. Prioridade P0, superior ao diff-check sob o princípio 3.

- **D3 — Campo `trigger` passa a ser condição de aplicação: `on=<cond>`.** Não é removido; é feito pagar o próprio custo.
  - **ARCH**: vocabulário **fechado** — `on=ssot`, `on=boundary`, `on=ordering`, `on=state`, `on=exclusive`, `on=ownership`. Valor fora do conjunto ⇒ warning `invalid_trigger`.
  - **REGR / DEPRECATED**: token livre em snake_case `[a-z][a-z0-9_]{2,47}`, descrevendo a condição de mudança (`on=normalization_order`, `on=schema_change`).
  | Why: o campo consome ~10 caracteres do recurso mais escasso do sistema e hoje tem **zero** efeito de runtime — `RULE` vs `CONSTRAINT` não é distinguido em lugar nenhum do engine, e `WARNING` vs `CRITICAL` não altera nada porque `diff_check` bloqueia qualquer REGR não coberta independentemente do trigger. Convertê-lo em condição atende de uma vez: a estrutura da REGR pedida pelo report (condição → invariante → alvos) sem gastar caracteres na constraint; a qualidade do ARCH como vocabulário fechado executável pelo validador em vez de prosa de skill (que a própria lista "Não implementar" veta); e o princípio 3, porque o agente sem ferramenta passa a **grepar por condição** e descartar constraints antes de ler o texto. É economia de token no único lugar onde hoje ela não existe: fora do MCP.
  | Rejeitada: **remover o campo** — devolve o slot mas não dá filtro ao agente cego; converte um desperdício em ausência, quando há ganho disponível pelo mesmo preço.
  | Rejeitada: **codificar a condição em prosa na constraint** (forma do report) — custa caracteres no recurso mais escasso, produz algo não processável, e piora o agente cego: linha mais longa, condição misturada à obrigação, leitura integral obrigatória para descobrir se a constraint sequer se aplica.

- **D4 — Registro de linguagens: `.py`, `.js`, `.jsx`, `.ts`, `.tsx`, `.go`, além de `.dart` e `.ps1`.** A lista vira dimensão de primeira classe da matriz de compatibilidade, documentada no README. `FAIL CLOSED` para extensão não registrada permanece. | Why: hoje o pilar 2 tem dois estados para qualquer consumidor fora de Flutter/PowerShell — desligado ou bloqueando tudo. Python é obrigatório porque é a linguagem do próprio engine: sem ele o SAC não consegue proteger a si mesmo e o dogfooding é impossível, não apenas pendente. JS/TS e Go cobrem o grosso do universo de adoção restante. `FAIL CLOSED` é mantido porque silenciar arquivo não registrado com tag SAC seria fallback silencioso.

- **D5 — Marcador de comentário deixa de ser whitelist.** Passa a ser qualquer prefixo de comentário não-alfanumérico de até 4 caracteres antes de `SAC:`, cobrindo `//`, `#`, `--`, `%`, `;`, `<!--`, `/*`, `"""`. Delimitador de fechamento na mesma linha (`-->`, `*/`, `"""`) é removido do fim da constraint antes do parsing. | Why: subtrativo — remove uma lista em vez de estendê-la. Hoje SQL, Lua, Haskell, Erlang, Lisp, HTML, XML e Markdown não conseguem sequer portar uma tag, e o agente cego nesses arquivos não tem linha nenhuma para ler. Para um projeto público, escalabilidade é quantos repositórios podem adotar.

- **D6 — Idioma do vocabulário imperativo: PT + EN.** `_ARCH_IMPERATIVE_RE` aceita `MUST|NEVER|ONLY|DEVE|NUNCA|SOMENTE|APENAS`. | Why: template e documentação já escrevem constraints misturando os dois idiomas, então toda constraint em português dispara `arch_imperative_required` permanentemente. Aceitar os dois é a decisão normativa mais barata e não afrouxa o gate: a exigência de imperativo continua valendo.

- **D7 — `file` sempre relativo à raiz, qualquer que seja a forma de `--root`.** Vale para `matches`, para warnings e para `_perf.sac_root`, que passa a ser omitido do payload. | Why: 16,1 % do payload medido é caminho absoluto de máquina, em fixture rasa; com `C:\Users\<nome>\projects\<app>\` cresce. Cada byte é um caminho que não ajuda o agente a decidir nada — o oposto exato de contexto gravado para economia de token. Corrige também um vazamento de dados da máquina do usuário para dentro do contexto do LLM e, conforme o host, para telemetria de terceiros. E torna a paridade CLI ≡ MCP verdadeira **em bytes**, não só em forma: hoje `--root .` e `--root $PWD` produzem payloads diferentes para a mesma consulta lógica.

- **D8 — Unidade de bytes única: a emitida.** O orçamento (`SAC_CONTEXT_MAX_BYTES`) passa a medir a mesma serialização que a CLI imprime e o adapter emite. `_perf.payload_bytes` passa a medir os bytes efetivamente escritos em stdout, incluindo `_perf` e indentação. | Why: hoje o orçamento mede compacto e o sistema emite `indent=1` — razão medida 1,215× —, então `SAC_CONTEXT_MAX_BYTES=12288` autoriza ~14,9 KB reais; e `_perf.payload_bytes` sub-relata 23,9 %, o que significa que o instrumento com que se mede a economia do pilar 1 está errado, e a otimização é feita às cegas. Somados, o payload real é ~1,45× o que o orçamento acredita governar.
  | Nota de contrato: casos de corpus que comparam root relativo vs absoluto e separador de path **não** são normalizados antes da comparação. Normalizar ali suprimiria exatamente o sinal que D7 corrige.

- **D9 — `OVER_SELECT` deixa de contar tags auto-incluídas.** `uncontracted_context_count` passa a considerar apenas tags selecionadas **por anchor**; REGR e DEPRECATED, que `_context_selected_keys` inclui automaticamente por política, saem do numerador. A exigência de claim de papel `REGRESSION:REGR` para o domínio permanece intacta. | Why: como `context_selected` inclui automaticamente toda REGR e toda DEPRECATED, cada REGR nova exige hoje uma claim nova para o domínio não sair de `FIT` — o manifesto cresce linearmente com o número de tags e o contrato de capillarity **taxa a densidade semântica**. Isso põe "mais densidade" e "menos contexto persistido" em antagonismo por construção, e a vítima adicional é o princípio 3, porque o manifesto é justamente o artefato legível sem MCP. Uma tag incluída por política não é over-selection: over-selection é a tag que o anchor arrastou sem contrato. Corrigir o denominador é a mudança mínima que desfaz o antagonismo sem tocar schema, sem quebrar claim existente e sem afrouxar a cobertura de papéis.
  | Rejeitada: **desacoplar claims de tags permitindo claim multi-símbolo** — resolve o crescimento linear mas muda o schema de claims de 5 colunas, quebra todo manifesto existente e é mais caro que corrigir um numerador.

- **D10 — Piso de anchors declarado, não minimizado às cegas.** A recomendação "anchors = menor conjunto necessário" é adotada com o piso explícito: **o conjunto de símbolos das claims ARCH**. Documentado no template e verificado pelo `assess`, que passa a reportar o piso junto com o excedente. | Why: `_context_selected_keys` seleciona por `symbol ∈ anchors`, e claim casada cujo alvo não está no selecionado produz `context_unfit_claims` ⇒ `UNFIT`. Logo toda claim ARCH **obriga** que seu símbolo seja anchor: não é recomendação, é condição de PASS. Minimizar anchors sem minimizar antes as claims ARCH leva a FAIL. Tornar o piso visível é o que torna a recomendação executável.

- **D11 — `DIAGNOSE` fica fora do schema.** Não entra em `_BASE_SCENARIOS` nem em `_OPTIONAL_SCENARIOS`. Existe apenas como cenário de benchmark documentado em `docs/`. | Why: entrar como base tornaria `INVALID_CONTRACT` todo domínio já onboardado com capillarity, exigiria nova linha de claim em cada um sob pena de `TOO_THIN`, e derrubaria `quality_status` de PASS para FAIL em toda a base instalada — um MAJOR de schema de domínio proposto sob o título "não criar novas tags". E como `_SCENARIO_REQUIRED_TAG_TYPE` só pode mapeá-lo para `ARCH` (não há tag de diagnóstico e criar uma é vetado), uma claim `DIAGNOSE` é satisfeita pelas mesmas tags que já satisfazem `SUMMARY` e `EXTEND`: o domínio ganha uma linha de manifesto e **zero** requisito estrutural novo. O critério que ele quer medir — reduzir uma falha a um slice inicial sem busca global — não é propriedade de `tag_type` nenhuma; é propriedade do `files:` boundary + anchors, e se mede por comportamento.

- **D12 — Porta de entrada em `AGENTS.md` na raiz.** Bloco tool-neutral apontando: onde está o manifesto (`.sac/domains.md`), a gramática da tag em três linhas, o significado de `files:` como **limite de busca** e o caminho degradado sem MCP (comando de CLI equivalente). | Why: `AGENTS.md` é o arquivo que todo agente lê por convenção e hoje tem zero menções a SAC; a única referência de raiz é `.cursorrules`, específico de um host, e trata de governança de mirror. Sem porta de entrada o agente sem ferramenta só encontra uma tag por acidente, e todo o pilar 1 — Route, boundary, `files:` como limite de busca — é inexistente para ele. É a omissão mais grave sob o princípio 3 e custa um bloco de texto.

- **D13 — M9 restante: camada de atalho normalizada e subtrativa.**
  - Nome único de entrada nas três skills públicas: `PROMPT.md`. `prompt_resumido.md` é absorvido — a cadeia cai de três níveis para dois.
  - Tabela *frase do usuário → contrato derivado* obrigatória nas três, generalizando o que já existe e funciona em `sac-onboard`.
  - Verbo de atalho estável e disjunto: `SAC` → overlay de execução; `SAC ONBOARD <id>` → onboard (ASSESS default, read-only); `SAC TAG` → gramática. Convivem com os literais que já autorizam Write (`APROVAR SAC REGISTER <id>`, `APROVAR SAC TAG_DELTA <id>`), que continuam sendo os únicos.
  - Bloco "sem MCP" no topo de cada `PROMPT.md`, com o comando de CLI equivalente em duas linhas.
  - Corrigir o item `15.` duplicado e a linha `Pipeline:` divergente em `sac-execution-overlay/PROMPT.md`.
  | Why: remove um nível de indireção, remove ambiguidade e remove uma duplicação; o único conteúdo novo é replicação de um artefato já provado. O bloco "sem MCP" é o par obrigatório de D12 — sem ele, `AGENTS.md` aponta para skills cuja entrada assume MCP.

- **D14 — Layer A mínima, escopada aos invariantes que este bloco toca.** `unittest` da stdlib, sem framework, sem fixture de terceiros. Cobre exatamente: ordenação de `_is_covered` (D1), parsing de `verify:` com ponto e token inválido (D2), vocabulário e forma de `on=` incluindo tag legada (D3), resolução de extensão do registro (D4), reconhecimento de marcador (D5), e o numerador de `OVER_SELECT` (D9). | Why: F1 sobreviveu precisamente porque não há teste unitário de `_is_covered`; este bloco muda gramática, fitness e cobertura de linguagens ao mesmo tempo, e nenhuma dessas mudanças é provável por inspeção manual — o defeito original era invisível a olho nu e dependia da ordem alfabética dos caminhos. Escopo mínimo respeita a política de custo: trava o que o bloco muda e nada além.

- **D15 — `diff-check` renomeado na promessa pública para `co-edit gate`.** README e docs declaram: o gate verifica que **algo com o nome do alvo foi editado**, não que o teste existe, não que passou, não que cobre o símbolo. | Why: `_is_covered` é lexical por construção (coerente com C4/DP-1, sem AST) e é uma escolha defensável — mas chamar isso de "prevenção de regressão" promete o que não entrega, e é o tipo de promessa que um contributor externo testa no primeiro dia. Renomear a promessa é a correção; o mecanismo permanece.

- **D16 — Ordem de execução dentro do bloco: D2 → D3 → D12+D13 → D1 → D4 → D7+D8 → D9+D10 → D5+D6 → D11+D15.** | Why: os quatro primeiros são os únicos de toda a coleção de relatórios que **aumentam** o benefício ao agente cego; os demais defendem os outros dois pilares e são, sob o princípio 3, manutenção. A ordem deixa de ser escolhida por custo e passa a ser escolhida por princípio.

## Selected solution

- **Approach.** Correção predominantemente subtrativa, sem mecanismo novo e sem tag nova. O pilar 2 não ganha máquina: ganha uma correção de ordenação (D1), uma promessa honesta (D15) e mais entradas numa tabela (D4). O pilar 1 não ganha compressão: para de gastar 16 % com caminho absoluto (D7) e passa a medir na unidade que emite (D8). O princípio 1 ganha espaço fazendo o campo `trigger` pagar o próprio custo (D3), única mudança de gramática, e ela **devolve** orçamento em vez de consumir. O princípio 3 ganha um bloco de texto na raiz (D12) e o par de atalho sem MCP (D13). O antagonismo entre densidade semântica e contexto persistido é desfeito corrigindo um numerador (D9), não mudando schema.

- **Why best.** É o único conjunto que move o princípio 3 — o critério que o próprio produto elege como decisivo — em vez de apenas preservá-lo. As alternativas examinadas nos relatórios ou não o movem (diff-check em duas fases, anchors mínimos, `DIAGNOSE` como cenário-base) ou o movem para trás (estrutura da REGR codificada em prosa na constraint). E é o conjunto com menor risco de refactor futuro: nenhuma tag nova, nenhum schema de claims alterado, nenhum artefato paralelo, nenhum caminho quente com provenance. Cada mudança tem um mecanismo existente como dono.

- **Rejected viable alternative 1: `DIAGNOSE` como cenário-base + REGR estruturada em prosa + anchors mínimos** (forma escrita do report externo). | Reason: duas das quatro P0/P1 não são executáveis juntas — `DIAGNOSE` mapeia para ARCH, exige mais uma claim ARCH e portanto empurra anchors para cima, enquanto "minimizar anchors" os empurra para baixo, e o eixo de fitness torna as duas pressões simultaneamente vinculantes. `DIAGNOSE` como base é ainda um MAJOR silencioso sobre a base instalada.

- **Rejected viable alternative 2: remover o campo `trigger`.** | Reason: devolve o slot mas não entrega filtro ao agente sem ferramenta; troca desperdício por ausência quando o ganho está disponível pelo mesmo preço de linha.

- **Rejected viable alternative 3: claims multi-símbolo para desacoplar claims de tags.** | Reason: resolve o crescimento linear mas altera o schema de claims de 5 colunas e quebra todo manifesto existente; D9 obtém o mesmo efeito corrigindo um numerador.

- **Executor latitude:** apenas escolhas mecânicas. Nenhuma abordagem alternativa, nenhuma heurística, nenhuma decisão semântica.

## Contracts and prohibitions

- **C1** — Must: três tags e apenas três (`ARCH`, `REGR`, `DEPRECATED`). | Must not: criar tag nova, criar cenário-base novo, criar campo novo na linha. | Evidence: `_KNOWN_TAGS` e `_BASE_SCENARIOS` inalterados no diff.
- **C2** — Must: engine e CLI permanecem stdlib-only e lexicais. | Must not: AST, code graph, dependência de terceiros, geração dinâmica de contexto pelo MCP, provenance no hot path, documentação causal paralela. | Evidence: gate de CI de imports + revisão contra a lista "Não implementar" publicada.
- **C3** — Must: tag malformada continua parseável e emite warning. | Must not: tag sumir do resultado por erro de sintaxe. | Evidence: casos de Layer A com tag inválida presente no output com warning.
- **C4** — Must: nenhum alvo de `verify:` é descartado sem warning. | Must not: `[^.]+` ou qualquer terminação que trunque token válido. | Evidence: Layer A sobre `Cache.key, Adapter` e sobre token inválido.
- **C5** — Must: paridade CLI ≡ MCP em **bytes** para a mesma consulta lógica, com root relativo e absoluto. | Must not: normalizar path nos casos de corpus que comparam forma do root, separador ou ordenação. | Evidence: caso explícito não-normalizado em `mcp/smoke.mjs`.
- **C6** — Must: o agente que lê a linha crua nunca recebe mais informação que o agente com MCP. | Must not: qualquer caminho em que a ferramenta entregue menos que a leitura direta. | Evidence: caso de smoke comparando alvos de `verify:` na linha com os alvos no payload.
- **C7** — Must: `on=` de ARCH é vocabulário fechado, verificado pelo validador. | Must not: qualidade de ARCH definida apenas em prosa de skill. | Evidence: warning `invalid_trigger` disparado para valor fora do conjunto.
- **C8** — Must: `FAIL CLOSED` preservado para extensão não registrada com tag SAC. | Must not: silenciar arquivo não registrado. | Evidence: fixture em linguagem fora do registro com tag ⇒ exit 1.
- **C9** — Must: a exigência de claim de papel `REGRESSION:REGR` permanece após D9. | Must not: afrouxar `TOO_THIN` ou `UNFIT`. | Evidence: Layer A sobre domínio sem claim REGR ⇒ `TOO_THIN`.
- **C10** — Must: o repositório SAC valida a si mesmo no CI (dogfooding real, com `diff-check` ligado). | Must not: job `diff-check` não-bloqueante. | Evidence: PR no próprio repositório com REGR não coberta ⇒ CI vermelha.
- **C11** — Must: `RELEASE_GATE.md` integralmente satisfeito antes da tag `0.1.0`. | Must not: tag `0.1.0` com item pendente. | Evidence: checklist do gate com evidência citada por item.

## Risk-specific requirements

- **R1** — Risk: D3 é mudança do **formato persistido**; toda tag já escrita em qualquer repositório é estado antigo alcançável. | Required protection: parser dual (mecanismo que já existe para tags legadas), matriz de estados antigos fechada abaixo, warning explícito em vez de rejeição, e nenhuma perda de constraint. | Proof: fixture com tag legada e tag nova no mesmo arquivo, ambas parseadas, a legada com warning.
- **R2** — Risk: D5 amplia o reconhecimento de marcador e pode produzir falso positivo dentro de literal de string. | Required protection: prefixo limitado a 4 caracteres não-alfanuméricos imediatamente antes de `SAC:`, ancorado após espaço inicial da linha; remoção do delimitador de fechamento antes do parsing. | Proof: fixture com `"SAC:ARCH:"` dentro de literal de string e com tag real na mesma fixture; apenas a real é reconhecida.
- **R3** — Risk: D9 afrouxa um sinal de fitness e pode mascarar over-selection real. | Required protection: o numerador exclui **apenas** tags cuja inclusão veio da política REGR/DEPRECATED; tags trazidas por anchor sem contrato continuam contando. | Proof: Layer A com dois casos — REGR extra (não conta) e ARCH arrastada por anchor sem claim (conta).
- **R4** — Risk: D4 liga o gate em Python, JS/TS e Go, e regex de símbolo mal calibrada produz falso positivo ou falso negativo em massa no primeiro dia público. | Required protection: cada linguagem entra com fixture própria cobrindo declaração positiva e linha que **não** deve casar; dogfooding do próprio repositório é a validação de campo. | Proof: fixtures por linguagem + CI do próprio repositório verde com `diff-check` ligado.
- **R5** — Risk: D7/D8 mudam o payload e podem quebrar a paridade sem que o smoke perceba, porque o smoke chama a CLI com a mesma string de root do adapter. | Required protection: C5 — caso explícito comparando root relativo vs absoluto **sem** normalização. | Proof: o caso novo falha propositalmente se `--root` voltar a vazar para dentro de `file`.
- **R6** — Risk: D1 corrige o falso positivo e expõe violações reais que estavam sendo mascaradas, quebrando PRs que antes passavam. | Required protection: é o comportamento correto e desejado; o `CHANGELOG` declara a mudança de veredicto como breaking de comportamento do gate, e `SAC-ACK` continua disponível como saída explícita e auditável. | Proof: fixture antes/depois com os dois veredictos documentados.
- **R7** — Risk: as correções chegam mas a promessa pública continua inflada, e o primeiro contributor externo desmente o README. | Required protection: D15 aplicado antes da tag `0.1.0`. | Proof: revisão do README contra o que `_is_covered` faz.

## Old reachable states

O contrato quebrado é a **gramática da tag no campo `trigger`** (D3). Toda tag SAC já escrita é estado persistido alcançável.

| Estado antigo alcançável | Detecção | Caminho explícito |
|---|---|---|
| `SAC:ARCH: RULE - Sym: …` / `SAC:ARCH: CONSTRAINT - Sym: …` | trigger casa `RULE\|CONSTRAINT` | **Migrar na leitura, sem reescrever o arquivo**: parseada normalmente, `on` fica vazio, warning `legacy_trigger` com a sugestão do vocabulário fechado. Constraint, símbolo e `verify:` preservados integralmente. Nunca descartada. |
| `SAC:REGR: WARNING - Sym: …` / `CRITICAL` | trigger casa `WARNING\|CRITICAL` | **Migrar na leitura**: idem, com warning `legacy_trigger`. O comportamento de bloqueio do `diff-check` é idêntico ao de hoje, porque o trigger já não o alterava. |
| `SAC:DEPRECATED: WARNING\|CRITICAL - Sym: …` | idem | **Migrar na leitura**: idem. `replacement:` continua obrigatório. |
| `on=<valor fora do vocabulário ARCH>` | tag nova com valor inválido | **Rejeitar com recuperação**: warning `invalid_trigger` listando o conjunto permitido. A tag continua parseável e visível — nunca some. |
| `verify:` com alvo contendo ponto, hoje truncado | qualquer tag REGR existente | **Regenerar o resultado**: o alvo passa a ser devolvido inteiro. Nenhuma migração de arquivo; muda apenas o que o parser lê. Efeito colateral desejado: PRs que passavam por alvo perdido podem passar a falhar — declarado no `CHANGELOG`. |
| Alvo de `verify:` que não casa `[A-Za-z_][A-Za-z0-9_.$-]*` | validação por token | **Rejeitar com recuperação**: warning `invalid_verify_target` nomeando o token. Nunca descartado em silêncio. |
| Manifesto com claim para cada REGR (escrito sob a taxa de densidade de hoje) | qualquer manifesto existente | **Preservar**: D9 relaxa o numerador, então manifestos com claims a mais continuam `FIT`. Nenhuma ação do usuário. |
| Domínio com `quality_status: PASS` antes do bloco | avaliação de capillarity | **Preservar**: nenhuma decisão deste bloco adiciona cenário-base nem papel obrigatório (D11). Nenhum domínio existente cai para `INVALID_CONTRACT` ou `TOO_THIN`. |
| Arquivo em linguagem recém-registrada, com tag SAC, que hoje dá `FAIL CLOSED` | extensão passa a existir no registro | **Migrar**: passa a ser avaliado de verdade. Pode revelar violação real antes mascarada por `FAIL CLOSED` genérico. Declarado no `CHANGELOG`. |
| `prompt_resumido.md` de `sac-onboard` | presença do arquivo | **Migrar por absorção**: conteúdo integrado ao `PROMPT.md` e o arquivo removido. Sem redirect, sem stub. |

Nenhum estado antigo tem fallback silencioso. Nenhuma tag existente deixa de ser lida. Nenhum manifesto existente muda de veredicto para pior.

## Planned outcomes

1. **`verify:` deixa de truncar no ponto.**
   `_VERIFY_TERMINAL_RE` termina em `;` ou fim de linha; cada alvo validado por token; `invalid_verify_target` como quinto warning canônico.
   | Acceptance: `verify: Cache.key, Adapter` → `['Cache.key','Adapter']`; token inválido presente nos warnings e ausente dos alvos, sem sumiço silencioso. | Verify: Layer A + caso de smoke comparando a linha crua com o payload. | Likely owners: `src/sac_engine.py`, `tests/test_verify_parse.py`, `mcp/smoke.mjs`

2. **ADR e implementação do campo `on=`.**
   ADR em `docs/adr/`; parser canônico aceita `on=<cond>`; vocabulário fechado para ARCH; token snake_case livre para REGR/DEPRECATED; parser dual preserva tags legadas com `legacy_trigger`; template, skills e docs atualizados.
   | Acceptance: cada linha da matriz de estados antigos reproduzida com o veredicto declarado; nenhuma tag legada perdida. | Verify: Layer A sobre as seis primeiras linhas da matriz + fixture mista legada/nova. | Likely owners: `docs/adr/`, `src/sac_engine.py`, `templates/domains.template.md`, `skills/`

3. **Porta de entrada + camada de atalho.**
   Bloco SAC em `AGENTS.md` (manifesto, gramática em três linhas, `files:` como limite de busca, caminho degradado sem MCP); M9 restante nas três skills públicas (nome único `PROMPT.md`, tabela frase→contrato, verbos disjuntos, bloco "sem MCP", correção do item 15 duplicado e da linha `Pipeline:` divergente).
   | Acceptance: um agente que abre só `AGENTS.md` chega ao manifesto e ao comando de CLI sem MCP; `prompt_resumido.md` não existe mais; nenhuma duplicação remanescente no overlay. | Verify: leitura dirigida partindo apenas de `AGENTS.md` + inspeção das três skills. | Likely owners: `AGENTS.md`, `skills/sac-context/`, `skills/sac-onboard/`, `skills/sac-execution-overlay/`

4. **`_is_covered` avalia contra o conjunto completo.**
   Dois laços: montagem completa de `changed_symbols`/`changed_files`, depois avaliação.
   | Acceptance: alvo em `test/pay_test.dart` e o mesmo alvo em `aaa/pay_test.dart` produzem veredicto **idêntico**. | Verify: Layer A com as duas ordenações + fixture git reproduzindo o caso original. | Likely owners: `src/sac_diff.py`, `tests/test_is_covered.py`

5. **Registro de linguagens + dogfooding real.**
   `.py`, `.js`, `.jsx`, `.ts`, `.tsx`, `.go` no `_SYMBOL_REGISTRY`, cada uma com fixture positiva e negativa; matriz de compatibilidade no README com linguagem como dimensão de primeira classe; job `diff-check` ligado na CI do próprio repositório.
   | Acceptance: PR no próprio repositório com REGR não coberta ⇒ CI vermelha; extensão fora do registro com tag ⇒ `FAIL CLOSED` preservado. | Verify: fixtures por linguagem + PR de prova no próprio repositório. | Likely owners: `src/sac_diff.py`, `tests/test_symbol_registry.py`, `.github/workflows/ci.yml`, `README.md`

6. **Path relativo + unidade de bytes única.**
   `file` sempre relativo à raiz em matches e warnings; `_perf.sac_root` removido; orçamento e `_perf.payload_bytes` medidos sobre a serialização emitida; caso de corpus não-normalizado comparando root relativo vs absoluto.
   | Acceptance: payload idêntico byte a byte para `--root .` e `--root <absoluto>`; `_perf.payload_bytes` igual aos bytes escritos em stdout. | Verify: caso novo em `mcp/smoke.mjs` + medição direta de stdout. | Likely owners: `src/sac_engine.py`, `src/sac_scan.py`, `mcp/server.mjs`, `mcp/smoke.mjs`

7. **Fitness: fim da taxa de densidade + piso de anchors visível.**
   `uncontracted_context_count` exclui tags auto-incluídas por política; `assess` reporta o piso de anchors (símbolos das claims ARCH) junto com o excedente; template documenta o piso.
   | Acceptance: adicionar uma REGR a um domínio `FIT` sem adicionar claim mantém `FIT`; ARCH arrastada por anchor sem claim continua produzindo `OVER_SELECT`; domínio sem claim REGR continua `TOO_THIN`. | Verify: Layer A com os três casos. | Likely owners: `src/sac_engine.py`, `tests/test_fitness.py`, `templates/domains.template.md`

8. **Marcadores de comentário + idioma imperativo.**
   Whitelist de marcador substituída por prefixo não-alfanumérico de até 4 caracteres antes de `SAC:`, com remoção do delimitador de fechamento; `_ARCH_IMPERATIVE_RE` aceita PT e EN.
   | Acceptance: tag reconhecida em `--`, `%`, `;`, `<!-- -->`, `/* */`, `"""`; `SAC:ARCH:` dentro de literal de string **não** é reconhecida; constraint em português não dispara `arch_imperative_required`. | Verify: Layer A com fixture multilíngue e fixture de falso positivo. | Likely owners: `src/sac_engine.py`, `tests/test_markers.py`

9. **Promessa honesta + `DIAGNOSE` como benchmark documentado + release.**
   README declara o gate como **co-edit gate** com o que ele verifica e o que não verifica; `DIAGNOSE` documentado apenas como cenário de benchmark, fora do schema; lista "Não implementar" publicada como política; `CHANGELOG` com as mudanças de veredicto (D1, D2, D4); `RELEASE_GATE.md` satisfeito item a item; tag `0.1.0`.
   | Acceptance: cada item do `RELEASE_GATE.md` com evidência citada; `_BASE_SCENARIOS` e `_OPTIONAL_SCENARIOS` inalterados no diff do bloco; `git tag` mostra `0.1.0`. | Verify: inspeção cruzada do gate + diff dos dois frozensets. | Likely owners: `README.md`, `CHANGELOG.md`, `RELEASE_GATE.md`, `docs/`

## Open decisions

none

## Approval

status: AWAITING_APPROVAL
