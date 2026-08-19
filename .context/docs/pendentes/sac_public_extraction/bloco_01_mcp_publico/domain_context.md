# Domain Context — Bloco 01: SAC como MCP público

Cápsula factual reutilizável. Só fatos necessários ao Bloco 01, cada um citado.

## Focus

- Objective area: transformar o SAC de subsistema interno do monorepo `rabelo-standards` em projeto público autocontido, clonável, instalável e aberto a PR, hospedado em `C:\Users\Rabelo\projects\semantic-architecture-context`.
- Entry point: `mcp/server.mjs` (adapter MCP stdio, Node) → `src/sac_scan.py` (CLI, SSOT semântico) @ `rabelo-standards/sac-context/`
- Out of focus: qualidade funcional dos três pilares (F1–F10, `verify:` truncation, campo `trigger`, `_SYMBOL_REGISTRY`, benchmark, M9 completo). Todos pertencem ao Bloco 02.

## Current flow

1. Host MCP inicia `node mcp/server.mjs` via stdio @ `mcp/server.mjs:327`
2. Adapter resolve root (`SAC_ROOT` ou cwd) e python (`SAC_PYTHON`) @ `mcp/server.mjs:42,49`
3. Cada tool monta argv e chama a CLI como subprocesso, sempre com `--root <absoluto>` @ `mcp/server.mjs:199,215,228,243,257`
4. Subprocesso herda o ambiente completo do host: `{ ...process.env, ...opts.env }` @ `mcp/server.mjs:78`
5. CLI parseia tags SAC do fonte e o manifesto Route, devolve JSON em stdout @ `src/sac_scan.py`
6. Adapter envelopa em `withPerf` e serializa com `JSON.stringify(obj, null, 1)` @ `mcp/server.mjs:285,266`
7. Distribuição atual ao consumidor: cópia de arquivos por `scripts/mirror-sac-tooling.ps1` a partir de `rabelo-standards` (base propagadora, não consumidora), com exclusão por nome para preservar o manifesto do projeto

## Contracts and invariants

- Semântica vive só no Python; o adapter Node é fino (ADR-001..005, confirmado por leitura de `mcp/server.mjs`)
- Engine é stdlib-only (contrato C1/DP-1)
- Paridade CLI ≡ MCP é o invariante central verificado por `mcp/smoke.mjs` (873 linhas)
- Manifesto Route é markdown, legível sem ferramenta — requisito do princípio 3
- `_BASE_SCENARIOS = {SUMMARY, EXTEND, REGRESSION}`; ausência ⇒ `INVALID_CONTRACT` @ `src/sac_domains.py:36-38`

## Owners and dependents

- Owner do caminho do manifesto: `_DOMAINS_REL = os.path.join("sac-context","docs","SAC_domains.md")` @ `src/sac_domains.py:14`
- Owner da resolução: `sac_domains_path(root)` @ `src/sac_domains.py:44`
- Dependentes do caminho: `sac_scan.py` (todos os subcomandos), skill `sac-onboard`, skill `sac-execution-overlay`, `docs/SAC_BOOTSTRAP.md`, `scripts/mirror-sac-tooling.ps1:121-133`
- Owner da versão publicada: hoje triplo e sem canônico — `mcp/package.json` `"version": "1.0.0"`, `new McpServer({version:"1.6.0"})` @ `mcp/server.mjs:327`, e o gate D4 da skill `sac-evolution`
- Segunda superfície MCP (eliminada na Track 04): servidor Python legado não-gated com dependência externa

## Critical surfaces

- **Identity**: identidade de versão tripla e não canônica (acima). O projeto público precisa de SSOT única de versão antes de qualquer tag. Não há `.git` no destino: `git rev-parse` falha em `semantic-architecture-context`.
- **Persistence/compatibility**: o único arquivo `owned` do consumidor (`SAC_domains.md`) mora dentro da árvore `managed` que o installer sobrescreve @ `src/sac_domains.py:14`. Consequência já em produção: o consumidor nunca recebe atualização de schema/template/manual — está congelado na versão do dia do bootstrap.
- **Topologia real de consumo** (verificada, corrige premissa dos relatórios): `rabelo-standards` **não é consumidor** do SAC. É base propagadora de recursos operacionais para outros projetos, e não possui manifesto de projeto — seu `sac-context/docs/SAC_domains.md` contém apenas template e howto. Os consumidores reais são dois, cada um com sua própria cópia propagada de `sac-context/`:
  - `C:\Users\Rabelo\projects\api_robot` — manifesto com 1 domínio real (`pocket-backend-core`); servidor MCP registrado em `.mcp.json` como `sac_api_robot`, apontando para sua cópia local de `mcp/server.mjs`, com `SAC_PYTHON` no bloco `env`; tags SAC em arquivos **`.py`** (`backend/app_v3/**`).
  - `C:\Users\Rabelo\projects\to_de_plantao` — manifesto com 7 domínios reais (`convites`, `boot_sync`, `realtime_streams`, `estado01_offline_first`, `estado02_remote_ssot`, `calendar_ui_click_handlers`, `admin_privileges_remote_ssot`); tags SAC em arquivos **`.dart`** e **`.ts`** (`supabase/functions/**`).
  - `api_robot.worktrees/greeting-response-oi` é worktree git de `api_robot`, não projeto distinto.
  Consequência sobre o pilar 2: das três linguagens em que os consumidores reais escrevem tags, apenas `.dart` está em `_SYMBOL_REGISTRY`. `.py` e `.ts` produzem `FAIL CLOSED` hoje. Confirmação de campo do defeito, e justificativa direta da lista de linguagens escolhida no Bloco 02.
  Consequência sobre dogfooding: como `rabelo-standards` nunca foi consumidor, o dogfooding não é dívida dele — é responsabilidade do repositório público sobre si mesmo.
  Escopo: nenhum dos três é tocado pelo Bloco 01 nem pelo Bloco 02 (decisão do usuário; migração só após testes estáveis pós-Bloco 02).
- **Security/permission**: três escapes de HALT são atingíveis pelo bloco `env` da config do host MCP, por herança de ambiente @ `mcp/server.mjs:78` — `SAC_ALLOW_UNSCOPED` @ `src/sac_scan.py:354`, `SAC_ALLOW_FILEPATH_OUTSIDE_DOMAINS` @ `src/sac_domains.py:478`, `SAC_ALLOW_HOP1_FULL_SCAN` @ `src/sac_domains.py:537`. O payload permissivo é hoje indistinguível do payload gated: nenhum campo, nenhum warning.
- **External boundary**: `ci/sac_guard.yml` roda em `pull_request` e injeta `SAC_PR_BODY: ${{ github.event.pull_request.body }}`. Enquanto privado, o autor da PR é o dono. Publicado, o autor da PR é qualquer pessoa — parsing próprio sobre conteúdo hostil e interpolação de expressão em env.
- **Artefatos de máquina versionados**: 4 `.pyc` CPython 3.12 rastreados em `src/__pycache__/`, contendo `C:\Users\Rabelo\projects\rabelo-standards\...`. Mesmo defeito em `skills/.../sac-onboard/prompt_resumido.md` e `PROMPT.md`, onde o caminho absoluto é a **primeira instrução que o agente lê**.
- **Classe de erro apagada**: `sac_scan.py` usa exit 2 em 8 pontos (root inválido, erro de uso do argparse) escrevendo só em stderr; o adapter cai no ramo "empty stdout" e converte em `lookup_failed`/`context_failed`. É a classe mais provável na primeira instalação de um usuário desconhecido.
- **Runtime floor**: nenhum módulo usa sintaxe acima de 3.9 (sem `match`, sem `tomllib`, sem `removeprefix`; todos com `from __future__ import annotations`). `mcp/package.json` declara `node >= 18`.

## Unknowns

- none
