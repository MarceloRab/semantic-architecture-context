---
name: generate-feature
description: Generates a complete feature module (View, Controller, Binding, Repository) following Rabelo Standards (GetX Pattern + Theme System + Modern UI Excellence).
version: 2.0.0
updated: 2026-02-23
tags: [feature, scaffold, getx, architecture, generator, modern-ui]
difficulty: intermediate
estimated_time: 10-15min
---

# Feature Generator (Rabelo Standards) 🏭

Cria um feature module production-ready orquestrando arquitetura (GetX) e design (flutter_design skill). A UI resultante deve ser **visualmente premium** — não apenas estruturalmente correta.

## When to use
- Iniciar uma nova tela ou módulo funcional.
- "Criar feature de login", "Adicionar tela de configurações", "Gerar módulo de perfil".
- Necessidade de consistência em arquitetura (Bindings, Controllers) **e** UI.

## Prerequisites
- Projeto usa GetX Pattern.
- **VERIFICAR** os paths reais do projeto antes de criar arquivos:
  - Rotas: procurar `app_pages.dart` e `app_routes.dart` (pode estar em `lib/routes/` ou `lib/app/routes/`)
  - Módulos: procurar pasta `modules/` (pode estar em `lib/modules/` ou `lib/app/modules/`)
  - Use `find_by_name` ou `list_dir` para confirmar antes de criar

## Mandatory Skill Orchestration

Ao criar qualquer tela ou widget, esta skill DEVE chamar a skill de UI e aplicar suas regras:

- **Skill path**: `domains/platform-flutter/ui-theming/flutter_design/SKILL.md`
- **Escopo**: design tokens, tipografia, spacing, anti-hardcoding, Modern UI Excellence
- **Regra inviolável**: Não entregue nenhuma View/Widget sem passar **todos** os Quality Gates do `flutter_design` — incluindo os gates de Design Excellence.

---

## Workflow

1. **Analisar o Pedido**: Entender escopo (ex: "Perfil de usuário com formulário de edição").
2. **Verificar Estrutura Real**: Localizar `modules/`, `routes/` e arquivos de rota existentes.
3. **Planejar a Hierarquia Visual**: Antes de escrever código, definir:
   - Qual é o elemento **hero** da tela? (título, imagem, dado principal)
   - Quais são as **seções** principais?
   - Quais são os **detalhes/metadados**?
4. **Gerar os 4 Arquivos**: View, Controller, Binding e (opcional) Repository.
5. **Registrar a Rota**: Adicionar em `AppPages` e `Routes`.
6. **Aplicar o `flutter_design`**: Enforçar tokens + Modern UI Excellence na View e em todos os novos widgets.
7. **Executar Quality Gates**: Completar ambos os checklists (`generate-feature` + `flutter_design`) antes de entregar.

---

## Standard Structure (GetX Pattern)

Para um feature chamado `[feature_name]` (snake_case):

### 1. View (`[modules_path]/[feature_name]/views/[feature_name]_view.dart`)
- Extends `GetView<[FeatureName]Controller>`.
- **NÃO** usar `Scaffold` vazio — definir AppBar com identidade visual.
- Body com padding mínimo de 16px e estrutura hierárquica.
- Usa tokens de tema (`colorScheme`, `textTheme`), nunca valores hardcoded.
- Tem tratamento de **loading** e **empty state** dignos.

### 2. Controller (`[modules_path]/[feature_name]/controllers/[feature_name]_controller.dart`)
- Extends `GetxController`.
- Define estado reativo (`.obs`).
- Implementa `onInit` e `onReady`.
- Inclui estado de loading (`isLoading.obs`) para feedback visual.

### 3. Binding (`[modules_path]/[feature_name]/bindings/[feature_name]_binding.dart`)
- Extends `Bindings`.
- Usa `Get.lazyPut` para o Controller.
- Registra Repositories/Providers necessários.

### 4. Repository (Opcional) (`[modules_path]/[feature_name]/data/...`)
- Se houver busca de dados, criar interface e implementação.

---

## Step-by-Step Instructions

### Step 1: Verificar e Criar o Diretório do Feature

```
1. Localizar a pasta modules/ real do projeto (lib/modules/ ou lib/app/modules/)
2. Criar [modules_path]/[feature_name]/ com subpastas: views/, controllers/, bindings/
```

### Step 2: Criar o Controller

Incluir variáveis de estado básicas + estado de loading.

```dart
class [FeatureName]Controller extends GetxController {
  final isLoading = false.obs;
  // ... outros estados reativos

  @override
  void onInit() {
    super.onInit();
    _loadData();
  }

  Future<void> _loadData() async {
    isLoading.value = true;
    try {
      // lógica de carregamento
    } finally {
      isLoading.value = false;
    }
  }
}
```

### Step 3: Criar o Binding

```dart
class [FeatureName]Binding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<[FeatureName]Controller>(() => [FeatureName]Controller());
  }
}
```

### Step 4: Criar a View com UI Premium

A View **deve** seguir os princípios do `flutter_design`. Template mínimo:

```dart
class [FeatureName]View extends GetView<[FeatureName]Controller> {
  const [FeatureName]View({super.key});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;

    return Scaffold(
      backgroundColor: colorScheme.surface,
      appBar: AppBar(
        title: Text(
          '[Título da Tela]',
          style: textTheme.titleLarge?.copyWith(
            color: colorScheme.primary,
            fontWeight: FontWeight.w600,
          ),
        ),
        centerTitle: false,
        elevation: 0,
        scrolledUnderElevation: 1,
        backgroundColor: colorScheme.surface,
        surfaceTintColor: colorScheme.primary,
      ),
      body: Obx(
        () => controller.isLoading.value
            ? const _LoadingState()
            : const _ContentBody(),
      ),
    );
  }
}

// Extrair partes em StatelessWidgets separados:
class _LoadingState extends StatelessWidget {
  const _LoadingState();
  @override
  Widget build(BuildContext context) {
    return const Center(child: CircularProgressIndicator());
    // Idealmente: skeleton/shimmer screen
  }
}

class _ContentBody extends StatelessWidget {
  const _ContentBody();
  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Hero element
          // Seções com Card e borderRadius >= 12
          // Gaps entre seções de 24px
        ],
      ),
    );
  }
}
```

### Step 5: Registrar a Rota

1. **Routes** (`app_routes.dart`):
   ```dart
   static const [FEATURE_NAME] = '/[feature-name]';
   ```
2. **AppPages** (`app_pages.dart`):
   ```dart
   GetPage(
     name: _Paths.[FEATURE_NAME],
     page: () => const [FeatureName]View(),
     binding: [FeatureName]Binding(),
   ),
   ```

---

## Quality Checklist

**Arquitetura:**
- [ ] View extends `GetView`.
- [ ] Controller tem `onInit` e estado de `isLoading`.
- [ ] Binding usa `lazyPut`.
- [ ] Rota registrada em `AppPages`.
- [ ] Imports limpos (relativos ou package).

**Design (flutter_design Quality Gates aplicados):**
- [ ] Zero valores hardcoded de cor, font-size ou spacing.
- [ ] `.withValues(alpha:)` usado (nunca `.withOpacity()`).
- [ ] AppBar com título estilizado via `textTheme` e `colorScheme`.
- [ ] Hierarquia visual clara (hero → seção → detalhe).
- [ ] Cards/containers com `borderRadius` ≥ 12 e elevação ou sombra sutil.
- [ ] Padding lateral mínimo de 16px, gaps entre seções mínimo de 24px.
- [ ] Estado de loading com feedback visual adequado (não spinner solto).
- [ ] Estado vazio com ícone + texto orientativo (se aplicável).
- [ ] Elementos interativos com splash/highlight coloridos via tema.
- [ ] Partes da UI extraídas em `StatelessWidget` (sem métodos `_buildXxx()`).
- [ ] `Obx` somente no leaf-node de mutação.
- [ ] `const` em todos os widgets imutáveis.

## Example Command
`Executing @[/generate-feature] "products_list"`
