# Inventorio de Ferramentas Invocaveis

## Skills do Catalogo

### Prioridade Alta (Gatekeepers)

| Skill | Dominio | Quando Usar | Prioridade |
|-------|---------|-------------|------------|
| context-orchestrator | context-governance | Validar contexto GO/NO-GO antes de execucao | Sempre antes de tarefas complexas |
| planning-and-deciding | planning | Tarefas complexas, trade-offs, decisoes | Quando ha multiplas abordagens |

### Domnio: Context Governance

| Skill | Funcao | Quando Usar |
|-------|--------|-------------|
| context-orchestrator | Gate GO/NO-GO | Antes de tarefas com impacto estrutural |
| context-maintenance | Limpeza de contexto | Contexto desatualizado ou poluido |
| updating-project-status | Atualizar status | Apos completar tarefas |
| validating-context-efficacy | Auditoria de contexto | Contexto nao funciona bem |

### Dominio: Planning

| Skill | Funcao | Quando Usar |
|-------|--------|-------------|
| planning-and-deciding | Planejamento estruturado | Tarefas medias e grandes |
| lean-planning-decisions | Planejamento enxuto | Decisoes rapidas de media complexidade |
| mobile-planning | Planejamento mobile | Features mobile especificas |

### Dominio: Platform Flutter

| Skill | Funcao | Quando Usar |
|-------|--------|-------------|
| generate-feature | Gerar feature | Criar view+controller+bindings |
| clean-code-flutter | Qualidade de codigo | Refatoracao Flutter |
| flutter-design-principles | Design UI | Questoes de design/UI |
| injection-routes-getx | Configuracao GetX | Setup de dependencias e rotas |
| offline-first-drift | Integracao Drift | BD local/offline |
| using-search-app-bar-page | Search UI | Integracao de busca |

### Dominio: Validation

| Skill | Funcao | Quando Usar |
|-------|--------|-------------|
| quality-standards | Framework tecnico | Analise detalhada pre-implementacao |
| reviewing-code-changes | Review de mudancas | Validar codigo alterado |
| validating-flutter-projects | Auditoria Flutter | Validacao de arquitetura |
| validating-task-blocks | Validacao de tarefas | Gate antes de execucao |
| performance-profiling-flutter | Profiling | Identificar gargalos |

### Dominio: Debugging

| Skill | Funcao | Quando Usar |
|-------|--------|-------------|
| investigating-bugs | Debug estruturado | Investigar causa raiz |
| intelligent-debug-logging | Instrumentacao | Adicionar logs estruturados |

### Dominio: Delivery

| Skill | Funcao | Quando Usar |
|-------|--------|-------------|
| refactoring | Refatoracao segura | Mudancas estruturais |
| documentation | Documentacao | Gerar/atualizar docs |
| commit-message | Mensagens de commit | Commits padronizados |
| deployment-flutter | Deploy | Release de app |

### Dominio: Architecture

| Skill | Funcao | Quando Usar |
|-------|--------|-------------|
| briefing-architecture-drawers | Gavetas de arquitetura | Documentar arquitetura |
| briefing-structural-architecture | Briefing estrutural | Overview de arquitetura |

### Dominio: Code Quality

| Skill | Funcao | Quando Usar |
|-------|--------|-------------|
| clean-code | Qualidade geral | Refatoracao decodigo |

### Dominio: Security

| Skill | Funcao | Quando Usar |
|-------|--------|-------------|
| security-audit | Auditoria de seguranca | Review de seguranca |

---

## Ferramentas MCP

### Dart

| MCP Tool | Uso | Quando Usar |
|----------|-----|-------------|
| mcp__dart__analyze_files | Analise estatica | Validar codigo Dart |
| mcp__dart__list_libraries | Listar bibliotecas | Entender dependencias |

### Supabase

| MCP Tool | Uso | Quando Usar |
|----------|-----|-------------|
| mcp__supabase__execute_sql | Executar SQL | Queries diretas |
| mcp__supabase__list_tables | Listar tabelas | Entender schema |
| mcp__supabase__get_table_schema | Schema de tabela | Estrutura de dados |

### Filesystem

| MCP Tool | Uso | Quando Usar |
|----------|-----|-------------|
| mcp__filesystem__read_text_file | Ler arquivo | Operacoes de arquivo |
| mcp__filesystem__write_text_file | Escrever arquivo | Criar/modificar |
| mcp__filesystem__list_directory | Listar diretorio | Navegar estrutura |
| mcp__filesystem__search_files | Buscar arquivos | Encontrar arquivos |

---

## Scripts Uteis

### Flutter

| Script | Uso | Quando Rodar |
|--------|-----|--------------|
| scripts/flutter_lint_runner.ps1 | Lint | Apos mudancas |
| scripts/getx_audit.ps1 | Auditoria GetX | Apos mudancas em controllers |
| scripts/flutter_arch_check.ps1 | Check arquitetura | Apos mudancas estruturais |

### Validad oes

| Script | Uso | Quando Rodar |
|--------|-----|--------------|
| scripts/rebuild-skills-catalog.ps1 | Rebuild registry | Apos adicionar skills |

---

## Comandos Diretos

### Flutter/Dart

| Comando | Uso |
|---------|-----|
| flutter analyze | Analise estatica |
| flutter test | Executar testes |
| dart format . | Formatar codigo |
| flutter pub get | Instalar dependencias |
| flutter pub upgrade | Atualizar dependencias |

### Git

| Comando | Uso |
|---------|-----|
| git status | Status do repo |
| git diff | Ver mudancas |
| git log --oneline | Historico |
| git branch -a | Listar branches |

### Build/Run

| Comando | Uso |
|---------|-----|
| flutter run | Rodar app |
| flutter build apk | Build Android |
| flutter build ios | Build iOS |

---

## Ordem de Prioridade de Invocacao

### Para Tarefas de Implementacao

```
1. context-orchestrator (se necessario)
2. planning-and-deciding (se complexa)
3. generate-feature / clean-code-flutter
4. reviewing-code-changes
```

### Para Tarefas de Debug

```
1. context-orchestrator (se necessario)
2. investigating-bugs
3. intelligent-debug-logging (se precisar instrumentar)
```

### Para Tarefas de Refatoracao

```
1. context-orchestrator (se necessario)
2. planning-and-deciding (se grande)
3. refactoring
4. reviewing-code-changes
```

### Para Tarefas de Planejamento

```
1. context-orchestrator
2. planning-and-deciding OU lean-planning-decisions
3. quality-standards (se precisar de framework detalhado)
```

---

## Ferramentas por Tipo de Tarefa

### Feature Nova

| Ordem | Ferramenta | Justificativa |
|-------|------------|---------------|
| 1 | context-orchestrator | Validar contexto |
| 2 | planning-and-deciding | Planejar feature |
| 3 | generate-feature | Gerar codigo |
| 4 | testing-patterns-flutter | Validar |

### Bug Fix

| Ordem | Ferramenta | Justificativa |
|-------|------------|---------------|
| 1 | context-orchestrator | Validar contexto |
| 2 | investigating-bugs | Investigar |
| 3 | clean-code-flutter | Refatorar se necessario |

### Refatoracao

| Ordem | Ferramenta | Justificativa |
|-------|------------|---------------|
| 1 | context-orchestrator | Validar contexto |
| 2 | refactoring | Executar refatoracao |
| 3 | reviewing-code-changes | Validar mudancas |

### Documentacao

| Ordem | Ferramenta | Justificativa |
|-------|------------|---------------|
| 1 | context-orchestrator | Validar contexto |
| 2 | documentation | Gerar docs |

---

## Combinacoes Comuns

### Implementacao Complexa

```
context-orchestrator → planning-and-deciding → generate-feature → reviewing-code-changes
```

### Debug de Producao

```
context-orchestrator → investigating-bugs → intelligent-debug-logging → clean-code-flutter
```

### Refatoracao Grande

```
context-orchestrator → planning-and-deciding → refactoring → quality-standards → reviewing-code-changes
```

### MVP Rapido

```
lean-planning-decisions → generate-feature → (skip reviewing para velocidade)
```