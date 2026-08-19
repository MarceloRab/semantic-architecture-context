# SAC — Extração Pública: Terceira Avaliação (Adversarial, com acesso ao repositório)

**Objeto:** relatórios v1 ("Extração Pública e Hardening MCP") e v2 ("Arquitetura Pública e Hardening MCP v2").
**Método:** leitura do código real em `sac-context/`, `skills/sac-evolution/`, `skills/catalog/domains/context-governance/{sac-context,sac-onboard,sac-execution-overlay}/` e `scripts/mirror-sac-tooling.ps1`, com execução do CLI sobre fixture controlada.
**Postura:** adversarial. O que segue são defeitos verificados no código, não preferências de estilo.

---

## 0. Veredito

**v1 e v2 estão arquiteturalmente corretos e empiricamente desinformados.**

Ambos raciocinam a partir da descrição do sistema (docstrings, skills, contratos declarados), não a partir do estado do sistema. As camadas, os ADRs, a ordem das tracks e a disciplina de gates são sólidos — mantenha. O que falha é a **premissa factual** de várias seções normativas: o v2 escreve invariantes que o layout atual torna inimplementáveis, gates que o código atual já falharia, e um modelo de ameaça que declara fora de escopo exatamente o ator que a publicação cria.

O v2 é melhor que o v1 em quase tudo (modelo de ameaça, tiers, precedência de limites, `serveStdio`, ADR-010). Mas o v2 herda do v1 o defeito estrutural: **auditoria não foi feita antes de normatizar.**

Recomendação: **GO condicionado** a uma track nova, anterior a tudo (T-1 abaixo), e a sete correções normativas no v2.

---

## 1. Defeitos factuais verificados no código

### 1.1 [BLOQUEANTE] O arquivo `owned` mora dentro da árvore `managed`

`sac-context/src/sac_domains.py:14`:

```python
_DOMAINS_REL = os.path.join("sac-context", "docs", "SAC_domains.md")
```

O manifesto do consumidor — o único arquivo classificado `owned` no §12.2 do v2 — é um caminho **hardcoded dentro do diretório que o installer sobrescreve**. Pior: o mesmo caminho serve, no repositório SAC, como *schema + template + manual de uso* (`## _template`, tabela COR-3, seção "Como usar").

Consequências, todas presentes hoje:

1. O `mirror-sac-tooling.ps1:121-133` resolve isso por exclusão de nome. Funciona — e por isso **o consumidor nunca recebe atualização do schema, do template nem do manual COR-3**. O documento normativo do padrão está congelado na versão do dia do bootstrap, permanentemente, em todo projeto filho. Isso não é um risco de upgrade; é uma regressão silenciosa já em produção.
2. `rabelo-standards` **não faz dogfooding** hoje: não existe `SAC_domains.md` de projeto, porque o único slot disponível já está ocupado pelo template. O gate T2 do v2 ("dogfooding: o repositório SAC valida a si mesmo com SAC no CI") não é um checkbox — é trabalho novo, com conflito de layout, e o v2 o precifica como se fosse configuração.

A classificação `managed`/`owned`/`seeded` do v2 é a análise certa e **não é implementável no layout atual**. O que ela exige de verdade é uma mudança de caminho:

```
sac-context/docs/SAC_domains.md   →  template/schema (managed, sempre atualizado)
<root>/.sac/domains.md (ou eq.)   →  manifesto do projeto (owned, nunca tocado)
```

Isso é breaking para todo consumidor existente e para `sac_domains.py`, `sac-onboard`, `mirror`, docs e as três skills. Precisa acontecer **em T2/T3, antes da 0.1.0** — depois de publicar, o custo multiplica pelo número de consumidores.

### 1.2 [ALTO] Existia um segundo adapter MCP, com semântica divergente

Existia um servidor MCP Python legado que expunha `get_sac_constraints` chamando `sac_engine.lookup` **diretamente**, com `root = os.getcwd()`, sem passar por `sac_domains`. Resultado: sem gate de membership, sem `filepath_required` PAUSE, `filepath` opcional de verdade.

Ou seja: **a paridade CLI ≡ MCP já é falsa hoje**, para um dos dois adapters. Ele está marcado "LEGACY / debug" em docstring e no invariante DP-1 da `sac-evolution` — mas marcação em comentário não é gate. Nenhum dos dois relatórios menciona sua existência; o ADR-003 do v2 ("Node MCP adapter é thin") fala no singular de um sistema que tem dois.

Decisão exigida antes de T2: **deletar** (recomendado — a CLI já é o fallback de debug) ou **manter e submetê-lo aos mesmos gates**, o que contradiz o C2/DP-1 (stdlib-only) e adiciona uma superfície de release Python que o ADR-008 quis adiar.

### 1.3 [ALTO] Não existe suíte de testes para engine, domains ou CLI

Busca por `test_*.py` / `conftest.py` / `*.test.mjs` sob `sac-context/`: **zero**. A única verificação é `sac-context/mcp/smoke.mjs` (873 linhas).

Isto inverte a leitura que ambos os relatórios fazem da estratégia de testes:

- **A Layer A do v2 (Python engine: grammar, Route, Context, Discover, Verify, domains, capillarity, diff, validate) não existe.** São ~3.400 linhas de Python sem um único teste unitário. O v2 apresenta as Layers A–E como *separação* de testes existentes; na verdade A é construção do zero e é, de longe, o maior item de custo do plano inteiro. Nem v1 nem v2 o dimensionam ou o sequenciam.
- **O smoke é subestimado.** Ele já faz parity CLI≡MCP por fixture, checa forma do catalog, slimness do discover, PAUSE negativo, membership, hop1 scoped, overflow de contexto. Isso é Layer B + Layer C + corpus de paridade, não "Layer E smoke". O "corpus golden" do T0 do v2 deve ser **extensão do smoke**, não artefato paralelo.
- O gate do T2 ("corpus golden passa no repo novo") é um proxy fraco de equivalência comportamental quando não há teste unitário embaixo. Um refactor de extração que preserve o smoke pode quebrar caminhos que o smoke nunca toca.

Nota operacional: `smoke.mjs` importa `server.mjs`, que importa o SDK. Sem `npm install` o smoke não roda **nem para as checagens puramente CLI**. Em CI de contributor externo isso é um ponto de falha gratuito.

### 1.4 [ALTO] `_perf.payload_bytes` não mede o que os dois relatórios assumem

`server.mjs`: `withPerf` calcula `Buffer.byteLength(JSON.stringify(payload))` — payload **sem** `_perf` e **sem** indentação. `jsonToolResult` então emite `JSON.stringify(obj, null, 1)` — **com** `_perf` e **com** indentação.

Medido sobre uma fixture de 3 constraints:

```
_perf.payload_bytes reporta:            1.599 bytes
bytes efetivamente escritos em stdout:  2.101 bytes
sub-relato:                             23,9 %
```

O §9.1 do v2 define `payload_bytes` como "bytes UTF-8 emitidos ao host". O campo existente **não é isso**, e o v2 o adota como parte da telemetria de baseline sem verificar. Baseline construído sobre esse número já nasce com ~24 % de erro sistemático — exatamente o tipo de erro que invalida os gates de §13.

### 1.5 [MÉDIO-ALTO] O orçamento semântico mede uma unidade que o sistema não emite

`sac_engine.py:636` mede o payload com `separators=(",",":")` (compacto). `sac_scan.py` imprime com `indent=1`. Medido:

```
compacto (unidade do budget): 1.599 bytes
indent=1 (o que a CLI imprime): 1.942 bytes   → 1,215×
```

Logo `SAC_CONTEXT_MAX_BYTES=12288` autoriza ~14,9 KB de stdout pela CLI e mais pelo MCP. A regra 3 do §5 do v2 ("ambos os limites contam bytes UTF-8 do stream, unidade única") está certa como norma e **descreve um sistema que não é o atual**. A regra 1 (`SAC_MAX_CLI_STDOUT_BYTES > SAC_CONTEXT_MAX_BYTES + margem`) tem de ser derivada dessa razão medida, não de "margem de envelope".

Correção adicional de fato: o §5 do v2 afirma que `context_payload_too_large` retorna "exit code de sucesso operacional". Falso — `sac_scan.py:444` retorna **1**. O adapter só o aceita porque `child.on("close")` tem um caminho especial que parseia stdout em exit≠0 e aceita se `parsed.error || parsed.mode === "capillarity"`.

### 1.6 [ALTO] O payload já vaza caminhos absolutos de máquina — e o v2 mira no lugar errado

O adapter sempre passa `--root <absoluto>`. O engine prefixa `file` com a string de root recebida. Verificado:

```
--root fx        → "file": "fx/lib/a.py"
--root $PWD/fx   → "file": "/tmp/.../fx/lib/a.py"     ← o que o MCP sempre produz
```

Dois efeitos que nenhum relatório captura:

1. **T6 do v2 já é realidade, e no payload, não na telemetria.** O §9.2 do v2 exige que "campos que contenham path sejam omissíveis por configuração" — mas restringe isso a telemetria. O vazamento primário é o corpo da resposta: cada match, cada warning e o `_perf.sac_root` carregam o caminho absoluto da máquina do usuário para dentro do contexto do LLM e, conforme o host, para telemetria de terceiros. `DECISION-6` está mal escopada.
2. **A paridade CLI≡MCP é condicional à forma do root.** O usuário que roda `python sac_scan.py lookup X --root .` recebe bytes diferentes do que o MCP recebe para a mesma consulta lógica. O smoke não detecta porque chama a CLI com a mesma string de root do adapter. E aqui a ironia: o §14.6 do v2 exige normalizar paths antes de comparar o corpus golden — **essa normalização esconderia exatamente este defeito**. Normalização prescrita como remédio é, neste caso, supressão de sinal. O corpus precisa de um caso explícito que compare root relativo vs. absoluto **sem** normalizar.

### 1.7 [ALTO] Três escapes de HALT são alcançáveis via MCP e não são atestados na resposta

`runCliJson` faz `{ ...process.env, ...opts.env }` — o subprocesso herda todo o ambiente do host. Portanto `SAC_ALLOW_UNSCOPED`, `SAC_ALLOW_FILEPATH_OUTSIDE_DOMAINS` e `SAC_ALLOW_HOP1_FULL_SCAN`, documentados como "debug", são configuráveis pelo bloco `env` do arquivo de config do host MCP e valem para todas as chamadas.

Verificado:

```
$ sac_scan.py lookup hidden_sym --root fx --path secret/s.py --json
{"error": true, "code": "filepath_not_in_sac_domains", ...}

$ SAC_ALLOW_FILEPATH_OUTSIDE_DOMAINS=1 sac_scan.py lookup hidden_sym --root fx --path secret/s.py --json
{"found": true, "matches": [{"file": "fx/secret/s.py", ...}], ...}
```

O payload permissivo é **indistinguível** de um payload gated: nenhum campo `gates_bypassed`, nenhum warning. O agente não tem como saber se a resposta que recebeu respeitou o contrato de domínio.

Sob o próprio §2.2 do v2 (host = *semi-confiável*, "pode ter bugs"), este é precisamente o caso que importa, e o §21 ("MUST NOT relaxar HALTs") o trata como regra para o executor futuro enquanto o código já embarca três relaxamentos silenciosos. **Requisito novo:** toda resposta MUST declarar os gates ativos/burlados; o smoke MUST cobrir cada escape ligado.

### 1.8 [MÉDIO] Artefatos com caminhos da máquina do autor estão versionados

`git ls-files sac-context/src/__pycache__` retorna quatro `.pyc` **rastreados**. Dentro:

```
C:\Users\Rabelo\projects\rabelo-standards\sac-context\src\sac_engine.py
```

Três problemas: (a) o §1.2 do v2 ("sem dependência de paths de máquina específica") é violado pelo próprio conteúdo do repo; (b) publicar carrega isso para o histórico público; (c) `Copy-Item` preserva `LastWriteTime`, então um projeto espelhado pode **executar bytecode obsoleto** se o par mtime/tamanho bater — hazard de correção real, não cosmético. São `.pyc` de CPython **3.12**, enquanto `DECISION-1` ainda trata a versão de Python como indefinida.

Corolário: nenhum dos relatórios trata do **histórico git** na extração. Publicar exige decidir entre carregar 52 commits não auditados ou iniciar do zero, e exige uma varredura de segredos no histórico. Isso é gate do T2 e está ausente nos dois.

### 1.9 [MÉDIO] Erros de classe "ambiente/uso" são apagados no adapter

`sac_scan.py` usa exit **2** para "root não é diretório" e argparse usa exit 2 para erro de uso — ambos escrevem só em **stderr**, stdout vazio. O adapter então cai no ramo "empty stdout" e devolve `Error` genérico, que o handler converte em `lookup_failed` / `context_failed`.

Ou seja: o §4.3 do v2 propõe duas classes (`sac.` semântica, `mcp.` transporte) para um sistema que tem **três**. A terceira — falha de uso/ambiente da CLI, exit 2 — hoje é indistinguível de falha de transporte, e é a classe com a maior probabilidade de ocorrer na primeira instalação de um usuário desconhecido. Exatamente o caminho do §1.2 ("projeto desconhecido, máquina limpa").

### 1.10 [BAIXO] Identidade de versão tripla

`package.json` diz `1.0.0`; `new McpServer({version: "1.6.0"})`; a `sac-evolution` fala em "MCP v1.6.0+" como gate de DoD (D4). Três fontes, nenhuma canônica. O §6 do v2 introduz semver público sem resolver de onde a versão vem nem quem a valida em CI.

### 1.11 [BAIXO] Código morto no adapter

`runCliJson` tem `if (!cliArgs.includes("--root")) args.push("--root", root)`, mas **todos** os call sites já injetam `--root`. Ramo inalcançável. Irrelevante isolado; relevante porque é do tipo de coisa que a Layer C do v2 deveria pegar e não pegaria, já que o v2 especifica testes por cenário, não por cobertura.

---

## 2. Defeitos de raciocínio nos relatórios

### 2.1 O modelo de ameaça do v2 exclui o ator que a publicação cria

O §2.4 declara "adversário remoto — fora de escopo". Correto para o runtime local. **Incorreto para o projeto publicado.**

`sac-context/ci/sac_guard.yml` roda em `pull_request`, executa `index-build` e `validate` sobre a árvore da PR e injeta `SAC_PR_BODY: ${{ github.event.pull_request.body }}`. Enquanto o repo é privado, o autor da PR é o dono. Publicado, o autor da PR é **qualquer pessoa na internet**, e o CI passa a executar parsing próprio sobre conteúdo hostil (arquivos gigantes, encoding inválido, tags patológicas, ReDoS nos regexes de `sac_engine.py` — há `.*?` e `[^.]+` em padrões aplicados linha a linha).

Isso é ordinariamente aceitável (`pull_request`, não `pull_request_target`: token read-only, sem segredos) — mas é uma **ameaça nova, criada pela decisão central do documento**, e o §2 do v2, que é sua principal contribuição, a exclui por construção. O ator "autor de fork PR" precisa entrar na tabela §2.2, e o T9 precisa de um gate de CI de fork.

### 2.2 A dependência circular que o ADR-010 resolve não era a mais séria

O ADR-010 (0.x antes do hardening) é a melhor decisão do v2. Mas a circularidade real é outra: **o v2 exige medição antes de fixar valores (regra anti-heurística) e ao mesmo tempo prescreve os controles a serem medidos.** §10.2 aplica o ceticismo corretamente ao cap de concorrência (`GATED`, pode terminar em `NO_CHANGE`). §5, §7.4 e §9.1 não aplicam: ceilings de stdout/stderr, timeout e o conjunto de campos de telemetria são tratados como obrigatórios, e só seus *valores* ficam para medição.

Coerência exige o mesmo tratamento. Concretamente: o timeout de 30 s existe desde sempre; se o T0 mostrar p99 de 400 ms, o ceiling físico de stdout protege contra um cenário que a duração já limita — e vira código e um código de erro público mantidos contra ameaça hipotética, exatamente o argumento que o próprio v2 usa para adiar o cap de concorrência.

### 2.3 A ordem das tracks coloca a migração de SDK antes do hardening — e isso está errado

O v2 fixa T5 (SDK v2) → T6 (lifecycle). A justificativa é isolamento de diff. Mas:

- ADR-011 (do próprio v2) diz que a migração é **agendada, não emergencial**, com v1.x recebendo suporte por ≥6 meses;
- T6 corrige **T1 (processos órfãos)**, que é a única ameaça da tabela §2.3 com dano acumulativo e observável hoje;
- T5 força Node 20+, que é **MAJOR para consumidores** (o próprio §6.3 do v2) — logo o v2 agenda um breaking change *antes* de corrigir vazamento de processo, e ainda dentro da janela 0.x onde não há consumidor para justificar a pressa.

Inverta: **T6 antes de T5.** O hardening de lifecycle no SDK v1 não é trabalho jogado fora — a lógica de árvore de processos, grace period e reap vive em `runCliJson`, não na camada de protocolo. E inverter significa que a 0.1.0 sai com lifecycle correto e sem exigir Node 20 de ninguém.

### 2.4 "Diff sem mudança semântica" continua não-falsificável mesmo com corpus golden

O v2 melhora o v1 exigindo normalização (§14.6). Mas, dado §1.3 (não há Layer A) e §1.6 (a normalização de path mascara um defeito real), o gate do T2 permanece fraco em ambas as pontas: cobre pouco e apaga o que cobre. O gate honesto exige as duas coisas — Layer A mínima antes de mover código, e casos de corpus deliberadamente **não** normalizados para as dimensões onde a normalização esconde divergência (forma do root, separador de path, ordenação).

### 2.5 O `sac-evolution` público é maior do que o §19 admite

O §19 diz "remover autoridade pai→filho, manter matriz de impacto". Lendo a skill: a matriz de impacto atual tem ~20 linhas de checklist anti-lacuna, e boa parte referencia artefatos que **mudam de identidade** na extração (`templates/project-base`, `mirror`, `propagation_status: mirrored|pending_by_user`, `.cursorrules` do pai, `skills_registry.json`). O invariante 9 ("pipeline alinhado") e o contrato "Propagação" são estruturalmente sobre topologia de monorepo, não sobre governança de padrão. Reescrever é mais próximo de reautoria do que de remoção — o T9 do v2 lista isso como um bullet entre seis.

---

## 3. O que os dois relatórios acertam e deve ser preservado sem alteração

Para não haver dúvida sobre o escopo desta crítica:

- Separação de camadas e ADR-001..005: correta e comprovada pelo código. `server.mjs` é de fato thin; a semântica está de fato no Python.
- ADR-006 / ADR-007 (HTTP e worker persistente gated por evidência): correto, e o §1.4 acima reforça — sem telemetria confiável não há como decidir.
- ADR-010 (0.x antes do hardening): a melhor decisão dos dois documentos.
- §13.1 do v2 sobre `serveStdio(factory)` e o alerta de que atualizar o SDK **não** muda a revisão negociada: é o ponto técnico mais preciso dos dois relatórios, e o requisito de *assertar a revisão efetivamente negociada* é exatamente o teste que pegaria a falha silenciosa.
- §7.2 (árvore de processos no Windows como requisito, não como analogia) e §7.3 (morte do parent → órfão Node): ambas corrigem lacunas reais do v1.
- §22 (ordem de precedência em conflito) e §21 (non-goals): mantenha literalmente.
- A tese central — "o maior risco é transformar a publicação numa reescrita prematura" — está certa. Nada nesta avaliação a contradiz; o que ela acrescenta é que **o inverso também é risco**: publicar sem auditar transforma defeitos privados em contratos públicos.

---

## 4. Correções normativas exigidas no v2

| # | Seção do v2 | Correção |
|---|---|---|
| C1 | §12.2 | `owned` não pode residir dentro de `managed`. Exigir mudança de caminho do manifesto e separação template/manifesto, em T2/T3, antes da 0.1.0. |
| C2 | ADR-003, §14 | Reconhecer adapter Python legado. Decidir: deletar ou submeter aos mesmos gates. Gate do T2. |
| C3 | §14.1, T0/T2 | Declarar que a Layer A não existe. Precificar e sequenciar antes de mover código. Reconhecer o smoke como Layer B+C existente e estender, não duplicar. |
| C4 | §9.1, §5 | `payload_bytes` atual sub-relata 23,9 %. Redefinir como bytes efetivamente escritos. Unificar a unidade do orçamento semântico (compacto) com a da emissão (indent=1) ou declarar a razão medida. Corrigir a afirmação de que `context_payload_too_large` sai com exit 0 — sai com 1. |
| C5 | §2.2, §9.2, DECISION-6 | Reescopar T6: o vazamento primário de path é o **payload**, não a telemetria. Adicionar "autor de fork PR" à tabela de atores, criada pela própria publicação. |
| C6 | §4.3, §11 | Modelar a terceira classe de erro (uso/ambiente da CLI, exit 2), hoje apagada pelo adapter. É a classe mais provável na primeira instalação. |
| C7 | §15, §21 | Inverter T5 e T6. Lifecycle antes de SDK. Adicionar requisito de atestação de gates na resposta (§1.7) e de auditoria de histórico git + remoção dos `.pyc` versionados (§1.8). |

---

## 5. Track nova, anterior a tudo

### T-1 — Auditoria de estado real (entry: nenhum)

O T0 do v2 mede performance. Falta medir **verdade**.

Escopo fechado:

1. Inventário de superfícies MCP existentes (achado: duas, não uma).
2. Inventário de cobertura de testes por camada (achado: Layer A = 0).
3. Auditoria de todos os caminhos hardcoded e de colisão `managed`/`owned`.
4. Auditoria de todos os `SAC_ALLOW_*` e de qualquer outro escape de gate, com prova de que o payload não os atesta.
5. Auditoria de vazamento de path no payload e no `_perf`.
6. Auditoria do histórico git: segredos, artefatos de build versionados, caminhos de máquina.
7. Verificação da unidade de bytes ponta a ponta (engine → CLI → adapter → host).

**Exit gate (binário):**
- [ ] cada achado registrado com arquivo:linha e reprodução
- [ ] cada achado classificado: `corrigir antes da extração` | `corrigir antes da 0.1.0` | `aceitar e documentar`
- [ ] nenhuma seção normativa do v2 permanece contradita por código não corrigido ou não documentado

Sem T-1, o T0 produz um baseline preciso de um sistema mal compreendido.

---

## 6. Decisão

**GO**, com a arquitetura dos dois relatórios preservada, e sob três condições:

1. **T-1 antes do T0.** Auditar antes de medir; medir antes de normatizar.
2. **Sete correções normativas (C1–C7)** aplicadas ao v2 antes de qualquer track iniciar.
3. **T6 antes do T5.**

O v1 propôs uma arquitetura. O v2 a endureceu em contratos. Falta a etapa que nenhum dos dois fez: **confrontar os contratos com o código que eles pretendem governar.** Sete das onze constatações da §1 são defeitos que já estão em produção — e o efeito da publicação, sem T-1, é congelá-los como comportamento público documentado.
