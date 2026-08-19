# SAC — Handoff de Melhorias para o Projeto Pai (`rabelo-standards`)

> Documento para o agente que constrói/mantém **rabelo-standards**.
> **Regra de governança:** não alterar runtime/skills SAC diretamente em projetos filhos. Implementar e aprovar nas autoridades canônicas do pai (`sac-context/` + 3 bundles do catalog) e propagar pelo mirror. `templates/project-base` é snapshot derivado, nunca fonte.
>
> Complementa: [`SAC_V2.md`](SAC_V2.md), [`SAC_domains.md`](SAC_domains.md), skill `sac-onboard` (Etapas 1–4).

---

## Função deste arquivo (para o agente)

| Escopo | O quê |
| --- | --- |
| **Pai (`rabelo-standards`)** | Processo, scaffold, ferramental, docs, CI — **propagável** |
| **Filho** | Tags no app, `SAC_domains.md`, drawers — **específico do app; não copiar para o pai** |

Este handoff registra **bloqueios e decisões** do padrão SAC. O menor caminho aceitável **não** é o correto: o que quebra o objetivo da feature deve ficar explícito aqui até decisão humana.

---

## Bloqueio / status — MCP SAC no Cursor (2026-07-19 → atualizado)

### 1. Problema histórico (instabilidade Python FastMCP no Cursor)

**Objetivo da feature:** `get_sac_constraints` via MCP como via **principal** de consulta SAC no agente.

**Evidência no Cursor com FastMCP Python (Windows, 2026-07-19):**

- Chamadas MCP falhavam com `Connection closed` / **timeout** (minutos), enquanto o processo Python ficava ocioso (CPU ~0).
- O mesmo lookup via CLI respondia em ~100–200 ms:
  `python sac-context/src/sac_scan.py lookup <symbol> --root .`
- Foram observados processos `sac_mcp_server.py` duplicados (pai + filho).
- `__pycache__/sac_engine.cpython-312.pyc` é só efeito de import — não é a causa.

**Conclusão (histórica):** o **engine é estável**; o caminho **Python FastMCP stdio no Cursor** não era funcional com estabilidade. Isso **quebrava o objetivo** da feature neste host. Não documentar como “opcional por desenho”.

### 2. Resolução canônica (implementação no pai)

**Decisões MCP-1…9 (trilha `sac_mcp_node_stability`):**

1. **SSOT** = engine + CLI (`sac_engine.lookup` / `sac_scan.py lookup --json`).
2. **Entry Cursor** = adapter Node (`sac-context/mcp/server.mjs`) → spawn CLI; zero parse.
3. **FastMCP** `sac_mcp_server.py` = **LEGACY/debug only**.
4. Engine: `filepath` restringe scan; `ignore_dirs` expandido (T1).
5. Smoke CLI Node≡CLI: `npm run smoke` / `smoke_sac_mcp_node.ps1` (T2 PASS).
6. **Cursor smoke host** = gate de COMPLETE (T5) — ainda **pendente**.

**Status 2026-07-19 (pós T2/T3):**

| Camada | Status |
| --- | --- |
| Engine + CLI | OK |
| Adapter Node + lockfile + smoke local | **FEITO** (T2) |
| Docs/skills Node primary | **FEITO** (T3) |
| Mirror PROP-1 (DestinationPath obrigatório; templates fora do escopo desta feature) | **FEITO** (T4) |
| Smoke Cursor `get_sac_constraints` &lt;5s | **PASS** (T5, 2026-07-19) |

**Não recomendado:** normalizar “MCP opcional + soft-fail” como arquitetura final — isso rebaixa a feature (MCP-9).

### 3. Codex e OpenCode — status (pesquisa + evidência local)

| Host | MCP stdio suportado? | Estável para SAC **neste ambiente**? | Notas |
| --- | --- | --- | --- |
| **Cursor** (FastMCP Python) | Sim (config) | **Não** — evidência 2026-07-19 | Timeout / connection closed (histórico) |
| **Cursor** (Node adapter) | Sim (`~/.cursor/mcp.json` → `node …/server.mjs`) | **PASS** T5 | `user-sac` / `get_sac_constraints` listável; `found=true` em símbolo tagueado; resposta imediata (&lt;5s); sem connection closed |
| **Codex** | Sim (`~/.codex/config.toml`) | **SKIP** nesta trilha | Preferir Node; smoke não medido |
| **OpenCode** | Sim (`opencode.json`) | **SKIP** nesta trilha | Preferir Node; smoke não medido |
| **CLI Python** | N/A | **Sim** | Via universal |

```text
Autoridade de lookup: python sac-context/src/sac_scan.py lookup <symbol> --root <project> [--path <file>] --json
MCP entry Cursor: node sac-context/mcp/server.mjs (SAC_ROOT=project; SAC_PYTHON opcional)
MCP Cursor Node: PASS 2026-07-19 — feature cumprida neste host
```

### Decisão T5 — fechada

- [x] `C:\Users\Rabelo\.cursor\mcp.json` atualizado com entry Node `sac`
- [x] Smoke Cursor PASS (tool listável + found=true &lt;5s)
- [x] Codex / OpenCode = SKIP (fora do gate Cursor)

---

## 4. Gate de injeção física no `sac-onboard` (2026-07-24)

**Origem:** auditoria do delta `realtime_streams` no filho mostrou `SAC_domains.md`/drawer/índice atualizados sem novas tags físicas no fonte.

**Causa raiz:** MCP/CLI são corretamente read-only; a skill não bloqueava visualmente o closeout quando a injeção não tinha evidência.

**Decisão canônica:**

- agente apenas propõe linhas ARCH/REGR/DEPRECATED; humano aprova o texto literal;
- delta estrutural exige injeção física + lookup `found=true` por símbolo;
- domínio, drawer e índice ficam proibidos até `injection_gate: PASS`;
- arquivo novo usa apenas CLI `lookup --pre-onboard --path`, bounded ao arquivo e indisponível em READ/EXECUTE;
- `validate` avisa `UNMAPPED_ANCHOR_SYMBOL` para anchor sem tag física;
- delta administrativo não cria tags e deve fechar sem esse warning.

**Escopo:** `EMPTY_DOMAIN_FILE` permanece fora desta trilha por risco de falso positivo em arquivos de suporte sem anchor próprio.

**Fechamento:** `parent_pipeline_status: aligned`; `propagation_status: mirrored`. Pai e filho passaram no smoke; mirror ficou idempotente e preservou o hash do `SAC_domains.md`. A auditoria do filho expôs 15 anchors sem tag (7 em `realtime_streams`) sem escrever tags automaticamente.

Detalhes e DoD: [`SAC_report_melhoria_sac_onboard_injection.md`](SAC_report_melhoria_sac_onboard_injection.md).

---

## 5. Recomendações de Evolução — Validação de Símbolos (`MUST verify:`) e Portabilidade Zero-MCP (2026-08-15)

### A. Validador Estático de Símbolos no CI/CLI (`MUST verify:` Drift Guard)
- **Contexto / Risco:** As tags `# SAC:REGR:` / `// SAC:REGR:` prescrevem causalidade estrita via cláusula `MUST verify: [SymbolA, SymbolB]`. Em refatorações onde funções/classes são renomeadas ou movidas, esses tokens podem se tornar referências fantasmas (*silent drift*).
- **Proposta para o Pai (`sac-context/src/sac_scan.py`):**
  - Estender o comando `sac_scan.py validate` (ou flag `--check-verify-symbols`) para resolver os tokens de `verify:` contra o índice de símbolos/AST do projeto.
  - Emitir warning/erro canônico `UNRESOLVED_VERIFY_TARGET` caso um símbolo citado no `MUST verify` não exista fisicamente nos arquivos do domínio.
  - Integrar como step opcional de pre-commit / CI no `rabelo-standards`.

### B. Diretriz Canônica para Agentes sem MCP (Zero-MCP Graceful Degradation)
- **Contexto:** A eficácia do SAC reside na localidade (*in-situ context*). Mesmo agentes sem ferramentas MCP ativas leem os comentários imediatamente acima das assinaturas via visualizadores de arquivo padrão.
- **Proposta no Pai:** Incluir no `.cursorrules` / template de governança do pai uma instrução explícita de L0:
  > *"Comentários `# SAC:` ou `// SAC:` contêm invariantes de arquitetura e pontos críticos de regressão em gramática RFC 2119. Devem ser respeitados como restrições absolutas de código no ponto de edição."*

---

## Referências rápidas

- Gramática / CI: [`SAC_V2.md`](SAC_V2.md)
- Ativação: [`SAC_BOOTSTRAP.md`](SAC_BOOTSTRAP.md)
- Skills: `sac-context`, `sac-onboard`, `sac-execution-overlay`, `sac-evolution`
- Mirror: `scripts/mirror-sac-tooling.ps1` (preserva `docs/SAC_domains.md` se já existir no destino)

## Changelog

| Data | Nota |
| --- | --- |
| 2026-07-19 | Limpeza: handoff focado em função + bloqueio MCP Cursor; status Codex/OpenCode; recomendação SSOT CLI + smoke por host |
| 2026-07-19 | T3: Node primary documentado; FastMCP LEGACY; Cursor smoke permanece gate T5 |
| 2026-07-19 | T5: Cursor Node MCP PASS (`~/.cursor/mcp.json`); Codex/OpenCode SKIP |
| 2026-07-24 | Seção 4: INJECTION-GATE, lookup CLI bounded pré-onboard e warning `UNMAPPED_ANCHOR_SYMBOL` |
| 2026-08-15 | Seção 5: Recomendações de evolução — Validação estática de símbolos `MUST verify:` no CLI/CI e diretriz canônica Zero-MCP |
