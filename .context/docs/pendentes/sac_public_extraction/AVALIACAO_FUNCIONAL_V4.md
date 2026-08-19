# SAC — Avaliação Funcional da Feature

**Objeto:** o SAC como *feature*, não como projeto a publicar.
**Critério:** os três princípios declarados e os três pilares, e nada mais.
**Método:** leitura do código + reprodução em fixture git controlada.
**Relação com as avaliações anteriores:** v1, v2 e v3 avaliaram o **veículo de entrega** (extração, MCP, lifecycle, CI). Nenhuma das três perguntou se o produto entrega os pilares. Esta pergunta é mais importante, e a resposta muda a ordem das tracks.

---

## 0. Veredito

| | Estado | |
|---|---|---|
| **Pilar 1** — Contexto gravado / economia de tokens | **Forte, com desperdício mensurável** | o design está certo; a implementação joga fora 16 % do payload |
| **Pilar 2** — Prevenção de regressão | **Quebrado no caso comum** | dois defeitos reproduzidos abaixo; hoje o gate treina o hábito que existe para impedir |
| **Pilar 3** — Base para escalabilidade | **Sólido conceitualmente, sem eixo de escala real** | escala por domínio; não escala por linguagem |
| **Princípio 1** — Compacto, cabe em uma linha | **Cumprido, com um campo desperdiçado** | `trigger` consome o recurso mais escasso e não informa |
| **Princípio 2** — Normatizado | **Cumprido** | melhor parte do sistema |
| **Princípio 3** — Benefício ao agente cego | **Parcialmente cumprido, sem porta de entrada** | a tag serve; o resto do sistema é invisível sem MCP |

**A conclusão que reordena tudo:** o pilar mais fraco é o pilar do meio, e ele não é fraco por falta de hardening — é fraco por defeito funcional. Publicar o SAC hoje publica um gate de regressão que **bloqueia mudanças corretas** no layout de projeto mais comum que existe.

---

## 1. Pilar 2 — Prevenção de regressão: **quebrado**, com prova

Este é o achado central desta avaliação.

### 1.1 O gate suporta duas linguagens: `.dart` e `.ps1`

`sac_diff.py:36` — `_SYMBOL_REGISTRY` tem exatamente duas entradas. Não há Python, JS/TS, Java, Go, Kotlin, Swift, C#, Rust.

`sac_diff.py:392` — extensão fora do registro **e** arquivo com tag SAC ⇒ `FAIL CLOSED`.

Reproduzido, projeto Python com uma tag REGR:

```
$ sac_scan.py diff-check --base HEAD~1 --root .
SAC diff-check: exit 1
FAIL CLOSED - changed files in unsupported languages with SAC tags:
  lib/pay.py
```

Consequências funcionais, todas diretas:

- **O SAC não consegue proteger a si mesmo.** O engine é Python; o gate não roda em Python. O "dogfooding" que o v2 põe como checkbox do T2 não é trabalho pendente — é **impossível** no código atual.
- Para qualquer consumidor fora de Flutter/PowerShell, o pilar 2 tem dois estados: **desligado** (sem tags) ou **bloqueando tudo** (com tags). Não há estado útil.
- A matriz de compatibilidade do v2 (§17) cataloga SO, Node, Python e host MCP — e **omite a única dimensão que decide se o produto funciona: a linguagem do consumidor.** Nem v1, nem v2, nem v3 mencionam o `_SYMBOL_REGISTRY`.

### 1.2 A cobertura depende da ordem alfabética dos caminhos

`sac_diff.py:427` avalia cada alvo `verify:` contra `changed_symbols` — uma lista **construída incrementalmente dentro do próprio laço**. Símbolos de arquivos processados depois ainda não existem quando o alvo é verificado. `changed_files` (cobertura por basename) é completo desde o início; `changed_symbols` não é.

Reproduzido — **mudança logicamente idêntica, dois veredictos**:

```
verify: testChargeIdem, definido em  test/pay_test.dart   (test/ > lib/)
  → exit 1   REGR violations (blocked)
             uncovered: testChargeIdem
             Changed symbols:
               lib/pay.dart:charge
               test/pay_test.dart:testChargeIdem     ← o alvo está na lista
                                                       e mesmo assim é "uncovered"

o mesmo alvo, movido para  aaa/pay_test.dart          (aaa/ < lib/)
  → exit 0   No SAC violations found.
```

`git diff` ordena por caminho. Fonte em `lib/`, `src/`, `app/`; teste em `test/`, `tests/`. A fonte é **sempre** processada antes. Portanto, para o layout de projeto convencional, o alvo `verify:` que aponta para um teste é **sistematicamente marcado como não coberto**, mesmo quando o teste foi alterado na mesma PR.

Isso não é um edge case. É o caso principal: `verify:` existe para apontar testes.

### 1.3 O efeito comportamental é o pior possível

A única saída do usuário é `SAC-ACK: <symbol>` no corpo da PR. Ou seja: **o gate, no caso de uso primário, ensina o desenvolvedor a escrever o bypass em toda PR.** Depois de dez PRs, o ACK é reflexo, e a próxima regressão real passa junto.

Um gate que produz falso positivo sistemático é pior que gate nenhum: gate nenhum não corrói a disciplina.

### 1.4 Teto de projeto: `_is_covered` não é um gate de regressão

Mesmo corrigidos 1.1 e 1.2, `sac_diff.py:323` define cobertura como:

> (a) um símbolo alterado tem o nome do alvo; ou (b) o basename de um arquivo alterado é o alvo.

Isto é **"você editou algo com esse nome"**. Não é "o teste existe", não é "o teste passou", não é "o teste cobre o símbolo". Renomear uma variável dentro de `testChargeIdem` satisfaz o gate; escrever o teste certo em outro nome não satisfaz.

Isso é uma escolha defensável — é lexical, stdlib-only, sem AST, coerente com C4/DP-1 — mas precisa ser **declarada como o que é**: um *co-edit gate*, um lembrete de que existe um teste a tocar. Chamar isso de "Prevenção de Regressão" no material público promete o que não entrega, e é o tipo de promessa que um contributor externo testa no primeiro dia.

---

## 2. Pilar 1 — Contexto gravado / economia de tokens: **forte, com desperdício**

O design está certo e é a melhor parte do sistema: um domínio por task, `files:` como **limite de busca e não fila de leitura**, catalog L0 sem `files[]` e sem `tag_count`, `tag_count` deliberadamente não persistido (evita métrica stale), overflow explícito em vez de truncamento silencioso, Context montando anchors + todas REGR/DEPRECATED + hop1 numa chamada. Nada disso deve mudar.

Três desperdícios medidos, todos contra o pilar:

**(a) Caminhos absolutos — 16,1 % do payload.** O adapter sempre envia `--root <absoluto>`; o engine prefixa `file` com a string recebida. Mesma consulta, medida:

```
root relativo : 1.599 bytes
root absoluto : 1.857 bytes      → +258 bytes = +16,1 %
```

Em fixture rasa. Com `C:\Users\<nome>\projects\<app>\` o custo cresce. **Todo** payload MCP paga. Cada byte é um caminho de máquina que não ajuda o agente a fazer nada — é o oposto exato de contexto gravado para economia.

**(b) A unidade do orçamento não é a unidade emitida.** O budget mede compacto (`separators=(",",":")`); a CLI imprime `indent=1`. Medido: **1,215×**. `SAC_CONTEXT_MAX_BYTES=12288` autoriza ~14,9 KB de saída real. O mecanismo de economia de token está calibrado em uma unidade que o sistema não usa.

**(c) `_perf.payload_bytes` sub-relata 23,9 %.** Detalhado na v3. Relevante aqui porque é o instrumento com que se *mede* a economia. Instrumento errado ⇒ a otimização do pilar 1 é feita às cegas.

Somados: o payload real é ~1,45× o que o orçamento acredita governar, e ~16 % dele é lixo posicional.

---

## 3. Pilar 3 — Base para escalabilidade: **eixo errado**

O sistema escala bem no eixo que escolheu: mais domínios não aumentam o custo por task, porque o Route entrega catalog compacto e o Context carrega exatamente um domínio. `hop1` tem cap (`_HOP1_CAP = 10`). O índice de símbolos é gerado, não versionado. Correto.

O eixo em que **não** escala é o que determina adoção: **linguagem**. Duas no gate de regressão (§1.1); no parser de tags, a gramática é agnóstica (só exige `//` ou `#` como marcador), mas isso significa que linguagens com `--` (SQL, Lua, Haskell), `%` (Erlang, LaTeX), `;` (Lisp, assembly), `<!-- -->` (HTML, XML, Markdown) e `"""` não conseguem sequer **portar uma tag**.

Para um projeto público, escalabilidade é: quantos repositórios podem adotar. Hoje: repositórios Dart/PowerShell com comentários `//` ou `#`. A track T8 do v2 valida SO × Node × Python × host — e nenhuma dessas dimensões muda esse número.

---

## 4. Princípio 1 — Compacto: **um campo não paga o próprio custo**

A gramática é:

```
<marcador> SAC:<TAG>: <TRIGGER> - <Símbolo>: <Constraint>
```

Cabe em uma linha, fica junto do símbolo, é greppável. Correto.

Mas `_ALLOWED_TRIGGERS` (`sac_engine.py:102`) é:

```python
"ARCH":       ("RULE", "CONSTRAINT")
"REGR":       ("WARNING", "CRITICAL")
"DEPRECATED": ("WARNING", "CRITICAL")
```

Isto é **severidade**, não gatilho. O nome do campo promete "quando isto se aplica"; o vocabulário entrega "quão grave isto é". E, pior:

- para `ARCH`, `RULE` vs `CONSTRAINT` não tem diferença semântica definida em lugar nenhum — o engine não trata os dois de forma distinta;
- para `REGR`/`DEPRECATED`, `WARNING` vs `CRITICAL` **também** não altera comportamento algum: `diff_check` bloqueia em qualquer REGR não coberto, independentemente do trigger.

Ou seja: um campo obrigatório, ~10 caracteres do orçamento mais escasso do sistema, **zero efeito** no runtime e zero informação para o agente. No princípio "cabe em uma linha", cada caractere disputa espaço com a constraint — que é a única parte que o agente cego realmente usa.

O campo tem duas saídas honestas: **remover** (parser dual já existe, compatibilidade retroativa é o padrão da casa) ou **fazer valer o nome** — passar a carregar a condição de aplicação (`on=edit`, `on=add_field`, `on=new_dependency`), que é exatamente o que permite ao agente filtrar constraints sem ler todas. A segunda opção fortalece os três princípios de uma vez: mesma linha, mais normatizado, e o agente cego ganha um filtro legível.

---

## 5. Princípio 2 — Normatizado: **cumprido**

É a dimensão mais bem executada. Gramática regular, vocabulário fechado, quatro warnings canônicos (`invalid_trigger`, `arch_imperative_required`, `regr_verify_required`, `deprecated_replacement_required`), `verify:` restrito a tokens `[A-Za-z_][A-Za-z0-9_.$-]*` com narrativa explicitamente rejeitada, `replacement:` obrigatório em DEPRECATED, parser dual para tags legadas, e — decisão especialmente boa — **tag malformada continua parseável e emite warning, em vez de sumir**. Isso preserva o agente cego mesmo quando o autor errou a sintaxe.

Único reparo: `_ARCH_IMPERATIVE_RE` exige `MUST|NEVER|ONLY`, mas o `_template` e a documentação escrevem constraints em português e inglês misturados. Uma constraint em português ("DEVE validar…") dispara `arch_imperative_required` para sempre. Normatização precisa decidir a língua do vocabulário imperativo, ou aceitar as duas.

---

## 6. Princípio 3 — Agente cego: **a tag serve; o sistema é invisível**

O que funciona, e deve ser protegido a qualquer custo: a constraint está fisicamente ao lado do símbolo, em texto puro, dentro de um comentário. Um agente sem MCP que abre o arquivo **vê a restrição**. `verify:` e `replacement:` são legíveis. Isso é o núcleo do valor e está correto.

O que não funciona:

**(a) Não existe porta de entrada.** `AGENTS.md` na raiz do repositório — o arquivo que todo agente lê por convenção — tem **zero** menções a SAC. A única referência de raiz é `.cursorrules`, específico de um host, e seu conteúdo trata de *governança de mirror*, não de como usar SAC. O manifesto está em `sac-context/docs/SAC_domains.md`, caminho que nenhum agente adivinha.

Resultado: o agente cego só encontra uma tag **por acidente**, quando já abriu o arquivo certo por outro motivo. Ele nunca descobre o Route, nunca sabe que `files:` limita a busca, nunca sabe que existe economia disponível. O pilar 1 é, para ele, inexistente.

**(b) O manifesto é legível mas está mal endereçado.** `SAC_domains.md` é markdown — ótima escolha, um agente cego consegue lê-lo e derivar Route/Context manualmente. Esse é exatamente o design certo para o princípio 3, e ninguém consegue usá-lo porque ninguém sabe que ele existe.

**(c) O índice é JSON compacto** em `sac-context/.sac/symbol_index.json` — inútil para o agente cego, o que é aceitável (é otimização), desde que hop1 não vire pré-requisito de nada.

Corrigir (a) e (b) é barato — um bloco de texto na raiz — e é o que converte o princípio 3 de aspiração em recurso.

---

## 7. Recomendações funcionais, ordenadas por pilar

| # | Ação | Pilar | Custo | Efeito |
|---|---|---|---|---|
| **F1** | Corrigir a ordem em `_is_covered`: montar `changed_symbols` **completo** antes de avaliar violações (dois laços em vez de um) | P2 | ~10 linhas | Elimina o falso positivo sistemático. **Maior razão benefício/custo do plano inteiro.** |
| **F2** | Declarar publicamente que o gate é **co-edit**, não prova de regressão; renomear a promessa no material público | P2 | doc | Impede que a primeira PR externa desminta o README |
| **F3** | Abrir `_SYMBOL_REGISTRY` a Python, JS/TS e mais uma linguagem de alto uso; publicar a lista como dimensão de primeira classe da matriz de compatibilidade | P2, P3 | médio | Torna o pilar 2 utilizável fora de Flutter; **habilita o dogfooding** que o v2 exige |
| **F4** | Emitir `file` sempre relativo à raiz, independentemente da forma do `--root` | P1 | pequeno | −16 % de payload; elimina vazamento de path; torna CLI≡MCP verdadeiro em bytes |
| **F5** | Unificar a unidade de bytes: orçamento e emissão na mesma serialização | P1 | pequeno | O orçamento passa a governar o que existe |
| **F6** | Decidir o campo `trigger`: remover, ou convertê-lo em condição de aplicação (`on=…`) | Princ. 1 e 3 | médio | Devolve o slot mais caro da linha; dá ao agente cego um filtro |
| **F7** | Porta de entrada na raiz: bloco SAC em `AGENTS.md` (tool-neutral) apontando manifesto, gramática e o caminho degradado sem MCP | Princ. 3 | pequeno | Converte o princípio 3 de aspiração em recurso |
| **F8** | Separar template/schema (managed) do manifesto do projeto (owned) — mover o manifesto para fora de `sac-context/docs/` | P1, entrega | médio, breaking | Já detalhado na v3 §1.1; aqui reaparece porque **é o que permite o dogfooding** e destrava F3 |
| **F9** | Definir a língua do vocabulário imperativo de ARCH, ou aceitar PT+EN | Princ. 2 | trivial | Remove warning permanente em base lusófona |
| **F10** | Ampliar o marcador de comentário além de `//` e `#` | P3 | pequeno | Amplia o universo de repositórios adotáveis |

**F1 é a única correção deste documento que eu faria hoje, antes de qualquer outra coisa.** Dez linhas, defeito reproduzido, e sem ela cada dia de uso corrói a disciplina que o pilar 2 existe para criar.

---

## 8. Reordenação das recomendações anteriores contra os princípios

Nada abaixo contradiz v1/v2/v3 — o que muda é a **prioridade**, agora que os pilares são o critério.

### Sobem

| Recomendação | Origem | Por quê, em termos de pilar |
|---|---|---|
| Separação `managed`/`owned` + mudança de caminho do manifesto | v2 §12.2 / v3 §1.1 | Deixa de ser higiene de installer e vira **pré-requisito de P2**: sem ela não há dogfooding, e sem dogfooding o registro de linguagens nunca é exercitado |
| Layer A (testes de engine) | v2 §14.1 / v3 §1.3 | O defeito F1 sobreviveu porque não há teste unitário de `_is_covered`. Layer A deixa de ser dívida de qualidade e vira **defesa dos pilares** |
| Matriz de compatibilidade | v2 §17 | Só se ganhar o eixo **linguagem**. Sem ele, mede a dimensão errada |

### Descem

| Recomendação | Origem | Por quê |
|---|---|---|
| Migração MCP SDK v2 (T5) | v1 §9 / v2 T5 | Zero efeito sobre os três pilares. É manutenção de protocolo com prazo de 6 meses (ADR-011 do próprio v2) e força Node 20+, um MAJOR, antes de o produto funcionar. **Depois de F1–F5.** |
| Cap global de concorrência | v1 §16 | Já `GATED` no v2, corretamente. Contra ameaça hipotética; nenhum pilar |
| Ceilings físicos de stdout/stderr | v1 §14 / v2 §5 | Proteção de memória do adapter. Nenhum pilar. O timeout já limita a janela |
| Streamable HTTP, worker persistente | ambos | Já `DEFERRED`. Corretos assim |

### Mudam de natureza

| Recomendação | Antes | Agora |
|---|---|---|
| Cancellation / árvore de processos / morte do parent | Hardening de lifecycle | Continua **P0** — mas por motivo diferente: processo órfão no Windows segura lock de arquivo, e o SAC é filesystem-centric. É defesa do P1, não higiene genérica |
| `stdout` protocol-only | Correção de protocolo | Continua P0. Lint estático resolve; o teste dinâmico do v2 é suficiente e não precisa crescer |
| Telemetria decomposta | v2 §9, pré-requisito do T0 | Continua pré-requisito — mas o campo a corrigir primeiro é `payload_bytes`, porque é o **instrumento do pilar 1** |

---

## 9. Ordem revista

```
F1   corrigir ordem em _is_covered                    ← hoje, isolado, com teste
F4+F5 path relativo + unidade de bytes única           ← P1, barato, mensurável
T-1  auditoria de estado real (v3 §5), com o eixo
     linguagem incluído
F8   separar template/manifesto                        ← destrava dogfooding
F3   ampliar registro de linguagens + dogfooding real  ← P2 passa a existir
Layer A sobre engine, domains e diff                   ← trava F1/F3 contra regressão
F6   decisão sobre o campo trigger                     ← ADR própria, é gramática
F7+F9+F10 porta de entrada, língua, marcadores         ← P3, barato
T0   baseline instrumentado (agora com instrumento
     correto)
T2/T3 extração + installer
RELEASE 0.1.0
T6   lifecycle hardening
T5   MCP SDK v2
T7/T8 escalabilidade + compatibilidade
RELEASE 1.0.0
```

Diferença material frente ao v2: **cinco correções funcionais de baixo custo antecedem toda a infraestrutura**, e a migração de SDK cai para depois da 0.1.0 e depois do hardening.

---

## 10. Resposta direta à pergunta

**Dá para melhorar funcionalmente sem violar os princípios?** Sim — e o caminho é quase todo *subtrativo*, que é o que os princípios pedem:

- **P2** não precisa de mecanismo novo. Precisa de uma correção de ordenação (F1), de uma promessa honesta (F2) e de mais entradas numa tabela (F3). Nenhuma linha a mais na tag.
- **P1** não precisa de compressão nova. Precisa parar de gastar 16 % com caminho absoluto (F4) e medir na unidade que emite (F5). Ambas removem, não adicionam.
- **Princípio 1** ganha espaço **removendo** o campo `trigger` ou fazendo-o pagar o próprio custo (F6). É a única mudança de gramática que proponho, e ela devolve orçamento em vez de consumir.
- **Princípio 3** precisa de um bloco de texto na raiz (F7). Nada de runtime, nada de protocolo.

O que **fortalece** os princípios em vez de apenas os preservar é F6 na variante `on=<condição>`: mantém uma linha, aumenta a normatização, e dá ao agente cego a capacidade de **filtrar** constraints antes de ler — que é economia de token no único lugar onde ela hoje não existe, ou seja, fora do MCP.

E o que os três relatórios anteriores não viram, com uma frase: **eles planejaram como publicar bem um produto cujo pilar do meio bloqueia mudanças corretas em qualquer repositório com testes em `test/`.**
