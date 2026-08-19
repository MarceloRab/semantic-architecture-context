# SAC Bootstrap — Como ativar SAC em um projeto filho

> Guia operacional para projetos que já receberam o scaffold SAC via `bootstrap-new-project.ps1` ou `mirror-sac-tooling.ps1`. Não substitui [`SAC_V2.md`](SAC_V2.md); é o ponto de partida prático.

---

## 1. Verifique o scaffold

Após o bootstrap, o projeto deve conter:

```text
sac-context/
  src/sac_engine.py
  src/sac_scan.py
  src/sac_diff.py
  src/sac_validate.py
  mcp/server.mjs          # primary MCP stdio (Node)
  mcp/package.json
  mcp/package-lock.json
  templates/domains.template.md
  .sac/domains.md
  docs/SAC_V2.md
  docs/SAC_validate.md
  docs/SAC_improvement_roadmap.md
  docs/SAC_BOOTSTRAP.md
  ci/sac_guard.yml
  ci/sac_ci_guard.ps1
.context/skills/catalog/domains/context-governance/
  sac-context/SKILL.md
  sac-onboard/SKILL.md
  sac-execution-overlay/SKILL.md
```

> O arquivo `.sac/domains.md` é de posse exclusiva do projeto (`owned`) e nunca sobrescrito por updates de tooling. O template/schema correspondente reside em `templates/domains.template.md` (`managed`).

---

## 2. Ativar o CI guard (GitHub Actions)

1. Copie ou mova `sac-context/ci/sac_guard.yml` para `.github/workflows/sac_guard.yml`.
2. Ajuste a branch alvo se necessário (padrão: `main`).
3. O workflow já roda `diff-check` e `validate` em modo **warning-only** por padrão (ver item 4 abaixo).

```powershell
New-Item -ItemType Directory -Path .github/workflows -Force | Out-Null
Copy-Item sac-context/ci/sac_guard.yml .github/workflows/sac_guard.yml
```

---

## 3. Registrar o MCP SAC (Node primary)

Entry Cursor/stdio = **Node** (`sac-context/mcp/server.mjs`). Tags no código = SSOT; Python CLI = implementação canônica de leitura.

Antes do primeiro uso: `cd sac-context/mcp && npm ci`. Se a IDE não achar `python`, defina `SAC_PYTHON` no `env` do servidor.

### Cursor

Arquivo **`~/.cursor/mcp.json`** (global — validado Windows). **Não** usar `<projeto>/.cursor/mcp.json` neste host.

```json
{
  "mcpServers": {
    "sac": {
      "type": "stdio",
      "command": "node",
      "args": [
        "C:\\Users\\Rabelo\\projects\\<FILHO>\\sac-context\\mcp\\server.mjs"
      ],
      "env": {
        "SAC_PYTHON": "C:\\Users\\Rabelo\\AppData\\Local\\Programs\\Python\\Python312\\python.exe"
      }
    }
  }
}
```

Pipeline execução: **session boot** `list_sac_domains()` → auto-route somente com 1 intent compatível → `get_sac_context(domain_id)` → `get_sac_constraints(symbol, filepath, domain_id)` quando houver alvo preciso. `discover_sac` fica como inventário opcional.

> Filho = mirror. Mudanças SAC aplicam-se nas autoridades canônicas do **pai**: `rabelo-standards/sac-context/` (runtime/docs) e `rabelo-standards/skills/catalog/domains/context-governance/sac-{context,onboard,execution-overlay}/` (skills). Propagar com `mirror-sac-tooling.ps1` após aprovação. `templates/project-base/sac-context/` é snapshot derivado de bootstrap e nunca fonte do mirror.

### OpenCode

Arquivo `.opencode.json` (projeto) ou `~/.opencode.json` (`cwd` = raiz do projeto):

```json
{
  "mcpServers": {
    "sac": {
      "type": "stdio",
      "command": "node",
      "args": ["./sac-context/mcp/server.mjs"],
      "env": {
        "SAC_ROOT": "."
      }
    }
  }
}
```

### Codex (OpenAI)

Arquivo `~/.codex/config.toml` (user) ou `.codex/config.toml` (projeto trusted):

```toml
[mcp_servers.sac]
command = "node"
args = ["./sac-context/mcp/server.mjs"]
env = { SAC_ROOT = "." }
```

---

## 4. Ordem de degradação para consulta SAC (READ only)

Os MCPs SAC **só leem** constraints; não pedem alteração no projeto e **não autorizam** criar tags. As tags no código permanecem SSOT; o MCP apenas monta o contexto.

**Session boot (qualquer intenção de código/arquitetura):** chamar `list_sac_domains()` antes do primeiro Read. Exatamente 1 intent compatível autoriza auto-route; zero → busca bounded-unmapped; múltiplos → HALT. Falha MCP → anunciar CLI; **não** `rg` global.

**Modo READ (pergunta):** Route → Context → Verify preciso; resposta compacta ≤15 linhas; citar `sac_perf: <ms>, <bytes>B` se `_perf` presente.

Se o MCP não estiver disponível, siga esta ordem e anuncie cada nível ao usuário:

1. **Route:** `list_sac_domains` / `.sac/domains.md` (1 intent → auto-route; zero → bounded-unmapped; múltiplos → HALT). No modo unmapped: `fd` somente em diretórios objetivos → `rg` scoped → `bat`; nunca PowerShell equivalente para contornar bloqueio.
2. **Context:** `get_sac_context({domain_id})` — anchors + todas `REGR`/`DEPRECATED` + hop1 em uma varredura de um único domínio; `context_payload_too_large` → nenhuma constraint, seguir Discover/Verify focado
3. **MCP Verify:** `get_sac_constraints(symbol, filepath?, domain_id?)` — omitido → PAUSE `filepath_required` (≡ CLI)
4. **Discover opcional:** `discover_sac({domain_id})` quando o overlay não localizar o alvo
5. **CLI:** `list-domains`; `context --domain`; `lookup --path`; `discover --domain` — mesmo JSON que MCP
6. **Fallback manual:** `rg "SAC:" -n <file>` somente nos `files:` do domínio e somente para tags existentes
7. **Índice hop1:** `index-build` / `--check`

**Anti-inventário:**

| Situação | Ação |
| --- | --- |
| Alvo sem `SAC:` | **Não faça nada** sobre tags |
| Path tagueado + MCP e CLI down | **NO-GO / STOP** |
| MCP ausente | **Não** invente `// SAC:`; **não** dispare `sac-onboard` automaticamente |

WRITE de tags = skill `sac-onboard` (ou pedido humano explícito) apenas. Ver [`SAC_V2.md`](SAC_V2.md) § READ vs WRITE.

### 4.1 Smoke MCP (aceite operacional pós-registro — obrigatório)

Após registrar o servidor Node, na sessão do agente confirme:

1. Servidor `sac` / `user-sac` = **Ready** (Settings → MCP).
2. Boot probe: `list_sac_domains()` retorna catalog em **&lt; 5s**.
3. Tools listadas: `list_sac_domains`, `get_sac_context`, `discover_sac`, `get_sac_constraints`.
4. Em domínio resolvido: `get_sac_context(domain_id)` retorna anchors + `REGR`/`DEPRECATED` + hop1 em **&lt; 5s**; `files:` permanece limite de busca, não fila de leitura.
5. Em símbolo tagueado: `get_sac_constraints(symbol, filepath=<file>)` → `found=true` em **&lt; 5s**.
6. Respostas MCP incluem `_perf.elapsed_ms` e `_perf.payload_bytes` — citar 1 linha no report; não dump JSON.
7. Smoke local: `cd sac-context/mcp && npm run smoke`.

Sem smoke verde no host → **BLOQUEIO** documentado; use CLI anunciado; **não** declare feature MCP cumprida.

### 4.2 DoD operacional (2 sessões)

| # | Gate |
|---|------|
| D1 | MCP Ready |
| D2 | Boot probe OK |
| D3 | Q&A ou edit via Route→Context→Verify sem rg global |
| D4 | `_perf.elapsed_ms` + `_perf.payload_bytes` citados quando presentes |
| D5 | `npm run smoke` exit 0 |

**Aceite:** D1–D5 PASS em **2 sessões consecutivas** sem erro IPC (`MessagePort`).

### 4.3 DoD cristalino (referência)

Ver `SAC_V2.md` § DoD operacional. Resumo: hot path = Context `missing=[]` **ou** overflow explícito + Discover→Verify (sem thin); onboard = ASSESS sem diff → APROVAR → 1 TAG_DELTA; capillarity = cold path; revert = FAIL.

Falhas comuns se a tool não listar:

- `npm ci` não rodado em `sac-context/mcp`.
- `args` apontando para `server.mjs` de outro repo (SAC-MCP-01).
- `<projeto>/.cursor/mcp.json` neste host Windows.
- Lookup MCP sem `filepath` → rejeição de schema Zod (`filepath` required).
- `python` / `SAC_PYTHON` fora do PATH da IDE (adapter spawna CLI).
- Configuração de MCP apontando para caminho inexistente ou inválido.
- Servidor `sac` desabilitado na UI MCP.

Ausência de MCP na sessão ≠ inventar comentários; autoriza só degradação anunciada → CLI/`rg` **ou** `NO-GO` conforme a tabela acima. MCP “opcional por desenho” = **proibido**.
---

## 5. Path canônico de skills

As skills SAC vivem em:

```text
.context/skills/catalog/domains/context-governance/
```

> O template `project-base` pode espelhar com ou sem o segmento `catalog` dependendo da versão do `rabelo-standards`. A fonte da verdade é sempre `skills/catalog/domains/<domain>/<skill>/SKILL.md` no `rabelo-standards`.

---

## 6. Validate — fases de adoção

A validação AST é opcional/lazy: funciona sem `tree-sitter` para Python, mas precisa de `tree-sitter` + `tree-sitter-dart` para Dart.

### Fase 1 — dry-run (recomendado)

```powershell
python sac-context/src/sac_scan.py validate --root . --json
```

Colete orphans e warnings existentes. Sem falhar no CI.

### Fase 2 — warning-only

O CI template já roda `validate` em warning-only. Isso significa que a presença de orphans **não** bloqueia o merge. O objetivo é observar e corrigir gradualmente.

### Fase 3 — hard-fail

Quando o projeto tiver:

- `tree-sitter` + `tree-sitter-dart` instalados no CI
- `0` orphans no baseline
- Equipe treinada em `SAC-ACK`

Remova a condição warning-only do `sac_guard.yml` e deixe o `validate` falhar em orphans.

---

## 7. Primeiro onboard

Para adicionar o primeiro domínio SAC ao projeto, siga a skill `sac-onboard`:

```text
Use a skill sac-onboard (skills/catalog/domains/context-governance/sac-onboard/SKILL.md) para avaliar a funcionalidade [NOME] e criar as linhas SAC necessárias.
```

A skill exige aprovação do usuário antes de injetar tags (Etapa 1 → Etapa 2).

---

## 8. Edições futuras

Para qualquer pergunta, plano, review ou implementação de código/arquitetura em projeto SAC-enabled, ative `sac-execution-overlay` antes da primeira leitura de código.

```text
Use a skill sac-execution-overlay (skills/catalog/domains/context-governance/sac-execution-overlay/SKILL.md) antes de editar [ARQUIVO].
```

Se o contexto revelar lacuna de tags, não invente nem grave automaticamente: use `sac-onboard delta` para propor o mínimo necessário e aguarde aprovação humana.

---

## Referências

- [`SAC_V2.md`](SAC_V2.md) — gramática, CLI, MCP, CI, contrato READ vs WRITE.
- [`.sac/domains.md`](../.sac/domains.md) — índice de domínios onboardados (owned).
- [`templates/domains.template.md`](../templates/domains.template.md) — schema e template managed.
- [`SAC_validate.md`](SAC_validate.md) — critérios de adoção do `validate`.
- [`SAC_improvement_roadmap.md`](SAC_improvement_roadmap.md) — evolução propagável do scaffold.
