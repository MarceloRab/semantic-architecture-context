---
name: surgical-request
description: Executa uma tarefa de forma cirúrgica, lendo apenas arquivos canônicos definidos nas gavetas de arquitetura. Proíbe expressamente varreduras cegas (anti-scan) no repositório. Triggers include 'tarefa cirurgica', 'ação pontual', 'surgical request', 'modo cirurgico', 'anti-scan'.
version: 1.0.0
tags: [prompting, context, token-economy, anti-scan, surgical]
difficulty: advanced
estimated_time: 2-5min
---

# Surgical Request (Anti-Scan Execution)

## When to use this skill

- Quando o usuário pede uma modificação rápida e pontual (ex: "consertar erro x na view Y", "adicionar campo no banco").
- Quando deseja-se impor uma economia drástica de tokens (anti-scan) para prolongar a vida da sessão atual.
- Em projetos maduros que possuam a infraestrutura de "Gavetas de Arquitetura" (`.context/docs/architecture_drawers/`) e documentação canônica bem definida.

## Core Principles (The "Anti-Scan" Rule)

⚠️ **ESTRITAMENTE PROIBIDO O USO DE:**

- `find_by_name` (buscas cegas em diretórios amplos tentando adivinhar caminhos)
- `grep_search` genéricos sem alvo certo na pasta raiz
- `list_dir` na pasta `lib/` de forma recursiva ou em subpastas grandes
- Solicitar arquivos, ler dezenas de linhas ou abrir componentes inteiros fora do escopo estrito necessário para a tarefa.

## Execution Workflow

1. **Gatekeeping (Status Check - Leve)**
   - Leia APENAS: `.context/active_context.md` e `.context/docs/pendentes/current_execution.md` (para saber o estado/contexto atual).
   - Trate `.context/active_context.md` como snapshot compacto de reinício, não como handoff detalhado.
   - Não pergunte por arquivo de handoff para tarefa cirúrgica pontual.
   - Só leia ou peça `handoff_file` se a tarefa estiver explicitamente marcada como trilha sequencial em `current_execution.md`.

2. **Routing (Drawer Look-up - Indexador)**
   - Identifique, baseado no pedido, qual Gaveta (`01` a `05` localizadas em `.context/docs/architecture_drawers/`) detém os ponteiros da responsabilidade estrutural solicitada.
   - Leia APENAS essa respectiva gaveta.

3. **Targeting (Canonical Files - Alvo)**
   - Baseado na seção _Mechanism Topology_, _Critical Flows_ ou _Canonical Files_ presentes no final da respectiva gaveta lida:
     - Isole a exata tríade (ou menos) de arquivos necessários (exemplo: `meals_table.dart`, `meal_repository.dart` e `meal_controller.dart`).
   - Use `view_file` (com limites de linhas, se possível) de forma extremamente focada APENAS nas entidades identificadas. Nunca vá para cima ou para baixo na árvore da aplicação.

4. **Execution (Surgical Edit - Modificação do arquivo)**
   - Planeje as mudanças antes de usar a tool.
   - Aplique modificações direcionadas e minuciosas (ex: `replace_file_content` ou `multi_replace_file_content` no método local, sem mexer no esqueleto).
   - Se o problema não for o que parece, ou estourar o escopo do arquivo lido: **Pare e peça instruções.** Não tente consertar saindo em exploração não autorizada.

5. **Reporting (Zero-Fluff)**
   - Após executar as alterações cirúrgicas, responda de forma ultra enxuta e assertiva (estilo militar):
     > "Operação Cirúrgica completa. Alteração efetuada nos arquivos [X] e [Y] via Drawer [Z]. Nenhuma varredura colateral na base foi realizada."

## Refusal & Circuit Breaker

Se um pedido "cirúrgico" na verdade exigir:

- Modificações em 3 ou mais áreas grandes
- Entendimento sistêmico não descrito nas gavetas lidas
- Abertura de mais de 5 arquivos de projeto simultâneos
  => **Abortar fluxo Cirúrgico.** Sugerir fallback para as skills de `planning` (`planning-and-deciding`) e comunicar o risco do escopo ao usuário antes de torrar o contexto.
