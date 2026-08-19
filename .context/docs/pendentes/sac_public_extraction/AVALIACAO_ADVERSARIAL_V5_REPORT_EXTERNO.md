# Avaliação Adversarial — Report Externo "Melhorias Funcionais do SAC"

**Objeto:** report externo de melhoria funcional.
**Critério:** os três princípios e os três pilares, com o princípio do **agente cego lido como obrigação de aumento** — uma melhoria funcional que apenas *preserva* o benefício ao agente cego não é melhoria, é manutenção.
**Método:** cada afirmação testável do report foi executada contra o parser e o assessor reais.

---

## 0. Veredito

**O report é o melhor dos quatro documentos em diagnóstico de *direção*, e o mais perigoso em *execução*.**

Ele acerta a tese que os outros três não formularam — *"MCP não deve compensar conteúdo SAC ruim; a melhoria deve ocorrer na qualidade das linhas persistidas"* — e a lista "Não implementar" é a melhor defesa dos princípios já escrita neste projeto.

Mas três das suas quatro recomendações P0/P1 colidem com mecânicas do código que ele não inspecionou. Uma delas é um **breaking change MAJOR do schema de domínio apresentado sob o título "Não criar novas tags"**. Duas outras se contradizem entre si. O report deixa passar um bug ativo no exato campo que elege como centro da sua proposta.

E — aplicando o critério corrigido — **nenhuma das suas quatro P0/P1 aumenta o benefício ao agente cego. Uma delas o reduz.**

Recomendação: **aceitar a direção, rejeitar duas das quatro P0 na forma proposta, e reordenar por ganho ao agente cego.**

---

## 1. Teste do princípio: quem aumenta o benefício ao agente cego?

O agente cego é o agente que abre o arquivo e lê. Ele não tem Route, não tem Context, não tem hop1, não tem CI. Tudo o que ele tem é **a linha**. Portanto, "aumentar benefício ao agente cego" significa exatamente uma coisa: **mais decisão correta por caractere lido, sem ferramenta.**

Sob esse critério, medindo cada proposta:

| Proposta | Origem | Efeito sobre o agente cego |
|---|---|---|
| Condição de mudança no campo `trigger` (`on=…`) | esta avaliação | **AUMENTA** — filtro legível antes de ler a constraint |
| Vocabulário fechado de ARCH no `trigger` | esta avaliação | **AUMENTA** — `ssot`/`boundary`/`ordering` visível em 8 caracteres |
| Corrigir truncamento de `verify:` no ponto | esta avaliação | **AUMENTA** — devolve alvos que hoje somem da linha que ele lê |
| Porta de entrada em `AGENTS.md` | avaliação funcional (F7) | **AUMENTA** — é o que torna Route e `files:` descobríveis sem MCP |
| Ampliar marcadores além de `//` e `#` | avaliação funcional (F10) | **AUMENTA** — o agente cego em SQL/Lua/HTML hoje não tem linha nenhuma |
| `verify:` = obrigação de revisão | report P0 | neutro — corrige a promessa, não a linha |
| Curadoria pós-bug | report P1 | neutro a positivo — melhora o que se escreve, sem mudar a forma |
| diff-check em duas fases | report P0 | **neutro** — é CI; o agente cego nunca o vê |
| Anchors mínimos | report P1 | **neutro** — `anchor_symbols` vive no manifesto, e o manifesto é indescobrível |
| `DIAGNOSE` como cenário-base | report P0 | **neutro**, com custo — mais linha de manifesto que ele não lê |
| REGR estruturada em prosa na constraint | report P0 | **REDUZ** — linha mais longa, condição não filtrável, constraint diluída |

Isto não invalida o diff-check nem os anchors: pilar 2 e pilar 1 são objetivos legítimos por si. Mas mostra que **o report, sendo um documento de melhoria funcional, não move o princípio 3 em nenhuma das suas propostas — e a proposta que mais desenvolve, a estrutura da REGR, move-o para trás.**

O corolário prático está em 2.7: existe um campo já normalizado, hoje inerte, que resolve simultaneamente a estrutura da REGR (report P0), a qualidade do ARCH (report P0) e o princípio 3 — sem custar um caractere.

---

## 2. O que o report acerta — e deve ser adotado sem alteração

| | |
|---|---|
| **P0 diff-check em duas fases** | Correto, e coincide com o F1 da avaliação funcional. Maior razão benefício/custo do plano. "Não alterar a semântica de `verify:`" é a ressalva certa |
| **"Não criar novas tags"** | Correto e disciplinado. Três tags é o número certo |
| **Lista "Não implementar"** | A melhor seção dos quatro documentos, e é a única que defende o princípio 3 explicitamente: `code graph`, `AST como requisito`, `geração dinâmica pelo MCP` — todos deslocam valor para fora da linha, que é onde o agente cego lê. Manter literalmente |
| **`verify:` = *regression review obligation*, não prova de teste** | Nomeia com precisão o que `_is_covered` faz. Resolve em uma frase a promessa inflada do material público |
| **Invariante funcional** | É o critério certo. Deve virar texto normativo |
| **Pós-bug com portão** | Protege o pilar 1 contra o modo de falha mais provável: o corpus inchar por reflexo |

Verificado — **o exemplo de REGR do report parsa corretamente** no engine atual:

```
// SAC:REGR: WARNING - A: If changing normalization order, MUST preserve
   downstream key identity; MUST verify: CacheKey, PersistenceAdapter

→ symbol='A'  trigger='WARNING'  verify=['CacheKey','PersistenceAdapter']  warnings=[]
```

Inclusive com ponto no meio da constraint. O report não propôs gramática inválida.

---

## 3. Defeitos verificados

### 3.1 [BLOQUEANTE] `DIAGNOSE` como cenário-base é um MAJOR silencioso

O report lista:

```text
SUMMARY
EXTEND
DIAGNOSE
REGRESSION
```

sob a afirmação de que não cria tag nova. Correto quanto a tags — e irrelevante, porque o custo não está nas tags.

`sac_domains.py:36-38`:

```python
_BASE_SCENARIOS     = frozenset({"SUMMARY", "EXTEND", "REGRESSION"})   # obrigatórios
_OPTIONAL_SCENARIOS = frozenset({"MIGRATION"})                          # opcionais
```

`sac_domains.py:225` — domínio sem um cenário-base ⇒ `scenarios_base_missing` ⇒ **`INVALID_CONTRACT`**.

Se `DIAGNOSE` entrar como base:

- **todo domínio já onboardado com capillarity vira `INVALID_CONTRACT` imediatamente**;
- cada um precisa de nova linha de claim, senão `missing_roles` ⇒ `TOO_THIN` (`sac_engine.py:1039`);
- `quality_status` cai de PASS para FAIL em toda a base instalada.

É a categoria que o v2 §6.3 classifica como **MAJOR** ("schema de domínio incompatível"), proposta como P0 de qualidade. Sem menção a migração, compatibilidade ou base instalada.

A alternativa não-quebradora já existe no código: entrar em `_OPTIONAL_SCENARIOS`, como `MIGRATION`. Mas aí é opt-in, e não produz o efeito de corpus que o report quer.

### 3.2 [ALTO] Como cenário, `DIAGNOSE` é cerimônia: custa linha e não prova nada novo

`sac_engine.py:964` fecha o mapa cenário → tag_type exigida:

```python
"SUMMARY": "ARCH",  "EXTEND": "ARCH",  "REGRESSION": "REGR",  "MIGRATION": "ARCH"
```

`DIAGNOSE` só pode mapear para `ARCH` — não há tag de diagnóstico, e o report corretamente proíbe criar uma. Logo **uma claim `DIAGNOSE` é satisfeita pelas mesmas tags ARCH que já satisfazem `SUMMARY` e `EXTEND`.** O domínio ganha uma linha e **zero** requisito estrutural novo.

Contra o pilar 1, perda líquida. Contra o princípio 3, custo puro: o manifesto é markdown, então cresce o arquivo que o agente cego teria de ler — e ele não ganha nada em troca.

O critério que o próprio report define —

> "o agente consegue reduzir uma falha a um slice inicial plausível **sem busca global**?"

— não é propriedade de `tag_type` nenhuma. É propriedade do **`files:` boundary + anchors**, medida por comportamento. **`DIAGNOSE` pertence ao benchmark do P1 do próprio report, não ao schema.** O report o coloca nos dois lugares; só um funciona.

**Correção:** manter `DIAGNOSE` exclusivamente como cenário de benchmark. Zero schema, zero breaking. E aí ele passa a servir ao princípio 3 por via indireta e legítima: um domínio que passa em DIAGNOSE tem `files:` e anchors bons o bastante para um agente **sem MCP** achar o slice — desde que exista a porta de entrada (F7).

### 3.3 [ALTO] O P1 "minimizar anchors" contradiz o P0 "DIAGNOSE"

`sac_engine.py:981` — o Context seleciona uma tag se `symbol ∈ anchors` **ou** `tag_type ∈ {REGR, DEPRECATED}`.
`sac_engine.py:1019-1042` — claim casada cujo alvo **não** está no selecionado ⇒ `context_unfit_claims` ⇒ **`UNFIT`**.

Combinando: **toda claim `ARCH` obriga que seu símbolo seja anchor.** Não é recomendação, é condição de PASS.

Portanto:

- o P1 ("anchors = menor conjunto necessário") tem um **piso rígido** invisível no report: o conjunto de símbolos das claims ARCH. Abaixo dele ⇒ `UNFIT` ⇒ FAIL;
- o P0 `DIAGNOSE`, mapeando para ARCH, exige **mais uma** claim ARCH ⇒ potencialmente **mais um anchor**.

**P0 empurra anchors para cima; P1 os empurra para baixo; o eixo de fitness torna as duas pressões simultaneamente vinculantes.** As duas recomendações não são executáveis juntas como escritas.

A intenção do P1 continua certa. Falta reconhecer que anchors não são livres: para minimizá-los é preciso minimizar **antes** as claims ARCH.

### 3.4 [ALTO] Acoplamento oculto: enriquecer tags infla o manifesto

`sac_engine.py:1037` — `uncontracted_context_count = |context_selected| − contracted_in_context`; qualquer excedente ⇒ **`OVER_SELECT`**.

Como `context_selected` inclui **automaticamente toda REGR e toda DEPRECATED**, segue que **cada REGR nova exige uma claim nova** para o domínio não sair de FIT.

O P0 do report pede REGR mais rica — "grafo compacto de risco". Cada aresta custa uma linha de tag **mais** uma linha de claim. O manifesto cresce linearmente com o número de tags.

O report quer simultaneamente "mais densidade semântica" e "menos contexto persistido". No mecanismo atual essas metas são **antagônicas por construção** — e a vítima adicional é o princípio 3, porque o manifesto é justamente o artefato legível sem MCP.

Esta é a questão de design mais importante em aberto no SAC: **o contrato de capillarity taxa a densidade.** Ou as claims deixam de ser 1:1 com tags, ou pilar 1, qualidade de corpus e agente cego permanecem em conflito.

### 3.5 [BLOQUEANTE — bug novo] `verify:` trunca no ponto e **descarta alvos em silêncio**

O report elege `verify:` como centro da proposta e não testa o campo. Testado:

```
verify: Cache.key, Adapter     →  ['Cache']                 ← 'Adapter' sumiu. warnings=[]
verify: CacheKey, Adapter.     →  ['CacheKey','Adapter']    (ponto final: ok)
Se mudar X, entao Y. MUST verify: CacheKey  →  ['CacheKey'] (ponto no meio: ok)
```

Causa: `_VERIFY_TERMINAL_RE = r".*\bverify:\s*(?P<targets>[^.]+)"`. A classe `[^.]+` **para no primeiro ponto**; tudo depois é descartado, sem warning.

Agravante de normatização: a `sac-evolution` declara que `verify:` aceita tokens `[A-Za-z_][A-Za-z0-9_.$-]*` — **com ponto**. Gramática declarada e parser se contradizem, e quem perde é o parser, em silêncio.

Blast radius: `Cache.key`, `user.service`, `Order.validate`, métodos em JS/Dart/Kotlin, testes versionados (`test_charge.v2`).

Impacto no princípio 3, que é o que torna isto P0 e não P1: o agente cego **lê a linha inteira** e vê `Cache.key, Adapter`. O agente com MCP recebe `['Cache']`. **A ferramenta entrega menos que a leitura crua** — inversão exata do contrato do produto, e um estado em que MCP e agente cego discordam sobre o mesmo texto.

### 3.6 [MÉDIO-ALTO] Os critérios de qualidade não têm mecanismo — e viram a doc paralela que o report proíbe

O report define qualidade de `ARCH` como "ownership, SSOT, boundary, ordering, state invariant, exclusividade" e manda "evitar linhas que apenas descrevem o código".

Hoje o único enforcement é `_ARCH_IMPERATIVE_RE` (`sac_engine.py:107`): presença de `MUST|NEVER|ONLY`. `"MUST call save()"` passa e viola todos os critérios do report.

Sem mecanismo, os critérios só vivem em prosa de skill — e a lista "Não implementar" do próprio report veta **"documentação causal paralela"**. O report propõe um controle que, na única forma em que poderia existir, ele mesmo veta. Pior para o princípio 3: prosa de skill é invisível ao agente cego por definição.

Saída subtrativa e normativa: transformar as seis categorias em **vocabulário fechado**, como `_ALLOWED_TRIGGERS` e `_ALLOWED_SCENARIOS` já são. Há campo livre para isso, e ele não custa um caractere — ver 3.7.

### 3.7 [ALTO] O único movimento que aumenta o benefício ao agente cego, e o report passa ao lado dele

O report define a forma da boa REGR:

```text
condição de mudança → risco/invariante afetada → targets mínimos
```

e a codifica **na constraint, em prosa**: `"If changing normalization order, MUST preserve…"`.

Isso custa caracteres no recurso mais escasso (princípio 1), produz algo **não processável** (princípio 2) e — o ponto decisivo — **reduz** o benefício ao agente cego (princípio 3): a linha fica mais longa, a condição fica misturada à obrigação, e ele precisa **ler tudo** para descobrir se a constraint sequer se aplica ao que vai fazer.

Enquanto isso, o campo `trigger` está a três caracteres de distância carregando `WARNING` — que, verificado, **não altera comportamento algum**: `diff_check` bloqueia qualquer REGR não coberta independentemente do trigger, e `RULE` vs `CONSTRAINT` não é distinguido em lugar nenhum do engine. O report usa `WARNING` no próprio exemplo sem examinar o que ele faz.

```
hoje    // SAC:REGR: WARNING - A: If changing normalization order, MUST preserve
                                  downstream key identity; MUST verify: CacheKey

alvo    // SAC:REGR: on=normalization_order - A: MUST preserve downstream key
                                              identity. verify: CacheKey
```

Mesma linha ou mais curta. E, para o agente cego, a mudança é qualitativa:

- hoje ele precisa **ler todas** as constraints do arquivo para saber quais se aplicam à sua tarefa;
- com `on=`, ele **grepa** `SAC:` e descarta por condição antes de ler o texto.

É economia de token no único lugar onde hoje ela não existe — fora do MCP. Nenhuma outra proposta em nenhum dos quatro documentos faz isso.

Para ARCH, o mesmo slot absorve o vocabulário de 3.6: `on=ssot`, `on=boundary`, `on=ordering`, `on=state`, `on=exclusive`, `on=ownership`. O agente cego passa a saber **que tipo de invariante** enfrenta antes de ler a frase — e o validador ganha um vocabulário fechado para fazer cumprir a qualidade que o report pede.

Uma mudança de gramática, compatível com o parser dual que já existe, que atende de uma vez: report P0 (estrutura da REGR), report P0 (qualidade do ARCH), princípio 1, princípio 2 e princípio 3.

### 3.8 [MÉDIO] Curadoria exigida, metadata de curadoria proibida

O invariante do report exige persistir "somente conhecimento cuja ausência aumente a probabilidade de reincidência", e o P1 pós-bug cria tags a partir de investigações concretas.

Mas a lista "Não implementar" veta **provenance** e **documentação causal paralela**. Sem registro de por que uma tag existe, não há como decidir depois se ela ainda se paga. O corpus só cresce — e cada tag morta é ruído que o agente cego lê integralmente.

O report tem P0 e P1 para **entrada** de conhecimento e **nenhum** para saída. `TAG_DELTA` suporta `REMOVE`, mas nada gera o sinal de quando usá-lo. `OVER_SELECT` sinaliza tag sem contrato, não tag obsoleta.

O veto é a `provenance no hot path`, e está certo. Falta permitir explicitamente o caminho frio: campo opcional fora do payload de Context, ou sinal derivado (símbolo sem mudança há N releases e sem violação registrada).

### 3.9 [MÉDIO] O benchmark do P1 é uma harness de eval, não uma medição — e sua métrica de agente cego mede a metade fácil

"arquivos abertos até o slice correto", "tokens em discovery", "root cause em DIAGNOSE", "regressões introduzidas" — nada é observável pelo SAC, que não vê o que o agente abre. Cada métrica exige tarefas rotuladas, ground truth, execução com e sem SAC e — sendo o sujeito um LLM — **N execuções com variância**. "Regression Recall" exige ainda **anotação manual** do que era relevante.

É trabalho de harness, provavelmente o segundo maior item de custo do plano (o primeiro é a Layer A de testes), apresentado em cinco bullets como instrumentação.

E a métrica **Blind-Agent Utility** está escopada a "apenas o arquivo contendo tags". Honesto e testável — e por isso mesmo mede só a metade fácil. A metade que decide o princípio 3 é se o agente cego **chega** ao arquivo certo: Route, `files:` como limite de busca, boundary do domínio. Como está, a métrica não consegue detectar melhora nem piora naquilo que mais importa para o princípio que ela leva no nome.

### 3.10 [ALTO] Três omissões que bloqueiam o próprio report

- **`_SYMBOL_REGISTRY` = `.dart` + `.ps1`** (`sac_diff.py:36`). O P0 de duas fases corrige a ordenação de um gate que faz `FAIL CLOSED` em Python, JS/TS, Go, Java e todo o resto. E o benchmark do P1 não pode ter piloto fora de Dart/PowerShell.
- **16,1 % do payload é caminho absoluto** (medido). "Context Compression Effectiveness" mediria essa perda como característica do SAC, quando é defeito de uma linha.
- **`AGENTS.md` não menciona SAC.** É a omissão mais grave sob o critério corrigido: sem porta de entrada, o agente cego só encontra uma tag **por acidente**, e todo o pilar 1 (Route, boundary, `files:` como limite de busca) é inexistente para ele. O report propõe medir utilidade ao agente cego sem propor nada que a aumente.

---

## 4. Onde o report e a avaliação funcional convergem

1. diff-check em duas fases é P0 (report P0 = F1);
2. `verify:` é obrigação de revisão, não prova de teste (report explicita = F2);
3. o valor está na linha persistida, não no MCP (tese do report = princípio 3 levado a sério).

A divergência é de escopo, não de direção: o report otimiza a **qualidade** do corpus assumindo que os mecanismos que o consomem funcionam. Três não funcionam — ordenação, truncamento de `verify:`, registro de linguagens — e dois dos que funcionam (fitness e claims) impõem restrições que invalidam duas das suas recomendações.

---

## 5. Recomendação consolidada

**Adotar sem alteração:** P0 diff-check duas fases · `verify:` como obrigação de revisão · curadoria pós-bug · invariante funcional · lista "Não implementar" (acrescentando permissão explícita de provenance **fora** do hot path, por 3.8).

**Adotar com correção:**

| Item do report | Correção exigida |
|---|---|
| `DIAGNOSE` | **Somente** cenário de benchmark. Fora do `_BASE_SCENARIOS`. Zero mudança de schema |
| Minimizar anchors | Reconhecer o piso: minimizar **claims ARCH primeiro**; anchors seguem |
| Qualidade de ARCH | Vocabulário fechado no campo `trigger` (3.7), não prosa em skill |
| Estrutura da REGR | Condição no `trigger` normalizado, não na constraint em prosa — **é aqui que o princípio 3 aumenta** |
| Benchmark | Precificar como harness; e escopar Blind-Agent Utility também ao *encontrar* o arquivo, não só ao lê-lo |

**P0 novo, ausente do report:** truncamento de `verify:` no ponto (3.5). Prioridade igual ao diff-check, e superior sob o princípio 3: é o único defeito conhecido em que o MCP entrega **menos** do que a leitura crua da linha.

**Ordem, agora ponderada por ganho ao agente cego:**

```
1. verify: truncamento no ponto        P0  AUMENTA agente cego  (MCP < leitura crua)
2. ADR do campo trigger (on=…)         P0  AUMENTA agente cego  (absorve 3.6 e 3.7)
3. porta de entrada em AGENTS.md       P0  AUMENTA agente cego  (barato, destrava pilar 1 sem MCP)
4. diff-check duas fases               P0  neutro               (report P0 = F1)
5. _SYMBOL_REGISTRY: Python, JS/TS     P1  neutro               (destrava pilar 2 e o benchmark)
6. path relativo + unidade de bytes    P1  neutro               (pilar 1: 16 % + 1,215×)
7. DIAGNOSE como cenário de benchmark  P1
8. desacoplar claims de tags (3.4)     P1  (design em aberto)
9. marcadores além de // e #               AUMENTA agente cego
10. harness de benchmark
```

Diferença frente à ordem anterior: **os três primeiros itens deixaram de ser escolhidos por custo e passaram a ser escolhidos por princípio.** Os itens 1, 2, 3 e 9 são os únicos de toda a coleção de quatro relatórios que aumentam o benefício ao agente cego; os demais defendem os outros dois pilares e são, sob o princípio 3, manutenção.

---

## 6. Veredito

O report externo está **certo sobre onde investir** — a linha persistida, não o protocolo — e é o único dos quatro documentos que enuncia isso. Sua lista de vetos deve virar política pública literalmente.

Onde ele erra é sempre no mesmo lugar: **propõe contra o sistema descrito, não contra o sistema executado.** É o defeito que o v2 tinha na dimensão de infraestrutura, repetido na dimensão funcional. O sintoma é característico: a proposta é coerente consigo mesma e incompatível com uma mecânica de três linhas que ninguém abriu.

Duas das quatro P0/P1 não são executáveis na forma escrita: `DIAGNOSE` como cenário-base quebra a base instalada, e "minimizar anchors" é contraditório com ela. Uma terceira, a estrutura da REGR, funciona — mas escolhe o suporte mais caro, menos processável e **pior para o agente cego**, quando há um campo normalizado inerte ao lado que faria o oposto nas três dimensões.

E o campo que o report coloca no centro da sua proposta perde alvos em silêncio quando o nome tem um ponto — de modo que, hoje, quem lê a linha crua sabe mais do que quem chama a ferramenta.

---

# Adendo — M9: Camada de atalho das skills

**Motivação:** "aponta a skill e o agente já sabe o que fazer." Hoje isso não acontece, e o motivo é ergonômico, não conceitual.

## 7.1 Estado auditado

Quatro skills do mesmo produto, **quatro ergonomias diferentes**:

| Skill | Entrada | Cadeia |
|---|---|---|
| `sac-context` | só `SKILL.md` | **nenhum atalho** |
| `sac-onboard` | `prompt_resumido.md` → `PROMPT.md` → `SKILL.md` | 3 níveis |
| `sac-execution-overlay` | `PROMPT.md` → `SKILL.md` | 2 níveis |
| `sac-evolution` | atalho embutido no fim do `SKILL.md` | 1 nível, escondido |

Defeitos verificados:

**(a) [BLOQUEANTE] O artefato de atalho embute o caminho da máquina do autor.**
`sac-onboard/prompt_resumido.md` abre com:

> *"se este arquivo foi aberto em `C:\Users\Rabelo\projects\rabelo-standards\skills\...`, leia integralmente `C:\Users\Rabelo\projects\...\PROMPT.md`"*

É **a primeira instrução que o agente lê**. Em qualquer consumidor, o caminho não existe — o atalho começa mandando o agente resolver algo impossível, e a resolução do harness cai justamente na heurística que o próprio arquivo proíbe. Mesmo defeito dos `.pyc` versionados, num lugar muito pior. Também presente em `sac-onboard/PROMPT.md`.

**(b) [ALTO] Duas skills disputam o mesmo gatilho.** As descrições de frontmatter são quase idênticas:

```
sac-context           "Gate de contexto para qualquer pergunta, plano, review ou implementação…"
sac-execution-overlay "Gate obrigatório para qualquer pergunta, plano, review ou implementação…"
```

O roteador de skills não tem como escolher. O usuário aponta e o agente adivinha — o oposto do objetivo.

**(c) [MÉDIO] `sac-context` e `sac-evolution` não têm entrada curta.** Duas das quatro skills só podem ser acionadas lendo o `SKILL.md` inteiro (195 e 342 linhas).

**(d) [MÉDIO] Defeito de edição no atalho quente.** `sac-execution-overlay/PROMPT.md` tem o item **`15.` duplicado** e duas linhas `Pipeline:` divergentes:

```
Pipeline: boot → list_sac_domains → get_sac_context → Verify se alvo → edit/read
Pipeline: boot → Route → Context ou bounded-unmapped → Verify/Discover → Capillarity(on-demand) → Gate
```

**(e) [ALTO — princípio 3] Nenhum atalho serve o agente cego.** Todos assumem MCP. O overlay tem o item 7 ("MCP down → CLI+jq"), mas o agente sem MCP nunca chega ao `PROMPT.md`: não há nada na raiz que o mande até lá.

**(f) O melhor artefato de ergonomia do repositório está em uma skill só.** A tabela *"frase do usuário → contrato derivado"* do `prompt_resumido.md` é exatamente o mecanismo que o usuário pede — uma linha vira contrato, sem heurística — e existe apenas no `sac-onboard`.

## 7.2 M9 — proposta

Camada de atalho **normalizada**, subtrativa (remove um nível, não adiciona artefato):

1. **Nome único de entrada nas quatro skills: `PROMPT.md`.** Já é maioria (2 de 4). `prompt_resumido.md` é absorvido — a cadeia passa de três níveis para dois: `PROMPT.md` (atalho, ≤ 1 tela) → `SKILL.md` (contrato).
2. **Resolução do irmão sempre relativa.** Zero caminho absoluto, zero nome de máquina, zero nome do monorepo. Corrige (a) e é pré-requisito de publicação.
3. **Tabela "frase → contrato derivado" obrigatória nas quatro.** Generaliza (f), que já provou funcionar.
4. **Um verbo de atalho estável e disjunto por skill**, com prefixo único — mesma disciplina de vocabulário fechado de `_ALLOWED_TRIGGERS`:

   ```
   SAC              → sac-execution-overlay   (caminho quente: Route → Context → Verify)
   SAC ONBOARD <id> → sac-onboard             (ASSESS default, read-only)
   SAC TAG          → sac-context             (gramática: o que é tag, como escrever)
   SAC EVOLVE       → sac-evolution           (mudar o padrão)
   ```

   Convive com os literais já existentes (`APROVAR SAC REGISTER <id>`, `APROVAR SAC TAG_DELTA <id>`), que continuam sendo os únicos que autorizam Write.
5. **Desambiguar as descrições de frontmatter** (b): `sac-context` = *gramática e escrita de tag*; `sac-execution-overlay` = *gate de execução*. Gatilhos disjuntos.
6. **Bloco "sem MCP" no topo de cada `PROMPT.md`** — o comando CLI equivalente, em duas linhas. Isso, somado à porta de entrada em `AGENTS.md` (A3), fecha o caminho: o agente cego chega ao atalho e o atalho lhe dá o comando.
7. **Corrigir o item 15 duplicado e a linha `Pipeline:` divergente** no overlay (d).

## 7.3 Classificação

**M9 é melhoria, não adição:** remove um nível de indireção, remove caminhos de máquina, remove ambiguidade de gatilho e remove uma duplicação — e o único conteúdo novo (tabela frase→contrato nas outras três) é replicação de algo que já existe e funciona.

Efeito sobre o princípio 3: **AUMENTA**, via item 6 — é o par obrigatório de A3. Sem M9, `AGENTS.md` aponta para skills cuja entrada assume MCP; com M9, o agente cego recebe o comando executável no mesmo lugar.

## 7.4 Posição na ordem

M9 entra junto com A3, e o item (a) — caminhos absolutos no artefato de atalho — sobe para **P0 de extração**: é impeditivo de publicação, pela mesma razão dos `.pyc`.

```
1. verify: truncamento no ponto        P0  AUMENTA agente cego
2. ADR do campo trigger (on=…)         P0  AUMENTA agente cego
3. A3 + M9  porta de entrada + atalhos P0  AUMENTA agente cego
4. diff-check duas fases               P0  neutro
5. _SYMBOL_REGISTRY: Python, JS/TS     P1  neutro
6. path relativo + unidade de bytes    P1  neutro
7. DIAGNOSE como cenário de benchmark  P1
8. desacoplar claims de tags           P1  (design em aberto)
9. marcadores além de // e #               AUMENTA agente cego
10. harness de benchmark
```
