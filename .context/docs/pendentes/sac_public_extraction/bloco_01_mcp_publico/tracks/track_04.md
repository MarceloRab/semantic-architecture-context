# Track 04 — Superfície MCP única e SSOT de versão

[governance]
1. Deliver the goal and DoD literally; do not invent observable behavior.
2. Follow the required approach; choose only mechanically equivalent details.
3. Read only causal dependencies and record mechanically necessary unexpected writes.
4. Replan on any DoD, strategy or authority gap; do not replace it with insight, heuristic or a merely functional result.
5. No silent fallback, masked error, weak critical heuristic, TODO/stub, optional improvement or self-certification.
[/governance]

## Goal

O repositório tem exatamente uma superfície MCP e exatamente uma fonte de versão, anunciando `0.1.0` de forma consistente na CLI, no servidor e no pacote.

## Context capsule

- Current flow: hoje existem **duas** superfícies MCP. A segunda, `src/sac_mcp_server.py` (não copiada em track_03), é um FastMCP que chama `sac_engine.lookup` direto com `root = os.getcwd()`, sem passar por `sac_domains` — logo sem gate de membership e sem PAUSE de `filepath_required`. Ela é também o único arquivo Python com dependência de terceiros.
- Current flow: a versão hoje tem três fontes divergentes — `mcp/package.json` `"version": "1.0.0"`, `new McpServer({ version: "1.6.0" })` @ `mcp/server.mjs:327`, e o gate D4 da skill `sac-evolution` ("MCP v1.6.0+").
- Owner: `mcp/package.json` passa a ser a fonte única de versão.
- Dependency: `mcp/server.mjs` já é módulo ESM e pode ler JSON; `sac_scan.py` tem `json` da stdlib disponível.

## Semantic authority

- Must: remover toda referência a `sac_mcp_server.py` em `docs/`, em `ci/` e em qualquer texto rastreado. O arquivo já não existe no destino.
- Must: `mcp/package.json` → `"version": "0.1.0"` e `"engines": { "node": ">=22" }`.
- Must: `mcp/server.mjs` lê a versão de `mcp/package.json` em vez do literal `"1.6.0"`.
- Must: `sac_scan.py` ganha `--version`, que lê a mesma `mcp/package.json` com o `json` da stdlib.
- Must: um gate de CI falha se aparecer literal de versão semver fora de `mcp/package.json` em arquivo rastreado.
- Must not: reintroduzir adapter Python; adicionar dependência de terceiros em `src/`; criar arquivo `VERSION`; alterar comportamento de qualquer tool MCP.
- Error behavior: se `mcp/package.json` não puder ser lido, a CLI e o servidor falham explicitamente com erro nomeado. Nunca assumem versão padrão.

## Required approach

- Owner and boundary: `mcp/package.json` é o SSOT. `server.mjs` e `sac_scan.py` são leitores.
- Data/control flow: leitura do JSON na inicialização → valor propagado ao `McpServer` e ao `--version`.
- Integration rule: o engine permanece stdlib-only (contrato herdado). Ler `package.json` com `json` da stdlib não viola isso.
- Executor latitude: mechanically equivalent details only

## Focus

- Likely writes: `mcp/package.json`, `mcp/server.mjs`, `src/sac_scan.py`, `.github/workflows/`, `docs/`
- Essential reads: `mcp/server.mjs:327`, `docs/` (referências ao adapter Python)
- Forbidden work: tocar caminho do manifesto; alterar payload; mexer em `SAC_ALLOW_*`; migrar SDK
- Stop if: alguma tool depender do literal `1.6.0` para negociar comportamento
- Depends on: track_03

## DoD

1. Busca por `FastMCP` e por `sac_mcp_server` em arquivos rastreados retorna zero resultados. | Proof: inspect
2. `initialize` do servidor MCP anuncia `0.1.0`; `sac_scan.py --version` imprime `0.1.0`; `mcp/package.json` declara `0.1.0`. | Proof: manual (três execuções)
3. Reintroduzir um literal semver em `mcp/server.mjs` faz o gate de CI falhar. | Proof: manual
4. `mcp/smoke.mjs` continua verde. | Proof: manual
5. `src/` continua sem import fora da stdlib. | Proof: inspect

## Handoff

- File: .context/docs/pendentes/sac_public_extraction/bloco_01_mcp_publico/handoff.md
- Terminal: `EXECUTED`; review requires a separate manual trigger
