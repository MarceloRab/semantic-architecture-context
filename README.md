# Semantic Architecture Context (SAC)

[![CI](https://github.com/semantic-architecture-context/semantic-architecture-context/actions/workflows/ci.yml/badge.svg)](https://github.com/semantic-architecture-context/semantic-architecture-context/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node 22+](https://img.shields.io/badge/node-22+-green.svg)](https://nodejs.org/)

**Semantic Architecture Context (SAC)** é um framework e protocolo de MCP (Model Context Protocol) que anexa restrições e contratos arquiteturais diretamente no código-fonte através de tags padronizadas de uma linha (`SAC:ARCH`, `SAC:REGR`, `SAC:DEPRECATED`), expondo-os de forma determinística e cirúrgica para assistentes e agentes de IA via MCP e CLI.

---

## 3 Princípios Fundamentais do SAC

1. **Compacto e Orientado a Orçamento (Token Economy — SAC-PR1)**
   Uma única linha por restrição (`SAC:ARCH`, `SAC:REGR`, `SAC:DEPRECATED`). Informação semântica cirúrgica que cabe no orçamento de token de qualquer modelo de IA, sem gerar ruído nem inflar o payload da janela de contexto.

2. **Normatizado com Vocabulário Fechado e Executável (SAC-PR2)**
   Sem regras vagas ou prosa solta em documentações esquecidas. O SAC utiliza imperativos formais (`MUST`, `NEVER`, `ONLY`, `DEVE`, `NUNCA`) e condições explícitas (`on=ssot`, `on=ordering`, `verify:`), permitindo validação e parsing determinísticos sem suposições heurísticas.

3. **Benefício ao Agente Cego & Degradação Graciosa (Blind-Agent Utility — SAC-PR3)**
   **O grande diferencial**: os invariantes residem no próprio código-fonte, imediatamente acima do símbolo que protegem. O agente de IA ou desenvolvedor humano que lê o arquivo diretamente no editor ou via `grep` recebe exatamente o mesmo contrato semântico que o agente conectado via MCP. O servidor MCP orçamenta e acelera o roteamento, mas **nunca entrega menos informação do que a leitura direta da linha crua**.

---

## Como o Agente Opera (Com e Sem MCP)

* **Com Servidor MCP Ativo**: O assistente descobre domínios via `list_sac_domains`, obtém overlays compactos via `get_sac_context` e consulta contratos cirúrgicos via `get_sac_constraints` com controle estrito de orçamento de bytes e resolução de dependências de 1º salto (*hop1*).
* **Sem MCP (Caminho Degradado / Agente Cego)**:
  1. O agente lê o manifesto [`.sac/domains.md`](.sac/domains.md) para identificar os domínios e seus arquivos delimitadores (`files:`).
  2. Localiza restrições cirúrgicas no terminal com um simples filtro:
     ```bash
     grep -n "SAC:" src/seu_modulo.py
     ```
  3. Respeita os imperativos declarados na linha comentada antes de gerar qualquer diff.

---

## Requisitos de Sistema

- **Python**: versão **3.11** ou superior.
- **Node.js**: versão **22** ou superior (para o servidor stdio MCP).
- **Git**: para clonagem e rastreamento.

---

## Quickstart (5 Passos)

### 1. Clonar o repositório SAC
```bash
git clone https://github.com/semantic-architecture-context/semantic-architecture-context.git
cd semantic-architecture-context
```

### 2. Inicializar o SAC no seu projeto
Execute o instalador informando o diretório raiz do seu projeto alvo:
```bash
python install.py --target /caminho/para/seu/projeto
```
O instalador valida os runtimes, inicializa `.sac/domains.md` (se ausente, sem jamais alterar arquivos existentes) e imprime o bloco de configuração MCP.

### 3. Configurar o host MCP
Copie o bloco JSON gerado no passo anterior para o arquivo de configuração do seu host MCP.

**Exemplo para Claude Desktop** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "sac": {
      "command": "node",
      "args": [
        "/caminho/absoluto/para/semantic-architecture-context/mcp/server.mjs"
      ],
      "env": {
        "SAC_ROOT": "/caminho/para/seu/projeto",
        "SAC_PYTHON": "python"
      }
    }
  }
}
```

### 4. Testar a conectividade
Verifique se o seu projeto responde à descoberta de domínios via CLI:
```bash
python src/sac_scan.py list-domains --root /caminho/para/seu/projeto
```

### 5. Usar no seu assistente / agente
Reinicie seu host MCP. O agente agora pode invocar:
- `list_sac_domains()`: Lista os domínios mapeados do projeto.
- `get_sac_context(domain_id)`: Obtém o overlay de âncoras e restrições do domínio.
- `get_sac_constraints(symbol, filepath)`: Valida o contrato e requisitos de verificação de um símbolo específico.
- `discover_sac(domain_id)`: Retorna o inventário slim de tags do domínio.

---

## Ferramentas MCP Disponíveis

| Tool | Função | Finalidade Principal |
|---|---|---|
| `list_sac_domains` | Route | Catalog compacto de módulos e contagem de arquivos sem dump massivo. |
| `get_sac_context` | Context | Monta o overlay do domínio (âncoras, REGR, DEPRECATED e hop1) em uma chamada. |
| `get_sac_constraints` | Verify | Consulta cirúrgica das constraints e requisitos de verificação de um símbolo. |
| `discover_sac` | Discover | Inventário slim de tags estruturais dentro dos limites dos arquivos do domínio. |
| `assess_sac_capillarity` | Capillarity | Assessor on-demand de capilaridade e aderência de cenários de teste/revisão. |

---

## Mecanismo de Verificação: Co-Edit Gate

O SAC utiliza um **co-edit gate** como modelo de verificação estática. Quando uma tag `SAC:REGR` define alvos em `verify: [TargetA, TargetB]`, o verificador lexical do SAC checa se os arquivos e símbolos associados foram co-editados na mesma alteração (diff).

> [!NOTE]
> O co-edit gate é um verificador léxico e determinístico de co-edição de alvos declarados. Ele **não** constitui execução de testes dinâmicos ou garantia formal em runtime, atuando como uma guarda estática de escopo e rastreabilidade para agentes e desenvolvedores.

---

## Suporte de Linguagens e Limitações Atuais

Na versão corrente (`0.1.0-rc`), o SAC possui suporte ativo para:
- **`.dart`** (comentários `// SAC:`)
- **`.ps1`** (comentários `# SAC:`)

Esta é uma limitação técnica conhecida do Bloco 01. O registro formal de suporte poliglota (`.py`, `.js`, `.ts`, `.go`) e o endurecimento do parser de cláusulas estão mapeados no [Release Gate](RELEASE_GATE.md) como requisitos obrigatórios para a tag final `0.1.0` no Bloco 02.

---

## Documentação Adicional

- [Release Gate (Critérios para Tag 0.1.0)](RELEASE_GATE.md)
- [Changelog e Histórico de Releases](CHANGELOG.md)
- [Guia Detalhado de Instalação](docs/INSTALL.md)
- [Especificação Operacional SAC v2](docs/SAC_V2.md)
- [Template de Domínios](templates/domains.template.md)
- [Governança Aberta](GOVERNANCE.md)
- [Guia de Contribuição](CONTRIBUTING.md)
- [Código de Conduta](CODE_OF_CONDUCT.md)
- [Licença MIT](LICENSE)

