---
name: using-search-app-bar-page
description: Implements searchable list pages using the `search_app_bar_page` package with GetX reactive state management (`SearchAppBarPageObx`). Triggers include 'create search page', 'add search bar to list', 'implement SearchAppBarPageObx', 'build searchable screen'. Use when building pages that need a filterable/searchable list with an integrated AppBar search field.
version: 1.0.0
tags: [flutter, search, getx, search-app-bar, list, filtering]
difficulty: intermediate
estimated_time: 10min
---

# SearchAppBarPage with GetX Integration

## When to use this skill

- When building a new page that displays a searchable/filterable list of items
- When the user asks to "add search" to a list view or "create a search page"
- When implementing keyboard navigation (Up/Down arrows + Enter) on Web/Desktop
- When integrating `SearchAppBarPageObx` with a GetX controller (`GetxController` or `GetView`)

## Prerequisites

- `search_app_bar_page` package in `pubspec.yaml`
- GetX state management (`get` package)
- A data model class with a search method (e.g., `contemPalavra(String query)`)

## Dependencies

**Required:**

- `search_app_bar_page: ^latest` (pub.dev)
- `get: ^4.x` (GetX state management)

**Import:**

```dart
import 'package:search_app_bar_page/search_app_bar_page.dart';
import 'package:get/get.dart';
```

## Decision Tree: Which Widget to Use?

1. **Are you filtering data from an API or Database asynchronously?**
   - **YES** → Use `SearchAppBarPageVariableList<T>`.
   - **NO** (Full list in memory) → Go to step 2.

2. **Are you using GetX for State Management?**
   - **YES** → Use `SearchAppBarPageObx<T>` ← **This is our standard.**
   - **NO** → Use `SearchAppBarPage<T>`.

> **In this project (rede_alyne_flutter), always use `SearchAppBarPageObx` because we use GetX.**

## Instructions

### Step 1: Controller Setup

The controller MUST provide:

- An `RxList<T>` for the reactive data source
- A `GlobalKey<SearchAppBarPageState>` for programmatic search control (clear, etc.)
- An `RxString expandedTopicId` if using expansion/toggle behavior

**Use the base class `BaseProtocoloController` when dealing with protocol-like data:**

```dart
// File: lib/shared/controllers/base_protocolo_controller.dart
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:search_app_bar_page/search_app_bar_page.dart';

abstract class BaseProtocoloController extends GetxController {
  final RxList<TopicoProtocolo> topicosFiltrados = <TopicoProtocolo>[].obs;
  final Rx<String?> categoriaSelecionada = Rx<String?>(null);
  final ScrollController scrollController = ScrollController();
  final RxDouble scrollOffset = 0.0.obs;
  final RxString expandedTopicId = ''.obs;

  // KEY: This GlobalKey controls the search bar programmatically
  final GlobalKey<SearchAppBarPageState> navigatorKey =
      GlobalKey<SearchAppBarPageState>();

  void toggleExpandedTopic(String topicId) {
    if (expandedTopicId.value == topicId) {
      expandedTopicId.value = '';
    } else {
      expandedTopicId.value = topicId;
    }
  }

  // ... lifecycle methods and abstract methods
}
```

**For a custom controller (non-protocol data):**

```dart
class MySearchController extends GetxController {
  final RxList<MyModel> items = <MyModel>[].obs;
  final GlobalKey<SearchAppBarPageState> searchKey =
      GlobalKey<SearchAppBarPageState>();

  @override
  void onInit() {
    super.onInit();
    items.value = loadItems(); // populate your list
  }
}
```

### Step 2: View Implementation with `SearchAppBarPageObx`

The core widget replaces both `Scaffold` and `AppBar`. It provides:

- An integrated search field in the AppBar
- Reactive filtering via `whereFilter`
- Keyboard navigation via `onSubmit`, `onEnter`, and `highlightIndex`

**Complete Pattern (copy-paste ready):**

```dart
class MySearchPage extends GetView<MyController> {
  const MySearchPage({super.key});

  @override
  Widget build(BuildContext context) {
    return SearchAppBarPageObx<MyModel>(
      // ─── 1. REQUIRED: Data Binding ───
      globalKey: controller.searchKey,
      listRx: controller.items,

      // ─── 2. REQUIRED: Filter Logic ───
      // CRITICAL: Use whereFilter, NOT stringFilter
      whereFilter: (item, query) => item.contemPalavra(query ?? ''),

      // ─── 3. AppBar Configuration ───
      searchAppBarTitle: Text('Page Title'),
      searchAppBarCenterTitle: true,
      searchAppBarElevation: 0,
      searchAppBarBackgroundColor: Colors.transparent,
      searchAppBarModeSearchBackgroundColor: Colors.white,
      searchAppBarHintText: 'Buscar por palavra-chave...',

      // ─── 4. Theming (match project palette) ───
      magnifyGlassColor: AppColors.primary,
      searchAppBarElementsColor: AppColors.primary,
      searchTextColor: AppColors.primary,
      searchAppBarIconTheme: const IconThemeData(color: AppColors.primary),
      extendBodyBehindAppBar: true,
      searchPageBackgroundColor: AppColors.petalLight,

      // ─── 5. AppBar Actions (optional) ───
      searchAppBarActions: [
        IconButton(
          icon: const Icon(Icons.info, color: AppColors.primary),
          onPressed: () { /* action */ },
          tooltip: 'Action tooltip',
        ),
      ],

      // ─── 6. Keyboard Navigation (recommended for Web/Desktop) ───
      onSubmit: (query, listFiltered, highLightIndex) {
        if (highLightIndex >= 0 && highLightIndex < listFiltered.length) {
          controller.toggleExpandedTopic(listFiltered[highLightIndex].id);
        }
      },
      onEnter: (listFull, highLightIndex) {
        if (highLightIndex >= 0 && highLightIndex < listFull.length) {
          controller.toggleExpandedTopic(listFull[highLightIndex].id);
        }
      },

      // ─── 7. REQUIRED: List Builder ───
      // Use obxListBuilder (NOT body) for access to highlightIndex
      obxListBuilder: (context, foundList, isModSearch, highlight) {
        return foundList.isEmpty
            ? Center(child: Text('Nenhum item encontrado'))
            : ListView.builder(
                padding: const EdgeInsets.only(
                    top: 8, bottom: 80, left: 16, right: 16),
                itemCount: foundList.length,
                itemBuilder: (context, index) {
                  return MyItemWidget(
                    item: foundList[index],
                    isHighlighted: index == highlight,
                  );
                },
              );
      },
    );
  }
}
```

### Step 3: Programmatic Search Control

Use `navigatorKey.currentState` to control search from outside (e.g., filter chips):

```dart
// Clear search when changing filters
controller.navigatorKey.currentState?.clearSearch();
```

This is especially important when combining category filters with the search bar.

## Configuration Cheat Sheet

| Parameter                       | Function               | Notes                                                |
| :------------------------------ | :--------------------- | :--------------------------------------------------- |
| **`listRx`**                    | Reactive data source   | Pass `RxList<T>` directly                            |
| **`whereFilter`**               | Filtering logic        | **Mandatory**. Use this, NOT `stringFilter`          |
| **`globalKey`**                 | Programmatic control   | Type: `GlobalKey<SearchAppBarPageState>`             |
| **`searchAppBarTitle`**         | AppBar title widget    | Replaces standard `title`                            |
| **`searchAppBarActions`**       | AppBar action buttons  | Replaces standard `actions`                          |
| **`obxListBuilder`**            | Custom list builder    | Signature includes `highlightIndex` for keyboard nav |
| **`onSubmit`**                  | Enter key (with query) | Fired when typing + Enter. Access `highLightIndex`   |
| **`onEnter`**                   | Enter key (no query)   | Fired when Enter pressed without search text         |
| **`extendBodyBehindAppBar`**    | Transparent AppBar     | Set `true` for gradient backgrounds                  |
| **`searchPageBackgroundColor`** | Page background        | Use project background color                         |
| **`magnifyGlassColor`**         | Search icon color      | Match project theme                                  |
| **`searchAppBarElementsColor`** | AppBar elements        | Back button, close button color                      |
| **`searchTextColor`**           | Search input text      | Color of typed search text                           |
| **`searchAppBarHintText`**      | Placeholder text       | Shown when search field is empty                     |

## Common Pitfalls

### ❌ Using `stringFilter` instead of `whereFilter`

```dart
// WRONG - stringFilter is limited
stringFilter: (item) => item.name,

// CORRECT - whereFilter gives full control
whereFilter: (item, query) => item.contemPalavra(query ?? ''),
```

### ❌ Using `body` instead of `obxListBuilder`

```dart
// WRONG - body does NOT provide highlightIndex
body: (context, list, index) { ... },

// CORRECT - obxListBuilder provides highlightIndex for keyboard navigation
obxListBuilder: (context, foundList, isModSearch, highlight) { ... },
```

### ❌ Forgetting to guard `highLightIndex` bounds

```dart
// WRONG - may crash with index out of range
controller.doSomething(list[highLightIndex]);

// CORRECT - always check bounds
if (highLightIndex >= 0 && highLightIndex < list.length) {
  controller.doSomething(list[highLightIndex]);
}
```

### ❌ Not clearing search when changing category filters

```dart
// WRONG - search query persists after filter change, causing confusion
controller.filtrarPorCategoria(categoria);

// CORRECT - clear search when changing filters
controller.filtrarPorCategoria(categoria);
controller.navigatorKey.currentState?.clearSearch();
```

## Project-Specific Patterns

### Highlight + Auto-Scroll Pattern

When using `ExpansionTile` items with keyboard navigation, combine `highlightIndex` with `Scrollable.ensureVisible`:

```dart
class MyItemWidget extends StatefulWidget {
  final bool isHighlighted;
  // ...

  @override
  void didUpdateWidget(covariant MyItemWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.isHighlighted && !oldWidget.isHighlighted) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) {
          Scrollable.ensureVisible(
            context,
            alignment: 0.5,
            duration: const Duration(milliseconds: 300),
            curve: Curves.easeInOut,
          );
        }
      });
    }
  }
}
```

### Reactive Expansion Control Pattern

Track which item is expanded via the controller and react with `ExpansibleController`:

```dart
class _MyItemState extends State<MyItemWidget> {
  final ExpansibleController _expansionController = ExpansibleController();
  late Worker _expandedTracker;

  @override
  void initState() {
    super.initState();
    final controller = Get.find<MyController>();
    _expandedTracker = ever(controller.expandedTopicId, (String id) {
      if (id == widget.item.id) {
        if (!_expansionController.isExpanded) _expansionController.expand();
      } else {
        if (_expansionController.isExpanded) _expansionController.collapse();
      }
    });
  }

  @override
  void dispose() {
    _expandedTracker.dispose();
    super.dispose();
  }
}
```

## Real Project References

Working implementations in this project:

- `lib/modules/protocolo_pn/views/protocolo_pn_view.dart` → `ProtocoloPreNatalPage` (line ~363)
- `lib/modules/protocolo_pd/views/protocolo_pd_view.dart` → `ProtocoloPediatriaPage` (line ~377)
- `lib/shared/controllers/base_protocolo_controller.dart` → Base controller with `GlobalKey<SearchAppBarPageState>`

## Success Criteria

- `SearchAppBarPageObx` renders with integrated search bar
- Typing in search field filters the list reactively
- Up/Down arrow keys highlight items (Web/Desktop)
- Enter key triggers `onSubmit` / `onEnter` correctly
- Filter chips + search work together without conflicts
- No runtime errors on empty lists or out-of-bound indices

## Changelog

### v1.0.0 (2026-02-24)

- Initial release based on AI_USAGE_GUIDE.md from search_app_bar_page project
- Includes real implementation patterns from protocolo_pn and protocolo_pd modules
- Documents controller setup, view patterns, theming, and keyboard navigation
