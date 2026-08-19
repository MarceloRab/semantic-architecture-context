# Referência Supabase — Offline-First com Drift

## Regra principal com Supabase

Toda query ao Supabase deve estar exclusivamente no `SyncService`. Controllers e widgets nunca acessam o cliente Supabase diretamente.

---

## Pull incremental com Supabase

O cursor incremental usa `updated_at` como filtro. A query deve buscar apenas registros modificados desde o último sync.

```dart
Future<PullResult<T>> pull(String userId, {DateTime? since}) async {
  var query = supabase
      .from('meals')
      .select()
      .eq('user_id', userId)
      .order('updated_at');

  if (since != null) {
    // gte = greater than or equal
    query = query.gte('updated_at', since.toIso8601String());
  }

  final response = await query;
  final items = (response as List).map((row) => _fromRow(row)).toList();

  final newCursor = items.isEmpty
      ? null
      : items.map((i) => i.updatedAt).reduce((a, b) => a.isAfter(b) ? a : b);

  return PullResult(items: items, newCursor: newCursor);
}
```

---

## Realtime com Supabase — uso correto

O Supabase oferece canais Realtime (WebSocket). Em projetos offline-first, Realtime **não substitui o sync por TTL** — ele o complementa para casos onde atualização imediata é crítica (ex: notificações, colaboração em tempo real).

### Quando usar Realtime

- Notificações de eventos críticos (ex: médico recebe alerta de paciente)
- Colaboração simultânea entre usuários
- **Não usar** para dados que podem ter latência de 30 minutos

### Padrão correto de Realtime no SyncService

```dart
RealtimeChannel? _channel;

void subscribeToRealtime(String userId) {
  _channel = supabase
      .channel('public:meals:user_id=eq.$userId')
      .onPostgresChanges(
        event: PostgresChangeEvent.all,
        schema: 'public',
        table: 'meals',
        filter: PostgresChangeFilter(
          type: PostgresChangeFilterType.eq,
          column: 'user_id',
          value: userId,
        ),
        callback: (payload) async {
          // Realtime dispara um sync incremental — não atualiza UI diretamente
          await syncEntity(userId, 'meals');
          // O Drift emite via stream, a UI atualiza automaticamente
        },
      )
      .subscribe();
}

void unsubscribeFromRealtime() {
  _channel?.unsubscribe();
  _channel = null;
}
```

**Regra:** O callback do Realtime chama `syncEntity`, que escreve no Drift, que emite o stream. A UI nunca recebe dados do Realtime diretamente.

---

## Row Level Security (RLS) — obrigatório

Todo projeto Supabase em produção deve ter RLS habilitado. Sem RLS, qualquer usuário autenticado pode ler dados de outros usuários.

```sql
-- Habilitar RLS na tabela
ALTER TABLE meals ENABLE ROW LEVEL SECURITY;

-- Policy de leitura
CREATE POLICY "users_read_own_meals"
  ON meals FOR SELECT
  USING (auth.uid() = user_id);

-- Policy de escrita
CREATE POLICY "users_write_own_meals"
  ON meals FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Policy de update
CREATE POLICY "users_update_own_meals"
  ON meals FOR UPDATE
  USING (auth.uid() = user_id);
```

---

## Soft delete com Supabase

```dart
// Query local — sempre filtrar deletados
Future<List<Meal>> getMeals(String userId) =>
  (select(meals)
    ..where((t) => t.userId.equals(userId) & t.deletedAt.isNull()))
  .get();
```

```sql
-- No Supabase, filtrar soft deletes no pull
-- (RLS + query combinados)
SELECT * FROM meals
WHERE user_id = auth.uid()
  AND deleted_at IS NULL
  AND updated_at >= $1
ORDER BY updated_at;
```

---

## Push — enviar dados locais ao Supabase

```dart
Future<void> pushPendingChanges(String userId) async {
  final pending = await db.getPendingUpserts(userId);

  if (pending.isEmpty) return;

  // Upsert em batch — mais eficiente que múltiplos inserts
  await supabase.from('meals').upsert(
    pending.map((item) => item.toJson()).toList(),
    onConflict: 'id',           // coluna de conflito
    ignoreDuplicates: false,    // atualizar em conflito
  );

  await db.markAsSynced(pending.map((i) => i.id).toList());
}
```

---

## Autenticação e userId

```dart
String get _currentUserId {
  final user = supabase.auth.currentUser;
  if (user == null) throw StateError('syncService called without authenticated user');
  return user.id;
}
```

---

## Índices recomendados no Supabase

```sql
-- Índice para pull incremental (crítico para performance)
CREATE INDEX idx_meals_user_updated
  ON meals (user_id, updated_at);

-- Índice para soft delete queries
CREATE INDEX idx_meals_user_active
  ON meals (user_id)
  WHERE deleted_at IS NULL;
```

---

## Checklist Supabase

- [ ] Nenhuma query Supabase fora do SyncService
- [ ] Pull usa `updated_at >= lastSyncAt` como filtro incremental
- [ ] RLS habilitado em todas as tabelas com dados de usuário
- [ ] Soft delete implementado (`deleted_at` nullable)
- [ ] Realtime (se usado) chama `syncEntity`, não atualiza UI diretamente
- [ ] Push em batch com `upsert` e `onConflict`
- [ ] Índices em `(user_id, updated_at)` para queries de sync
- [ ] `userId` vem de `supabase.auth.currentUser`, nunca de storage local
