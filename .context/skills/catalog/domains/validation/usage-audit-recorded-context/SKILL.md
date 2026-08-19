---
name: usage-audit-recorded-context
description: Auditor do uso e conformidade com memória gravada. Esta skill será aplicada manualmente toda vez que o usuário precisar validar o uso do contexto gravado pelo agende de ai. Necessidade de evitar ao máximo o uso de tokens de leitura improdutivo diante de um trabalho já feito e documentado.
version: 1.0.0
tags:
  [
    validation,
    context-governance,
    token-efficiency,
    memory-audit,
    recorded-context,
    policy-compliance,
    usage-audit,
    token-optimization,
    context-maintenance,
    recorded-memory,
  ]
difficulty: low
estimated_time: 5-10min
---

# Token Audit — Conformidade com Memória Gravada

Tokens são recurso escasso. O agente deve sempre preferir memória gravada e justificar formalmente qualquer leitura extra.

---

## Fontes canônicas (consultar nesta ordem antes de qualquer scan)

1. `.context/active_context.md` → snapshot compacto de reinício
2. `.context/docs/pendentes/current_execution.md` → status de execução e decisões recentes
3. `.context/support/architecture_drawer_contract.md` → router arquitetural
4. `.context/docs/architecture_drawers/` → detalhes de módulos e componentes, quando roteado por intenção

Somente se as 4 fontes acima forem insuficientes, partir para scan livre — que exige justificativa formal.

---

## Declaração obrigatória antes de qualquer ferramenta

Caminho econômico (fontes 1–4):
[AUDIT] Fonte: <nome do arquivo consultado>
[AUDIT] Motivo: <razão da escolha>

Scan novo (fora das fontes canônicas) — campos obrigatórios extras:
[AUDIT] ⚠️ SCAN NOVO
[AUDIT] Fontes canônicas consultadas: <quais foram lidas e por que foram insuficientes>
[AUDIT] Escopo: <arquivos/diretórios que serão lidos>
[AUDIT] Tokens extras: <estimativa>
[AUDIT] Evitável no futuro: <sim/não — o que gravar na memória>

---

## Relatório ao final de toda tarefa com ferramentas

[AUDIT-REPORT] Fontes: <lista> | Violações: <nenhuma | V-XX: descrição> | Gravar na memória: <sugestão ou "nada">

Violações reconhecidas:

- V-01 Scan livre sem esgotar as 4 fontes canônicas primeiro
- V-02 Re-leitura de arquivo já presente no contexto da conversa
- V-03 Leitura de diretório completo quando arquivo canônico era suficiente
- V-04 Ignorou active_context.md (restart snapshot) sendo parte da cadeia obrigatória
