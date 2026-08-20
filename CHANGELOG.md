# Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [0.1.0-rc] - 2026-08-19

Release candidate consolidando a conclusão do Bloco 01 (SAC como MCP Público independente e universal).

### Breaking
- **Veredicto do gate `diff-check` independente da ordem dos caminhos**: a cobertura `verify:` agora é avaliada somente após reunir todos os símbolos e arquivos alterados. Esta correção muda o comportamento do gate: PRs que antes passavam porque um alvo ainda não havia sido visto podem agora falhar com a violação real, enquanto alvos coeditados deixam de exigir `SAC-ACK` apenas por aparecerem depois na ordenação do diff.

### Adicionado
- **Repositório Público Independente**: Repositório extraído e auditado (`AUDIT.md`), sob licença permissiva MIT e Código de Conduta Contributor Covenant v2.1.
- **Superfície MCP Única em Node ESM**: Servidor MCP stdio em `mcp/server.mjs` como autoridade única de interface MCP, eliminando o legado Python MCP.
- **Engine e CLI Python stdlib**: CLI e motor de varredura `src/sac_scan.py` e `src/sac_engine.py` compatíveis com Python 3.11+ utilizando 100% biblioteca padrão (zero dependências externas).
- **Separação Estrita de Manifestos**: Manifesto do projeto `owned` em `.sac/domains.md` preservado e template de referência `managed` em `templates/domains.template.md`, com suporte a transição determinística de layouts legados.
- **Atestação de Gates de Segurança**: Campo `gates_bypassed` incluído no payload estruturado quando variáveis de escape (`SAC_ALLOW_*`) estiverem ativas, e terceira classe unificada de erros de ambiente (`sac.environment.*`).
- **Instalador Universal `install.py`**: Script stdlib de setup rápido e validação de pré-requisitos (`--target`), preservando byte a byte manifestos pré-existentes.
- **Skills Públicas Sanitizadas**: Três skills para agentes de IA (`skills/sac-context/`, `skills/sac-onboard/`, `skills/sac-execution-overlay/`) com caminhos 100% relativos e desambiguação estrita de escopo.
- **Governança Aberta**: Documentação de modelo de decisão e contribuição em `GOVERNANCE.md`, `CONTRIBUTING.md` e repositório de ADRs em `docs/adr/`.
- **Pipeline de CI com Matriz de Runtime**: Workflow GitHub Actions (`.github/workflows/ci.yml`) testando PRs de forks em matriz Python (3.11, 3.12, 3.13) × Node (22, 24) com permissões mínimas (`contents: read`) e gates de higiene/versão.
- **Release Gate para Bloco 02**: `RELEASE_GATE.md` estabelecendo os 9 critérios obrigatórios para a liberação da tag final `0.1.0`.
