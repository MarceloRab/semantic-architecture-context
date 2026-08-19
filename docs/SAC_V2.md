# Semantic Architecture Context (SAC) V2

> Governança ativa de arquitetura funcional: restrições embarcadas no código-fonte, consumidas por agentes via MCP/CLI e validadas no CI.

## O que é SAC

SAC (Semantic Architecture Context) é um padrão de anotação em comentários de código que associa restrições arquiteturais aos símbolos que as representam. Ele substitui a documentação passiva por um contrato verificável:

- **Agentes** consultam restrições antes de modificar símbolos arquiteturais.
- **CI** bloqueia merges que alterem `SAC:REGR` sem cobrir os alvos declarados.
- **Humanos** liberam exceções explicitamente via `SAC-ACK: <symbol>`.

### Pilares

- **Motor/core:** tags no código são a única SSOT de constraints e regressões.
- **Cérebro:** índices + MCP localizam tags e montam contexto; nunca duplicam constraints.
- **Agente consciente:** Route + overlay antes da primeira leitura de código.
- **Agente cego:** recebe a tag passivamente ao ler o símbolo; CI aplica `REGR` mesmo sem skill.

## Escopo de aplicação

Injete SAC nos escopos de triagem do `sac-onboard`:

- State Managers / Gerenciadores de estado
- Repositórios / Data sources
- Interfaces de Integração (APIs, gateways, clients)
- Orquestradores públicos / Use cases expostos

O `sac-onboard` possui três modos fechados: `ASSESS` (read-only), `REGISTER` (index-only em [`SAC_domains.md`](SAC_domains.md)) e `TAG_DELTA` (ADD/REPLACE/REMOVE literal de tags). Drawer e relatório persistente nunca são saída padrão. Agentes roteiam intent pelo índice; edições usam `sac-execution-overlay` + `get_sac_constraints`.

## READ vs WRITE (contrato anti-inventário)

O MCP `get_sac_constraints` é **somente leitura** (lookup JSON). Não pede e não autoriza criar tags.

```text
EXECUTE: read SAC only (MCP get_sac_constraints → sac_scan lookup → rg "SAC:")
WRITE SAC tags: sac-onboard only (aprovação humana)
No SAC: on target → do nothing about tags (EXECUTE)
Tagged path + MCP and CLI down → NO-GO / STOP
Invent SAC: / compliance comments outside onboard = contract failure
```

| Situação | Ação canônica | Proibido |
| --- | --- | --- |
| EXECUTE, alvo sem `SAC:` | Seguir a trilha; **no-op** quanto a tags | Inventar `// SAC:` ou comentário de compliance |
| EXECUTE, arquivo já tagueado, MCP+CLI falham | **NO-GO** | Soft-fail + inventar tag |
| `sac-onboard` sem modo literal | `ASSESS` read-only | Inferir REGISTER/TAG_DELTA ou escrever |
| `APROVAR SAC REGISTER <id>` | Atualizar somente `SAC_domains.md` com cobertura física já válida | Criar tags, drawer ou relatório |
| `APROVAR SAC TAG_DELTA <id>` + tabela literal | Aplicar somente ADD/REPLACE/REMOVE aprovados | Completar/reformular linhas ou aumentar densidade |

Ausência de MCP **não** autoriza inventar nem disparar `sac-onboard` automaticamente.

### Gate do `sac-onboard`

`ASSESS` é o default seguro e nunca escreve. `REGISTER` exige `APROVAR SAC REGISTER <domain_id>`, reutiliza somente tags físicas canônicas e altera exclusivamente `SAC_domains.md`; não cria tag, drawer, relatório ou `tag_count` manual.

`TAG_DELTA` é o único modo que altera tags. Exige `APROVAR SAC TAG_DELTA <domain_id>` e tabela literal com operação `ADD|REPLACE|REMOVE`, arquivo, assinatura, linha atual e linha nova. A aprovação congela operação e texto. ADD/REPLACE devem retornar `found=true`; REPLACE/REMOVE devem provar ausência da linha anterior; qualquer linha extra, warning, orphan ou divergência exige HALT. Somente após `tag_delta_gate: PASS` o índice de domínio pode mudar. Aprovação genérica e pedido de novo domínio nunca autorizam tags.

## Como o agente usa o projeto (filho)

Ordem fixa. Não pule camadas.

```text
1. Boot    → em toda intenção de código/arquitetura, list_sac_domains() antes de Read
2. Route   → catalog: domain_id + summary + files_count ONLY
             exatamente 1 intent compatível → auto-selecionar
             zero intents → bounded-unmapped; múltiplos → ask/NO-GO; proibido chutar ou expandir múltiplos
3. Context → get_sac_context({domain_id})
             anchors + todas REGR/DEPRECATED + hop1, constraints lidas das tags
4. Verify  → get_sac_constraints(symbol_name, filepath, domain_id)
             fast path preciso quando símbolo/path já existem
5. Discover→ discover_sac({domain_id}) para inspeção detalhada
             fallback anunciado: rg somente nos files: do domínio
6. Capillarity (on-demand) → assess_sac_capillarity({domain_id}) ou CLI capillarity --domain
             **nunca no boot**; só auditoria explícita, onboard ASSESS, suspected_stale ou context overflow
7. Gate    → index-build (CI) + diff-check / validate
```

**Tools MCP**

| Tool | Camada | Papel |
|------|--------|-------|
| `list_sac_domains` | L0 Route | Catalog mínimo; auto-rota só com exatamente 1 intent compatível |
| `get_sac_context` | Context fast path | Anchors + todas `REGR` + hop1; uma leitura dos `files:` |
| `discover_sac` | L1 Discover | Tags só em `files:` do `domain_id` — cards slim (sem constraint) |
| `get_sac_constraints` | L2 Verify | Constraint precisa **ou** PAUSE `filepath_*` (MCP≡CLI) |
| `assess_sac_capillarity` | On-demand | (A) claims vs tags, (B) context fitness, (C) payload; **proibido** no boot Route→Context |

**COR-GATE (token economy):** após `filepath_*` → PARAR; mostrar pause_hint; oferecer catalog mínimo. Após catalog, auto-selecionar somente se exatamente 1 intent for compatível; zero → busca bounded-unmapped; múltiplos → PARAR. **Proibido** expandir múltiplos domínios, chutar path ou colar JSON cru.

**Busca bounded:** `files:` do único domínio selecionado é limite de busca, nunca fila de leitura. Após o overlay, abrir o alvo primário; cada arquivo adicional exige alvo explícito, `verify`/hop1, import/chamada direta ou evidência de staleness. Sem domínio, usar `fd` apenas em diretórios objetivos, depois `rg` scoped e `bat` por intervalo. Nunca contornar busca ampla bloqueada com PowerShell equivalente. A resposta registra `sac_scope`, `context_domains_loaded`, `search_scope`, arquivos abertos+motivo, `deprecated_risk` e `domain_index_status`; missing file/anchor ou alvo necessário fora do domínio → `suspected_stale` + `sac-onboard mode=ASSESS`, sem atualização automática.

**Auditoria de suficiência:** qualidade é cobertura de risco, não densidade. Distinções fechadas:

| Conceito | O que mede | Onde |
|---|---|---|
| **coverage_claims** | Rastreabilidade humana aprovada (`claim_id\|scenario\|tag_type\|symbol\|filepath`) | `SAC_domains.md`; ausentes ⇒ capillarity `UNRATED` |
| **minimum_source_tag_lines** | Cardinalidade de tuples físicos únicos `(filepath, symbol, tag_type)` exigidos pelos claims | Payload capillarity; ≠ contagem de claims |
| **tags físicas** | Linhas `SAC:` no código — SSOT semântica | Fonte; constraints nunca vêm do manifesto |
| **files_scanned** | Arquivos lidos pelo motor (Context/Discover/capillarity) | Telemetria MCP/CLI; ≠ arquivos **abertos** pelo agente |
| **open (agente)** | Arquivos efetivamente lidos na sessão | Handoff; motivo por arquivo |

Reportar `files_scanned` separado de arquivos abertos; tag fora de `anchor_symbols` é `non_anchor_tag`, não orphan; orphan só via `validate` AST. Métricas declaram origem (`MCP-measured|CLI-validated|inferred`). Tag parseável continua visível, mas o motor emite `invalid_trigger`, `arch_imperative_required`, `regr_verify_required` ou `deprecated_replacement_required`; qualquer desses warnings em risco crítico torna a cobertura capillarity `INSUFFICIENT`. `non_contract_tags` é informativo; nunca autoriza remoção automática.

**Skills por momento**

| Momento | Skill |
|---------|--------|
| Gramática / o que é tag | `sac-context` |
| Editar código já tagueado | `sac-execution-overlay` |
| Avaliar/registrar domínio ou ADD/REPLACE/REMOVE de tags | `sac-onboard` (`ASSESS|REGISTER|TAG_DELTA`) |
| Mudar o padrão no pai | `sac-evolution` (não vai no mirror) |

**Propagar atualização do pai → filho**

Autoridade fixa: `rabelo-standards/sac-context/` para runtime/docs e `rabelo-standards/skills/catalog/domains/context-governance/sac-{context,onboard,execution-overlay}/` para skills. `templates/project-base/sac-context/` é apenas snapshot derivado de bootstrap: nunca é entrada, fallback ou SSOT do mirror.

```powershell
.\scripts\mirror-sac-tooling.ps1 -DestinationPath "C:\Users\Rabelo\projects\<FILHO>"
cd <FILHO>
python sac-context/src/sac_scan.py index-build --root .
python sac-context/src/sac_scan.py index-build --check --root .
```

Mirror copia diretamente das autoridades canônicas do pai para `DestinationPath`: `sac-context/` + 3 skill bundles (SKILL + prompts existentes); **preserva** `SAC_domains.md` do filho se já existir. Fonte alternativa — inclusive `templates/project-base` — é rejeitada. Recarregar MCP Cursor após mirror.

Detalhe de registro MCP: [`SAC_BOOTSTRAP.md`](SAC_BOOTSTRAP.md).

## Pipeline otimizado (Route → Context → Verify/Discover → Capillarity → Gate)

| Camada | Ferramenta | Papel |
|--------|------------|-------|
| **Route** | `list_sac_domains` | Catalog mínimo; 1 intent → auto-rota; zero → bounded-unmapped; múltiplos → HALT |
| **Context** | `get_sac_context(domain_id)` | Anchors + todas `REGR` + hop1 em uma chamada |
| **Discover** | `discover_sac(domain_id)` | Inventário slim para inspeção detalhada (opcional) |
| **Verify** | `get_sac_constraints(symbol, filepath, domain_id)` | Contrato preciso (JSON ≡ CLI) |
| **Capillarity** | `assess_sac_capillarity(domain_id)` / `capillarity --domain` | **Cold path:** auditoria, onboard ASSESS, evolução — **nunca** READ/EXECUTE boot |
| **Overlay** | skill `sac-execution-overlay` | Compacto; cache por sessão |
| **Gate** | `sac_scan diff-check` / CI | Regressão pós-merge |

**Regras fechadas:**

- Toda intenção de código/arquitetura → `list_sac_domains` antes de ler código.
- Exatamente 1 intent compatível → auto-rota + `get_sac_context`; zero → bounded-unmapped; múltiplos → perguntar / NO-GO.
- **COR-GATE:** MCP sem `filepath` → JSON `filepath_required` (≡ CLI), **zero matches** — Zod **optional**, handler hard (não schema error opaco).
- CLI `lookup` sem `--path` → mesmo PAUSE (escape: `SAC_ALLOW_UNSCOPED=1`).
- `filepath` ∉ união `files:` → `filepath_not_in_sac_domains`; com `domain_id` e path fora daquele domínio → `filepath_not_in_domain` (escape: `SAC_ALLOW_FILEPATH_OUTSIDE_DOMAINS=1`).
- Hop1 REGR: índice **filtrado** pelos `files:` do domínio do path/`domain_id`; senão scan **só** esses files (`hop1_domain_scan_no_index`). Full-root: `SAC_ALLOW_HOP1_FULL_SCAN=1` ou projeto sem domains.
- Após PAUSE: agente **não** retenta com path chutado; **não** dumpa JSON no chat.

**Modos L0–L4:** ver skill `sac-execution-overlay`.

### `index-build` (hop1 sem full scan)

```powershell
python sac-context/src/sac_scan.py index-build --root .
python sac-context/src/sac_scan.py index-build --check --root .
```

- Gera `sac-context/.sac/symbol_index.json`. Executar após `REGISTER`/`TAG_DELTA`, após clone ou quando tags mudarem materialmente.
- **`--check`:** não escreve; exit `0` se o índice on-disk ≡ scan fresco (`tag_count` + `symbols`); exit `1` se ausente/inválido/stale. Não rebuild automático em todo lookup.
- **Política git (fechada):** artefato **local / gerado** — **não** versionar. Em muitos templates Flutter/Dart, `.sac` já cai em ignore genérico. Após clone: `index-build` obrigatório antes de confiar em hop1 via índice. CI: regenerar no job (`index-build`) antes de `diff-check`.

## Gramática

### Forma canônica (preferida)

```dart
// SAC:<TAG>: <TRIGGER> - <Symbol>: <constraint>
// SAC:REGR: WARNING - calculateDose: you MUST verify: pediatric_module, ui_graph.
```

**Regra espacial:** uma tag fica imediatamente acima da assinatura. Quando um símbolo possui múltiplas tags, elas formam um bloco contíguo, sem linha em branco, na ordem `ARCH` → `REGR` → `DEPRECATED` → assinatura. O validator associa todo o bloco à declaração seguinte.

Campos:

- `TAG`: `ARCH` (invariante), `REGR` (alvos de verificação) ou `DEPRECATED` (risco de uso obsoleto).
- `TRIGGER`: matriz fechada — `ARCH=RULE|CONSTRAINT`; `REGR=WARNING|CRITICAL`; `DEPRECATED=WARNING|CRITICAL`. Fora dela gera `invalid_trigger`.
- `Symbol`: nome exato do símbolo declarado na linha seguinte.
- `constraint`: imperativa. `ARCH` contém `MUST|NEVER|ONLY`; `REGR` preserva a obrigação semântica e termina com `verify:` não vazio contendo apenas tokens `[A-Za-z_][A-Za-z0-9_.$-]*` separados por vírgula, nunca frase narrativa; `DEPRECATED` termina com `replacement: <símbolo|none>`. Ausências geram warnings canônicos.

Exemplo ARCH:

```dart
// SAC:ARCH: RULE - pediatric_module: MUST validate pediatric dosing.
class pediatric_module {
  void validate() {}
}
```

Exemplo REGR:

```dart
// SAC:REGR: WARNING - calculateDose: you MUST verify: pediatric_module, ui_graph.
double calculateDose() { ... }
```

Exemplo DEPRECATED:

```dart
// SAC:DEPRECATED: WARNING - legacyDose: MUST NOT be used by new code; replacement: calculateDose
double legacyDose() { ... }
```

Uso novo/nova dependência de `DEPRECATED` → HALT. Leitura, diagnóstico, remoção ou migração explicitamente pedidos podem prosseguir. Ausência de `replacement` gera `deprecated_replacement_required` e risco bloqueante.

### Forma legada REGR (ainda parseada, mas não use em novo código)

```dart
// SAC:REGR: WARNING - If modifying calculateDose, you MUST verify: pediatric_module, ui_graph.
double calculateDose() { ... }
```

> Preferir sempre a forma canônica. A forma legada existe apenas para compatibilidade com código V1.

## Ferramental

Todos os comandos partem do diretório raiz do projeto e usam o engine em `sac-context/src/sac_engine.py`.

### `sac_scan.py lookup`

Consulta restrições de um símbolo:

```powershell
python sac-context/src/sac_scan.py lookup calculateDose --root . --path lib/dosing/calculate_dose.dart --json
python sac-context/src/sac_scan.py lookup calculateDose --root . --path lib/dosing/calculate_dose.dart --domain dosing --json
```

Sem `--path` → PAUSE `filepath_required`. Com `--domain`, membership e hop1 ficam scoped àquele módulo.

Durante `sac-onboard`, um arquivo ainda fora do índice não passa pela membership do domínio. Em `ASSESS/REGISTER`, use o modo CLI somente para comprovar tags existentes em paths/símbolos explícitos; em `TAG_DELTA`, use-o após aplicar literalmente a operação aprovada:

```powershell
python sac-context/src/sac_scan.py lookup NewSymbol --root . --path lib/new_file.dart --pre-onboard --json
```

`--pre-onboard` exige `--path`, rejeita `--domain`, proíbe path fora da raiz e restringe lookup/hop1 ao próprio arquivo. Só existe dentro de `sac-onboard` com scope explícito; não é escape de READ/EXECUTE e não existe no MCP.

### `sac_scan.py context`

Monta o overlay de um domínio em uma leitura scoped:

```powershell
python sac-context/src/sac_scan.py context --domain dosing --root . --json
```

Retorna constraints dos anchors, todas as tags `REGR` e `DEPRECATED`, hop1, anchors ausentes e gaps. Constraints continuam originadas exclusivamente das tags no código. O limite preventivo padrão é **12288 bytes** (`SAC_CONTEXT_MAX_BYTES`); se excedido, retorna `context_payload_too_large` sem constraints e **MUST** Discover→Verify focado — nunca truncamento silencioso e **MUST NOT** reduzir `files:`/tags/claims aprovados só para caber no budget.

### `sac_scan.py discover`

Inventário slim de tags só nos `files:` de um domínio (L1 motor):

```powershell
python sac-context/src/sac_scan.py discover --domain dosing --root . --json
```

Cada card: `file`, `line`, `tag_type`, `symbol` (+ `verify` se REGR). **Sem** `constraint`/`trigger` — isso é L2 Verify.

### `sac_scan.py capillarity` (on-demand)

Compara `coverage_claims` declarados no domínio contra tags físicas nos `files:` — **não** faz parte do boot Route→Context.

```powershell
python sac-context/src/sac_scan.py capillarity --domain dosing --root . --json
```

MCP equivalente: `assess_sac_capillarity({domain_id})` (JSON ≡ CLI + `_perf`).

**Quando chamar:** auditoria explícita, `sac-onboard` ASSESS, `suspected_stale`, ou `context_payload_too_large`. **Proibido** em task normal de código/arquitetura.

**Status fechados (eixo A — coverage):** `UNRATED` (sem `context_scenarios`/`coverage_claims`), `INVALID_CONTRACT` (schema parcial ou inválido), `INSUFFICIENT` (claim/tag ausente ou warning canônico), `SUFFICIENT` (coverage 100%, zero missing/warning contratado).

**Eixo B — context fitness (`fitness_status`):** `null` quando UNRATED/INVALID; senão `TOO_THIN` (papel estrutural ausente por cenário declarado — `SUMMARY`→≥1 ARCH, `EXTEND`→≥1 ARCH, `REGRESSION`→≥1 REGR; `MIGRATION`→≥1 ARCH se declarado; não é cota numérica), `UNFIT` (claim matched não entraria em `get_sac_context` — `ARCH` fora de `anchor_symbols`; `REGR`/`DEPRECATED` sempre selecionados), `OVER_SELECT` (`uncontracted_context_tag_count>0` — tags selecionadas pelo Context além do contrato de claims), `FIT` (papéis cobertos, matched claims ⊆ seleção Context). **`OVER_BUDGET` não força `OVER_SELECT`.**

**Eixo C — payload:** `payload_status` (`OK`|`OVER_BUDGET` vs `SAC_CONTEXT_MAX_BYTES`, default **12288**). Quando `OVER_BUDGET`, emitir `payload_warn=OVER_BUDGET` (WARN) e **MUST** `discover_sac` → `get_sac_constraints`; **MUST NOT** thin do domínio para “passar” métrica.

**Qualidade composta:** `quality_status=PASS` com `status=SUFFICIENT` **e** `fitness_status=FIT` **e** (`payload_status=OK` **ou** `payload_status=OVER_BUDGET`). Cobertura insuficiente (`INSUFFICIENT`) e fitness `TOO_THIN`/`UNFIT`/`OVER_SELECT` continuam FAIL.

**Campos JSON adicionais:** `fitness_status`, `uncovered_scenarios`, `missing_roles`, `context_unfit_claims`, `uncontracted_context_tag_count`, `context_selected_tag_count`, `payload_warn` (`null`|`OVER_BUDGET`).

Schema de claims e cenários: [`SAC_domains.md`](SAC_domains.md). Domínio legado sem metadata ⇒ `UNRATED` e Route/Context inalterados.

### `sac_scan.py diff-check`

Valida um PR contra restrições REGR:

```powershell
# Contra um patch unificado
python sac-context/src/sac_scan.py diff-check --patch changes.patch --root .

# Contra uma ref git (modo CI/pre-push)
python sac-context/src/sac_scan.py diff-check --base origin/main --root .
```

Exit codes:

- `0`: sem violação.
- `1`: REGR violado ou arquivo com SAC tag em linguagem fora do registry.
- `2`: erro de uso ou I/O.

### `sac_scan.py validate`

Detecta tags SAC órfãs (tags sem declaração de símbolo correspondente no arquivo via AST) e avisa quando um `anchor_symbols` do domínio não possui tag física em seus `files:` (`UNMAPPED_ANCHOR_SYMBOL`):

```powershell
# Scanning local
python sac-context/src/sac_scan.py validate --root .

# Saída JSON
python sac-context/src/sac_scan.py validate --root . --json

# Warning-only (não falha mesmo com órfãos)
python sac-context/src/sac_scan.py validate --root . --warning-only
```

Exit codes:

- `0`: sem órfãos (ou warning-only ativo); warnings de consistência, incluindo `UNMAPPED_ANCHOR_SYMBOL`, continuam visíveis.
- `1`: órfãos detectados.
- `2`: erro de uso ou I/O.

Dependência: `tree-sitter` + `tree-sitter-dart` para parsing Dart. Sem a dependência, Dart retorna `unsupported_language` (não blocking). Python usa `ast` stdlib.

> O CI template usa `--warning-only` por padrão (VAL-2). Remova a flag quando o projeto tiver `0` órfãos e tree-sitter instalado no CI.

#### O que é um órfão

Uma tag SAC é órfã quando a linha onde ela aparece **não coincide** com o range de declaração de um símbolo (class, function, method, variable) no arquivo-fonte. Tags em comentários de documentação ou em linhas sem correspondência de símbolo são órfãs.

#### Formato JSON

```json
{
  "orphans": [
    {
      "file": "lib/foo.dart",
      "line": 42,
      "tag_type": "ARCH",
      "symbol": "Foo",
      "reason": "no symbol declaration found on this line"
    }
  ],
  "warnings": [
    "lib/bar.dart:0: unsupported_language dart (tree-sitter not installed)"
  ],
  "count": 1
}
```

## Ativar SAC MCP em projeto filho (checklist do agente)

Objetivo observável: no workspace do **filho**, `get_sac_constraints(<symbol>, filepath=<file>)` retorna `found: true` e `hop1` com paths **desse** repositório (não de outro).

Ordem obrigatória:

### 1. Propagar scaffold do pai

Na raiz do `rabelo-standards`:

```powershell
.\scripts\mirror-sac-tooling.ps1 -DestinationPath "C:\Users\Rabelo\projects\<FILHO>"
```

- `-DestinationPath` é **obrigatório** (não espelhar “no vazio”).
- Se `sac-context/docs/SAC_domains.md` **já existir** no filho, o mirror **não** sobrescreve (índice por projeto).
- Confirme que o filho tem `sac-context/mcp/server.mjs` + `package.json` + `package-lock.json`.

### 2. Instalar deps Node no filho

```powershell
cd C:\Users\Rabelo\projects\<FILHO>\sac-context\mcp
npm ci
```

- `node_modules/` **não** vai para o git — garantir no `.gitignore` do filho:
  - `node_modules/`
  - `sac-context/mcp/node_modules/`
  - `sac-context/**/__pycache__/`

### 3. Registrar MCP no Cursor (global — validado Windows)

**Não usar `<FILHO>/.cursor/mcp.json` no Cursor (Windows).** Neste host a IDE não detectou SAC com registro só no projeto.

Registrar em **`C:\Users\Rabelo\.cursor\mcp.json`**, `args` apontando para o `server.mjs` **do filho ativo**:

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

- `SAC_ROOT` opcional — inferido pelo path de `server.mjs`.
- Ao trocar de filho ativo: atualizar `args` antes de editar código tagueado.

**Proibido (SAC-MCP-01):** `args` de um filho enquanto workspace é outro; `<FILHO>/.cursor/mcp.json` neste host; FastMCP LEGACY; MCP OK sem smoke.

**Preferência:** global + path absoluto + `npm ci` no filho. Evidência T5: [`SAC_handoff_melhorias.md`](SAC_handoff_melhorias.md).

### 4. Smoke (gate — sem isto o filho não está funcionante)

Com workspace Cursor = raiz do filho, recarregar MCP, depois:

1. Local (sem IDE):

```powershell
cd sac-context\mcp
$env:SAC_ROOT = (Resolve-Path ..\..).Path
npm run smoke
```

2. CLI (paridade + hop1):

```powershell
python sac-context\src\sac_scan.py lookup <symbol_tagueado> --path <file_in_domain> --root . --json
```

Esperado: `found: true`; em REGR, `hop1` com `found: true` e paths sob o filho. Sem `--path` → `filepath_required`.

3. MCP na sessão: `get_sac_constraints(symbol_name, filepath=<file>)` → `found: true` em &lt; 5s; paths/warnings referem o filho. Chamada **sem** `filepath` → JSON `filepath_required` (PAUSE ≡ CLI), **zero** matches — Zod optional + handler hard.

Sem smoke verde → **BLOQUEIO** documentado; usar CLI anunciado; **não** inventar tags; **não** chamar feature MCP cumprida.

Detalhe operacional: [`SAC_BOOTSTRAP.md`](SAC_BOOTSTRAP.md).

## Registro MCP (contrato)

**Contrato (MCP-1…9):** entry Cursor/stdio = **Node** (`sac-context/mcp/server.mjs`); tags no código = SSOT; Python CLI = implementação canônica de leitura/montagem; adapter Node = zero parse; FastMCP `sac_mcp_server.py` = **LEGACY/debug only** — não registrar como primary. Feature MCP só é cumprida com **smoke verde** no host (tools listáveis + chamadas &lt; 5s). Sem smoke → BLOQUEIO documentado + CLI anunciado; **proibido** rebaixar MCP a “opcional por desenho” ou inventar tags.

Pré-requisito Node: `cd sac-context/mcp && npm ci`. Env: `SAC_ROOT` = raiz do **workspace ativo**; opcional `SAC_PYTHON`.

### Cursor (primary — Node)

Arquivo: **`~/.cursor/mcp.json`** (global — validado Windows). Path absoluto do filho em `args`. **Não** usar `<projeto>/.cursor/mcp.json` neste host.

Execução: `list_sac_domains()` → `get_sac_context(domain_id)` → `get_sac_constraints(symbol_name, filepath, domain_id)` quando houver alvo preciso.

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

### OpenCode

Arquivo: `.opencode.json` (projeto) ou `~/.opencode.json`. Preferir Node; `cwd` = raiz do projeto.

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

Arquivo: `~/.codex/config.toml` (user) ou `.codex/config.toml` (projeto trusted).

```toml
[mcp_servers.sac]
command = "node"
args = ["./sac-context/mcp/server.mjs"]
env = { SAC_ROOT = "." }
```

### LEGACY (não usar no Cursor)

`python …/sac-context/src/sac_mcp_server.py` (FastMCP) permanece no repo só para debug. Não é entry de host.

Tools: `list_sac_domains` (Route) + `get_sac_context(domain_id)` (overlay em lote) + `discover_sac(domain_id)` (inspeção) + `get_sac_constraints(symbol_name, filepath?, domain_id?)` (Verify preciso) + `assess_sac_capillarity(domain_id)` (capillarity on-demand; nunca boot). `filepath` omitido → `filepath_required` PAUSE. JSON de máquina idêntico ao CLI; `_perf` é envelope exclusivo do MCP.

## CI Guard

O workflow `sac_guard.yml` roda em todo `pull_request` e executa:

```bash
python sac-context/src/sac_scan.py diff-check --base origin/${{ github.base_ref }}
python sac-context/src/sac_scan.py validate --root .
```

O corpo do PR é passado via env `SAC_PR_BODY` para reconhecimento de `SAC-ACK`.

### Override humano: `SAC-ACK`

A única forma de liberar uma violação REGR é incluir, no corpo do PR ou em mensagem de commit, o token exato:

```text
SAC-ACK: calculateDose
```

Regras:

- Por símbolo apenas.
- `SAC-ACK: all` é ignorado (override em lote proibido).
- Só libera o símbolo explicitamente nomeado.

### Wrapper local Windows

```powershell
.\sac-context\ci\sac_ci_guard.ps1 -Base origin/main
```

Útil para validação pre-push ou execução manual no ambiente de desenvolvimento.

> **Capillarity no CI:** o guard atual valida `diff-check` + `validate` (tags órfãs/REGR). **Não** valida schema `context_scenarios`/`coverage_claims` em `SAC_domains.md`. Domínios legados sem capillarity metadata permanecem válidos; contrato inválido **presente** no manifesto não é bloqueado pelo CI até opt-in explícito de schema guard (fora desta trilha).

## Cobertura REGR (C16)

Um alvo `verify:` é considerado coberto quando:

1. Um símbolo alterado no diff tem o mesmo nome do alvo; **ou**
2. O basename (sem extensão) de um arquivo alterado no diff é igual ao alvo.

Qualquer outra forma (substring, fuzzy, diretório) **não cobre**.

## Registry de linguagens (C14)

V2 mapeia declarações para Dart e PowerShell. Outras linguagens com SAC tags causam **fail closed** (exit 1) se alteradas.

### Dart

- `class Foo`, `abstract class Foo`, `extension Foo`, `enum Foo`, `mixin Foo`
- Funções com tipo de retorno explícito: `void`, `Future`, `Stream`, `dynamic`, `Object`, `String`, `int`, `double`, `bool`, `num`, `Widget`, `List`, `Map`, `Set`

### PowerShell

- `function Foo`
- `$foo = ...`

## V2.1 — validate (completo)

A V2.1 adiciona validação AST para detectar tags SAC órfãs:

- Parser AST Dart via `tree-sitter-dart`.
- Parser AST Python via `ast` stdlib.
- Comando `sac_scan.py validate` fail-fast (exit 1 na presença de órfãos).
- Integrado no `sac_guard.yml` (CI) e `sac_ci_guard.ps1` (local).

### Overrides para validate

Diferente do diff-check, o validate detecta órfãos. Para liberar um símbolo órfão, use `SAC-ACK` no comentário da mesma linha:

```dart
// SAC-ACK: orphanSymbol
// SAC:ARCH: WARNING - orphanSymbol: ...
class orphanSymbol {} // a tag agora casa com a declaração
```

## DoD operacional (cristalino)

Regra-mãe: **1 intenção → 1 pacote de contexto suficiente → 1 ação (responder ou editar) → evidência binária.** Sem métrica pós-hoc no hot path, sem revert, sem segundo chat de auditoria.

### Hot path (READ / EXECUTE — código)

| # | PASS | FAIL automático |
|---|------|-----------------|
| D1 | `list_sac_domains` → 1 domínio (ou PAUSE) | Chute de domínio; rg global |
| D2 | `get_sac_context(domain_id)` → `missing=[]` | Context thin → improviso/read amplo |
| D3 | Context monta **ou** overflow explícito + Discover→Verify (sem thin) | Truncar; thin domain; ignorar overflow |
| D4 | Resposta/edit usa constraints do packet | Dump JSON; inventar `SAC:` |
| D5 | `_perf` citado em 1 linha | Dump `_perf`/JSON |

**Capillarity proibido** em READ/EXECUTE normal. Só: auditoria humana explícita, `sac-onboard ASSESS`, ou `suspected_stale` encaminhando onboard.

### Onboard (`sac-onboard`)

| # | PASS | FAIL automático |
|---|------|-----------------|
| O1 | ASSESS: diff persistente = ∅ | Qualquer tag/`SAC_domains.md` antes de `APROVAR` |
| O2 | Proposta: `coverage_strategy` + claims + tabela TAG_DELTA (se needed) | Amostra representativa implícita |
| O3 | PAUSE + `approval_required` | Write no mesmo turno que ASSESS |
| O4 | TAG_DELTA: 1 apply; diff ⊆ tabela aprovada | write→capillarity→revert |
| O5 | `files_listed == files_tagged == claims_listed` (ou strategy aprovada + `files:` reduzido) | 14 em `files:`, 4 tagueados |
| O6 | `validate` zero orphan no recorte | REGISTER com tags ausentes |

Capillarity **pós** TAG_DELTA: somente verificação; FAIL → report + HALT; **proibido** REMOVE/revert automático. PASS capillarity ≠ COMPLETE se O5 falhar.

### Session boot (5 checks)

`user-sac` Ready → `list_sac_domains()` OK → `get_sac_context` `missing=[]` → payload OK → `sac_perf` agregado. Falha D1–D2: CLI anunciado ou NO-GO.

### Fricção humana permitida

- READ/EXECUTE: **zero** aprovação extra.
- Onboard: **no máximo 2** interações (`ASSESS` → `APROVAR SAC TAG_DELTA|REGISTER`).

## Referências

- `sac-context/src/sac_engine.py` — engine stdlib-only.
- `sac-context/src/sac_scan.py` — CLI.
- `sac-context/src/sac_diff.py` — diff engine.
- `sac-context/src/sac_validate.py` — validação AST (tree-sitter Dart + ast Python).
- `sac-context/mcp/server.mjs` — adaptador MCP stdio Node (primary Cursor).
- `sac-context/src/sac_mcp_server.py` — FastMCP LEGACY/debug only.
- `sac-context/ci/sac_guard.yml` — template GitHub Actions.
- `sac-context/ci/sac_ci_guard.ps1` — wrapper local.
- `sac-context/docs/SAC_validate.md` — operacionalidade e critérios de avaliação.
- `skills/catalog/domains/context-governance/sac-context/SKILL.md` — origem do padrão.
- `skills/catalog/domains/context-governance/sac-onboard/SKILL.md` — triagem de escopo.
