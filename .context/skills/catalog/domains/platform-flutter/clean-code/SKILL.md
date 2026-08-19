---
name: clean-code-flutter
description: Adaptação da skill clean-code para o domínio platform-flutter. Aplica regras pragmáticas de Clean Code em Dart/Flutter (GetX), com foco em nomenclatura, estrutura, responsabilidades e qualidade contínua.
version: 1.0.0
tags: [platform-flutter, clean-code, dart, flutter, getx, code-quality]
priority: CRITICAL
---

# Clean Code para Platform Flutter

> Skill do domínio `platform-flutter` para reforçar práticas de Clean Code em tarefas Flutter.

## Fonte canônica das recomendações

As recomendações base são herdadas da skill:

- `skills/catalog/domains/code-quality/clean-code/SKILL.md`

Use essa referência como regra principal para nomenclatura, tamanho de funções, organização de código, anti-patterns e checklist final.

## Aplicação obrigatória em Flutter

Ao implementar no domínio Flutter, reforçar os pontos abaixo:

1. **Widgets imutáveis por padrão** (`const` e `final` sempre que possível).
2. **Obx mínimo** (observar apenas o menor subwidget necessário).
3. **Sem regras de negócio na UI** (controllers/services concentram lógica).
4. **Estados explícitos** (loading, empty, error, success).
5. **Sem valores hardcoded de tema** (usar tokens centralizados).

## Checklist rápido antes de finalizar

- [ ] Nomes claros e consistentes em Dart (`PascalCase`, `camelCase`, `snake_case`).
- [ ] Funções curtas e com responsabilidade única.
- [ ] Sem duplicação relevante (DRY).
- [ ] Código simples e direto (KISS/YAGNI).
- [ ] Sem anti-patterns de performance/UX comuns em Flutter.

Se qualquer item falhar, refatore antes de concluir.
