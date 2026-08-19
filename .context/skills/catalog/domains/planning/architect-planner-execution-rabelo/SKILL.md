---
name: architect-planner-execution-rabelo
description: Planning overlay for Flutter+GetX projects optimized for low-capability executors. Inherits from architect-planner and routes to generate-feature, refactoring, and reviewing-code-changes with deterministic checkpoints.
version: 2.0.0
tags:
  [planning, flutter, getx, haiku-ready, task-decomposition]
difficulty: advanced
estimated_time: 8-20min
---

# Architect Planner - Execution Quality (Flutter/GetX)

## Inheritance & Scope

Este skill **herda** os princípios do `architect-planner`:

- Decomposição atômica de tarefas
- Executor Protocol e Fallback Protocol
- Validação executável antes de prosseguir

**Diferencial:** Adaptado para **Flutter + GetX**, com templates concretos e routing fixo.

**Premissa crítica:** Executor pode ser Haiku. Seja explícito, não assuma conhecimento prévio.

---

## EXECUTOR PROTOCOL (para agentes de baixa capacidade)

> **ATENÇÃO EXECUTOR:** Leia ANTES de qualquer tarefa.

### Regras Absolutas

1. **NUNCA invente** quando não entender → use FALLBACK PROTOCOL
2. **NUNCA pule tarefas** → respeite ordem do grafo
3. **SEMPRE valide** → execute checkpoints após cada tarefa
4. **SEMPRE documente** decisões em `decisions.md`
5. **NUNCA modifique testes** para passar

### Fluxo de Execução

```
PARA CADA tarefa na ordem do grafo:
  1. Leia a tarefa COMPLETA
  2. Verifique dependências concluídas
  3. Implemente usando o skill especificado (generate-feature ou refactoring)
  4. Execute checkpoint de validação
  5. SE passou → marque concluída, próxima
     SE falhou → consulte "Armadilhas" → se persistir, FALLBACK PROTOCOL
```

---

## FALLBACK PROTOCOL (quando algo dá errado)

### 1. Instrução Não Compreendida

```
PARE → Releia GLOSSÁRIO → Releia Context Help
SE ainda bloqueado:
  - Crie/edite `decisions.md`:
    ## BLOCKED: T[N]
    - Instrução: [copie a instrução]
    - Interpretação: [o que você acha]
    - Ação: PULEI para próxima independente
```

### 2. Validação/Teste Falhou

```
NÃO modifique teste → Releia "Armadilhas Conhecidas"
SE problema no seu código → corrija e re-valide
SE problema no teste/spec → documente e prossiga:
  ## VALIDATION_FAILED: T[N]
  - Comando: [qual falhou]
  - Erro: [mensagem]
  - Ação: PROSSEGUI com ressalva
```

### 3. Conflito Entre Tarefas

```
Tarefa com ID MENOR tem precedência.
Documente:
  ## CONFLICT: T[maior] vs T[menor]
  - Conflito: [descreva]
  - Resolução: Segui T[menor]
```

### 4. Dependência Não Disponível

```
NUNCA prossiga sem dependências prontas.
SE não há tarefas independentes → documente e PARE.
```

---

## CONTEXT HELP — Flutter/GetX (leia primeiro)

### Estrutura Padrão do Projeto

```
lib/
├── app/
│   ├── modules/                # Features isoladas (GetX Pattern)
│   │   └── [feature_name]/
│   │       ├── views/          # UI (GetView)
│   │       ├── controllers/    # Lógica (GetxController)
│   │       ├── bindings/       # DI (Bindings)
│   │       └── data/           # Repositories (opcional)
│   ├── routes/
│   │   ├── app_pages.dart      # Registro de rotas
│   │   └── app_routes.dart     # Constantes de rotas
│   └── theme/                  # MyTheme, AppColors
└── main.dart
```

### Stack Tecnológica

| Tech    | Versão | Papel               | Verificação                    |
| ------- | ------ | ------------------- | ------------------------------ |
| Flutter | 3.x+   | Framework           | `flutter --version`            |
| GetX    | 4.x+   | State + DI + Routes | `flutter pub deps \| grep get` |
| Dart    | 3.x+   | Linguagem           | `dart --version`               |

### Convenções Obrigatórias

| Elemento          | Padrão                      | Exemplo                        |
| ----------------- | --------------------------- | ------------------------------ |
| Feature folder    | snake_case                  | `user_profile/`                |
| View file         | `[feature]_view.dart`       | `user_profile_view.dart`       |
| Controller file   | `[feature]_controller.dart` | `user_profile_controller.dart` |
| Binding file      | `[feature]_binding.dart`    | `user_profile_binding.dart`    |
| Classe View       | PascalCase + `View`         | `UserProfileView`              |
| Classe Controller | PascalCase + `Controller`   | `UserProfileController`        |
| Classe Binding    | PascalCase + `Binding`      | `UserProfileBinding`           |
| Variável reativa  | `.obs` suffix               | `final count = 0.obs;`         |

### Glossário GetX

| Termo          | Significa                              | Exemplo                                            |
| -------------- | -------------------------------------- | -------------------------------------------------- |
| GetView        | Widget que já tem acesso ao Controller | `class LoginView extends GetView<LoginController>` |
| GetxController | Controlador com ciclo de vida          | `class LoginController extends GetxController`     |
| Binding        | Injeção de dependência lazy            | `Get.lazyPut(() => LoginController())`             |
| .obs           | Variável reativa observável            | `var count = 0.obs;`                               |
| Obx            | Widget que reconstrói quando .obs muda | `Obx(() => Text('${controller.count}'))`           |
| Get.toNamed    | Navegação por rota nomeada             | `Get.toNamed(Routes.LOGIN)`                        |

### Decisões de Arquitetura

| Decisão                | Quando                            | Como Decidir                            |
| ---------------------- | --------------------------------- | --------------------------------------- |
| usar Repository        | Feature acessa API/DB             | Sim, crie em `data/`                    |
| usar Provider          | Repository precisa de HTTP client | Sim, injete no Binding                  |
| usar Obx vs GetBuilder | State simples vs complexo         | Obx para .obs, GetBuilder para update() |

---

## DIRETRIZES GetX (TODAS as tarefas devem seguir)

### Diretriz 1: View estende GetView

**REGRA:** Todo View estende `GetView<XController>`, nunca StatelessWidget direto.

**Certo:**

```dart
class LoginView extends GetView<LoginController> {
  const LoginView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Obx(() => Text(controller.message.value)),
    );
  }
}
```

**Errado:**

```dart
class LoginView extends StatelessWidget {  // ❌ Não usa GetView
  @override
  Widget build(BuildContext context) {
    final controller = Get.find<LoginController>();  // ❌ Manual
    ...
  }
}
```

---

### Diretriz 2: Controller usa .obs e onInit

**REGRA:** State reativo com `.obs`, inicialização em `onInit()`.

**Certo:**

```dart
class LoginController extends GetxController {
  final email = ''.obs;
  final isLoading = false.obs;

  @override
  void onInit() {
    super.onInit();
    loadInitialData();
  }

  @override
  void onClose() {
    // Cancele workers, streams, listeners aqui
    super.onClose();
  }
}
```

**Errado:**

```dart
class LoginController extends GetxController {
  String email = '';  // ❌ Não é reativo

  void init() {  // ❌ Use onInit, não init customizado
    loadData();
  }
}
```

---

### Diretriz 3: Binding usa lazyPut

**REGRA:** Use `Get.lazyPut` para Controllers, `Get.put` para Singletons.

**Certo:**

```dart
class LoginBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<LoginController>(() => LoginController());
    Get.put(ApiProvider());  // Singleton
  }
}
```

**Errado:**

```dart
class LoginBinding extends Bindings {
  @override
  void dependencies() {
    Get.put(LoginController());  // ❌ Instancia imediatamente
  }
}
```

---

### Diretriz 4: Theme System (MyTheme)

**REGRA:** Use tokens do Theme System, NUNCA hardcode cores/tamanhos.

**Certo:**

```dart
Text(
  'Title',
  style: Get.textTheme.headlineMedium,  // ✅ Theme token
)
Container(
  color: Get.theme.colorScheme.primary,  // ✅ Theme token
)
```

**Errado:**

```dart
Text(
  'Title',
  style: TextStyle(fontSize: 24, color: Colors.blue),  // ❌ Hardcoded
)
```

---

### Diretriz 5: Validação Executável

**REGRA:** Após cada tarefa, execute estes comandos:

```bash
# 1. Análise estática
flutter analyze

# 2. Formato de código
dart format --set-exit-if-changed lib/

# 3. Testes (se existirem)
flutter test test/modules/[feature]/
```

---

## TASK CARD TEMPLATE (Flutter/GetX)

Use este formato para TODAS as tarefas:

````markdown
## Task T[N] - [Verbo Imperativo] [Feature Name]

**Tipo:** feature | refactor | bugfix | test
**Depende de:** none | T[X], T[Y]
**Skill de implementação:** generate-feature | refactoring

### Por Quê

[2-3 frases: contexto de negócio, problema que resolve]

### Objetivo

[1 frase: "Criar/Modificar X para que o usuário possa Y"]

### Passos (numerados)

1. **Criar** pasta `lib/app/modules/[feature_name]/`
2. **Criar** Controller usando Template GetX
3. **Criar** View usando Template GetX
4. **Criar** Binding usando Template GetX
5. **Registrar** rota em `app_pages.dart` e `app_routes.dart`

### Arquivos Produzidos

| Arquivo                                                   | Ação      | Descrição             |
| --------------------------------------------------------- | --------- | --------------------- |
| `lib/app/modules/login/controllers/login_controller.dart` | criar     | Controlador de login  |
| `lib/app/modules/login/views/login_view.dart`             | criar     | Tela de login         |
| `lib/app/modules/login/bindings/login_binding.dart`       | criar     | DI do módulo          |
| `lib/app/routes/app_pages.dart`                           | modificar | Adicionar GetPage     |
| `lib/app/routes/app_routes.dart`                          | modificar | Adicionar const LOGIN |

### Critérios de Aceite (DADO-QUANDO-ENTÃO)

- [ ] **DADO** que abro o app
      **QUANDO** navego para `/login`
      **ENTÃO** vejo a tela de login sem crash

- [ ] **DADO** que digito email inválido
      **QUANDO** pressiono "Entrar"
      **ENTÃO** vejo mensagem "Email inválido"

- [ ] **DADO** que digito credenciais válidas
      **QUANDO** pressiono "Entrar"
      **ENTÃO** navego para tela principal

### Checkpoint de Validação

```bash
# 1. Verificar que compila
flutter analyze --no-fatal-infos

# 2. Verificar que roda
flutter run --debug

# 3. Testar navegação manual
# - Abrir app
# - Navegar para a feature
# - Verificar que não trava
```
````

### Armadilhas Conhecidas

| Problema           | Sintoma                       | Solução                                  |
| ------------------ | ----------------------------- | ---------------------------------------- |
| Rota não funciona  | "Route not found"             | Verifique `app_pages.dart` → routes list |
| Controller null    | "null is not a subtype"       | Verifique `lazyPut` no Binding           |
| State não atualiza | Mudança não reflete na UI     | Use `.obs` + `Obx()`                     |
| Import errado      | "Target of URI doesn't exist" | Use path relativo ou package:            |

### Exemplo de Código Correto (LoginController)

```dart
// lib/app/modules/login/controllers/login_controller.dart
import 'package:get/get.dart';

class LoginController extends GetxController {
  final email = ''.obs;
  final password = ''.obs;
  final isLoading = false.obs;

  Future<void> login() async {
    if (!email.value.contains('@')) {
      Get.snackbar('Erro', 'Email inválido');
      return;
    }

    isLoading.value = true;
    try {
      // Lógica de autenticação aqui
      await Future.delayed(Duration(seconds: 2));
      Get.offAllNamed(Routes.HOME);
    } catch (e) {
      Get.snackbar('Erro', e.toString());
    } finally {
      isLoading.value = false;
    }
  }
}
```

```

---

## EXECUTION ROUTING (obrigatório)

Cada tarefa DEVE usar um destes skills:

| Skill | Quando Usar |
|-------|-------------|
| `generate-feature` | Criar nova feature do zero (View + Controller + Binding) |
| `refactoring` | Modificar feature existente, extrair lógica, renomear |
| `reviewing-code-changes` | SEMPRE após concluir cada tarefa (gate de qualidade) |

**Fluxo obrigatório:**
```

TAREFA → [generate-feature OU refactoring] → reviewing-code-changes → próxima tarefa

````

---

## CHECKPOINTS (ordem obrigatória)

### Checkpoint 1: Pre-Execution (antes de começar)
- [ ] Todas as tarefas têm critérios DADO-QUANDO-ENTÃO
- [ ] Todas as tarefas têm checkpoints executáveis
- [ ] Grafo de dependências está completo

### Gate 2: During Execution (após cada tarefa)
- [ ] Checkpoint de validação passou
- [ ] `reviewing-code-changes` executado
- [ ] Nenhum critical issue encontrado

### Gate 3: Final (antes de entregar)
- [ ] `flutter analyze` → 0 errors
- [ ] Todas as rotas registradas funcionam
- [ ] Nenhuma tarefa ficou bloqueada sem resolução

---

## PLANNER OUTPUT CONTRACT (produza sempre estas seções)

```markdown
# PLAN: [Feature Name]

## 1. CONTEXT SNAPSHOT
[2-3 parágrafos: o que o sistema faz, o que esta feature adiciona]

## 2. TASK GRAPH
````

T1 (Feature Structure) ────▶ T2 (Controller Logic) ────▶ T3 (View UI)
│
▼
T4 (Integration)

```

**Execution Order:** T1 → T2 → T3 → T4

## 3. TASK CARDS
[Use TASK CARD TEMPLATE para cada tarefa]

## 4. QUALITY GATES
- Pre: validating-task-blocks (se disponível)
- During: reviewing-code-changes (após cada tarefa)
- Final: flutter analyze + manual navigation test

## 5. NO-GO CONDITIONS
[Liste condições que bloqueariam o plano]
- Dependency X não está disponível
- Architecture boundary Y é desconhecida
```

---

## PLANNER VALIDATION CHECKLIST

Antes de entregar o plano, verifique:

### Completude

- [ ] Toda tarefa tem skill de implementação especificado
- [ ] Toda tarefa tem critérios DADO-QUANDO-ENTÃO
- [ ] Toda tarefa tem checkpoint executável
- [ ] Grafo de dependências está visual (ASCII)

### Clareza (para Haiku)

- [ ] Nenhum termo técnico sem estar no GLOSSÁRIO
- [ ] Exemplos de código estão completos (não templates vazios)
- [ ] Armadilhas conhecidas têm solução específica
- [ ] Passos são atômicos (<10 palavras cada)

### Executabilidade

- [ ] Executor consegue começar sem perguntas adicionais
- [ ] FALLBACK PROTOCOL cobre os 4 cenários
- [ ] Checkpoints são comandos bash válidos

### Flutter/GetX Specifics

- [ ] Estrutura de pastas segue convenção GetX
- [ ] Controllers usam `.obs` e `onInit`
- [ ] Views estendem `GetView`
- [ ] Bindings usam `lazyPut`
- [ ] Rotas registradas em `app_pages.dart`

---

## Anti-Patterns (evite)

| ❌ Não Faça                     | ✅ Faça                                                   |
| ------------------------------- | --------------------------------------------------------- |
| "Crie o login" (vago)           | "Criar LoginView extends GetView com form de email/senha" |
| Critério: "Deve funcionar"      | DADO x QUANDO y ENTÃO z                                   |
| Checkpoint: "Teste manualmente" | `flutter run && navegar para /login`                      |
| Exemplo: `{{CONTROLLER_NAME}}`  | Código completo de LoginController                        |
| Tarefa com 5+ arquivos          | Divida em sub-tarefas                                     |

---

## Success Metrics

Plano é válido quando:

- ✅ Haiku consegue executar 100% sem perguntas
- ✅ Todos os checkpoints são comandos executáveis
- ✅ Todos os exemplos são código Flutter/GetX real
- ✅ `reviewing-code-changes` detectaria problemas

Plano FALHA quando:

- ❌ Tarefa usa termo não definido no glossário
- ❌ Checkpoint é "verifique se funciona"
- ❌ Exemplo de código tem `{{PLACEHOLDER}}`
- ❌ Esqueceu de registrar rota em `app_pages.dart`
