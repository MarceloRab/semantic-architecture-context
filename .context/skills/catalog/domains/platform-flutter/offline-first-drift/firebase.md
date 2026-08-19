# Referência Firebase/Firestore — Offline-First com Drift

## Regra principal com Firestore

`Source.server` é uma leitura paga e bloqueante. Nunca use dentro de controllers ou na inicialização de telas. Todo acesso com `Source.server` deve estar exclusivamente no `SyncService`.

---

## Pull incremental com Firestore

O cursor incremental usa `Timestamp` do Firestore. A query deve filtrar por `updatedAt >= lastSyncAt` para buscar apenas documentos modificados desde o último sync.

```dart
Future<PullResult<T>> pull(String userId, {DateTime? since}) async {
  Query query = _collection(userId);

  if (since != null) {
    query = query.where(
      'updatedAt',
      isGreaterThanOrEqualTo: Timestamp.fromDate(since),
    );
  }

  // NUNCA use Source.server fora do SyncService
  final snapshot = await query
      .orderBy('updatedAt')
      .get(const GetOptions(source: Source.server));

  final items = snapshot.docs.map((d) => _fromDoc(d)).toList();

  // Novo cursor = updatedAt do documento mais recente
  final newCursor = items.isEmpty
      ? null
      : items.map((i) => i.updatedAt).reduce((a, b) => a.isAfter(b) ? a : b);

  return PullResult(items: items, newCursor: newCursor);
}
```

### Por que não usar `Source.cache` do Firestore

`Source.cache` do Firestore **não é equivalente ao Drift**. O cache do Firestore:

- É gerenciado pelo SDK, sem controle de TTL
- Não tem schema tipado
- Pode ser descartado pelo SO a qualquer momento
- Não suporta queries complexas com joins

O Drift é o banco local. O `Source.cache` do Firestore não deve ser usado como substituto.

---

## Soft delete com Firestore

Documentos deletados localmente devem ser marcados com `deletedAt` no Drift e sincronizados como soft delete no Firestore. O campo `deletedAt` no Firestore permite que outros dispositivos saibam que o documento foi removido.

```dart
// Ao deletar localmente
await db.softDelete(entityId);

// No sync — enviar soft deletes pendentes ao Firestore
final pendingDeletes = await db.getPendingDeletes(userId);
for (final item in pendingDeletes) {
  await _collection(userId).doc(item.remoteId).update({
    'deletedAt': FieldValue.serverTimestamp(),
    'updatedAt': FieldValue.serverTimestamp(),
  });
}
```

```dart
// No pull — filtrar soft deletes recebidos
for (final item in pullResult.items) {
  if (item.deletedAt != null) {
    await db.softDelete(item.localId);
  } else {
    await db.upsert(item);
  }
}
```

---

## Autenticação e userId

O `userId` para sync deve vir sempre do `FirebaseAuth.instance.currentUser?.uid`.
Nunca armazene o userId em SharedPreferences como fonte primária — use o Auth como fonte de verdade.

```dart
// No SyncService
String get _currentUserId {
  final uid = FirebaseAuth.instance.currentUser?.uid;
  if (uid == null) throw StateError('syncService called without authenticated user');
  return uid;
}
```

---

## Regras de segurança no Firestore (Firestore Rules)

Todo documento deve ter `userId` e as regras devem garantir que um usuário só acessa seus próprios dados:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId}/{document=**} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

---

## Tratamento de conflitos

Em arquitetura offline-first com múltiplos dispositivos, conflitos podem ocorrer. A estratégia padrão é **last-write-wins por `updatedAt`**:

```dart
Future<void> upsertWithConflictResolution(T remote, T? local) async {
  if (local == null || remote.updatedAt.isAfter(local.updatedAt)) {
    await db.upsert(remote);
  }
  // Se local é mais recente, ele será enviado no próximo push
}
```

---

## Estrutura recomendada de coleções no Firestore

```
users/{userId}/
  meals/{mealId}
  exercises/{exerciseId}
  goals/{goalId}
  sync_metadata/{entity}   ← opcional, para server-side tracking
```

Estrutura hierárquica por `userId` facilita as Firestore Rules e queries incrementais.

---

## Checklist Firebase

- [ ] Nenhum `Source.server` fora do SyncService
- [ ] Pull usa `updatedAt >= lastSyncAt` como filtro incremental
- [ ] Soft delete sincronizado (campo `deletedAt` no Firestore)
- [ ] Firestore Rules restringem acesso por `userId`
- [ ] `userId` vem do `FirebaseAuth`, nunca de storage local
- [ ] Conflitos resolvidos por `updatedAt` (last-write-wins)
