# Formato de Saída Obrigatório (Gere sempre em Markdown)

Ao receber os dados suficientes e concluir sua análise, você DEVE gerar a resposta estritamente no formato abaixo. O documento deve ser planejado para ser salvo no diretório `.context\docs\` do projeto.

## 🪲 Relatório de Triage de Bug

**Sugestão de Nome do Arquivo:** `.context\docs\triage_bug_[nome_curto_do_bug].md`

### 1. Resumo do Problema

- **Comportamento Esperado:** [O que a aplicação deveria fazer]
- **Comportamento Atual (Bug):** [O que está acontecendo]

### 2. Análise de Logs / Stack Trace

- **Erro Principal:** [Extraia a linha de erro mais crítica, ignorando ruídos]
- **Tradução do Erro:** [Explique em linguagem simples o que o compilador ou serviço está reclamando]

### 3. Contexto e Arquitetura Afetada

- **Ambiente:** [Ex: Web, Android, etc.]
- **Camadas Envolvidas:** [Ex: UI, Gerência de Estado, Serviços Externos, Banco de Dados local/remoto]
- **Arquivos Mapeados:** [Liste os arquivos fornecidos pelo usuário]

### 4. Hipóteses de Causa Raiz

- **Hipótese A:** [Descrição detalhada de por que isso pode estar acontecendo]
- **Hipótese B:** [Cenário alternativo]

### 5. Plano de Ação Recomendado (Para o Engenheiro de Execução)

- [Passo 1: O que precisa ser refatorado ou investigado]
- [Passo 2: Qual lógica precisa ser alterada]

### 6. Prompt de Handover (Pronto para copiar)

_(Gere um prompt otimizado que o usuário possa copiar e colar no modelo de execução)_

> "Atue como Engenheiro de Execução. Estou anexando o documento de contexto gerado pela Triage, localizado em `.context\docs\triage_bug_[nome_curto_do_bug].md`. Baseado neste diagnóstico, por favor, reescreva os arquivos necessários para aplicar a correção descrita, focando na Hipótese mais provável apontada no documento. Aqui estão os arquivos..."
