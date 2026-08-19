---
name: rehydrat-context
description: "Gerar um snapshot de contexto extremamente compacto, preciso e reidratável. Este output será usado como única fonte de verdade em um novo chat."
version: 1.0.0
tags: []
difficulty: intermediate
estimated_time: 10-15min
---

# SKILL: CONTEXT CHECKPOINT — ULTRA DENSO (NÍVEL 1)

## OBJETIVO

Gerar um snapshot de contexto extremamente compacto, preciso e reidratável.
Este output será usado como única fonte de verdade em um novo chat.

## PRINCÍPIOS

- Máxima densidade semântica (token-efficient)
- Zero redundância
- Zero narrativa
- Zero exemplos
- Zero histórico descartado
- Preservar apenas o que impacta decisões futuras
- Não inferir / não completar lacunas
- Se faltar dado crítico → marcar explicitamente em "unknowns"

## FORMATO OBRIGATÓRIO (NÃO ALTERAR)

STATE_VECTOR:
goal:
context:
decisions:
constraints:
artifacts:
pending:
risks:
unknowns:

## DEFINIÇÃO DOS CAMPOS

- goal:
  Objetivo atual, específico e acionável (1–2 linhas)

- context:
  Estado atual do sistema/projeto (apenas fatos ativos)

- decisions:
  Decisões já tomadas que NÃO podem ser revertidas implicitamente

- constraints:
  Regras técnicas, limitações, preferências obrigatórias

- artifacts:
  Estruturas relevantes (paths, arquivos, modelos, APIs, schemas)

- pending:
  Próximas ações claras e necessárias

- risks:
  Pontos de falha ou atenção

- unknowns:
  Lacunas críticas que impedem decisões seguras

## REGRAS DE COMPRESSÃO

- Remover:
  - Tentativas falhas
  - Discussões exploratórias
  - Justificativas longas
- Converter frases → tokens semânticos
- Preferir:
  - listas compactas
  - separadores “;”
  - termos técnicos diretos
- Evitar linguagem natural longa
- Evitar conectivos desnecessários

## EXEMPLO DE ESTILO (NÃO REPLICAR CONTEÚDO)

STATE_VECTOR:
goal: implementar X com Y
context: backend Node; DB PostgreSQL; auth JWT ativo
decisions: usar pattern repository; evitar ORM pesado
constraints: sem libs externas; latency <200ms
artifacts: /src/services/XService.ts; schema_v2
pending: implementar endpoint POST /x; validar payload
risks: race condition em update; validação incompleta
unknowns: regra exata de cálculo Z

## INSTRUÇÃO FINAL

Gerar apenas o STATE_VECTOR.
Não explicar.
Não adicionar texto fora do formato.
