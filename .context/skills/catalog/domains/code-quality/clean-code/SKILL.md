---
name: clean-code
description: Pragmatic Dart/Flutter coding standards. Concise, direct, no over-engineering. Naming, function size, structure, and file-dependency rules. MANDATORY for every code task.
version: 1.0.0
tags: [code-quality, dart, flutter, naming, architecture, agnostic]
priority: CRITICAL
---

# Clean Code — Dart/Flutter Standards

> **CRITICAL SKILL** — Be concise, direct, and solution-focused. Applies to EVERY code task.

---

## Core Principles

| Principle     | Rule                                                         |
| ------------- | ------------------------------------------------------------ |
| **SRP**       | Single Responsibility — cada função/classe faz UMA coisa     |
| **DRY**       | Don't Repeat Yourself — extraia duplicação, reutilize        |
| **KISS**      | Keep It Simple — solução mais simples que funciona           |
| **YAGNI**     | You Aren't Gonna Need It — não construa features não pedidas |
| **Boy Scout** | Deixe o código mais limpo do que encontrou                   |

---

## Naming Rules (Dart)

| Elemento              | Convenção                         | Exemplo                                     |
| --------------------- | --------------------------------- | ------------------------------------------- |
| **Classes**           | PascalCase                        | `UserController`, `ThemeConfig`             |
| **Arquivos**          | snake_case                        | `user_controller.dart`, `theme_config.dart` |
| **Variáveis/funções** | camelCase + intenção              | `userCount`, `fetchUserById()`              |
| **Booleanos**         | Forma de pergunta                 | `isActive`, `hasPermission`, `canEdit`      |
| **Constantes**        | SCREAMING_SNAKE ou lowerCamelCase | `MAX_RETRY_COUNT` ou `defaultTimeout`       |
| **Privados**          | Prefixo `_`                       | `_controller`, `_buildCard()`               |

> **Regra:** Se você precisa de um comentário para explicar o nome, renomeie.

---

## Function Rules

| Regra                | Descrição                            |
| -------------------- | ------------------------------------ |
| **Pequena**          | Máx 20 linhas, ideal 5-10            |
| **Uma coisa**        | Faz uma coisa, faz bem               |
| **Poucos args**      | Máx 3 parâmetros, prefira 0-2        |
| **Sem side effects** | Não muta inputs inesperadamente      |
| **Guard Clauses**    | Retornos antecipados para edge cases |

```dart
// ❌ Errado: nesting profundo
Widget buildCard(User? user) {
  if (user != null) {
    if (user.isActive) {
      if (user.hasAvatar) {
        return Card(child: Avatar(url: user.avatarUrl));
      }
    }
  }
  return const SizedBox.shrink();
}

// ✅ Correto: guard clauses
Widget buildCard(User? user) {
  if (user == null) return const SizedBox.shrink();
  if (!user.isActive) return const SizedBox.shrink();
  if (!user.hasAvatar) return const SizedBox.shrink();
  return Card(child: Avatar(url: user.avatarUrl));
}
```

---

## Dart/Flutter Específico

| Regra                             | Razão                                           |
| --------------------------------- | ----------------------------------------------- |
| **`const` em widgets estáticos**  | Evita rebuilds desnecessários                   |
| **`final` sempre que possível**   | Imutabilidade por padrão                        |
| **`?` e `??` ao invés de `!`**    | Nunca force-unwrap sem certeza                  |
| **`late` com cautela**            | Apenas quando inicialização tardia é inevitável |
| **`extension` ao invés de utils** | Métodos de extensão são mais idiomáticos        |
| **Null safety completo**          | Sem `dynamic` sem justificativa                 |

```dart
// ❌ Errado
class MyWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        SizedBox(height: 16),
        Text('Título'),
        Icon(Icons.star),
      ],
    );
  }
}

// ✅ Correto
class MyWidget extends StatelessWidget {
  const MyWidget({super.key}); // const constructor

  @override
  Widget build(BuildContext context) {
    return const Column(
      children: [
        SizedBox(height: 16), // const implícito
        Text('Título'),
        Icon(Icons.star),
      ],
    );
  }
}
```

---

## GetX-Specific Rules

| Regra                                      | Descrição                                                  |
| ------------------------------------------ | ---------------------------------------------------------- |
| **`Obx` mínimo**                           | Wrapping do menor widget possível, nunca o Scaffold        |
| **Sem `setState` em Controller**           | Controllers = lógica, não UI                               |
| **`onClose()` obrigatório**                | Cancelar workers, streams e timers                         |
| **`Get.put` apenas em Binding**            | Nunca em View                                              |
| **Theme tokens**                           | Usar `MyThemeApp.*` / `AppColors.*`, nunca cores hardcoded |
| **`withValues(alpha:)` não `withOpacity`** | `withOpacity` está deprecated                              |

```dart
// ❌ Errado: Obx em torno de tudo
Obx(() => Scaffold(
  body: Column(children: [
    Text(controller.title.value),
    ElevatedButton(...),
  ]),
))

// ✅ Correto: Obx apenas onde muda
Scaffold(
  body: Column(children: [
    Obx(() => Text(controller.title.value)),
    ElevatedButton(...),
  ]),
)
```

---

## Code Structure

| Padrão                | Aplicar                                                         |
| --------------------- | --------------------------------------------------------------- |
| **Guard Clauses**     | Retornos antecipados para edge cases                            |
| **Flat > Nested**     | Evitar nesting profundo (máx 2 níveis)                          |
| **Composition**       | Widgets pequenos compostos                                      |
| **Colocation**        | Manter código relacionado próximo                               |
| **Feature structure** | `lib/modules/feature/` com bindings, controllers, views, models |

---

## AI Coding Style

| Situação             | Ação                  |
| -------------------- | --------------------- |
| Usuário pede feature | Escreva diretamente   |
| Usuário reporta bug  | Corrija, não explique |
| Sem requisito claro  | Pergunte, não assuma  |

---

## 🔴 Antes de Editar QUALQUER arquivo (PENSE PRIMEIRO)

| Pergunta                           | Por quê                    |
| ---------------------------------- | -------------------------- |
| **Quem importa este arquivo?**     | Pode quebrar dependentes   |
| **O que este arquivo importa?**    | Mudança de interface       |
| **Quais testes cobrem isso?**      | Testes podem falhar        |
| **É um componente compartilhado?** | Múltiplos lugares afetados |

> 🔴 **Regra:** Edite o arquivo + TODOS os dependentes na MESMA tarefa.
> 🔴 **Nunca deixe imports quebrados ou updates faltando.**

---

## Anti-Patterns (NÃO FAÇA)

| ❌ Padrão                     | ✅ Correção                   |
| ----------------------------- | ----------------------------- |
| Comentar cada linha           | Delete comentários óbvios     |
| Helper para one-liner         | Inline o código               |
| `print()` em produção         | Use `debugPrint()` ou remova  |
| Cores hardcoded               | Use tokens de tema            |
| `dynamic` sem justificativa   | Tipar corretamente            |
| Magic numbers                 | Constantes nomeadas           |
| God widget (500+ linhas)      | Dividir em subwidgets         |
| `!` (force unwrap)            | Use `?.`, `??` ou verificação |
| `setState` em GetX controller | Use `.value` ou `.update()`   |

---

## 🔴 Self-Check Antes de Concluir (OBRIGATÓRIO)

| Check                     | Pergunta                                  |
| ------------------------- | ----------------------------------------- |
| ✅ **Objetivo atingido?** | Fiz exatamente o que o usuário pediu?     |
| ✅ **Arquivos editados?** | Modifiquei todos os arquivos necessários? |
| ✅ **Código funciona?**   | Testei/verifiquei a mudança?              |
| ✅ **Sem erros?**         | `dart analyze` passa?                     |
| ✅ **Nada esquecido?**    | Edge cases cobertos?                      |

> 🔴 **Regra:** Se ALGUM check falhar, corrija antes de concluir.

---

## Validation Scripts

```bash
# Lint + análise estática
dart analyze .

# Formatação
dart format --set-exit-if-changed lib/

# Testes
flutter test
```

---

## Summary

| Faça                           | Não Faça                    |
| ------------------------------ | --------------------------- |
| Escreva código diretamente     | Escreva tutoriais           |
| Deixe código se autodocumentar | Adicione comentários óbvios |
| Corrija bugs imediatamente     | Explique o bug primeiro     |
| Use `const` onde possível      | Esqueça construtores const  |
| Nome revela intenção           | Use abreviações             |
| Funções pequenas               | Funções com 100+ linhas     |

> **O usuário quer código funcionando, não uma aula de programação.**
