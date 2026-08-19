---
name: flutter-design-principles
description: Flutter-first mobile design principles. Touch psychology, visual composition, domain-aware UX, performance rules, and platform conventions for Android/iOS, applied to Flutter widgets and GetX architecture. Prevents common AI-generated mobile anti-patterns.
version: 2.0.0
tags: [flutter, mobile-design, ux, performance, touch, platform, getx, visual-design, composition]
difficulty: intermediate
estimated_time: 10-15min
---

# Flutter Design Principles

> **Filosofia:** Touch-first. Battery-conscious. Platform-respectful. Visually coherent.
> **Princípio:** Mobile NÃO é um desktop menor. PENSE nas restrições do mobile E no domínio do usuário.

---

## When to use this skill

- Antes de criar qualquer nova tela ou widget Flutter
- Ao revisar código que implementa listas, animações ou gestos
- Quando o agente for ativado para tarefa de UI/UX Flutter
- Quando o usuário pedir: "criar tela", "componente", "layout", "UI", "design"

---

## 🧠 CHECKPOINT (Obrigatório Antes de Qualquer Código UI)

```
🧠 CHECKPOINT:

Plataforma:  [ Android / iOS / Ambas ]
Framework:   Flutter + GetX
Tela/Widget: [nome do que será criado]
Domínio:     [ SaaS/CRM / Consumer / Game / Outro ]

3 Princípios que Aplicarei:
1. _______________
2. _______________
3. _______________

Anti-Patterns que Evitarei:
1. _______________
2. _______________
```

> 🔴 Se não conseguir preencher o checkpoint, releia esta skill antes de codar.

---

## Design Philosophy & Domain Awareness

### Build with Empathy

- **Adapte o design ao domínio:** um app de gestão (SaaS, CRM, ERP) deve ser denso, utilitário e focado em trabalho — evite hero sections ilustradas, cards decorativos e layouts de marketing. Priorize informação organizada, navegação previsível e interfaces para scanning e ação repetida. Já um app consumer ou game pode ser mais expressivo, ilustrado e animado.
- **Pense no público-alvo:** quem vai usar? Com que frequência? Em que contexto? Isso decide layout, componentes, textos e padrões de interação.
- **Workflows comuns devem ser ergonômicos e eficientes:** o usuário deve navegar entre views sem atrito. Evite profundidade desnecessária para ações frequentes.

### First Screen Must Be Functional

```dart
// ❌ Errado: onboarding de 3 telas antes do app ser usável
class OnboardingPage extends StatelessWidget { ... } // 3 slides

// ✅ Correto: vai direto para a experiência funcional
class HomePage extends StatelessWidget { ... }
// Onboarding só se absolutamente necessário e skip-able
```

- **Não crie landing page/hero screen a menos que seja absolutamente necessário.**
- Quando pedido para criar um app ou ferramenta, a **primeira tela deve ser o produto usável**, não marketing ou conteúdo explicativo.

---

## Visual Composition & Layout Rules

### Cards & Containers

```dart
// ❌ Errado: card dentro de card
Card(
  child: Card(
    child: ListTile(...),
  ),
)

// ❌ Errado: página inteira estilizada como card flutuante
Scaffold(
  body: Card( // NUNCA
    margin: const EdgeInsets.all(16),
    child: Padding(...),
  ),
)

// ✅ Correto: seções são bandas de largura total ou layouts enquadrados
Scaffold(
  body: Container(
    padding: const EdgeInsets.all(16),
    color: Theme.of(context).colorScheme.surface,
    child: Column(...),
  ),
)

// ✅ Correto: cards APENAS para itens repetidos, modais e ferramentas genuinamente enquadradas
Card(
  shape: RoundedRectangleBorder(
    borderRadius: BorderRadius.circular(8), // ≤ 8px
  ),
  child: ListTile(...),
)
```

- **Cards são apenas para itens repetidos, modais e ferramentas genuinamente enquadradas.**
- **NÃO coloque cards dentro de outros cards.**
- **NÃO estilize seções de página como cards flutuantes.** Páginas devem ser bandas de largura total (`Container` com `color` do tema) ou layouts enquadrados com conteúdo interno limitado.
- **Border radius máximo de 8px** em cards, a menos que o design system existente exija outro valor.

### Decoration & Ornaments

```dart
// ❌ Errado: orbs/gradientes decorativos sem função
Container(
  decoration: const BoxDecoration(
    gradient: RadialGradient(
      colors: [Colors.purple, Colors.transparent],
    ),
  ),
)

// ✅ Correto: background limpo ou com propósito funcional
Container(
  color: Theme.of(context).colorScheme.surface,
)
```

- **NÃO adicione orbs, gradientes circulares decorativos ou bokeh blobs** como fundo ou enfeite.

### Layout Stability

```dart
// ❌ Errado: dimensões instáveis — loading pode redimensionar tudo
Column(
  children: [
    Text('Carregando...'), // pode quebrar linha e empurrar layout
    ElevatedButton(...),
  ],
)

// ✅ Correto: dimensões estáveis com constraints
ConstrainedBox(
  constraints: const BoxConstraints(minHeight: 48, maxHeight: 48),
  child: Center(child: CircularProgressIndicator()),
)
```

- Defina dimensões estáveis com constraints (`ConstrainedBox`, `AspectRatio`, `Expanded`, `Flexible`, `SizedBox`) para elementos de formato fixo: toolbars, icon buttons, counters, tiles, grids.
- Estados de hover, labels, ícones, peças, texto de loading ou conteúdo dinâmico **não podem redimensionar ou deslocar o layout**.

### Text Fit

```dart
// ❌ Errado: texto pode transbordar
Text('Título muito longo que não cabe no botão')

// ✅ Correto: garantir que texto caiba no elemento
FittedBox(
  fit: BoxFit.scaleDown,
  child: Text('Título muito longo que não cabe no botão'),
)

// ✅ Ou com constraints + ellipsis
Text(
  'Título muito longo que não cabe no botão',
  overflow: TextOverflow.ellipsis,
  maxLines: 1,
)
```

- **Texto deve caber dentro do elemento pai** em todos os viewports mobile.
- Se não couber, quebre linha; se ainda não couber, use `FittedBox`, `AutoSizeText` ou ellipsis.
- Texto **não pode sobrepor** conteúdo anterior ou subsequente de forma incoerente.

---

## Component Guidelines

### Choose the Right Widget for the Data

| Tipo de Dado / Ação | Widget Flutter | NUNCA Use |
| ------------------- | -------------- | --------- |
| Ferramenta / ação icônica | `IconButton`, `FloatingActionButton` | `TextButton` com texto longo |
| Modo / seleção única | `SegmentedButton`, `ToggleButtons` | `DropdownButton` para 2-3 opções |
| Configuração binária | `Switch`, `Checkbox`, `SwitchListTile` | `DropdownButton` para on/off |
| Valor numérico | `Slider`, `RangeSlider`, `TextField` (number) | `DropdownButton` para faixas |
| Conjunto de opções | `DropdownButton`, `PopupMenuButton`, `MenuAnchor` | 10 `RadioListTile` sem agrupamento |
| Navegação entre views | `TabBar` + `TabBarView`, `NavigationBar` | `Row` de `TextButton` como tabs |
| Comando claro | `ElevatedButton`, `TextButton`, `FilledButton` | `GestureDetector` em `Text` genérico |

```dart
// ❌ Errado: dropdown para booleano
DropdownButton<bool>(
  items: [
    DropdownMenuItem(value: true, child: Text('Ativo')),
    DropdownMenuItem(value: false, child: Text('Inativo')),
  ],
)

// ✅ Correto: switch para binário
SwitchListTile(
  title: const Text('Ativo'),
  value: isActive,
  onChanged: (v) => controller.setActive(v),
)
```

### Icons vs Text

```dart
// ❌ Errado: texto dentro de retângulo arredondado quando ícone familiar existe
ElevatedButton(
  onPressed: undo,
  child: const Text('Desfazer'),
)

// ✅ Correto: ícone familiar em botões de ferramenta
IconButton(
  icon: const Icon(Icons.undo),
  tooltip: 'Desfazer', // tooltip nomeia ícones não familiares
  onPressed: undo,
)

// ✅ Correto: ícone + texto para comandos claros
ElevatedButton.icon(
  onPressed: save,
  icon: const Icon(Icons.save),
  label: const Text('Salvar'),
)
```

- **Use ícones em botões para ferramentas** sempre que existir um símbolo familiar (ex: undo/redo, bold/italic, save/download/zoom).
- **Construa tooltips** (`Tooltip` widget) que nomeiam/descrevem ícones não familiares quando o usuário pressiona longo.
- **NÃO use retângulos arredondados com texto dentro** se puder usar um ícone familiar.
- Em Flutter, prefira **Material Icons** (Android) ou **Cupertino Icons** (iOS). Se houver uma biblioteca de ícones já configurada no projeto, use-a.

---

## Typography & Visual Hierarchy

### Match Display Text to Container

```dart
// ❌ Errado: headline grande dentro de card compacto
Card(
  child: Text(
    'Configurações',
    style: Theme.of(context).textTheme.headlineLarge, // MUITO grande
  ),
)

// ✅ Correto: tamanho proporcional ao container
Card(
  child: Padding(
    padding: const EdgeInsets.all(16),
    child: Text(
      'Configurações',
      style: Theme.of(context).textTheme.titleMedium, // adequado ao card
    ),
  ),
)
```

- **Reserve tipografia hero-scale para verdadeiros heroes.**
- Use headings menores e mais compactos dentro de panels, cards, sidebars, dashboards e superfícies de ferramenta.
- **NÃO escale tamanho de fonte com largura da tela.** Nunca use `MediaQuery.of(context).size.width * 0.05` como `fontSize`.
- **Letter spacing deve ser 0.** Não use `letterSpacing` negativo.

---

## Color & Assets

### Color Palette

```dart
// ❌ Errado: paleta monochromática — tudo em variações de roxo
ColorScheme.fromSeed(seedColor: Colors.deepPurple)
// Resultado: primary, secondary, tertiary todos no mesmo hue

// ✅ Correto: paleta com diversidade de hue
ColorScheme.fromSeed(
  seedColor: const Color(0xFF6750A4), // primary
  secondary: const Color(0xFF625B71),
  tertiary: const Color(0xFF7D5260),
  error: const Color(0xFFB3261E),
)
```

- **Evite paletas dominadas por variações de uma única família de cor.**
- Limite paletas dominadas por: roxo/roxo-azulado, bege/cream/areia/tan, azul escuro/slate, marrom/laranja/espresso.
- **Sempre use tokens do tema.** Nunca hardcode cores em widgets.

### Assets & Images

```dart
// ❌ Errado: ilustração SVG genérica quando foto real é possível
SvgPicture.asset('assets/generic_hero.svg')

// ✅ Correto: imagem real/produto quando o usuário precisa inspecionar
Image.asset('assets/product_photo.jpg')

// ✅ Correto: CachedNetworkImage para imagens remotas
CachedNetworkImage(
  imageUrl: product.imageUrl,
  placeholder: (context, url) => const CircularProgressIndicator(),
  errorWidget: (context, url, error) => const Icon(Icons.error),
)
```

- **Use imagens reais, de produto ou geradas** em vez de ilustrações genéricas ou SVGs decorativos, a menos que seja um game com assets altamente específicos.
- Imagens primárias devem revelar o produto, lugar, objeto, estado ou pessoa reais.
- **Evite imagens escuras, borradas, cortadas, stock-like ou puramente atmosféricas** quando o usuário precisa inspecionar a coisa real.
- Em Flutter: use `Image.asset` para locais, `CachedNetworkImage` para remotas, `SvgPicture` apenas para ícones técnicos ou ilustrações de interface.

---

## Touch Psychology (Obrigatório)

### Fitts' Law para Touch

```
Desktop: Cursor é preciso (1px)
Mobile:  Dedo é impreciso (~7mm de área de contato)

→ Touch targets DEVEM ser mínimo 44-48px
→ Ações importantes na THUMB ZONE (parte inferior)
→ Ações destrutivas LONGE do alcance fácil
```

### Thumb Zone (Uso com Uma Mão)

```
┌─────────────────────────────┐
│      DIFÍCIL DE ALCANÇAR    │ ← Navegação, menu, back
│        (esticar)            │
├─────────────────────────────┤
│      OK PARA ALCANÇAR       │ ← Ações secundárias
│        (natural)            │
├─────────────────────────────┤
│      FÁCIL DE ALCANÇAR      │ ← CTAs primários, tab bar
│    (arco natural do polegar)│ ← Interações principais
└─────────────────────────────┘
        [  HOME  ]
```

**Em Flutter:** Use `BottomNavigationBar` e `FloatingActionButton` para ações primárias (zona de fácil alcance).

---

## Tamanhos Mínimos de Target

| Plataforma | Mínimo      | Em Flutter                         |
| ---------- | ----------- | ---------------------------------- |
| iOS        | 44pt × 44pt | `SizedBox(width: 44, height: 44)`  |
| Android    | 48dp × 48dp | `SizedBox(width: 48, height: 48)`  |
| Universal  | 48pt/dp     | Use este valor para cross-platform |

```dart
// ❌ Errado: target muito pequeno
IconButton(
  icon: const Icon(Icons.close, size: 16),
  onPressed: onClose,
)

// ✅ Correto: target adequado
IconButton(
  icon: const Icon(Icons.close),
  iconSize: 24,
  padding: const EdgeInsets.all(12), // 24 + 12*2 = 48px total
  onPressed: onClose,
)
```

---

## Anti-Patterns de Performance (NUNCA FAÇA)

### Listas

| ❌ NUNCA                                   | Por Que é Errado                          | ✅ SEMPRE             |
| ------------------------------------------ | ----------------------------------------- | --------------------- |
| `SingleChildScrollView` para listas longas | Renderiza TODOS os itens, memória explode | `ListView.builder`    |
| Widget não-const em lista                  | Regenera a cada rebuild                   | `const` constructors  |
| `ScrollView` com `Column` para > 20 itens  | Mesma razão do item acima                 | `ListView.builder`    |
| Lógica pesada no `build()`                 | Executa a cada rebuild                    | Mover para controller |

```dart
// ❌ Errado
SingleChildScrollView(
  child: Column(
    children: items.map((item) => ItemWidget(item: item)).toList(),
  ),
)

// ✅ Correto
ListView.builder(
  itemCount: items.length,
  itemBuilder: (context, index) => ItemWidget(
    key: ValueKey(items[index].id), // Stable key
    item: items[index],
  ),
)
```

### Rebuilds desnecessários

```dart
// ❌ Errado: widget inteiro rebuilda por causa de ONE value
Obx(() => Column(
  children: [
    Header(), // Rebuilda sem necessidade
    Text(controller.counter.value.toString()),
    Footer(), // Rebuilda sem necessidade
  ],
))

// ✅ Correto: Obx no menor widget possível
Column(
  children: [
    const Header(),
    Obx(() => Text(controller.counter.value.toString())),
    const Footer(),
  ],
)
```

### Animações

```dart
// Transformações GPU-aceleradas (RÁPIDAS):
// ✅ transform, opacity

// ❌ Animar estas propriedades (CPU-bound, LENTO):
// width, height, top, left, right, bottom, margin, padding
AnimatedContainer(
  duration: const Duration(milliseconds: 300),
  // ❌ Evite animar tamanho assim — use Transform.scale
  width: isExpanded ? 200 : 100,
)

// ✅ Prefira:
AnimatedOpacity(
  duration: const Duration(milliseconds: 300),
  opacity: isVisible ? 1.0 : 0.0,
  child: widget,
)
```

---

## Anti-Patterns de UX (NUNCA FAÇA)

| ❌ NUNCA                        | Por Que é Errado                | ✅ SEMPRE                              |
| ------------------------------- | ------------------------------- | -------------------------------------- |
| Sem estado de loading           | Usuário pensa que app travou    | Mostrar `CircularProgressIndicator`    |
| Sem estado de erro              | Usuário fica preso, sem saída   | Mostrar erro + botão retry             |
| Sem estado vazio                | Tela em branco confunde         | Ilustração/mensagem + CTA              |
| Sem feedback de tap             | Ação não confirmada visualmente | `InkWell`, `ElevatedButton` com splash |
| Ação destrutiva sem confirmação | Delete acidental                | `AlertDialog` de confirmação           |
| Texto muito pequeno             | Ilegível em telas pequenas      | Mínimo 14sp para corpo                 |

```dart
// ✅ Todos os estados cobertos
Obx(() {
  if (controller.isLoading.value) {
    return const Center(child: CircularProgressIndicator());
  }
  if (controller.error.value.isNotEmpty) {
    return ErrorView(
      message: controller.error.value,
      onRetry: controller.loadData,
    );
  }
  if (controller.items.isEmpty) {
    return const EmptyStateView(message: 'Nenhum item encontrado');
  }
  return ListView.builder(
    itemCount: controller.items.length,
    itemBuilder: (_, i) => ItemWidget(item: controller.items[i]),
  );
});
```

---

## Anti-Patterns de Segurança Mobile

| ❌ NUNCA                         | Por Que é Errado                    | ✅ SEMPRE                             |
| -------------------------------- | ----------------------------------- | ------------------------------------- |
| Token em `SharedPreferences`     | Acessível em dispositivos rooteados | `flutter_secure_storage`              |
| API key hardcoded no código Dart | Visível no APK decompilado          | `--dart-define` + CI secrets          |
| Log de dados sensíveis           | Logs extraíveis                     | Verificar o que vai para `debugPrint` |
| HTTP sem TLS em produção         | MITM attacks                        | HTTPS obrigatório                     |

```dart
// ❌ Errado
SharedPreferences prefs = await SharedPreferences.getInstance();
prefs.setString('auth_token', token); // Inseguro!

// ✅ Correto
final storage = const FlutterSecureStorage();
await storage.write(key: 'auth_token', value: token);
```

---

## Anti-Patterns de Arquitetura (GetX)

| ❌ NUNCA                                              | ✅ FAÇA                        |
| ----------------------------------------------------- | ------------------------------ |
| Business logic na View                                | Mover para Controller/Service  |
| `Get.put()` na View                                   | Usar `Bindings`                |
| Navegação com `Navigator.push` misturado com `Get.to` | Usar apenas `Get.to`           |
| Workers sem cancelamento no `onClose()`               | Sempre cancelar em `onClose()` |
| `Get.find()` sem binding configurado                  | Verificar binding antes        |
| Controller acessando outro Controller diretamente     | Usar Service intermediário     |

```dart
// ❌ Errado: sem cleanup
class UserController extends GetxController {
  late Worker _worker;

  @override
  void onInit() {
    super.onInit();
    _worker = ever(user, (_) => sendAnalytics());
    // onClose() não existe = memory leak
  }
}

// ✅ Correto: cleanup garantido
class UserController extends GetxController {
  late Worker _worker;

  @override
  void onInit() {
    super.onInit();
    _worker = ever(user, (_) => sendAnalytics());
  }

  @override
  void onClose() {
    _worker.dispose();
    super.onClose();
  }
}
```

---

## Platform Decisions (Android vs iOS)

| Elemento           | Android              | iOS                          |
| ------------------ | -------------------- | ---------------------------- |
| **Navegação back** | Botão sistema/gesto  | Edge swipe esquerda          |
| **Snackbar**       | `SnackBar` (bottom)  | Banner (top)                 |
| **Data Picker**    | Material date picker | `CupertinoDatePicker`        |
| **Progress**       | Linear progress      | `CupertinoActivityIndicator` |
| **Ícones**         | Material Icons       | Cupertino Icons              |

```dart
// Adaptação por plataforma
Widget buildBackButton() {
  if (Platform.isIOS) {
    return const CupertinoNavigationBarBackButton();
  }
  return const BackButton();
}
```

---

## Before Every Screen Checklist

- [ ] Touch targets ≥ 44-48px?
- [ ] Primary CTA na thumb zone?
- [ ] Estado de loading existe?
- [ ] Estado de erro com retry existe?
- [ ] Estado vazio tratado?
- [ ] `Obx` wrapping apenas o necessário?
- [ ] Workers/timers cancelados no `onClose()`?
- [ ] Cores usando tokens do tema (não hardcoded)?
- [ ] `const` em todos os widgets estáticos?
- [ ] Design adaptado ao domínio (SaaS vs consumer vs game)?
- [ ] Cards NÃO estão aninhados?
- [ ] Texto cabe no container sem overflow?
- [ ] Paleta com diversidade de hue (não monochromática)?
- [ ] Assets visuais são reais/produto (não genéricos)?
- [ ] Primeira tela é funcional (não landing/hero)?
- [ ] Widget correto para cada tipo de dado (toggle, slider, tab, dropdown)?
- [ ] Sem orbs/gradientes decorativos sem função?

---

## Related Skills

- `ui-theming` — Sistema de tema e tokens de cor
- `validating-flutter-projects` — Validação de projeto completo
- `reviewing-code-changes` — Flutter/GetX specific addons
- `clean-code` — Dart naming e estrutura de widgets
