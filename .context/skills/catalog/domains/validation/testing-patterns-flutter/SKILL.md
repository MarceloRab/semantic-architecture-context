---
name: testing-patterns-flutter
description: Flutter testing patterns and principles. Unit, widget, integration tests with flutter_test, mockito, and AAA pattern. Covers testing pyramid, mocking strategies, and GetX controller testing.
version: 1.0.0
tags:
  [
    testing,
    flutter,
    dart,
    unit-test,
    widget-test,
    integration-test,
    mockito,
    getx,
    tdd,
  ]
difficulty: intermediate
estimated_time: 10-20min
---

# Testing Patterns — Flutter

> Testes são documentação viva. Se alguém não entende o que o código faz lendo os testes, reescreva-os.

---

## When to use this skill

- Ao criar testes para qualquer camada Flutter (model, controller, service, widget)
- Ao revisar código e verificar cobertura de testes
- Ao debugar behavior inesperado (escreva o teste antes de corrigir)
- Quando o usuário pedir: "adicionar testes", "cobrir com testes", "TDD", "testar o controller"

---

## Testing Pyramid (Flutter)

```
         /\          Integration (Poucos)
        /  \         Fluxos críticos end-to-end
       /----\
      /      \       Widget Tests (Alguns)
     /--------\      Componentes UI, interações
    /          \
   /------------\    Unit Tests (Muitos)
                     Controllers, Services, Models
```

---

## AAA Pattern (Obrigatório)

| Step        | Propósito                         |
| ----------- | --------------------------------- |
| **Arrange** | Configurar dados de teste e mocks |
| **Act**     | Executar o código sob teste       |
| **Assert**  | Verificar o resultado esperado    |

```dart
test('deve retornar usuário quando ID é válido', () {
  // Arrange
  final mockRepo = MockUserRepository();
  when(mockRepo.findById('123')).thenReturn(User(id: '123', name: 'João'));
  final service = UserService(mockRepo);

  // Act
  final result = service.getUser('123');

  // Assert
  expect(result?.name, equals('João'));
  verify(mockRepo.findById('123')).called(1);
});
```

---

## 1. Unit Tests (Controllers, Services, Models)

### Configuração base

```dart
// pubspec.yaml (dependências de teste)
dev_dependencies:
  flutter_test:
    sdk: flutter
  mockito: ^5.4.4
  build_runner: ^2.4.0
  fake_async: ^1.3.1
```

### GetX Controller Testing

```dart
// test/controllers/user_controller_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';

@GenerateMocks([UserRepository])
import 'user_controller_test.mocks.dart';

void main() {
  late UserController controller;
  late MockUserRepository mockRepo;

  setUp(() {
    // Arrange (compartilhado)
    mockRepo = MockUserRepository();
    Get.testMode = true; // OBRIGATÓRIO para GetX em testes
    controller = UserController(repository: mockRepo);
    controller.onInit();
  });

  tearDown(() {
    Get.reset(); // Limpar após cada teste
    controller.onClose();
  });

  group('UserController.fetchUser', () {
    test('deve definir isLoading como true durante fetch', () async {
      // Arrange
      when(mockRepo.fetchUser(any))
          .thenAnswer((_) async => User(id: '1', name: 'Ana'));

      // Act
      final future = controller.fetchUser('1');

      // Assert (durante execução)
      expect(controller.isLoading.value, isTrue);
      await future;
      expect(controller.isLoading.value, isFalse);
    });

    test('deve definir errorMessage quando fetch falha', () async {
      // Arrange
      when(mockRepo.fetchUser(any)).thenThrow(Exception('Network error'));

      // Act
      await controller.fetchUser('1');

      // Assert
      expect(controller.errorMessage.value, isNotEmpty);
      expect(controller.user.value, isNull);
    });
  });
}
```

### Model Testing

```dart
// test/models/user_test.dart
void main() {
  group('User.fromJson', () {
    test('deve criar User com campos válidos', () {
      // Arrange
      final json = {'id': '1', 'name': 'Maria', 'email': 'maria@email.com'};

      // Act
      final user = User.fromJson(json);

      // Assert
      expect(user.id, equals('1'));
      expect(user.name, equals('Maria'));
      expect(user.email, equals('maria@email.com'));
    });

    test('deve lançar FormatException quando id está ausente', () {
      // Arrange
      final json = {'name': 'Maria'};

      // Act & Assert
      expect(() => User.fromJson(json), throwsA(isA<FormatException>()));
    });
  });
}
```

---

## 2. Widget Tests

### Configuração base

```dart
// test/widgets/user_card_test.dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';

void main() {
  group('UserCard', () {
    testWidgets('deve exibir nome do usuário', (tester) async {
      // Arrange
      final user = User(id: '1', name: 'Pedro');

      // Act
      await tester.pumpWidget(
        GetMaterialApp( // Use GetMaterialApp para suporte a GetX
          home: UserCard(user: user),
        ),
      );

      // Assert
      expect(find.text('Pedro'), findsOneWidget);
      expect(find.byType(CircleAvatar), findsOneWidget);
    });

    testWidgets('deve chamar onTap quando tapped', (tester) async {
      // Arrange
      bool wasTapped = false;
      final user = User(id: '1', name: 'Pedro');

      // Act
      await tester.pumpWidget(
        GetMaterialApp(
          home: UserCard(user: user, onTap: () => wasTapped = true),
        ),
      );
      await tester.tap(find.byType(UserCard));
      await tester.pump();

      // Assert
      expect(wasTapped, isTrue);
    });

    testWidgets('deve exibir loading indicator quando isLoading=true', (tester) async {
      // Arrange + Act
      await tester.pumpWidget(
        const GetMaterialApp(home: UserCard(isLoading: true)),
      );

      // Assert
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
      expect(find.byType(ListTile), findsNothing);
    });
  });
}
```

### Testando Obx / Reactive Widgets

```dart
testWidgets('deve atualizar UI quando controller muda', (tester) async {
  // Arrange
  final controller = Get.put(CounterController());

  await tester.pumpWidget(
    GetMaterialApp(
      home: Obx(() => Text('${controller.count.value}')),
    ),
  );
  expect(find.text('0'), findsOneWidget);

  // Act
  controller.increment();
  await tester.pump(); // Necessário para rebuilds reativos

  // Assert
  expect(find.text('1'), findsOneWidget);
});
```

---

## 3. Integration Tests

```dart
// integration_test/app_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('Fluxo de Login', () {
    testWidgets('usuário consegue fazer login com credenciais válidas', (tester) async {
      // Arrange
      await tester.pumpWidget(const MyApp());
      await tester.pumpAndSettle(); // Aguarda animações

      // Act
      await tester.enterText(find.byKey(const Key('email_field')), 'user@email.com');
      await tester.enterText(find.byKey(const Key('password_field')), 'senha123');
      await tester.tap(find.byKey(const Key('login_button')));
      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Assert
      expect(find.text('Bem-vindo!'), findsOneWidget);
    });
  });
}
```

---

## 4. Mocking Patterns

### Quando mockar

| Deve Mockar                 | Não Deve Mockar   |
| --------------------------- | ----------------- |
| APIs externas / HTTP        | Código sob teste  |
| Banco de dados              | Pure functions    |
| SharedPreferences / Storage | Models simples    |
| GetX Services injetados     | Lógica de negócio |

### Gerando Mocks com Mockito

```dart
// 1. Anotar com @GenerateMocks
@GenerateMocks([UserRepository, AuthService])
void main() { ... }

// 2. Gerar com build_runner
// flutter pub run build_runner build --delete-conflicting-outputs

// 3. Usar o mock
final mockRepo = MockUserRepository();
when(mockRepo.fetchAll()).thenAnswer((_) async => [user1, user2]);
when(mockRepo.save(any)).thenThrow(DatabaseException());
```

### Fake Async (testar Timers e Delays)

```dart
import 'package:fake_async/fake_async.dart';

test('deve cancelar timer quando onClose é chamado', () {
  fakeAsync((async) {
    final controller = DebounceController();
    controller.onInit();

    controller.search('query');
    async.elapse(const Duration(milliseconds: 300));

    expect(controller.hasSearched.value, isTrue);

    controller.onClose();
  });
});
```

---

## 5. Test Naming Convention

| Padrão                                   | Exemplo                                      |
| ---------------------------------------- | -------------------------------------------- |
| `deve [comportamento] quando [condição]` | `deve lançar erro quando usuário não existe` |
| `deve [comportamento] com [dados]`       | `deve formatar CPF com máscara`              |
| `deve [fazer X] e [fazer Y]`             | `deve salvar e navegar para home`            |

---

## 6. TDD Workflow para Flutter

```
🔴 RED → Escreva o teste que vai falhar
    ↓
🟢 GREEN → Escreva o MÍNIMO de código para passar
    ↓
🔵 REFACTOR → Limpe sem quebrar os testes
    ↓
   Repita...
```

**Exemplo prático:**

```dart
// 1. RED — Teste falha (CpfValidator não existe)
test('deve validar CPF válido', () {
  expect(CpfValidator.isValid('11144477735'), isTrue);
});

// 2. GREEN — Implementação mínima
class CpfValidator {
  static bool isValid(String cpf) => cpf.length == 11;
}

// 3. REFACTOR — Lógica completa com algoritmo real
class CpfValidator {
  static bool isValid(String cpf) {
    if (cpf.length != 11) return false;
    // ... algoritmo completo
  }
}
```

---

## Anti-Patterns

| ❌ Não Faça                                   | ✅ Faça                                   |
| --------------------------------------------- | ----------------------------------------- |
| Testar implementação interna                  | Testar behavior/contrato                  |
| Esquecer `Get.reset()` no tearDown            | Sempre limpar estado GetX                 |
| `pump()` sem `pumpAndSettle()` para animações | Use `pumpAndSettle()` quando há animações |
| Testes longos com múltiplos asserts           | Um behavior por teste                     |
| Ignorar testes flaky                          | Investigar e corrigir a causa raiz        |
| `any` em mocks críticos                       | Ser específico com os arguments           |
| Modificar testes para fazê-los passar         | Corrigir a implementação                  |
| Usar `!` em código de teste                   | Use `expect(value, isNotNull)` antes      |

---

## Success Criteria

- Todos os testes passam em `flutter test`
- Sem warnings do `dart analyze` nos arquivos de teste
- Controllers são testados sem instanciar a View
- Mocks gerados com `build_runner` (não escritos manualmente)
- `Get.testMode = true` e `Get.reset()` nos testes GetX

---

## Related Skills

- `clean-code` — Aplicar naming conventions nos arquivos de teste
- `investigating-bugs` — Usar TDD para reproduzir bug antes de corrigir
- `reviewing-code-changes` — Verificar cobertura de testes no review
- `validating-flutter-projects` — Validação de cobertura de testes no projeto

## Validation

```bash
# Executar todos os testes
flutter test

# Com cobertura
flutter test --coverage
genhtml coverage/lcov.info -o coverage/html

# Gerar mocks
flutter pub run build_runner build --delete-conflicting-outputs
```
