# Handoff — Bloco 01: SAC como MCP público

## Plan

- Design: .context/docs/pendentes/sac_public_extraction/bloco_01_mcp_publico/design.md
- Approved by: usuário, 2026-08-19 — autorização explícita para ativar o builder
- Current: COMPLETED (Bloco 01 concluído em 0.1.0-rc)

## Tracks

| Track | Goal | Depends on | Status | Attempt |
| --- | --- | --- | --- | --- |
| track_01 | Auditoria de estado real consolidada em AUDIT.md, cada achado com anchor e classificação | none | APPROVED | 1 |
| track_02 | Esqueleto público: git do zero, MIT, .gitignore e gate de higiene que falha duro | track_01 | APPROVED | 1 |
| track_03 | Transplante verbatim de src/, mcp/, ci/, docs/ com smoke verde nos dois repositórios | track_02 | APPROVED | 1 |
| track_04 | Superfície MCP única e SSOT de versão em mcp/package.json, anunciando 0.1.0 | track_03 | APPROVED | 1 |
| track_05 | Manifesto owned em .sac/domains.md, template managed, matriz de estados antigos fechada | track_04 | APPROVED | 1 |
| track_06 | gates_bypassed no payload e terceira classe de erro sac.environment.* | track_05 | APPROVED | 1 |
| track_07 | install.py stdlib-only que nunca sobrescreve owned, e quickstart executável | track_06 | APPROVED | 1 |
| track_08 | Três skills públicas sem caminho de máquina e sem gatilho ambíguo, mais GOVERNANCE | track_07 | APPROVED | 1 |
| track_09 | CI pública que aceita PR de fork sem segredo, sem pull_request_target, sem diff-check | track_08 | APPROVED | 1 |
| track_10 | RELEASE_GATE.md, promessa honesta no README e tag 0.1.0-rc | track_09 | APPROVED | 1 |


Status: `PENDING` -> `EXECUTED` | `FAILED` | `REPLAN` -> `APPROVED` | `CHANGES_REQUIRED` | `REPLAN`.
Execution writes its own row status and attempt number. Review writes the post-verdict status and moves `Current` on `APPROVED`. Nobody edits another row.

## Attempts

Append entries; never rewrite history.

### track_01 — Attempt 1
- Date: 2026-08-19
- Status: EXECUTED
- Outcome: AUDIT.md criado na raiz de semantic-architecture-context com 28 achados consolidados (incluindo todos os 21 achados obrigatórios de Semantic Authority), anchors arquivo:linha, sintomas, passos de reprodução, classificação única e mapeamento explícito para tracks do Bloco 01 e Bloco 02.

### track_02 — Attempt 1
- Date: 2026-08-19
- Status: EXECUTED
- Outcome: Repositório inicializado do zero com git init (sem herança de histórico do monorepo), LICENSE MIT 2026 Semantic Architecture Context Authors, CODE_OF_CONDUCT.md (Contributor Covenant v2.1), .gitignore com cobertura de bytecode/caches/node_modules/symbol_index/.claude/.serena, e .github/workflows/hygiene.yml + .github/scripts/check_hygiene.py implementados com falha dura e verificados com testes manuais de injeção de bytecode (.pyc) e strings proibidas (C:\Users\ e rabelo-standards). Commit inicial realizado.

### track_03 — Attempt 1
- Date: 2026-08-19
- Status: EXECUTED
- Outcome: Transplante verbatim de 20 arquivos sob src/, mcp/, ci/, docs/ a partir de rabelo-standards/sac-context/ com 100% de paridade de hash SHA-256 e zero alteração de conteúdo. Servidor MCP Python legado e diretórios __pycache__ excluídos. npm ci executado com sucesso em mcp/. node mcp/smoke.mjs executado com sucesso produzindo exatamente o mesmo veredicto e paridade CLI ≡ MCP da origem. Gate de higiene python .github/scripts/check_hygiene.py validado e verde (exit code 0).

### track_04 — Attempt 1
- Date: 2026-08-19
- Status: EXECUTED
- Outcome: Superfície MCP única consolidada exclusivamente no adapter Node (mcp/server.mjs); todas as menções ao servidor MCP Python legado removidas dos arquivos rastreados (0 matches em git grep). mcp/package.json estabelecido como SSOT absoluto de versão com version=0.1.0 e engines.node >= 22. mcp/server.mjs atualizado para resolver dinamicamente a versão via resolvePackageVersion() a partir de package.json com erro explícito em falha e zero literais semver hardcoded. src/sac_scan.py atualizado com flag --version lendo package.json com json da stdlib (stdlib-only). Gate de consistência de versão implementado em .github/scripts/check_version.py e integrado em hygiene.yml. Smoke test 100% verde e gates validados.

### track_05 — Attempt 1
- Date: 2026-08-19
- Status: EXECUTED
- Outcome: Separação estrita entre owned (.sac/domains.md) e managed (templates/domains.template.md) implementada. docs/SAC_domains.md legado removido. .sac/domains.md do próprio repositório criado com o domínio sac_core cobrindo o engine src/**. Matriz completa de 5 estados antigos implementada em src/sac_domains.py via resolve_domains_manifest() com erros estruturados explícitos e recuperáveis da família sac.environment.* (domains_manifest_legacy_layout e domains_manifest_ambiguous) propagados por todos os subcomandos de sac_scan.py e sac_engine.py sem crash nem fallback silencioso. Todas as 5 linhas da matriz e teste de isolamento/precedência verificados com fixtures automatizadas e logs registrados. Smoke test mcp/smoke.mjs 100% verde. Gates check_hygiene.py e check_version.py 100% aprovados.

### track_06 — Attempt 1
- Date: 2026-08-19
- Status: EXECUTED
- Outcome: Atestação explícita de `gates_bypassed` implementada em Python (`src/sac_domains.py`, `src/sac_engine.py`, `src/sac_scan.py`) para os 3 escapes (`SAC_ALLOW_UNSCOPED`, `SAC_ALLOW_FILEPATH_OUTSIDE_DOMAINS`, `SAC_ALLOW_HOP1_FULL_SCAN`) com inclusão da lista de env vars ativas e warnings dedicados (`Gate bypassed by environment override: <VAR>`), e omissão estrita do campo quando nenhum escape estiver ativo (custo zero de bytes). Terceira classe de erro da CLI unificada com emissão de JSON estruturado em stdout (`code: sac.environment.*`, exit code 2) via `SacArgumentParser` (`sac.environment.invalid_arguments`) e `validate_root` (`sac.environment.root_not_found`, `sac.environment.root_not_directory`). Adapter Node MCP (`mcp/server.mjs`) atualizado para mapear erros de ambiente para `sac.environment_error` e propagar structured JSON da CLI sem fallback para `lookup_failed`/`context_failed`. Smoke test estendido em `mcp/smoke.mjs` cobrindo todos os cenários de escapes (on/off), erros de ambiente e paridade estrita CLI ≡ MCP 100% verde. Gates de higiene e versão validados com sucesso.

### track_07 — Attempt 1
- Date: 2026-08-19
- Status: EXECUTED
- Outcome: Instalador universal `install.py` implementado na raiz em 100% Python stdlib (sem dependências de terceiros). Verificação rígida de runtimes para Python >= 3.11 e Node.js >= 22 com falhas explícitas nomeadas (`sac.installer.*`). Gerenciamento estrito de `owned` vs `managed` garantindo inicialização de `.sac/domains.md` a partir de `templates/domains.template.md` quando ausente e preservação 100% byte a byte (SHA-256 idêntico) de manifestos pré-existentes. Emissão clara de bloco JSON para host MCP sem jamais editar arquivos de configuração do host automaticamente. `README.md` criado na raiz com apresentação, os 3 princípios fundamentais do SAC e quickstart executável em 5 passos sem promessas infladas de prevenção de regressão. `docs/INSTALL.md` criado com guia abrangente de instalação, opções de CLI e troubleshooting. Suíte completa de verificação dos 6 DoDs em `ci/test_track_07_dod.py` 100% aprovada, `node mcp/smoke.mjs` 100% verde, `check_hygiene.py` e `check_version.py` validados.

### track_08 — Attempt 1
- Date: 2026-08-19
- Status: EXECUTED
- Outcome: Publicação das 3 skills públicas (`skills/sac-context/`, `skills/sac-onboard/`, `skills/sac-execution-overlay/`) com resolução relativa (`./PROMPT.md`, `./SKILL.md`), 100% livres de caminhos de máquina e menções ao monorepo privado. Desambiguação de frontmatters comprovada (`sac-context` para gramática e sintaxe de tags; `sac-execution-overlay` para gate cirúrgico de execução). `sac-evolution` excluída e substituída por `GOVERNANCE.md` (modelo Issue -> ADR -> PR -> Review), `CONTRIBUTING.md` e diretório `docs/adr/` com template de ADRs. `prompt_resumido.md` preservado e sanitizado. Todos os 5 critérios do DoD verificados, `check_hygiene.py`, `check_version.py` e `node mcp/smoke.mjs` 100% aprovados.

### track_09 — Attempt 1
- Date: 2026-08-19
- Status: EXECUTED
- Outcome: Pipeline de CI pública implementado em `.github/workflows/ci.yml` configurado para executar em `push` e `pull_request` (sem `pull_request_target`), com permissão explícita no topo `permissions: contents: read`, sem segredos e com limites determinísticos `timeout-minutes: 10` em todos os jobs. Matriz de runtime completa cobrindo Python (3.11, 3.12, 3.13) × Node (22, 24) para os jobs de higiene (`check_hygiene.py`, `check_version.py`), validação (`validate`, `index-build`) e smoke (`npm --prefix mcp ci`, `node mcp/smoke.mjs`, `ci/test_track_07_dod.py`, `ci/test_track_09_dod.py`). Zero ocorrências de `pull_request_target`, zero interpolações `${{ }}` em comandos `run:`, zero `continue-on-error` e zero jobs de `diff-check` (D14). Script local `ci/sac_ci_guard.ps1` e template `ci/sac_guard.yml` harmonizados para o layout atual do repositório. Suíte de verificação automatizada `ci/test_track_09_dod.py` criada e validando 100% dos 6 critérios do DoD.

### track_10 — Attempt 1
- Date: 2026-08-19
- Status: EXECUTED
- Outcome: `RELEASE_GATE.md` criado na raiz enumerando nominalmente as 9 tracks/itens do Bloco 02 com caixas de verificação vazias `[ ]` como critérios obrigatórios para a liberação da tag final `0.1.0`. `README.md` atualizado estabelecendo formalmente a promessa honesta de **co-edit gate** (verificador lexical de co-edição no diff e não prova formal de teste) e declarando as linguagens com suporte ativo hoje (`.dart`, `.ps1`) como limitação conhecida até a entrega poliglota do Bloco 02, com zero ocorrências de reivindicações infundadas de prevenção de regressão. `CHANGELOG.md` criado documentando a release candidate `0.1.0-rc` e consolidando as entregas do Bloco 01. Tag anotada `0.1.0-rc` criada no Git (sem criação da tag `0.1.0`). Suíte de teste automatizada `ci/test_track_10_dod.py` criada validando todos os 5 DoDs, e gates de higiene, versão e smoke 100% verdes.



