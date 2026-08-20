# ADR 0001 — Condição de aplicação no campo obrigatório da tag SAC

- Status: accepted
- Date: 2026-08-20

## Decisão

A forma canônica é `SAC:<TAG>: on=<condition> - <Symbol>: <constraint>`. O campo obrigatório antes usado como severidade inerte passa a expressar a condição de aplicação, sem acrescentar campo ou alongar a linha. Assim, leitores sem ferramenta podem filtrar `SAC:` por `on=` com `grep` antes de ler constraints.

Para `ARCH`, o vocabulário é fechado e contém exatamente, nesta ordem: `ssot`, `boundary`, `ordering`, `state`, `exclusive`, `ownership`. Qualquer outro valor permanece parseável e visível, mas emite `invalid_trigger` com todo esse conjunto permitido.

Para `REGR` e `DEPRECATED`, a condição é um token livre validado exatamente por `[a-z][a-z0-9_]{2,47}`. Um valor inválido também permanece parseável e visível, com `invalid_trigger`.

## Compatibilidade

O parser dual tenta primeiro a forma canônica `on=<condition>` e depois o vocabulário anterior. `ARCH` com `RULE|CONSTRAINT` e `REGR`/`DEPRECATED` com `WARNING|CRITICAL` continuam parseáveis, preservando símbolo, constraint, `verify:` e `replacement:`. Essas tags legadas recebem condição vazia e `legacy_trigger`; as exigências existentes de `verify:` e `replacement:` continuam ativas. Nenhum arquivo legado é reescrito silenciosamente.
