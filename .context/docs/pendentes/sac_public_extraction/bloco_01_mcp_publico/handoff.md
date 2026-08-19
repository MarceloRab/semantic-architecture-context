# Handoff — Bloco 01: SAC como MCP público

## Plan

- Design: .context/docs/pendentes/sac_public_extraction/bloco_01_mcp_publico/design.md
- Approved by: usuário, 2026-08-19 — autorização explícita para ativar o builder
- Current: track_04

## Tracks

| Track | Goal | Depends on | Status | Attempt |
| --- | --- | --- | --- | --- |
| track_01 | Auditoria de estado real consolidada em AUDIT.md, cada achado com anchor e classificação | none | APPROVED | 1 |
| track_02 | Esqueleto público: git do zero, MIT, .gitignore e gate de higiene que falha duro | track_01 | APPROVED | 1 |
| track_03 | Transplante verbatim de src/, mcp/, ci/, docs/ com smoke verde nos dois repositórios | track_02 | APPROVED | 1 |
| track_04 | Superfície MCP única e SSOT de versão em mcp/package.json, anunciando 0.1.0 | track_03 | EXECUTED | 1 |
| track_05 | Manifesto owned em .sac/domains.md, template managed, matriz de estados antigos fechada | track_04 | PENDING | 0 |
| track_06 | gates_bypassed no payload e terceira classe de erro sac.environment.* | track_05 | PENDING | 0 |
| track_07 | install.py stdlib-only que nunca sobrescreve owned, e quickstart executável | track_06 | PENDING | 0 |
| track_08 | Três skills públicas sem caminho de máquina e sem gatilho ambíguo, mais GOVERNANCE | track_07 | PENDING | 0 |
| track_09 | CI pública que aceita PR de fork sem segredo, sem pull_request_target, sem diff-check | track_08 | PENDING | 0 |
| track_10 | RELEASE_GATE.md, promessa honesta no README e tag 0.1.0-rc | track_09 | PENDING | 0 |

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
