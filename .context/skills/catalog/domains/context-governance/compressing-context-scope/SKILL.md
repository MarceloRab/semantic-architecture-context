---
name: compressing-context-scope
description: "Atualiza e comprime as pastas de contexto e anti-scan de projetos filhos baseados no novo padrao LCR-A (Level-A Compression Rule)."
tags: [compression, context, anti-scan, maintenance]
difficulty: easy
estimated_time: 1min
---
# compressing-context-scope

mission: "Atualizar projetos filhos espelhando as politicas de alta densidade e compressao LCR-A em .cursorrules, .antigravityignore e pastas de context-governance"

steps:[
  "step1_mirror: Ler a fonte LCR-A em `rabelo-standards` e reescrever o `.cursorrules` e `.antigravityignore` do projeto destino. (Sobrecrever direto)",
  "step2_arquitetura: Iterar na pasta `.context/docs/architecture_drawers/` do projeto destino.",
  "step3_compress_drawers: Para cada drawer convertido, aplicar REGRA: [eliminar_scaffold_markdown, converter_tabelas_em_arrays_inline, remover_metalinguagem, preservar_fato_tecnico_hard_rule_id_relacionamentos]",
  "step4_docs_suporte: Iterar `.context/support/` local convertendo textos discursivos pesados sobre politicas em chaves curtas e pseudo-json/yaml array inline.",
  "step5_log_execution: Sinalizar no `current_execution.md` que a compressao densa LCR-A foi aplicada ao cluster de contexto."
]
guardrails:[
  "NEVER lose constraints/rules: compressao != perda. Extraia o DNA do repositorio e tire apenas a roupa bonita.",
  "Force Dry-run opcional: Para projetos criticos, fazer um output antes de aplicar o sobrescrever (se pedido)."
]
