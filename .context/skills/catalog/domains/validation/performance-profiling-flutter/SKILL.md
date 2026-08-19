---
name: performance-profiling-flutter
description: Flutter performance profiling and optimization. Identifies rebuild storms, memory leaks, jank, and web performance issues. Uses Flutter DevTools as primary tooling.
version: 1.0.0
tags:
  [performance, flutter, devtools, optimization, memory, rebuilds, web, dart]
difficulty: advanced
estimated_time: 15-30min
---

# Performance Profiling — Flutter

> Medir, analisar, otimizar — nessa ordem.
> **Nunca otimize sem medir primeiro.**

---

## When to use this skill

- Quando o app apresenta jank (animações não fluidas)
- Quando há lag/travamento durante scroll
- Quando memory usage cresce sem liberar (memory leak)
- Quando build times estão lentos
- Quando o usuário reporta: "app lento", "travando", "animation lag", "memória alta"

---

## Workflow de Profiling (4 Passos)

```
1. BASELINE  → Medir estado atual com Flutter DevTools
2. IDENTIFY  → Encontrar o gargalo (rebuild storm? jank? memory?)
3. FIX       → Mudança cirúrgica e pontual
4. VALIDATE  → Confirmar melhoria com nova medição
```

> ⚠️ NUNCA pule o passo 1. Sem baseline, não há como saber se o fix funcionou.

---

## Flutter DevTools — Setup

```bash
# Abrir DevTools (app rodando em debug mode)
flutter run
# No terminal, pressionar 'v' ou acessar a URL exibida

# Ou via VS Code: Ctrl+Shift+P → "Dart: Open DevTools"
# Ou via Android Studio: Flutter → Open DevTools
```

### Tabs Mais Importantes

| Tab                  | Quando Usar                                              |
| -------------------- | -------------------------------------------------------- |
| **Performance**      | Identificar jank, frame budget, UI thread vs Raster      |
| **Widget Inspector** | Ver árvore de widgets, encontrar rebuilds desnecessários |
| **Memory**           | Identificar memory leaks, ver alocações                  |
| **CPU Profiler**     | Ver qual código está consumindo CPU                      |

---

## 1. Identificar Rebuild Storms

### Via Widget Inspector

```bash
# No DevTools → Widget Inspector
# Ativar "Track Widget Rebuilds" (ícone de câmera)
# Widgets em VERMELHO = rebuilt frequentemente
```

### Via debugPrintRebuildDirtyWidgets

```dart
// main.dart — apenas em debug
import 'package:flutter/rendering.dart';

void main() {
  debugPrintRebuildDirtyWidgets = true; // Ver o que rebuilda
  runApp(const MyApp());
}
```

### Causas Comuns de Rebuild Storm

| Causa                                    | Exemplo                    | Fix                                    |
| ---------------------------------------- | -------------------------- | -------------------------------------- |
| `Obx` muito amplo                        | Wrapping o Scaffold        | Reduzir escopo do `Obx`                |
| `setState` em parent grande              | State no `_AppState`       | Extrair `StatefulWidget` menor         |
| Missing `const`                          | `Text('título')` sem const | Adicionar `const Text('título')`       |
| `context.watch` amplo                    | Watching model grande      | `context.select()` com seletor preciso |
| `ValueListenableBuilder` mal posicionado | Wrapping Column inteira    | Mover para o widget específico         |

```dart
// ❌ Rebuild storm: toda a Column rebuilda quando counter muda
class _MyPageState extends State<MyPage> {
  int counter = 0;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        ExpensiveHeader(), // rebuilda desnecessariamente!
        Text('$counter'),
        ExpensiveFooter(), // rebuilda desnecessariamente!
      ],
    );
  }
}

// ✅ Fix: extrair apenas o widget que muda
class MyPage extends StatelessWidget {
  const MyPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const Column(
      children: [
        ExpensiveHeader(), // const = nunca rebuilda
        CounterWidget(),   // apenas este rebuilda
        ExpensiveFooter(), // const = nunca rebuilda
      ],
    );
  }
}
```

---

## 2. Identificar e Corrigir Jank (60fps)

### Target de Performance

| Métrica           | Bom            | Ruim          |
| ----------------- | -------------- | ------------- |
| **Frame time**    | < 16ms (60fps) | > 16ms (jank) |
| **UI Thread**     | < 8ms          | > 8ms         |
| **Raster Thread** | < 8ms          | > 8ms         |

### Causas de Jank e Fixes

| Causa                              | Diagnóstico             | Fix                        |
| ---------------------------------- | ----------------------- | -------------------------- |
| **Listas sem builder**             | Lag no primeiro render  | `ListView.builder`         |
| **Imagens sem cache**              | Reblink de imagens      | `CachedNetworkImage`       |
| **Decodificação de imagem grande** | CPU spike no frame      | `precacheImage()` + resize |
| **Computação pesada no UI thread** | UI thread > 8ms         | `compute()` ou `Isolate`   |
| **Shader compilation**             | Primeiro frame lento    | Shader warmup              |
| **Rede síncrona**                  | Bloqueio do main thread | `async/await` corretos     |

```dart
// ❌ Computação pesada bloqueando UI
List<Verse> result = heavyTextProcessing(rawData); // bloqueia!

// ✅ Usar isolate via compute()
List<Verse> result = await compute(heavyTextProcessing, rawData);
```

### Animações — GPU vs CPU

```dart
// ✅ GPU-aceleradas (rápidas)
Transform.translate(offset: const Offset(x, y), child: widget)
Opacity(opacity: value, child: widget)
AnimatedOpacity(duration: ..., opacity: ..., child: ...)

// ❌ CPU-bound (evitar animar)
AnimatedContainer(
  width: value,    // ❌ Anima layout
  height: value,   // ❌ Anima layout
  padding: value,  // ❌ Anima layout
)

// ✅ Alternativa para escala
AnimatedScale(
  scale: isExpanded ? 1.2 : 1.0,
  duration: const Duration(milliseconds: 200),
  child: widget,
)
```

---

## 3. Memory Leaks — Diagnóstico e Fix

### Como Identificar no DevTools

1. DevTools → **Memory tab**
2. Clicar em "GC" (force garbage collection)
3. Navegar pelo app por ~5 minutos
4. Clicar em GC novamente
5. **Se heap não diminui → memory leak**

### Causas Mais Comuns em Flutter/GetX

| Causa                                 | Sintoma                   | Fix                                    |
| ------------------------------------- | ------------------------- | -------------------------------------- |
| **Worker não cancelado**              | Heap cresce com navegação | `worker.dispose()` em `onClose()`      |
| **StreamSubscription não cancelada**  | Listeners acumulam        | `subscription.cancel()` em `onClose()` |
| **Timer não cancelado**               | Callbacks pós-dispose     | `_timer.cancel()` em `onClose()`       |
| **AnimationController sem dispose**   | Animação continua ativa   | `_controller.dispose()` em `dispose()` |
| **FocusNode sem dispose**             | FocusNode fica na memória | `_focusNode.dispose()` em `dispose()`  |
| **TextEditingController sem dispose** | Controller persiste       | Sempre `.dispose()`                    |

```dart
// ✅ Template de GetX Controller com cleanup completo
class UserController extends GetxController {
  // Rx
  final users = <User>[].obs;
  final isLoading = false.obs;

  // Workers
  late Worker _userWatcher;

  // Streams
  StreamSubscription? _networkSub;

  // Timers
  Timer? _refreshTimer;

  @override
  void onInit() {
    super.onInit();
    _userWatcher = ever(users, _onUsersChanged);
    _networkSub = NetworkService.to.stream.listen(_onNetworkChange);
    _refreshTimer = Timer.periodic(
      const Duration(minutes: 5),
      (_) => _refresh(),
    );
  }

  @override
  void onClose() {
    _userWatcher.dispose();
    _networkSub?.cancel();
    _refreshTimer?.cancel();
    super.onClose();
  }
}
```

```dart
// ✅ Template de StatefulWidget com cleanup completo
class SearchWidget extends StatefulWidget { ... }

class _SearchWidgetState extends State<SearchWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _animController;
  late TextEditingController _textController;
  late FocusNode _focusNode;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(vsync: this, ...);
    _textController = TextEditingController();
    _focusNode = FocusNode();
  }

  @override
  void dispose() {
    _animController.dispose();
    _textController.dispose();
    _focusNode.dispose();
    super.dispose();
  }
}
```

---

## 4. Flutter Web — Performance

### Renderers

| Renderer                | Quando Usar                            | Trade-off               |
| ----------------------- | -------------------------------------- | ----------------------- |
| **CanvasKit** (default) | Pixel-perfect, custom UI               | Bundle maior (~2MB)     |
| **HTML**                | Conteúdo textual, SEO                  | Limitações de rendering |
| **Auto** (default web)  | Mobile usa HTML, desktop usa CanvasKit |                         |

```bash
# Escolher renderer no build
flutter build web --web-renderer canvaskit --release
flutter build web --web-renderer html --release
```

### Otimizações Web

```bash
# Tree shaking de fontes (reduz bundle)
flutter build web --release --tree-shake-icons

# Deferred loading (carregamento lazy de rotas)
# Configurar no main.dart com deferred imports
```

### Core Web Vitals Targets

| Métrica | Bom     | Ruim    | Mede                       |
| ------- | ------- | ------- | -------------------------- |
| **LCP** | < 2.5s  | > 4.0s  | Velocidade de carregamento |
| **INP** | < 200ms | > 500ms | Interatividade             |
| **CLS** | < 0.1   | > 0.25  | Estabilidade visual        |

---

## 5. Identificar Gargalos por Sintoma

| Sintoma              | Causa Provável                      | Ferramenta       |
| -------------------- | ----------------------------------- | ---------------- |
| Scroll lento         | Rebuild storm, listas sem builder   | Widget Inspector |
| Primeiro frame lento | Shader compilation, imagens pesadas | Performance tab  |
| Memória crescente    | Resource leak                       | Memory tab       |
| CPU alta constante   | Timer/Stream sem cleanup            | CPU Profiler     |
| App congelando       | Computação no UI thread             | Performance tab  |
| Imagens piscando     | Cache incorreto                     | Network tab      |

---

## Quick Wins (Impacto Alto, Esforço Baixo)

| Prioridade | Ação                                                                 | Impacto             |
| ---------- | -------------------------------------------------------------------- | ------------------- |
| 1          | Adicionar `const` em widgets estáticos                               | Elimina rebuilds    |
| 2          | Substituir `Column` + `SingleChildScrollView` por `ListView.builder` | Reduz memória       |
| 3          | Reduzir escopo de `Obx`                                              | Elimina rebuilds    |
| 4          | Adicionar `CachedNetworkImage`                                       | Elimina redownloads |
| 5          | Usar `compute()` para processamento pesado                           | Elimina jank        |
| 6          | Cancelar workers/subscriptions em `onClose()`                        | Elimina leaks       |

---

## Anti-Patterns

| ❌ Não Faça                         | ✅ Faça                                              |
| ----------------------------------- | ---------------------------------------------------- |
| Otimizar sem medir                  | Medir primeiro com DevTools                          |
| Micro-otimizar                      | Resolver o gargalo maior                             |
| `compute()` para tarefas simples    | `compute()` apenas para > 16ms                       |
| Ignorar testes flaky de performance | Investigar e corrigir                                |
| Profile em debug mode               | Sempre em **profile mode** (`flutter run --profile`) |

---

## Related Skills

- `flutter-design-principles` — Anti-patterns de performance em widgets
- `validating-flutter-projects` — Diagnóstico de rebuild storms e leaks
- `investigating-bugs` — Root cause analysis para regressions de performance
