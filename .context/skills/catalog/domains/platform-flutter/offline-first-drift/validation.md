# Critérios de Validação — Projeto Offline-First com Drift

Use este arquivo para auditar qualquer projeto que usa Drift + Firebase ou Drift + Supabase.
Cada critério tem nível de severidade: **CRÍTICO** (viola a arquitetura), **ALTO** (degrada performance ou confiabilidade), **MÉDIO** (má prática com impacto moderado).

---

## Como usar esta validação

Para cada arquivo listado abaixo, execute a busca correspondente e verifique se a condição é atendida. Ao final, calcule o score de conformidade.

```
Score = (critérios aprovados / total de critérios aplicáveis) × 100
```

- 90–100%: Projeto conforme
- 70–89%: Atenção — itens ALTO pendentes
- < 70%: Refatoração necessária antes de novas features

---

## Bloco 1 — Fluxo de dados (CRÍTICO)

### V-01 · A UI nunca lê diretamente do remoto

**O que buscar:**

```
# Buscar em lib/app/modules/**/views/ e lib/app/modules/**/controllers/
grep -rn "Source.server" lib/app/modules/
grep -rn "supabase.from" lib/app/modules/
grep -rn "FirebaseFirestore" lib/app/modules/
```

**Aprovado quando:** Zero ocorrências nos diretórios de modules (controllers e views).
Ocorrências só são aceitáveis em `lib/app/data/remote/` e `lib/app/services/sync_service.dart`.

**Severidade:** CRÍTICO

---

### V-02 · SyncService é o único ponto de acesso ao remoto

**O que buscar:**

```
grep -rn "Source.server\|supabase.from\|FirebaseFirestore" lib/ \
  --include="*.dart" \
  | grep -v "lib/app/data/remote\|lib/app/services/sync_service"
```

**Aprovado quando:** Zero ocorrências fora dos arquivos de remote source e sync service.

**Severidade:** CRÍTICO

---

### V-03 · Controllers leem do Drift, não do SyncService diretamente para popular UI

**O que verificar manualmente:**
Em cada controller que exibe dados, confirmar que:

1. Os dados exibidos vêm de uma query Drift (`db.query...`) ou stream Drift (`db.watch...`)
2. O SyncService é chamado apenas para atualizar o Drift, não para retornar dados à UI

**Aprovado quando:** Nenhum controller usa o retorno do SyncService para popular `RxList` ou variável observável.

**Severidade:** CRÍTICO

---

## Bloco 2 — Tabela syncStates e TTL (CRÍTICO/ALTO)

### V-04 · Tabela `sync_states` existe com campos obrigatórios

**O que verificar:**

```
grep -n "lastSyncAt\|last_sync_at" lib/app/data/local/app_database.dart
grep -n "updatedAt\|updated_at" lib/app/data/local/app_database.dart
```

**Aprovado quando:** A tabela de controle de sync existe e contém ambos os campos `lastSyncAt` (cursor) e `updatedAt` (timestamp de execução).

**Severidade:** CRÍTICO

---

### V-05 · `updatedAt` é sempre atualizado após sync bem-sucedido

**O que verificar em `sync_service.dart`:**

Localizar o bloco de upsert de sync state. Confirmar que `upsertSyncState` (ou equivalente) é chamado **fora** de qualquer condicional que dependa de `lastSyncAt != null` ou `result.items.isNotEmpty`.

```dart
// ❌ Falha V-05 — condicional impede atualização com 0 registros
if (result.newCursor != null) {
  await db.upsertSyncState(...);
}

// ✅ Passa V-05 — sempre atualiza
await db.upsertSyncState(
  userId, entity,
  lastSyncAt: result.newCursor ?? cursor,
  updatedAt: DateTime.now(),
);
```

**Aprovado quando:** `updatedAt` é sempre setado para `DateTime.now()` ao final de qualquer sync bem-sucedido.

**Severidade:** CRÍTICO

---

### V-06 · Controllers verificam TTL antes de disparar sync

**O que verificar em cada controller que carrega dados:**

```
grep -n "getSyncState\|updatedAt\|isFresh\|_ttl\|forceRefresh" \
  lib/app/modules/**/controllers/*.dart
```

**Aprovado quando:** Existe lógica de verificação de `updatedAt` com comparação de `Duration` antes de chamar `syncService`. A segunda abertura do mesmo recurso dentro do TTL não dispara nenhuma chamada de rede.

**Severidade:** CRÍTICO

---

### V-07 · TTL tem valor definido e documentado no controller

**O que verificar:**
Confirmar que o valor de TTL é uma constante nomeada (não um número mágico).

```dart
// ❌ Falha V-07
if (DateTime.now().difference(state.updatedAt!) < const Duration(minutes: 30)) { ... }

// ✅ Passa V-07
static const _kSyncTtl = Duration(minutes: 30);
if (DateTime.now().difference(state.updatedAt!) < _kSyncTtl) { ... }
```

**Aprovado quando:** TTL é constante nomeada, não literal inline.

**Severidade:** MÉDIO

---

## Bloco 3 — Streams e reatividade (ALTO)

### V-08 · Todo controller que assina stream cancela em `onClose`

**O que buscar:**

```
# Encontrar controllers com StreamSubscription
grep -rln "StreamSubscription" lib/app/modules/**/controllers/

# Para cada arquivo encontrado, verificar se tem cancel em onClose
grep -n "cancel()" lib/app/modules/**/controllers/*.dart
```

**Verificação manual:** Para cada `StreamSubscription` declarada, confirmar que existe `_subscription?.cancel()` dentro de `onClose()`.

**Aprovado quando:** Toda `StreamSubscription` é cancelada em `onClose`. Contagem de declarações == contagem de cancels.

**Severidade:** ALTO

---

### V-09 · Widgets usam `Obx` granular (por card/seção, não por tela)

**O que buscar:**

```
grep -n "Obx(" lib/app/modules/**/views/*.dart
```

**Verificação manual:** Para cada arquivo de view, confirmar que os `Obx` envolvem widgets individuais (cards, campos, indicadores), não `Scaffold`, `Column` raiz ou `ListView` completo.

**Aprovado quando:** Nenhum `Obx` envolve a tela inteira ou estruturas com mais de 3 widgets independentes.

**Severidade:** ALTO

---

### V-10 · Streams de alta frequência usam debounce

**O que verificar:**
Para entidades que atualizam frequentemente (ex: streams de posição, timers, contadores), confirmar uso de `debounce()` ou `throttle()` do GetX.

```dart
// ✅ Correto para stream de alta frequência
debounce(items, (_) => _recalculate(), time: const Duration(milliseconds: 300));
```

**Aprovado quando:** Streams que podem emitir mais de 1x por segundo têm debounce configurado.

**Severidade:** MÉDIO

---

## Bloco 4 — Schema Drift (ALTO/MÉDIO)

### V-11 · Toda tabela de dados tem `createdAt`, `updatedAt`, `deletedAt`

**O que verificar em `lib/app/data/local/tables/`:**

```
grep -n "deletedAt\|deleted_at" lib/app/data/local/**/*.dart
```

**Aprovado quando:** Toda tabela que representa entidade de negócio (não tabelas de controle como `sync_states`) possui os três campos de auditoria.

**Severidade:** ALTO

---

### V-12 · Queries locais filtram soft deletes

**O que buscar:**

```
grep -rn "select(meals)\|select(exercises)\|select(goals)" lib/ --include="*.dart"
```

**Verificação manual:** Para cada `select(tabela)`, confirmar que existe filtro `.where((t) => t.deletedAt.isNull())` ou equivalente.

**Aprovado quando:** Zero queries em tabelas com soft delete retornam registros com `deletedAt != null`.

**Severidade:** ALTO

---

### V-13 · Índices definidos em colunas de filtro frequente

**O que verificar em `app_database.dart`:**

```
grep -n "TableIndex\|customConstraints\|CREATE INDEX" lib/app/data/local/app_database.dart
```

**Aprovado quando:** Tabelas com mais de 1.000 registros esperados têm índice em `userId` e em colunas usadas em `WHERE` frequentes.

**Severidade:** MÉDIO

---

## Bloco 5 — UX offline-first (MÉDIO)

### V-14 · Toda tela com TTL tem botão de refresh manual

**O que verificar:**
Para cada controller que implementa TTL (V-06), confirmar que a view correspondente tem um `IconButton` com `Icons.refresh` ou equivalente que chama `forceRefresh()` ou método similar.

**Aprovado quando:** Usuário sempre tem controle manual para forçar atualização, independente do TTL.

**Severidade:** MÉDIO

---

### V-15 · Estado de loading exposto durante sync

**O que verificar:**

```
grep -n "isLoading\|isSyncing" lib/app/modules/**/controllers/*.dart
```

**Aprovado quando:** Controllers expõem variável observável de loading que é setada para `true` durante sync e `false` ao final (inclusive em caso de erro no `finally`).

**Severidade:** MÉDIO

---

### V-16 · Erros de sync não são silenciados

**O que buscar:**

```
grep -n "catch" lib/app/services/sync_service.dart
```

**Verificação manual:** Confirmar que blocos `catch` em `sync_service.dart` não estão vazios ou apenas logando sem relançar/expor o erro para o controller.

**Aprovado quando:** Erros de sync são propagados ao controller e expostos na UI (snackbar, banner ou estado de erro).

**Severidade:** ALTO

---

## Resumo dos critérios

| ID   | Descrição                               | Severidade |
| ---- | --------------------------------------- | ---------- |
| V-01 | UI não lê do remoto                     | CRÍTICO    |
| V-02 | SyncService é único ponto remoto        | CRÍTICO    |
| V-03 | Controllers leem do Drift               | CRÍTICO    |
| V-04 | Tabela sync_states com campos corretos  | CRÍTICO    |
| V-05 | updatedAt sempre atualizado após sync   | CRÍTICO    |
| V-06 | Controllers verificam TTL antes de sync | CRÍTICO    |
| V-07 | TTL como constante nomeada              | MÉDIO      |
| V-08 | Streams cancelados em onClose           | ALTO       |
| V-09 | Obx granular por widget                 | ALTO       |
| V-10 | Debounce em streams de alta frequência  | MÉDIO      |
| V-11 | Tabelas com campos de auditoria         | ALTO       |
| V-12 | Queries filtram soft deletes            | ALTO       |
| V-13 | Índices em colunas de filtro            | MÉDIO      |
| V-14 | Botão refresh em telas com TTL          | MÉDIO      |
| V-15 | Estado de loading exposto               | MÉDIO      |
| V-16 | Erros de sync não silenciados           | ALTO       |

**Critérios CRÍTICOS (6):** qualquer falha nestes invalida a arquitetura.
**Critérios ALTO (6):** falhas causam degradação de performance ou confiabilidade.
**Critérios MÉDIO (4):** falhas causam má experiência ou dívida técnica.
