source_of_truth: .context/DIRECTIVES.md
purpose: map directive_id to diff targets without duplicating semantic rules

| directive_id | applies_to | diff_targets | trigger_when | plan_action |
| --- | --- | --- | --- | --- |
| SAC-PR1 | gramática da tag | `src/sac_engine.py`, `templates/domains.template.md`, `skills/sac-context/` | tocar campo, marcador, trigger ou forma da linha | ler a diretiva antes de alterar a gramática |
| SAC-PR2 | vocabulário e warnings | `src/sac_engine.py`, `src/sac_validate.py`, `skills/sac-context/` | adicionar/alterar vocabulário fechado ou warning canônico | promover Rule a requisito da track |
| SAC-PR3 | leitura sem ferramenta | `src/sac_engine.py`, `mcp/server.mjs`, `AGENTS.md`, `skills/*/PROMPT.md` | alterar payload, linha da tag, manifesto ou porta de entrada | exigir prova linha crua × payload no DoD |
| SAC-PL1 | payload e orçamento | `src/sac_engine.py`, `src/sac_scan.py`, `mcp/server.mjs` | tocar serialização, `--root`, `SAC_CONTEXT_MAX_BYTES` ou `_perf` | exigir medição ponta a ponta no DoD |
| SAC-PL2 | gate de regressão | `src/sac_diff.py`, `ci/sac_guard.yml`, `.github/workflows/ci.yml`, `README.md` | tocar cobertura, `verify:`, ACK ou job de gate | exigir fixture em duas ordenações no DoD |
| SAC-PL3 | alcance de adoção | `src/sac_diff.py`, `src/sac_engine.py`, `README.md` | tocar `_SYMBOL_REGISTRY`, marcador ou matriz de compatibilidade | exigir fixture positiva e negativa por linguagem |
| SAC-X1 | pureza do engine | `src/`, `mcp/package.json`, `.github/workflows/` | qualquer import novo ou proposta de análise estrutural | bloquear e reportar se a proposta cair na lista de vetos |
| SAC-X2 | superfície semântica | `src/sac_engine.py`, `src/sac_domains.py` | qualquer proposta de tag ou cenário novo | bloquear; exigir diff vazio dos frozensets |
| SAC-X3 | estados antigos | `src/sac_engine.py`, `src/sac_domains.py`, `src/sac_scan.py`, `templates/` | tocar schema, parser, gramática persistida ou caminho de manifesto | exigir matriz de estados antigos fechada antes de executar |
| SAC-X4 | layout managed/owned | `src/sac_domains.py`, `install.py`, `templates/`, `.sac/` | tocar resolução de caminho de manifesto ou o installer | exigir prova de não-sobrescrita no DoD |
| SAC-X9 | fronteira de escrita | nenhum — proíbe alvos fora do repositório público | qualquer track que mencione consumidor ou propagação | bloquear escrita fora de `semantic-architecture-context` |
| SAC-X5 | gates e paridade | `src/sac_scan.py`, `src/sac_domains.py`, `mcp/server.mjs`, `mcp/smoke.mjs` | tocar `SAC_ALLOW_*`, payload ou casos de paridade | exigir caso de smoke por escape e caso não-normalizado |
| SAC-X6 | release | `mcp/package.json`, `RELEASE_GATE.md`, `CHANGELOG.md`, `.github/workflows/` | criar tag, alterar versão ou fechar bloco | bloquear tag sem checklist do gate com evidência |
| SAC-X7 | higiene de publicação | todo arquivo rastreado, `skills/`, `.gitignore`, `.github/workflows/hygiene.yml` | qualquer commit no repositório público | rodar gate de higiene antes de aceitar o diff |
| SAC-X8 | contrato de execução | toda track de `dh-exec-track-v5` | qualquer execução de track | rejeitar decisão semântica nova; devolver ao planejamento |
