# Semantic Architecture Context (SAC)

[![Hygiene Gate](https://github.com/semantic-architecture-context/semantic-architecture-context/actions/workflows/hygiene.yml/badge.svg)](https://github.com/semantic-architecture-context/semantic-architecture-context/actions/workflows/hygiene.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node 22+](https://img.shields.io/badge/node-22+-green.svg)](https://nodejs.org/)

**Semantic Architecture Context (SAC)** é um framework e protocolo de MCP (Model Context Protocol) que anexa restrições e contratos arquiteturais diretamente no código-fonte através de tags padronizadas de uma linha (`SAC:ARCH`, `SAC:REGR`, `SAC:DEPRECATED`), expondo-os de forma determinística e cirúrgica para assistentes e agentes de IA via MCP e CLI.

---

## 3 Princípios do SAC

1. **Locality & Zero-Cost Discovery (Pilar do Código)**
   Contratos e invariantes arquiteturais vivem colados nas declarações de funções, classes e módulos. Qualquer agente de IA ou desenvolvedor humano que abra o arquivo recebe imediatamente o contexto arquitetural relevante, sem depender de ferramentas proprietárias.

2. **Bounded Scope & Token Economy (Roteamento Delimitado)**
   Varreduras globais de repositório consomem dezenas de milhares de tokens e geram ruído. O SAC organiza projetos em domínios semânticos compactos (`.sac/domains.md`), permitindo descoberta cirúrgica em quatro camadas estruturadas: **Route** (`list_sac_domains`), **Context** (`get_sac_context`), **Verify** (`get_sac_constraints`) e **Discover** (`discover_sac`).

3. **Determinismo Estrito & Paridade Idêntica**
   Zero fallback silencioso, zero suposição ou heurística fraca. O servidor MCP Node é um adaptador estrito sobre o engine Python, garantindo 100% de paridade de payloads e mensagens de erro estruturadas (`sac.environment.*`). Manifestos do usuário (`.sac/domains.md`) são estritamente `owned` e nunca são sobrescritos ou mesclados pelo ferramental.

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

## Documentação Adicional

- [Guia Detalhado de Instalação](docs/INSTALL.md)
- [Especificação Operacional SAC v2](docs/SAC_V2.md)
- [Template de Domínios](templates/domains.template.md)
- [Código de Conduta](CODE_OF_CONDUCT.md)
- [Licença MIT](LICENSE)
