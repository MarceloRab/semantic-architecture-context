---
name: offline-first-drift
description: >
  Use this skill for any project that combines Drift (local SQLite) with a remote backend
  (Firebase/Firestore or Supabase). Triggers on: architecture review, new feature implementation,
  bug investigation, sync issues, performance problems, or any task involving local/remote data
  in Flutter/Dart projects. ALWAYS consult this skill before writing or modifying any code that
  touches data persistence, sync, streams, or controllers in these projects — even if the task
  seems small. A single wrong read (Source.server instead of local) or a missing updatedAt update
  can cascade into expensive network calls and broken offline behavior.
---

# Offline-First com Drift + Remote Backend

## Leia sempre antes de escrever qualquer código de dados

Este skill governa projetos Flutter/Dart que usam:

- **Drift** (banco local SQLite) como fonte primária de leitura
- **Firebase/Firestore** ou **Supabase** como backend remoto de sincronização
- **GetX** ou **Riverpod** como gerenciamento de estado reativo

Para detalhes específicos do backend, leia o arquivo de referência apropriado:

- [Firebase/Firestore](firebase.md)
- [Supabase](supabase.md)
- [Critérios de validação](validation.md)

---

## 1. Princípio fundamental: o fluxo de dados tem sentido único

```
Remote (Firestore / Supabase)
        ↓  [SyncService — escrita apenas]
     Drift (banco local — fonte de verdade)
        ↓  [Streams / Queries — leitura apenas]
   Controllers / ViewModels
        ↓
       UI
```

**Regra inviolável:** A UI nunca lê diretamente do remoto.
O remoto alimenta o Drift. O Drift alimenta a UI. Sempre.

Qualquer código que faça `Source.server` (Firestore) ou query direta ao Supabase
dentro de um controller ou widget é uma violação desta arquitetura.

---

## 2. O que o Drift deve ter em todo projeto offline-first

### 2.1 Tabela obrigatória: `sync_states`

Todo projeto deve ter uma tabela de controle de sincronização:

```dart
class SyncStates extends Table {
  TextColumn get userId => text()();           // FK para o usuário/entidade sincronizada
  TextColumn get entity => text()();           // ex: 'meals', 'exercises', 'goals'
  DateTimeColumn get lastSyncAt => dateTime().nullable()(); // cursor incremental
  DateTimeColumn get updatedAt => dateTime().nullable()();  // quando o sync rodou
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();

  @override
  Set<Column> get primaryKey => {userId, entity};
}
```

**Semântica dos campos — não confundir:**

| Campo        | O que representa                                      | Quando atualizar                                                  |
| ------------ | ----------------------------------------------------- | ----------------------------------------------------------------- |
| `lastSyncAt` | Cursor incremental — até onde os dados foram buscados | Só quando o pull retorna dados novos                              |
| `updatedAt`  | Quando o sync rodou pela última vez                   | **Sempre** após qualquer sync bem-sucedido, mesmo com 0 registros |

`updatedAt` é o árbitro de frescor (TTL). `lastSyncAt` é o cursor de dados. São conceitos distintos.

### 2.2 Regras de schema

- Toda tabela de dados deve ter `createdAt`, `updatedAt` e `deletedAt` (soft delete).
- `deletedAt` nullable — registros deletados localmente antes do sync não são apagados fisicamente.
- Use `withDefault(currentDateAndTime)` para `createdAt`.
- Defina índices em colunas usadas em `WHERE` frequentes, especialmente `userId` e `updatedAt`.

```dart
@override
List<String> get customConstraints => ['UNIQUE (user_id, remote_id)'];

// Índice explícito
@TableIndex(name: 'idx_meals_user', columns: {#userId})
class Meals extends Table { ... }
```

### 2.3 Método `getSyncState` no DatabaseService

```dart
Future<SyncState?> getSyncState(String userId, String entity) =>
  (select(syncStates)
    ..where((t) => t.userId.equals(userId) & t.entity.equals(entity)))
  .getSingleOrNull();

Future<void> upsertSyncState(String userId, String entity, {
  DateTime? lastSyncAt,
  required DateTime updatedAt,
}) async {
  await into(syncStates).insertOnConflictUpdate(SyncStatesCompanion(
    userId: Value(userId),
    entity: Value(entity),
    lastSyncAt: lastSyncAt != null ? Value(lastSyncAt) : const Value.absent(),
    updatedAt: Value(updatedAt),
  ));
}
```

---

## 3. SyncService — responsabilidades e regras

O SyncService é o único componente que faz leitura do remoto. Ele:

1. Puxa dados do remoto usando `lastSyncAt` como cursor (pull incremental)
2. Escreve os dados no Drift via upsert
3. **Sempre** atualiza `syncStates.updatedAt` ao final, independente de retornar dados ou não

### 3.1 Estrutura obrigatória do método de sync

```dart
Future<void> syncEntity(String userId, String entity) async {
  try {
    // 1. Buscar cursor atual
    final state = await db.getSyncState(userId, entity);
    final cursor = state?.lastSyncAt;

    // 2. Pull remoto incremental (desde o cursor)
    final result = await remoteSource.pull(userId, since: cursor);

    // 3. Upsert local
    if (result.items.isNotEmpty) {
      await db.upsertMany(result.items);
    }

    // 4. SEMPRE atualizar updatedAt — mesmo com 0 registros
    // cursor só avança se houver dados novos
    await db.upsertSyncState(
      userId,
      entity,
      lastSyncAt: result.newCursor ?? cursor, // não regride o cursor
      updatedAt: DateTime.now(),              // sempre agora
    );
  } catch (e, stack) {
    // Nunca silenciar erros de sync — logar e relançar
    log.error('syncEntity failed', e, stack);
    rethrow;
  }
}
```

**Erro crítico a evitar:**

```dart
// ❌ ERRADO — updatedAt não é atualizado quando pull retorna 0 registros
if (result.newCursor != null) {
  await db.upsertSyncState(userId, entity, lastSyncAt: result.newCursor!, updatedAt: DateTime.now());
}

// ✅ CORRETO — updatedAt sempre é atualizado
await db.upsertSyncState(
  userId, entity,
  lastSyncAt: result.newCursor ?? cursor,
  updatedAt: DateTime.now(),
);
```

---

## 4. Controllers — lógica de frescor (TTL)

Controllers nunca chamam o SyncService diretamente sem antes verificar o frescor dos dados.

### 4.1 Padrão de verificação de TTL

```dart
static const _ttl = Duration(minutes: 30);

Future<void> loadDataIfNeeded(String userId, String entity) async {
  // Flag de refresh forçado (botão "Atualizar" na UI)
  if (_forceRefresh) {
    _forceRefresh = false;
    await _syncAndLoad(userId, entity);
    return;
  }

  // Verificar frescor
  final state = await db.getSyncState(userId, entity);
  final isFresh = state?.updatedAt != null &&
      DateTime.now().difference(state!.updatedAt!) < _ttl;

  if (isFresh) {
    // Dados frescos — ler só do Drift
    await _loadFromLocal(userId);
  } else {
    // Dados ausentes ou stale — sincronizar e ler
    await _syncAndLoad(userId, entity);
  }
}

Future<void> _loadFromLocal(String userId) async {
  // Leitura direta do Drift — zero chamadas de rede
  final data = await db.queryData(userId);
  items.assignAll(data);
}

Future<void> _syncAndLoad(String userId, String entity) async {
  isLoading.value = true;
  try {
    await syncService.syncEntity(userId, entity);
    await _loadFromLocal(userId);
  } finally {
    isLoading.value = false;
  }
}
```

### 4.2 Botão de refresh obrigatório em telas com dados sincronizados

Toda tela que usa TTL deve expor um botão de atualização manual:

```dart
// No controller
bool _forceRefresh = false;
void forceRefresh() {
  _forceRefresh = true;
  loadDataIfNeeded(userId, entity);
}

// Na view (AppBar)
IconButton(
  icon: const Icon(Icons.refresh),
  onPressed: controller.forceRefresh,
)
```

---

## 5. O coração reativo — Streams do Drift

O Drift emite streams reativos a partir de queries. Este é o mecanismo central de atualização da UI: o SyncService faz upsert no Drift, o Drift emite, o controller reage, a UI atualiza. Sem polling, sem setState manual.

### 5.1 Padrão de stream no controller

```dart
class DataController extends GetxController {
  final RxList<DataItem> items = <DataItem>[].obs;
  StreamSubscription? _subscription;

  @override
  void onInit() {
    super.onInit();
    _subscribeToLocal();
  }

  void _subscribeToLocal() {
    // watchQuery retorna Stream<List<T>> do Drift
    _subscription = db.watchData(userId).listen(
      (data) => items.assignAll(data),
      onError: (e) => log.error('stream error', e),
    );
  }

  @override
  void onClose() {
    _subscription?.cancel(); // OBRIGATÓRIO — previne memory leak
    super.onClose();
  }
}
```

### 5.2 Regras de stream

- **Todo controller que assina stream deve cancelar em `onClose()`** — sem exceção.
- Streams do Drift são lazy — só emitem quando há assinante ativo.
- Use `watchSingleOrNull` para entidades únicas; `watch` para listas.
- Para streams de alta frequência, use `debounce` do GetX para evitar rebuilds excessivos.

```dart
// debounce para streams que emitem muito rápido
debounce(items, (_) => _recalculate(), time: const Duration(milliseconds: 300));
```

### 5.3 Granularidade de Obx na UI

```dart
// ❌ ERRADO — um Obx para a tela inteira causa rebuild completo
Obx(() => Column(children: [
  HeaderWidget(name: controller.name.value),
  ListWidget(items: controller.items),
  SummaryWidget(total: controller.total.value),
]))

// ✅ CORRETO — Obx granular por seção independente
Column(children: [
  Obx(() => HeaderWidget(name: controller.name.value)),
  Obx(() => ListWidget(items: controller.items)),
  Obx(() => SummaryWidget(total: controller.total.value)),
])
```

---

## 6. Estrutura de pastas esperada

```
lib/
├── app/
│   ├── data/
│   │   ├── local/
│   │   │   ├── app_database.dart          # Drift DB principal
│   │   │   ├── tables/                    # Uma classe Table por arquivo
│   │   │   └── daos/                      # DAOs por entidade
│   │   └── remote/
│   │       ├── firebase_source.dart       # ou supabase_source.dart
│   │       └── models/                    # DTOs do remoto
│   ├── services/
│   │   └── sync_service.dart              # ÚNICO ponto de acesso ao remoto
│   └── modules/
│       └── [feature]/
│           ├── controllers/               # TTL + stream subscription
│           └── views/                     # Obx granular
```

---

## 7. Erros arquiteturais mais comuns — referência rápida

| Erro                                       | Sintoma                                              | Correção                                                 |
| ------------------------------------------ | ---------------------------------------------------- | -------------------------------------------------------- |
| Controller lê direto do remoto             | Lentidão em toda navegação, uso de dados móveis alto | Mover leitura para Drift, usar TTL                       |
| `updatedAt` não atualizado com 0 registros | Sync disparado em toda visita mesmo com dados fresh  | Chamar `upsertSyncState` sempre ao final do sync         |
| Stream sem cancelamento em `onClose`       | Memory leak, listeners duplicados após navegação     | Adicionar `_subscription?.cancel()` em `onClose`         |
| `Obx` por tela inteira                     | UI trava ao atualizar um campo                       | Quebrar em `Obx` por widget independente                 |
| Soft delete ignorado                       | Dados deletados reaparecem após sync                 | Filtrar `deletedAt == null` em todas as queries locais   |
| Pull sem cursor incremental                | Rebusca todos os dados em cada sync                  | Usar `lastSyncAt` como parâmetro `since` na query remota |

---

## Próximos passos

- Backend Firebase: leia [firebase.md](firebase.md)
- Backend Supabase: leia [supabase.md](supabase.md)
- Validação do projeto: leia [validation.md](validation.md)
