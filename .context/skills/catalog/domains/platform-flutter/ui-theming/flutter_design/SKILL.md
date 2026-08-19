---
name: flutter_design
description: Agnostic, production-grade Flutter design skill. Enforces modern UI/UX excellence, atomic design tokens (Spacing, Colors, Typography), FlexColorScheme, GetX reactive state, and strict anti-hardcoding rules. Produces premium, visually distinctive interfaces.
version: 4.0.0
updated: 2026-02-23
tags: [flutter, design, theme, tokens, getx, flexcolorscheme, modern-ui, premium]
difficulty: advanced
estimated_time: 15-20min
author: antigravity-core + rabelo-standards
framework: flutter
type: architecture
---

# 🎭 Flutter Design Skill (Universal + Modern + Strict)

**OBJETIVO**: Produzir UI Flutter **visualmente premium e moderna**, usando FlexColorScheme, tokens atômicos de design e GetX — proibindo absolutamente valores hardcoded e entregando interfaces que surpreendem ao primeiro olhar.

> ⚠️ **Regra de Ouro**: UI correta mas visualmente genérica é **FALHA**. O resultado deve parecer produzido por um designer profissional, não por um template.

---

## 📋 PROTOCOLO DE ORQUESTRAÇÃO

### 1️⃣ Detecção de Intenção

| Intenção             | Gatilhos                                | Ação                                                      |
| -------------------- | --------------------------------------- | --------------------------------------------------------- |
| **NOVA_TELA**        | "criar tela", "criar widget"            | Pre-Check → Definir hierarquia visual → Gerar UI premium  |
| **CUSTOMIZAR_THEME** | "mudar cor", "trocar fonte"             | Atualizar `theme_config.dart` ou tokens                   |
| **MELHORAR_UI**      | "melhorar", "premium", "modernizar"     | Avaliar atomic tokens → Aplicar padrões de design moderno |
| **MIGRAÇÃO**         | "limpar cores", "tirar constants"       | Substituir `Colors.*` por `Theme.of()...`                 |

### 2️⃣ Pre-Check Obrigatório

Antes de criar qualquer UI:

1. **Verificar** arquivos base do design system (`theme_config.dart`, `spacing.dart`, etc.).
2. **Ler** os tokens disponíveis na paleta semântica do projeto.
3. **Definir** a hierarquia visual da tela (hero, seção, item, detalhe).
4. **Aplicar** tokens consistentemente via `Theme.of(context)` ou classes utilitárias.
5. NUNCA usar literais de cor, tamanho ou font hardcoded.

---

## 🎨 DESIGN TOKEN SYSTEM (MANDATÓRIO)

### 1. Cores Semânticas (FlexColorScheme)

| Uso                     | Token Recomendado                                   | ❌ Absolutamente Proibido  |
| ----------------------- | --------------------------------------------------- | -------------------------- |
| Fundo Principal         | `Theme.of(context).colorScheme.surface`             | `Colors.white`, `Color(X)` |
| Fundo de Cartões/Chips  | `Theme.of(context).colorScheme.surfaceContainer`    | `Colors.grey.shade100`     |
| Marcação Principal      | `Theme.of(context).colorScheme.primary`             | `Colors.blue`              |
| Acionamentos/Destaques  | `Theme.of(context).colorScheme.secondary`           | `Colors.amber`             |
| Texto Primário          | `Theme.of(context).colorScheme.onSurface`           | `Colors.black87`           |
| Status Sucesso/Teste    | `Theme.of(context).colorScheme.tertiary`            | `Colors.green`             |
| Texto Secundário (Hint) | `Theme.of(context).colorScheme.onSurfaceVariant`    | `Colors.grey`              |
| Bordas / Linhas sutis   | `Theme.of(context).dividerColor` / `outlineVariant` | `Colors.black12`           |

### 2. Typography (CRÍTICO)

Evite `TextStyle` com tamanho fixo. Use sempre a hierarquia textual do tema.

| Nível             | Token Material 3                       | ❌ Proibido               |
| ----------------- | -------------------------------------- | ------------------------- |
| Display / Hero    | `context.textTheme.displayMedium`      | `TextStyle(fontSize: 40)` |
| Título de Tela    | `context.textTheme.headlineMedium`     | `TextStyle(fontSize: 24)` |
| Subtítulo         | `context.textTheme.titleMedium`        | `TextStyle(fontSize: 18)` |
| Corpo de Texto    | `context.textTheme.bodyMedium`         | `TextStyle(fontSize: 14)` |
| Label / Caption   | `context.textTheme.labelMedium`        | `TextStyle(fontSize: 12)` |
| **Texto Custom**  | Utilitário local do projeto (se existir) | Estilos soltos no widget  |

### 3. Spacing e BorderRadius

Padronização elimina 'magic numbers'. Use o sistema de spacing do projeto (se existir) ou múltiplos de 4:

```dart
// Sistema de referência (adapte ao que o projeto já fornece):
// xs = 4  | sm = 8  | md = 16  | lg = 24  | xl = 32  | xxl = 48

// Radius padronizados:
// sm = 8  | md = 12  | lg = 16  | xl = 24  | pill = 999

// ❌ NUNCA:
padding: EdgeInsets.all(15)
borderRadius: BorderRadius.circular(7)

// ✅ SEMPRE (usando o sistema do projeto ou múltiplos de 4):
padding: EdgeInsets.all(16)          // md
borderRadius: BorderRadius.circular(12)  // md
```

### 4. Opacity (CRÍTICO — SDK atualizado)

```dart
// ❌ NUNCA use (deprecated)
color.withOpacity(0.5)

// ✅ SEMPRE use
color.withValues(alpha: 0.5)
```

---

## ✨ MODERN UI EXCELLENCE

Esta seção define o **padrão mínimo de qualidade visual** para qualquer tela gerada. UI genérica é inaceitável.

### Princípio 1 — Hierarquia Visual Clara

Toda tela deve ter **3 níveis de hierarquia** explícitos:

```
Hero / Destaque principal   → maior peso visual, cor primária
  └── Seções / Cards        → peso médio, superfície elevada
        └── Detalhes        → menor peso, onSurfaceVariant
```

### Princípio 2 — Cards com Profundidade

Cards nunca devem ser planos e sem elevação em telas modernas.

```dart
// ✅ Card com elevação e radius adequados
Card(
  elevation: 0,
  shape: RoundedRectangleBorder(
    borderRadius: BorderRadius.circular(16),
  ),
  color: Theme.of(context).colorScheme.surfaceContainer,
  child: Padding(
    padding: const EdgeInsets.all(16),
    child: ...,
  ),
)

// ❌ EVITAR: Card plano sem radius
Card(child: ListTile(...))
```

Para sombra customizada premium:

```dart
DecoratedBox(
  decoration: BoxDecoration(
    color: Theme.of(context).colorScheme.surface,
    borderRadius: BorderRadius.circular(16),
    boxShadow: [
      BoxShadow(
        color: Theme.of(context).colorScheme.shadow.withValues(alpha: 0.08),
        blurRadius: 12,
        offset: const Offset(0, 4),
      ),
    ],
  ),
  child: ...,
)
```

### Princípio 3 — Espaçamento Generoso

Interfaces apertadas parecem amadores. Regra mínima:

| Elemento                         | Espaçamento mínimo |
| -------------------------------- | ------------------ |
| Padding de tela (lateral)        | 16px               |
| Padding de tela (top/bottom)     | 20px               |
| Gap entre itens de lista         | 8px                |
| Gap entre seções                 | 24px               |
| Padding interno de card/chip     | 12–16px            |

### Princípio 4 — Micro-interações e Feedback Visual

Todo elemento interativo deve fornecer feedback perceptível:

```dart
// ✅ InkWell com splash e highlight colorido
InkWell(
  onTap: () {},
  borderRadius: BorderRadius.circular(12),
  splashColor: Theme.of(context).colorScheme.primary.withValues(alpha: 0.12),
  highlightColor: Theme.of(context).colorScheme.primary.withValues(alpha: 0.06),
  child: ...,
)

// ✅ AnimatedContainer para transições de estado
AnimatedContainer(
  duration: const Duration(milliseconds: 200),
  curve: Curves.easeOut,
  decoration: BoxDecoration(
    color: isSelected
        ? colorScheme.primaryContainer
        : colorScheme.surfaceContainer,
    borderRadius: BorderRadius.circular(12),
  ),
  child: ...,
)
```

### Princípio 5 — Empty States e Loading com Dignidade

Nunca exibir tela vazia ou spinner solto sem contexto visual.

```dart
// ✅ Loading — usar shimmer ou placeholder estruturado
// (adaptar à lib de shimmer ou skeleton do projeto)

// ✅ Empty state com ícone + texto orientativo
Column(
  mainAxisAlignment: MainAxisAlignment.center,
  children: [
    Icon(
      Icons.inbox_outlined,
      size: 64,
      color: Theme.of(context).colorScheme.onSurfaceVariant.withValues(alpha: 0.4),
    ),
    const SizedBox(height: 16),
    Text(
      'Nenhum item encontrado',
      style: context.textTheme.titleMedium?.copyWith(
        color: Theme.of(context).colorScheme.onSurfaceVariant,
      ),
    ),
    const SizedBox(height: 8),
    Text(
      'Tente ajustar os filtros ou adicione um novo item.',
      style: context.textTheme.bodySmall?.copyWith(
        color: Theme.of(context).colorScheme.outline,
      ),
      textAlign: TextAlign.center,
    ),
  ],
)

// ❌ NUNCA:
if (loading) CircularProgressIndicator()
if (list.isEmpty) Text('Vazio')
```

### Princípio 6 — AppBar e Navegação com Identidade

```dart
// ✅ AppBar com identidade visual
AppBar(
  title: Text(
    'Título da Tela',
    style: context.textTheme.titleLarge?.copyWith(
      color: Theme.of(context).colorScheme.primary,
      fontWeight: FontWeight.w600,
    ),
  ),
  centerTitle: false,           // mais moderno que centralizado
  elevation: 0,
  scrolledUnderElevation: 1,    // elevação sutil no scroll
  backgroundColor: Theme.of(context).colorScheme.surface,
  surfaceTintColor: Theme.of(context).colorScheme.primary,
)

// ❌ AppBar genérica sem estilo
AppBar(title: Text('Título'))
```

### Princípio 7 — Botões com Peso Visual Correto

| Ação                   | Widget Correto     | Quando usar                         |
| ---------------------- | ------------------ | ----------------------------------- |
| Ação principal única   | `FilledButton`     | CTA primário, confirmações          |
| Ação secundária        | `OutlinedButton`   | Cancelar, opções alternativas       |
| Ação terciária/inline  | `TextButton`       | Links, ações dentro de listas       |
| Ação flutuante global  | `FloatingActionButton` | Criar/adicionar (uso restrito)  |

```dart
// ✅ Botão primário com padding generoso
FilledButton(
  onPressed: () {},
  style: FilledButton.styleFrom(
    minimumSize: const Size.fromHeight(48), // altura confortável
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(12),
    ),
  ),
  child: const Text('Confirmar'),
)
```

### Princípio 8 — Chips e Tags

```dart
// ✅ Chip bem estilizado (filtros/categorias)
FilterChip(
  label: Text(label),
  selected: isSelected,
  onSelected: (_) {},
  shape: RoundedRectangleBorder(
    borderRadius: BorderRadius.circular(8),
  ),
  selectedColor: Theme.of(context).colorScheme.primaryContainer,
  checkmarkColor: Theme.of(context).colorScheme.primary,
)
```

### Princípio 9 — Gradients (uso moderado e intencional)

Use gradientes apenas para heroes, banners ou separação visual de seções — nunca como background de tela inteira.

```dart
// ✅ Gradiente em header/banner
DecoratedBox(
  decoration: BoxDecoration(
    gradient: LinearGradient(
      begin: Alignment.topLeft,
      end: Alignment.bottomRight,
      colors: [
        Theme.of(context).colorScheme.primary,
        Theme.of(context).colorScheme.primaryContainer,
      ],
    ),
    borderRadius: BorderRadius.circular(16),
  ),
  child: ...,
)
```

### Princípio 10 — Divisores e Separadores

Substitua `Divider()` genérico por espaçamento intencional sempre que possível.

```dart
// ✅ Separação por espaço (preferido)
const SizedBox(height: 24)

// ✅ Divider só quando há separação semântica real
Divider(
  height: 1,
  thickness: 1,
  color: Theme.of(context).colorScheme.outlineVariant,
)

// ❌ Divider como "quebra de linha" genérica
Divider()
```

---

## 🏗️ PADRÕES DE WIDGET

### Decomposição Obrigatória

Componentize para isolar contexto e minimizar rebuilds.

```dart
// ❌ NUNCA: Métodos gigantes que retornam UI com estado complexo
Widget _buildHeader() {
  return Container(...);
}

// ✅ SEMPRE: Classes separadas e com `const`
class _FeatureHeader extends StatelessWidget {
  const _FeatureHeader();

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return DecoratedBox(
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainer,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Text('Header', style: Theme.of(context).textTheme.titleLarge),
      ),
    );
  }
}
```

### GetX State Management — Leaf-Node Pattern

```dart
// ❌ NUNCA: Obx englobando layout completo
Obx(() => ListView.builder(
  itemCount: controller.items.length,
  itemBuilder: (ctx, i) => ItemTile(controller.items[i]),
))

// ✅ SEMPRE: Obx apenas no ponto de mutação (Leaf-Node)
ListView.builder(
  itemCount: controller.items.length,
  itemBuilder: (ctx, i) => Obx(() => ItemTile(controller.items[i])),
)
```

### Uso Estrito de `const`

```dart
// ✅ Performance Default — qualquer widget imutável
const SizedBox(height: 16),
const Divider(),
const Icon(Icons.home),
const SizedBox.shrink(),
```

---

## ✅ QUALITY GATES (Checklist de Entrega)

Execute cada checagem antes de declarar a UI como concluída:

**Anti-Hardcoding:**
- [ ] Zero `Colors.*` hardcoded — todos substituídos por `Theme.of(context).colorScheme.*`
- [ ] Zero `TextStyle(fontSize: X)` solto — todos usando `textTheme.*` ou utilitário do projeto
- [ ] Zero `.withOpacity()` — substituído por `.withValues(alpha:)`
- [ ] Espaçamentos são múltiplos de 4 ou usam o sistema de spacing do projeto

**Estrutura:**
- [ ] Nenhum método `_buildXxx()` retornando widget com estado — extraído em `StatelessWidget`
- [ ] Todos os `const` possíveis aplicados
- [ ] `Obx` no menor nível possível (leaf-node)

**Design Excellence:**
- [ ] Tela tem hierarquia visual clara (3 níveis: hero → seção → detalhe)
- [ ] Cards/containers têm `borderRadius` ≥ 8 e elevação ou sombra sutil
- [ ] Espaçamentos laterais ≥ 16px, gaps entre seções ≥ 24px
- [ ] Elementos interativos têm feedback (splash/highlight/AnimatedContainer)
- [ ] Estado vazio e estado de loading têm tratamento visual digno
- [ ] AppBar tem título estilizado com `textTheme` e `colorScheme`
- [ ] Botões usam o tipo correto (Filled/Outlined/Text) para o peso da ação

---

## 📖 RECURSOS / ESTRUTURA RECOMENDADA

Busque ou crie no projeto:

- `theme_config.dart` / `app_theme.dart` — FlexColorScheme core + ColorScheme Light/Dark.
- `spacing.dart` — constantes de espaçamento (xs, sm, md, lg, xl).
- `text_styles.dart` / extensão de tipografia — métodos utilitários responsivos.
- `app_colors.dart` — paleta semântica nomeada (brand, accent, status).

---

> "Boa UI não deve conhecer seu provedor de cores — ela pergunta ao tema, e o tema provê o que o usuário escolheu. Boa UI também não pode ser genérica: ela deve surpreender."
