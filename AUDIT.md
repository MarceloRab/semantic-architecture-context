# AUDIT — Auditoria de Estado Real do Semantic Architecture Context (SAC)

Documento normativo de consolidação de defeitos, inconsistências, desvios empíricos e limites funcionais auditados no código-fonte e na infraestrutura do SAC, derivado das avaliações adversariais e funcionais (V3, V4 e V5).

---

## 1. Resumo Executivo e Matriz de Classificação

Cada achado auditado possui um identificador estável (`A01` a `A28`), anchor `arquivo:linha`, sintoma, passo de reprodução e está classificado em exatamente **uma** das três categorias canônicas:

1. `corrigir antes da extração` — Resolvido cirurgicamente em tracks do **Bloco 01 (SAC como MCP Público)** antes da publicação do release candidate `0.1.0-rc`.
2. `corrigir antes da 0.1.0` — Resolvido em tracks do **Bloco 02 (Melhoria Funcional da Feature)** antes do release final `0.1.0`.
3. `aceitar e documentar` — Limitação técnica deliberada, não-meta ou contrato explícito a ser documentado na raiz (`README.md` / `RELEASE_GATE.md`).

### Matriz Sintética de Achados

| ID | Achado / Defeito | Anchor Principal | Classificação | Trilha Responsável / Destino |
|---|---|---|---|---|
| **A01** | Manifesto `owned` dentro da árvore `managed` | `src/sac_domains.py:14` | `corrigir antes da extração` | Bloco 01 Track 05 |
| **A02** | Segunda superfície MCP não-gated e com dep externa (legado) | Histórico de extração (`src/` legado) | `corrigir antes da extração` | Bloco 01 Track 04 |
| **A03** | Layer A de testes unitários inexistente (Layer A = 0) | `test_*.py` sob `sac-context/`: zero | `corrigir antes da 0.1.0` | Bloco 02 Tracks 01, 04, 05 |
| **A04** | `_perf.payload_bytes` sub-relata 23,9% | `mcp/server.mjs:291` vs `:266` | `corrigir antes da 0.1.0` | Bloco 02 Track 06 |
| **A05** | Unidade de orçamento 1,215x divergente (compacto vs indent=1) | `src/sac_engine.py:636` vs `src/sac_scan.py:444` | `corrigir antes da 0.1.0` | Bloco 02 Track 06 |
| **A06** | Vazamento de path absoluto de máquina no payload (16,1%) | `mcp/server.mjs:198-264`, `src/sac_engine.py` | `corrigir antes da 0.1.0` | Bloco 02 Track 06 |
| **A07** | Três escapes `SAC_ALLOW_*` não atestados no payload | `mcp/server.mjs:78`, `src/sac_scan.py:354`, `src/sac_domains.py:478,537` | `corrigir antes da extração` | Bloco 01 Track 06 |
| **A08** | Bytecode `.pyc` rastreado contendo caminhos absolutos do autor | `src/__pycache__/` | `corrigir antes da extração` | Bloco 01 Track 02 |
| **A09** | Identidade de versão tripla e conflitante | `mcp/package.json:3`, `mcp/server.mjs:327`, `sac-evolution` | `corrigir antes da extração` | Bloco 01 Track 04 |
| **A10** | Terceira classe de erro apagada (exit 2 emitindo só stderr) | `src/sac_scan.py:48-52`, `mcp/server.mjs:75-95` | `corrigir antes da extração` | Bloco 01 Track 06 |
| **A11** | `_SYMBOL_REGISTRY` limitado a duas linguagens (`.dart`, `.ps1`) | `src/sac_diff.py:36-45` | `corrigir antes da 0.1.0` | Bloco 02 Track 05 |
| **A12** | Ordenação alfabética em `_is_covered` causando falso positivo | `src/sac_diff.py:415-427` | `corrigir antes da 0.1.0` | Bloco 02 Track 04 |
| **A13** | Truncamento de `verify:` no primeiro ponto (`[^.]+`) | `src/sac_engine.py:43,146` | `corrigir antes da 0.1.0` | Bloco 02 Track 01 |
| **A14** | Campo `trigger` inerte no runtime sem impacto semântico | `src/sac_engine.py:102-106`, `src/sac_diff.py` | `corrigir antes da 0.1.0` | Bloco 02 Track 02 |
| **A15** | `AGENTS.md` sem nenhuma menção a SAC | Raiz do repositório (`AGENTS.md`) | `corrigir antes da 0.1.0` | Bloco 02 Track 03 |
| **A16** | Caminho absoluto de máquina em artefatos de atalho de skill | `skills/.../sac-onboard/prompt_resumido.md:1`, `PROMPT.md:1` | `corrigir antes da extração` | Bloco 01 Track 08 |
| **A17** | Colisão de gatilho no frontmatter de `sac-context` e `sac-execution-overlay` | `skills/.../sac-context/SKILL.md:3` vs `sac-execution-overlay/SKILL.md:3` | `corrigir antes da extração` | Bloco 01 Track 08 |
| **A18** | CI executando parsing sobre corpo de PR de fork | `ci/sac_guard.yml:34` | `corrigir antes da extração` | Bloco 01 Track 09 |
| **A19** | Inventário de superfícies MCP (duas superfícies no legado) | `mcp/server.mjs` e adapter Python legado | `corrigir antes da extração` | Bloco 01 Track 04 |
| **A20** | Cobertura de teste desbalanceada (Layer A = 0, smoke = Layer B+C) | `test_*.py` (0) vs `mcp/smoke.mjs:1-873` | `corrigir antes da 0.1.0` | Bloco 02 Tracks 01, 04, 05 |
| **A21** | Eixo linguagem ausente da matriz de compatibilidade | `docs/`, `README.md` | `aceitar e documentar` | Bloco 01 Track 10 / README |
| **A22** | Proposta de `DIAGNOSE` como cenário-base obrigatório | `src/sac_domains.py:36-38`, `src/sac_engine.py:964,1039` | `aceitar e documentar` | Não-meta (apenas benchmark) |
| **A23** | `_is_covered` atua como co-edit gate e não prova formal de teste | `src/sac_diff.py:323` | `aceitar e documentar` | Bloco 01 Track 10 / README |
| **A24** | Acoplamento de claims e tags (`OVER_SELECT` penaliza tags auto-incluídas) | `src/sac_engine.py:1037` | `corrigir antes da 0.1.0` | Bloco 02 Track 07 |
| **A25** | Restrição de marcadores de comentários a `//` e `#` | `src/sac_engine.py:27` | `corrigir antes da 0.1.0` | Bloco 02 Track 08 |
| **A26** | Vocabulário imperativo de ARCH restrito a inglês (`MUST|NEVER|ONLY`) | `src/sac_engine.py:107` | `corrigir antes da 0.1.0` | Bloco 02 Track 08 |
| **A27** | Código morto em `runCliJson` checando `--root` | `mcp/server.mjs:74-76` | `aceitar e documentar` | Bloco 01 Track 04 |
| **A28** | Histórico git monorepo com 52 commits privados não auditados | Histórico git raiz `rabelo-standards` | `corrigir antes da extração` | Bloco 01 Track 02 |

---

## 2. Detalhamento dos Achados Auditados

### A01 — Manifesto `owned` dentro da árvore `managed`
- **Anchor:** `src/sac_domains.py:14` (`_DOMAINS_REL = os.path.join("sac-context", "docs", "SAC_domains.md")`) e `scripts/mirror-sac-tooling.ps1:121-133`.
- **Sintoma:** O manifesto do consumidor (único arquivo classificado como `owned`) possui caminho hardcoded dentro do diretório que o instalador sobrescreve (`managed`). O mesmo arquivo serve como template, schema e manual (`_template`, COR-3).
- **Passo de Reprodução:**
  1. No bootstrap de um projeto consumidor, o arquivo `sac-context/docs/SAC_domains.md` é preenchido com domínios do projeto.
  2. Ao rodar atualização do ferramental, o script de espelhamento exclui o arquivo para não sobrescrever os domínios do consumidor.
  3. Resultado: o consumidor nunca recebe atualizações do schema, template ou manual COR-3, ficando permanentemente congelado na versão inicial.
- **Classificação:** `corrigir antes da extração`
- **Trilha Responsável:** **Bloco 01 Track 05** (Relocação do manifesto para `.sac/domains.md`, template em `templates/domains.template.md` e matriz de compatibilidade com estados antigos).

---

### A02 — Segunda superfície MCP não-gated e com dependência externa
- **Anchor:** Adapter Python legado (`mcp.server` legado).
- **Sintoma:** Existia um servidor MCP Python legado que chamava `sac_engine.lookup` diretamente sem passar por `sac_domains.py`, operando sem checagem de membership, sem PAUSE de `filepath_required`, com `root = os.getcwd()`. Além de divergir semanticamente do adapter Node (`mcp/server.mjs`), quebrava a invariante stdlib-only do Python (C1/DP-1).
- **Passo de Reprodução:**
  1. Executar o servidor MCP Python legado e chamar `get_sac_constraints("sym")` sem `filepath`.
  2. Observar retorno direto de matches sem o PAUSE estruturado exigido pela especificação Route L0/L1.
- **Classificação:** `corrigir antes da extração`
- **Trilha Responsável:** **Bloco 01 Track 04** (Remoção do adapter Python legado, consolidando `mcp/server.mjs` como superfície MCP única).

---

### A03 — Layer A de testes unitários inexistente (Layer A = 0)
- **Anchor:** Diretório `sac-context/` (busca por `test_*.py`, `conftest.py`: 0 resultados).
- **Sintoma:** ~3.400 linhas de Python (engine, domains, diff, scan, capillarity) sem um único teste unitário automatizado. Apenas testes de integração / protocolo existem em `mcp/smoke.mjs`.
- **Passo de Reprodução:**
  1. Executar `pytest` ou varredura de testes em `src/`.
  2. Constatar ausência total de suíte unitária de validação de regras de gramática, parsing, verificação de rotas e cobertura.
- **Classificação:** `corrigir antes da 0.1.0`
- **Trilha Responsável:** **Bloco 02 Tracks 01, 04, 05** (Construção incremental da Layer A nos módulos alterados).

---

### A04 — `_perf.payload_bytes` sub-relata 23,9% da telemetria
- **Anchor:** `mcp/server.mjs:291` (`Buffer.byteLength(JSON.stringify(payload))`) vs `mcp/server.mjs:266` (`JSON.stringify(obj, null, 1)`).
- **Sintoma:** `withPerf` calcula o tamanho em bytes do payload bruto sem o objeto `_perf` e sem indentação. Posteriormente, `jsonToolResult` serializa com indentação (`indent=1`) e com `_perf` incluído.
- **Passo de Reprodução:**
  1. Executar consulta via MCP em fixture com 3 constraints.
  2. Medir valor reportado em `_perf.payload_bytes`: 1.599 bytes.
  3. Medir bytes UTF-8 emitidos em stdout no envelope final: 2.101 bytes (sub-relato sistemático de 23,9%).
- **Classificação:** `corrigir antes da 0.1.0`
- **Trilha Responsável:** **Bloco 02 Track 06** (Ajuste de cálculo de `payload_bytes` sobre a serialização efetivamente emitida).

---

### A05 — Unidade de orçamento 1,215x divergente (compacto vs indent=1)
- **Anchor:** `src/sac_engine.py:636` (`separators=(",", ":")`) vs `src/sac_scan.py:444` (`indent=1`).
- **Sintoma:** O cálculo de `SAC_CONTEXT_MAX_BYTES` (12.288 bytes) no engine mede o JSON no formato compacto (`separators=(',', ':')`), enquanto a emissão em stdout da CLI imprime com `indent=1`.
- **Passo de Reprodução:**
  1. Gerar payload de contexto no engine: 1.599 bytes compactos.
  2. Imprimir via CLI (`sac_scan.py`): 1.942 bytes formatados (razão de 1,215x).
  3. O teto de 12 KB autoriza ~14,9 KB de stdout real.
- **Classificação:** `corrigir antes da 0.1.0`
- **Trilha Responsável:** **Bloco 02 Track 06** (Unificação da unidade de serialização de orçamento e emissão).

---

### A06 — Vazamento de path absoluto de máquina no payload (16,1%)
- **Anchor:** `mcp/server.mjs:198-264` (injeção de `--root <absoluto>`), `src/sac_engine.py:620-645` e `_perf.sac_root`.
- **Sintoma:** O adapter Node sempre injeta o `--root` absoluto do workspace. O engine prefixa o atributo `file` de cada match e warning com essa string absoluta, inflando o payload em 16,1% e vazando caminhos locais do host para o contexto do LLM.
- **Passo de Reprodução:**
  1. Executar consulta com `--root fx` (relativo): payload de 1.599 bytes.
  2. Executar mesma consulta via MCP (`--root $PWD/fx`): payload de 1.857 bytes (+258 bytes = +16,1%).
- **Classificação:** `corrigir antes da 0.1.0`
- **Trilha Responsável:** **Bloco 02 Track 06** (Emissão de paths relativos à raiz do projeto e remoção de `_perf.sac_root`).

---

### A07 — Três escapes `SAC_ALLOW_*` não atestados no payload
- **Anchor:** `mcp/server.mjs:78`, `src/sac_scan.py:354`, `src/sac_domains.py:478`, `src/sac_domains.py:537`.
- **Sintoma:** O subprocesso da CLI herda `process.env` do host. Se `SAC_ALLOW_UNSCOPED`, `SAC_ALLOW_FILEPATH_OUTSIDE_DOMAINS` ou `SAC_ALLOW_HOP1_FULL_SCAN` forem configurados no host MCP, as consultas contornam os gates de segurança sem nenhuma declaração no JSON retornado.
- **Passo de Reprodução:**
  1. Executar `sac_scan.py lookup hidden_sym --root fx --path secret/s.py --json` -> Erro `filepath_not_in_sac_domains`.
  2. Executar com `SAC_ALLOW_FILEPATH_OUTSIDE_DOMAINS=1` -> Retorna `{"found": true, "matches": [...]}` sem nenhum campo de aviso (`gates_bypassed`).
- **Classificação:** `corrigir antes da extração`
- **Trilha Responsável:** **Bloco 01 Track 06** (Inclusão de `gates_bypassed` e warning explícito no payload quando escapes estiverem ativos).

---

### A08 — Bytecode `.pyc` rastreado contendo caminhos absolutos do autor
- **Anchor:** `src/__pycache__/` em `sac-context/src/__pycache__/*.pyc`.
- **Sintoma:** Arquivos de bytecode compilados (`.pyc`) de CPython 3.12 versionados no git rastreado, contendo strings literais `C:\Users\Rabelo\projects\rabelo-standards\...`.
- **Passo de Reprodução:**
  1. Executar `git ls-files src/__pycache__`.
  2. Analisar o binário `.pyc` e localizar paths absolutos hardcoded da máquina de desenvolvimento original.
- **Classificação:** `corrigir antes da extração`
- **Trilha Responsável:** **Bloco 01 Track 02** (Inicialização de git limpo, `.gitignore` estrito e gate de higiene na CI).

---

### A09 — Identidade de versão tripla e conflitante
- **Anchor:** `mcp/package.json:3` (`"version": "1.0.0"`), `mcp/server.mjs:327` (`version: "1.6.0"`), gate D4 de `sac-evolution` ("MCP v1.6.0+").
- **Sintoma:** Três fontes de verdade divergentes para a versão do pacote, sem mecanismo canônico de sincronização.
- **Passo de Reprodução:**
  1. Inspecionar `package.json` (1.0.0).
  2. Executar `initialize` no servidor MCP (anuncia 1.6.0).
  3. Consultar docstrings e skills de evolução (citam 1.6.0+).
- **Classificação:** `corrigir antes da extração`
- **Trilha Responsável:** **Bloco 01 Track 04** (SSOT único em `mcp/package.json` iniciando em `0.1.0`, lido dinamicamente por Node e Python).

---

### A10 — Terceira classe de erro apagada (exit 2 emitindo só stderr)
- **Anchor:** `src/sac_scan.py:48-52`, `mcp/server.mjs:75-95`.
- **Sintoma:** Falhas de uso da CLI ou argumentos de ambiente inválidos (ex: root inexistente) retornam exit 2 e escrevem somente em stderr (stdout vazio). O adapter Node interpreta stdout vazio como erro genérico de transporte e converte para `lookup_failed`/`context_failed`.
- **Passo de Reprodução:**
  1. Chamar `sac_scan.py lookup Foo --root /diretorio/inexistente --json`.
  2. Observar exit 2 com mensagem crua em stderr.
  3. No MCP, observar o erro mascarado como falha de execução de lookup.
- **Classificação:** `corrigir antes da extração`
- **Trilha Responsável:** **Bloco 01 Track 06** (Emissão de JSON estruturado em stdout com códigos `sac.environment.*` para exit 2).

---

### A11 — `_SYMBOL_REGISTRY` limitado a duas linguagens (`.dart`, `.ps1`)
- **Anchor:** `src/sac_diff.py:36-45` e `src/sac_diff.py:392`.
- **Sintoma:** O registro de símbolos para verificação de diff só possui extratores para Dart e PowerShell. Arquivos modificados em qualquer outra linguagem (Python, JS/TS, Go, Java, Rust) que contenham tags SAC caem na cláusula `FAIL CLOSED`.
- **Passo de Reprodução:**
  1. Adicionar uma tag `SAC:REGR` em um arquivo Python (`lib/pay.py`).
  2. Executar `sac_scan.py diff-check --base HEAD~1 --root .`.
  3. Obter `FAIL CLOSED - changed files in unsupported languages with SAC tags`. O SAC é incapaz de proteger a si mesmo em Python.
- **Classificação:** `corrigir antes da 0.1.0`
- **Trilha Responsável:** **Bloco 02 Track 05** (Expansão do `_SYMBOL_REGISTRY` para Python, JS/TS e Go, habilitando dogfooding).

---

### A12 — Ordenação alfabética em `_is_covered` causando falso positivo sistemático
- **Anchor:** `src/sac_diff.py:415-427` (e `src/sac_diff.py:323`).
- **Sintoma:** A lista `changed_symbols` é montada incrementalmente dentro do laço que itera sobre arquivos modificados ordenados pelo `git diff` (alfabético). Como arquivos-fonte (`lib/`, `src/`) precedem arquivos de teste (`test/`, `tests/`), alvos de `verify:` apontando para testes são avaliados antes do teste ser registrado em `changed_symbols`, disparando falso positivo sistemático `uncovered`.
- **Passo de Reprodução:**
  1. Criar commit alterando `lib/pay.dart` (com `verify: testCharge`) e `test/pay_test.dart` (contendo o símbolo `testCharge`).
  2. Executar `diff-check` -> Violação `exit 1: uncovered: testCharge` (pois `test/` é processado após `lib/`).
  3. Mover `test/pay_test.dart` para `aaa/pay_test.dart` -> `exit 0: No SAC violations found`.
- **Classificação:** `corrigir antes da 0.1.0`
- **Trilha Responsável:** **Bloco 02 Track 04** (Construção completa de `changed_symbols` em primeiro passo antes de avaliar violações).

---

### A13 — Truncamento de `verify:` no primeiro ponto (`[^.]+`)
- **Anchor:** `src/sac_engine.py:43,146` (`_VERIFY_TERMINAL_RE = re.compile(r".*\bverify:\s*(?P<targets>[^.]+)", re.IGNORECASE)`).
- **Sintoma:** A regex usada para extrair a lista de alvos termina no primeiro ponto (`[^.]+`). Qualquer lista de alvos contendo símbolos qualificados com ponto (ex: `Cache.key`, `test_charge.v2`) descarta silenciosamente todos os alvos após o ponto sem emitir warning.
- **Passo de Reprodução:**
  1. Definir tag com constraint: `MUST verify: Cache.key, PersistenceAdapter`.
  2. Chamar `_parse_verify` -> Retorna `['Cache']`. O alvo `PersistenceAdapter` é descartado silenciosamente.
  3. O agente cego lendo o arquivo vê todos os alvos, mas o parser MCP descarta em silêncio.
- **Classificação:** `corrigir antes da 0.1.0`
- **Trilha Responsável:** **Bloco 02 Track 01** (Regex de `verify:` com terminação explícita em `;` ou fim de linha, preservando pontos em identificadores).

---

### A14 — Campo `trigger` inerte no runtime sem impacto semântico
- **Anchor:** `src/sac_engine.py:102-106` (`_ALLOWED_TRIGGERS`), `src/sac_diff.py`.
- **Sintoma:** O campo `<TRIGGER>` (`RULE|CONSTRAINT` para ARCH e `WARNING|CRITICAL` para REGR/DEPRECATED) consome ~10 caracteres da linha sem alterar nenhum comportamento de validação ou bloqueio do engine.
- **Passo de Reprodução:**
  1. Comparar tags com `RULE` vs `CONSTRAINT`: o engine trata de forma idêntica.
  2. Comparar `diff-check` com `WARNING` vs `CRITICAL`: o bloqueio ocorre em ambos os casos.
- **Classificação:** `corrigir antes da 0.1.0`
- **Trilha Responsável:** **Bloco 02 Track 02** (Evolução do campo para condição de mudança `on=...` com vocabulário fechado).

---

### A15 — `AGENTS.md` sem nenhuma menção a SAC
- **Anchor:** Raiz do repositório (`AGENTS.md` ausente ou sem menção a SAC).
- **Sintoma:** Agentes de IA sem acesso ao MCP não possuem porta de entrada na raiz para descobrir a existência do manifesto `.sac/domains.md` e a convenção de tags, tornando o SAC invisível a agentes cegos.
- **Passo de Reprodução:**
  1. Agente cego lê convenções de projeto em `AGENTS.md`.
  2. Sem ponte explicada, ignora `.sac/domains.md` e opera sem o recorte de contexto de domínio.
- **Classificação:** `corrigir antes da 0.1.0`
- **Trilha Responsável:** **Bloco 02 Track 03** (Criação de bloco normativo tool-neutral do SAC em `AGENTS.md`).

---

### A16 — Caminho absoluto de máquina em artefatos de atalho de skill
- **Anchor:** `skills/catalog/domains/context-governance/sac-onboard/prompt_resumido.md:1` e `PROMPT.md:1`.
- **Sintoma:** A primeira linha de instrução para o agente contém caminhos absolutos hardcoded: `C:\Users\Rabelo\projects\rabelo-standards\...`. Em ambientes externos, isso induz o agente a falhas ou buscas impossíveis.
- **Passo de Reprodução:**
  1. Abrir `prompt_resumido.md` em máquina limpa/clone.
  2. Ler a linha 1 exigindo verificar a existência do path local do autor original.
- **Classificação:** `corrigir antes da extração`
- **Trilha Responsável:** **Bloco 01 Track 08** (Resolução relativa de caminhos irmãos nas skills públicas).

---

### A17 — Colisão de gatilho no frontmatter de `sac-context` e `sac-execution-overlay`
- **Anchor:** `skills/.../sac-context/SKILL.md:3` vs `skills/.../sac-execution-overlay/SKILL.md:3`.
- **Sintoma:** Descrições de frontmatter quase idênticas ("Gate de contexto para qualquer pergunta..." vs "Gate obrigatório para qualquer pergunta..."), gerando concorrência e seleção imprevisível pelo roteador de skills dos agentes.
- **Passo de Reprodução:**
  1. Submeter intenção genérica a um agente com ambas as skills instaladas.
  2. Observar ambiguidade no roteamento por sobreposição total de intenções.
- **Classificação:** `corrigir antes da extração`
- **Trilha Responsável:** **Bloco 01 Track 08** (Desambiguação: `sac-context` para gramática/escrita de tags; `sac-execution-overlay` para gate operacional de execução).

---

### A18 — CI executando parsing sobre corpo de PR de fork
- **Anchor:** `ci/sac_guard.yml:34` (`SAC_PR_BODY: ${{ github.event.pull_request.body }}`).
- **Sintoma:** Workflow executando em `pull_request` sobre forks externos sem isolamento estrito de permissões, ausência de timeout explícito no job e interpolação direta que expõe o runner a conteúdo não-confiável.
- **Passo de Reprodução:**
  1. Inspecionar `ci/sac_guard.yml`.
  2. Constatar ausência de `timeout-minutes` e passagem direta de payload de PR sem step intermediário seguro.
- **Classificação:** `corrigir antes da extração`
- **Trilha Responsável:** **Bloco 01 Track 09** (CI pública com `permissions: contents: read`, `timeout-minutes` e isolamento nativo).

---

### A19 — Inventário de superfícies MCP (duas superfícies existentes)
- **Anchor:** `mcp/server.mjs` (Node stdio) e adapter Python legado.
- **Sintoma:** Existência de dois adapters MCP com contratos e dependências diferentes no mesmo repositório.
- **Passo de Reprodução:**
  1. Comparar as ferramentas expostas por `server.mjs` (5 ferramentas com envelopes completos) e o adapter legado (1 ferramenta sem envelopes).
- **Classificação:** `corrigir antes da extração`
- **Trilha Responsável:** **Bloco 01 Track 04** (Eliminação do adapter Python; consolidação de `mcp/server.mjs`).

---

### A20 — Cobertura de teste por camada desbalanceada (Layer A = 0, smoke = Layer B+C)
- **Anchor:** `test_*.py` (0 arquivos) vs `mcp/smoke.mjs:1-873`.
- **Sintoma:** Inversão da pirâmide de testes: zero testes unitários rápidos de engine/gramática (Layer A) e dependência total de smoke de protocolo e CLI (Layer B+C).
- **Passo de Reprodução:**
  1. Executar suíte de testes: depende exclusivamente do Node SDK e do `smoke.mjs`.
- **Classificação:** `corrigir antes da 0.1.0`
- **Trilha Responsável:** **Bloco 02 Tracks 01, 04, 05** (Construção da Layer A nos módulos de Python).

---

### A21 — Eixo linguagem ausente da matriz de compatibilidade
- **Anchor:** Documentação e matriz de compatibilidade (`docs/`, `README.md`).
- **Sintoma:** A matriz catalogava compatibilidade de SO, Node, Python e Host MCP, omitindo as linguagens de código-fonte suportadas pelo gate `diff-check` (`.dart`, `.ps1`), omitindo a limitação do pilar 2.
- **Passo de Reprodução:**
  1. Consultar matriz de compatibilidade pública original: ausência da coluna "Linguagens do Código-Fonte".
- **Classificação:** `aceitar e documentar` (no Bloco 01) / `corrigir antes da 0.1.0` (ampliação no Bloco 02).
- **Trilha Responsável / Destino:** **Bloco 01 Track 10** (Documentar no README e no `RELEASE_GATE.md` que o diff-check suporta atualmente `.dart` e `.ps1`, sendo co-edit gate); **Bloco 02 Track 05** (Expansão do suporte).

---

### A22 — Proposta de `DIAGNOSE` como cenário-base obrigatório
- **Anchor:** `src/sac_domains.py:36-38`, `src/sac_engine.py:964,1039`.
- **Sintoma:** Proposta em relatório externo de incluir `DIAGNOSE` como cenário-base obrigatório no schema (`_BASE_SCENARIOS`). Isso causaria `INVALID_CONTRACT` imediato em toda a base instalada de domínios onboardados (breaking change MAJOR desnecessário).
- **Passo de Reprodução:**
  1. Adicionar `"DIAGNOSE"` a `_BASE_SCENARIOS`.
  2. Executar `assess` sobre qualquer domínio existente sem a claim `DIAGNOSE` -> `scenarios_base_missing` -> `INVALID_CONTRACT`.
- **Classificação:** `aceitar e documentar`
- **Justificativa / Destino:** Não-meta de schema. `DIAGNOSE` é mantido estritamente como cenário conceitual de benchmark no Bloco 02, sem alteração de schema ou quebra de contratos existentes.

---

### A23 — `_is_covered` atua como co-edit gate e não prova formal de teste
- **Anchor:** `src/sac_diff.py:323`.
- **Sintoma:** `_is_covered` valida apenas se um símbolo ou arquivo com o mesmo nome do alvo `verify:` foi modificado na mesma PR (co-edição lexical). Não valida AST, compilação nem execução de testes.
- **Passo de Reprodução:**
  1. Modificar uma linha irrelevante em `test/pay_test.dart` -> O gate considera `testCharge` coberto.
- **Classificação:** `aceitar e documentar`
- **Justificativa / Destino:** **Bloco 01 Track 10** (README e `RELEASE_GATE.md` devem declarar explicitamente que o gate é de **co-edição** e obrigação de revisão, sem prometer prova formal de testes).

---

### A24 — Acoplamento de claims e tags (`OVER_SELECT` penaliza tags auto-incluídas)
- **Anchor:** `src/sac_engine.py:1037` (`uncontracted_context_count = len(context_selected) - contracted_in_context`).
- **Sintoma:** Toda tag REGR e DEPRECATED é automaticamente incluída no contexto do domínio. Com o contrato 1:1, cada tag nova criada exige uma linha de claim no manifesto para o domínio não sair de status FIT (`OVER_SELECT`).
- **Passo de Reprodução:**
  1. Adicionar nova tag `SAC:REGR` em arquivo pertencente ao domínio.
  2. Rodar `assess_sac_capillarity` sem atualizar o manifesto -> `OVER_SELECT`.
- **Classificação:** `corrigir antes da 0.1.0`
- **Trilha Responsável:** **Bloco 02 Track 07** (Desacoplar contagem de `OVER_SELECT` de tags auto-incluídas).

---

### A25 — Restrição de marcadores de comentários a `//` e `#`
- **Anchor:** `src/sac_engine.py:27` (`_COMMENT_PREFIX_RE = re.compile(r"^\s*(?://|#)\s*")`).
- **Sintoma:** Linguagens que utilizam outros delimitadores de comentário (ex: `--` em SQL/Lua/Haskell, `;` em Lisp/Assembly, `<!-- -->` em HTML/Markdown) não conseguem portar tags SAC.
- **Passo de Reprodução:**
  1. Inserir `-- SAC:ARCH: RULE - Mig: MUST run idempotently` em arquivo SQL.
  2. Executar `sac_scan.py scan --root .` -> Tag ignorada pelo parser.
- **Classificação:** `corrigir antes da 0.1.0`
- **Trilha Responsável:** **Bloco 02 Track 08** (Flexibilização de marcadores de comentário).

---

### A26 — Vocabulário imperativo de ARCH restrito a inglês (`MUST|NEVER|ONLY`)
- **Anchor:** `src/sac_engine.py:107` (`_ARCH_IMPERATIVE_RE = re.compile(r"\b(MUST|NEVER|ONLY)\b")`).
- **Sintoma:** Tags ARCH escritas em português (ex: `DEVE validar schema`) disparam permanentemente o warning `arch_imperative_required`.
- **Passo de Reprodução:**
  1. Criar tag `// SAC:ARCH: RULE - S: DEVE ser idempotente`.
  2. Executar lookup -> Retorna warning `arch_imperative_required`.
- **Classificação:** `corrigir antes da 0.1.0`
- **Trilha Responsável:** **Bloco 02 Track 08** (Inclusão de imperativos equivalentes em português: `DEVE|NUNCA|SOMENTE`).

---

### A27 — Código morto em `runCliJson` checando redundância de `--root`
- **Anchor:** `mcp/server.mjs:74-76` (`if (!cliArgs.includes("--root")) args.push("--root", root)`).
- **Sintoma:** Todos os pontos de chamada (`runLookup`, `runListDomains`, `runDiscover`, `runContext`, `runCapillarity`) já inserem explicitamente `--root`, tornando o condicional inalcançável.
- **Passo de Reprodução:**
  1. Inspecionar todas as invocações de `runCliJson` em `mcp/server.mjs`. Todas possuem `--root` montado.
- **Classificação:** `aceitar e documentar`
- **Justificativa / Destino:** Inofensivo como salvaguarda defensiva; registrado para conhecimento de cobertura.

---

### A28 — Histórico git monorepo com 52 commits privados não auditados
- **Anchor:** Histórico do repositório `rabelo-standards` (52 commits).
- **Sintoma:** O histórico original continha referências a múltiplos outros subprojetos, caminhos de máquinas privadas e artefatos de build não auditados para publicação aberta.
- **Passo de Reprodução:**
  1. Analisar `git log` original com commits contendo caminhos e contextos monorepo.
- **Classificação:** `corrigir antes da extração`
- **Trilha Responsável:** **Bloco 01 Track 02** (Inicialização de repositório git do zero com commit único e limpo no destino público).

---

## 3. Conclusão de Auditoria e Gates de Saída

- **Total de achados catalogados:** 28 (incluindo integralmente os 21 obrigatórios de Semantic Authority).
- **Classificação por Categoria:**
  - `corrigir antes da extração` (Bloco 01): **10 achados** (`A01`, `A02`, `A07`, `A08`, `A09`, `A10`, `A16`, `A17`, `A18`, `A19`, `A28`).
  - `corrigir antes da 0.1.0` (Bloco 02): **14 achados** (`A03`, `A04`, `A05`, `A06`, `A11`, `A12`, `A13`, `A14`, `A15`, `A20`, `A24`, `A25`, `A26`).
  - `aceitar e documentar` (Documentação / Limitações): **4 achados** (`A21`, `A22`, `A23`, `A27`).

Todos os achados estão vinculados a decisões de design e trilhas de execução específicas nos Blocos 01 e 02, satisfazendo integralmente a Definition of Done da Track 01.
