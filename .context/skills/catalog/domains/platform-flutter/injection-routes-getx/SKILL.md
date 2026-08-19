---
name: getx-architecture
description: >
  Use esta skill sempre que o agente precisar criar, modificar, mover ou refatorar
  qualquer elemento de um projeto Flutter com GetX e rotas nomeadas: criar nova tela,
  adicionar rota, mover ou reorganizar Bindings, criar controller, registrar serviço
  global, ou alterar a tela inicial. Acione também quando o usuário mencionar
  GetPage, Binding, Get.toNamed, MainBinding, AppPages, ou auth/sessão em contexto
  Flutter. Não acionar para projetos Flutter sem GetX ou que usem go_router/auto_route.
---

# GetX Architecture — Flutter com Rotas Nomeadas

Este projeto Flutter usa GetX com rotas nomeadas e injeção de dependência via Bindings.
Antes de criar ou modificar qualquer tela, rota ou controller, leia e respeite esta arquitetura.

---

## Estrutura canônica do projeto

```
lib/
├── main.dart                          ← initialBinding: MainBinding()
├── app/
│   ├── routes/
│   │   ├── app_routes.dart            ← constantes de rota (ex: '/home')
│   │   └── app_pages.dart             ← lista GetPage[] com name + page + binding
│   ├── core/
│   │   └── bindings/
│   │       └── main_binding.dart      ← injeções GLOBAIS (auth, sessão, tema...)
│   └── modules/
│       └── [feature]/
│           ├── bindings/
│           │   └── [feature]_binding.dart
│           ├── controllers/
│           │   └── [feature]_controller.dart
│           └── views/
│               └── [feature]_view.dart
```

---

## Auditoria de escopo — OBRIGATÓRIA antes de qualquer implementação

Antes de escrever qualquer Binding, controller ou injeção, execute este diagnóstico:

1. **Liste** todos os controllers envolvidos na tarefa.
2. **Para cada controller**, responda: em quantas features ele é usado (direta ou indiretamente)?
3. **Decida o escopo** usando a árvore abaixo.
4. **Se um controller já está num FeatureBinding e outra feature precisa dele** → refatore para MainBinding ANTES de qualquer outra mudança. Nunca implemente a nova feature enquanto a injeção estiver no escopo errado.

### Árvore de decisão de escopo

```
Quantas features usam este controller?
├── Apenas 1 → FeatureBinding com Get.lazyPut()
├── 2 ou mais → MainBinding com Get.put(..., permanent: true)
└── Incerto?  → MainBinding (default seguro)

Controller já existe num FeatureBinding e uma nova feature precisa dele?
└── Mova para MainBinding PRIMEIRO. Nunca injete o mesmo controller
    em dois FeatureBindings diferentes.
```

---

## Anti-padrão crítico — Controller Periférico

**Sintoma:** Controller X está no `FeatureABinding`. Feature B também precisa de Controller X. O agente propõe adicionar outra injeção de Controller X no `FeatureBBinding` ou cria um `SharedBinding` ad-hoc.

**Por que está errado:**
- GetX pode criar duas instâncias separadas → estado dessincronizado entre features
- Bugs silenciosos: reatividade não propaga entre as duas instâncias

**Solução correta — sempre:**
1. Remover `Get.lazyPut(() => ControllerX())` do `FeatureABinding`
2. Adicionar `Get.put(ControllerX(), permanent: true)` no `MainBinding`
3. Tanto Feature A quanto Feature B acessam via `Get.find<ControllerX>()`

```dart
// ERRADO — mesmo controller em dois FeatureBindings
class FeatureABinding extends Bindings {
  void dependencies() => Get.lazyPut(() => ControllerX());
}
class FeatureBBinding extends Bindings {
  void dependencies() => Get.lazyPut(() => ControllerX()); // ← NUNCA faça isso
}

// CERTO — controller cross-feature no MainBinding
class MainBinding extends Bindings {
  void dependencies() {
    Get.put(ControllerX(), permanent: true); // ← uma instância, acessível em todo lugar
  }
}
```

---

## Regra fundamental — escopo das injeções

### MainBinding → escopo global (`lib/app/core/bindings/main_binding.dart`)

Registra controllers e serviços que **duas ou mais features dependem**, além dos globais de auth/sessão.
É executado uma única vez, na inicialização do app, via `initialBinding` no `main.dart`.

```dart
// main.dart
GetMaterialApp(
  initialBinding: MainBinding(),
  ...
)
```

```dart
// main_binding.dart
class MainBinding extends Bindings {
  @override
  void dependencies() {
    Get.put(AuthController(), permanent: true);   // ← permanent: true para globais
    Get.put(UserSessionService(), permanent: true);
    // outros controllers/services usados em 2+ features
  }
}
```

> **REGRA CRÍTICA:** Se uma dependência é usada em mais de uma feature, ela pertence ao MainBinding — sem exceção. Nunca mova injeções cross-feature para o Binding de uma feature específica nem crie SharedBindings ad-hoc para isso.

### FeatureBinding → escopo local (`lib/app/modules/[feature]/bindings/`)

Registra controllers usados **exclusivamente naquela feature e em nenhuma outra**.
É executado pelo GetX automaticamente ao navegar para a rota.

#### Get.lazyPut vs Get.put no FeatureBinding

| Método | Quando usar |
|--------|-------------|
| `Get.lazyPut(() => Controller())` | O controller **pode** ser usado na feature, mas não é necessário imediatamente ao carregar o módulo. A instância só é criada quando `Get.find()` for chamado pela primeira vez. |
| `Get.put(Controller())` | O controller é **sempre necessário** assim que a feature carrega — a View ou outro controller depende dele no boot do módulo. |

```dart
// meal_binding.dart
class MealBinding extends Bindings {
  @override
  void dependencies() {
    Get.put(MealController());          // ← necessário no boot da feature
    Get.lazyPut(() => FilterController()); // ← pode ser usado, mas não no boot
  }
}
```

**Regra de decisão:**
- A View inicializa e **já precisa** do controller (ex: carrega dados no `onInit`)? → `Get.put`
- O controller só é acionado por interação do usuário ou fluxo condicional? → `Get.lazyPut`
- Dúvida? Prefira `Get.lazyPut` — instanciação tardia tem custo menor e o GetX garante a criação quando necessário.

---

## Fluxo de navegação (ordem de execução)

Ao chamar `Get.toNamed('/meal-analysis')`:

```
1. GetX localiza o GetPage pelo name em app_pages.dart
2. Executa o Binding associado (MealBinding) → injeta controllers/serviços da feature
3. Instancia a View (MealView) → que consome os controllers via Get.find()
```

Os controllers do MainBinding já estão disponíveis em qualquer ponto deste fluxo
porque foram injetados na inicialização do app.

---

## AppPages e AppRoutes — padrão de registro

```dart
// app_routes.dart
abstract class AppRoutes {
  static const home    = '/home';
  static const meal    = '/meal-analysis';
  static const profile = '/profile';
}
```

```dart
// app_pages.dart
class AppPages {
  static final pages = [
    GetPage(
      name: AppRoutes.home,
      page: () => HomeView(),
      binding: HomeBinding(),
    ),
    GetPage(
      name: AppRoutes.meal,
      page: () => MealView(),
      binding: MealBinding(),
    ),
  ];
}
```

---

## Regras de execução para o agente

### Ao criar uma nova tela:
1. Criar `[feature]_view.dart`, `[feature]_controller.dart`, `[feature]_binding.dart` no módulo correto
2. Registrar a rota em `app_routes.dart` (nova constante)
3. Registrar o `GetPage` em `app_pages.dart` (com name, page e binding)
4. No Binding da feature: usar `Get.put` se o controller é necessário no boot do módulo; usar `Get.lazyPut` se pode ser usado mas não é necessário imediatamente. Nunca usar `Get.put(..., permanent: true)` em FeatureBinding.
5. Verificar: o controller usa algo do MainBinding? → `Get.find<AuthController>()` funciona diretamente

### Ao criar ou redefinir a tela inicial:
1. A tela inicial muda em `GetMaterialApp(initialRoute: AppRoutes.novaRota)`
2. O `initialBinding: MainBinding()` **NUNCA muda de lugar** — permanece no `GetMaterialApp`
3. A nova tela inicial tem seu próprio Binding para dependências locais
4. Nunca transferir o conteúdo do MainBinding para o Binding da tela inicial

### Ao mover injeções entre Bindings:
- **Execute a auditoria de escopo (seção acima) antes de qualquer mudança**
- "Esta dependência é usada em 2+ features?" → MainBinding, permanent: true
- "Esta dependência é usada só nesta feature?" → FeatureBinding, lazyPut
- Se o controller já está num FeatureBinding e outra feature precisa → mova para MainBinding PRIMEIRO, não depois
- AuthController, SessionService, ThemeController → **sempre** MainBinding, permanent: true

---

## Validação antes de entregar

Antes de apresentar qualquer código ao usuário, verificar:

- [ ] `MainBinding` está referenciado em `main.dart` como `initialBinding` e não em nenhum `GetPage`
- [ ] Controllers globais (auth, sessão) estão no `MainBinding` com `permanent: true`
- [ ] Controllers de feature usam `Get.lazyPut` no FeatureBinding correspondente
- [ ] Nova rota registrada em `app_routes.dart` (constante) e em `app_pages.dart` (GetPage)
- [ ] Nenhum `Get.put` de controller global dentro de uma View ou Controller de feature
- [ ] A tela inicial pode mudar sem arrastar as injeções globais consigo

---

## Get.isRegistered — uso restrito e justificado

`Get.isRegistered<T>()` **não é um mecanismo de segurança** e não deve ser usado como fallback defensivo antes de `Get.find()`.

### Anti-padrão — fallback com isRegistered

```dart
// ERRADO — isRegistered usado para mascarar injeção mal configurada
final controller = Get.isRegistered<MyController>()
    ? Get.find<MyController>()
    : MyController(); // instância órfã, fora do grafo de DI
```

Esse padrão indica que a injeção está no escopo errado ou não foi registrada no Binding correto. A solução é corrigir a arquitetura — não adicionar guardas.

### Regra

Se você sentiu a necessidade de usar `Get.isRegistered`, pare e responda:

1. **O controller deveria estar no MainBinding?** → Mova para lá. O `isRegistered` não seria necessário.
2. **O controller deveria estar num FeatureBinding?** → Corrija o Binding. O `isRegistered` não seria necessário.
3. **A feature está sendo acessada antes da rota ser carregada?** → Corrija o fluxo de navegação.

### Único uso legítimo

`Get.isRegistered` só é justificado quando a **ausência da instância é um estado válido e esperado** — não uma falha de configuração. Exemplos raros:

- Plugins opcionais que podem ou não estar ativos na sessão atual
- Teardown explícito de controllers temporários com verificação antes de limpar
- Debugging/diagnóstico em modo desenvolvimento

Em todos os outros casos, se `Get.find<T>()` lança erro, a causa é injeção mal planejada — não falta de `isRegistered`.

---

## Erros comuns — nunca faça

| Erro | Correto |
|------|---------|
| Mover `AuthController` para o Binding da tela inicial | Manter no `MainBinding` |
| Usar `Get.put` sem `permanent: true` para globais | `Get.put(..., permanent: true)` |
| Registrar controller global no `GetPage` da home | Registrar no `initialBinding` do `GetMaterialApp` |
| Criar rota sem registrar em `app_pages.dart` | Sempre registrar name + page + binding |
| Instanciar controller diretamente na View | Usar `Get.find<Controller>()` |
| Injetar o mesmo controller em dois FeatureBindings | Mover para `MainBinding` com `permanent: true` |
| Criar `SharedBinding` ad-hoc para controller periférico | Se ≥ 2 features usam → `MainBinding`, não binding intermediário |
| Resolver "not found" adicionando `Get.put` na View | Auditar o Binding responsável; se cross-feature → mover para MainBinding |
| Propor múltiplas soluções para acesso cross-module | Parar — a solução é globalizar no MainBinding, não multiplicar injeções |
| Usar `Get.isRegistered` como fallback antes de `Get.find` | Corrigir o Binding responsável; `isRegistered` não substitui arquitetura correta |
| `Get.isRegistered ? Get.find() : MyController()` | Nunca instanciar fora do DI — corrigir o escopo da injeção |
