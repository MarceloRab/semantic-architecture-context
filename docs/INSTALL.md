# Guia de Instalação e Configuração do SAC

Este documento fornece instruções detalhadas para instalar, configurar e integrar o **Semantic Architecture Context (SAC)** em projetos de qualquer linguagem ou plataforma.

---

## 1. Pré-requisitos de Sistema

O SAC utiliza uma arquitetura híbrida de alto desempenho:
- **Engine de Análise & CLI**: Python 100% standard library (zero dependências externas no runtime de análise).
- **Servidor MCP**: Node.js adapter compatível com o protocolo oficial `@modelcontextprotocol/sdk`.

### Requisitos Mínimos:
1. **Python**: Versão **3.11** ou superior (`python --version` ou `python3 --version`).
2. **Node.js**: Versão **22** ou superior (`node --version`).
3. **Git**: Para clonar o repositório e rastrear diffs.

---

## 2. Instalação e Inicialização

O repositório SAC disponibiliza um instalador universal de arquivo único em Python puro na raiz: `install.py`.

### 2.1. Clonando o Repositório SAC

```bash
git clone https://github.com/semantic-architecture-context/semantic-architecture-context.git
cd semantic-architecture-context
```

### 2.2. Instalando as Dependências do Servidor MCP

No diretório `mcp/` do SAC, execute a instalação limpa de dependências do servidor MCP:

```bash
cd mcp
npm ci
cd ..
```

### 2.3. Executando o Instalador (`install.py`)

Para inicializar o SAC no diretório do seu projeto:

```bash
python install.py --target /caminho/para/seu/projeto
```

Se executado sem `--target`, o instalador utilizará o diretório atual (`.`):
```bash
python install.py
```

### 2.4. Opções de Linha de Comando do `install.py`

| Opção | Abreviação | Descrição |
|---|---|---|
| `--target <DIR>` | `-t <DIR>` | Especifica o diretório raiz do projeto onde o SAC será configurado. Padrão: diretório atual. |
| `--check-only` | | Valida apenas os runtimes de sistema (Python ≥ 3.11, Node ≥ 22) sem alterar nenhum arquivo. |
| `--json` | | Emite o relatório de instalação em formato JSON estruturado (útil para automações e CI). |
| `--help` | `-h` | Exibe a mensagem de ajuda com a lista completa de opções. |

---

## 3. Filosofia de Arquivos: Managed vs Owned

O SAC adota uma divisão rigorosa entre arquivos mantidos pela ferramenta (**managed**) e manifestos do usuário (**owned**):

- **Arquivos Managed**: Códigos do engine (`src/`), servidor MCP (`mcp/`) e templates de referência (`templates/domains.template.md`).
- **Arquivo Owned**: `<target>/.sac/domains.md`.
  - Este arquivo contém as declarações de domínios, intents, listas de arquivos e âncoras do seu projeto.
  - **Garantia Contratual**: O `install.py` **NUNCA** sobrescreve, mescla ou altera um `.sac/domains.md` já existente no projeto alvo. Se o arquivo já existir, ele é preservado byte a byte de forma 100% idêntica.

---

## 4. Configuração nos Hosts MCP

O instalador gera e imprime o bloco JSON pronto para o seu ambiente. O SAC **não modifica arquivos de configuração de hosts automaticamente**, garantindo que você tenha controle total sobre a configuração do seu ambiente.

### 4.1. Claude Desktop

Adicione a entrada `sac` no arquivo `claude_desktop_config.json`:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "sac": {
      "command": "node",
      "args": [
        "/caminho/absoluto/para/semantic-architecture-context/mcp/server.mjs"
      ],
      "env": {
        "SAC_ROOT": "/caminho/absoluto/para/seu/projeto",
        "SAC_PYTHON": "python"
      }
    }
  }
}
```

### 4.2. Cursor

No Cursor, você pode configurar o MCP nas Configurações (`Features -> MCP Servers`) ou no arquivo `.cursor/mcp.json` na raiz do seu projeto:

```json
{
  "mcpServers": {
    "sac": {
      "command": "node",
      "args": [
        "/caminho/absoluto/para/semantic-architecture-context/mcp/server.mjs"
      ],
      "env": {
        "SAC_ROOT": "/caminho/absoluto/para/seu/projeto",
        "SAC_PYTHON": "python"
      }
    }
  }
}
```

### 4.3. VS Code / Extensões MCP (Cline, Roo Code, Continue)

Configure o comando `node` apontando para `mcp/server.mjs` com as variáveis de ambiente `SAC_ROOT` e `SAC_PYTHON` correspondentes.

---

## 5. Verificação da Instalação

Após rodar o instalador e configurar seu host, você pode validar o funcionamento através da CLI:

```bash
# 1. Verificar versão instalada
python src/sac_scan.py --version

# 2. Listar domínios catalogados no projeto
python src/sac_scan.py list-domains --root /caminho/para/seu/projeto --json

# 3. Executar o smoke test da suíte MCP
node mcp/smoke.mjs
```

---

## 6. Resolução de Problemas (Troubleshooting)

### Erro: `Python >= 3.11 is required (found 3.X.X)`
- **Causa**: O Python padrão no seu ambiente (`PATH`) é anterior à versão 3.11.
- **Solução**: Instale o Python 3.11+ ou configure a variável `SAC_PYTHON` apontando para o executável correto (ex: `SAC_PYTHON=/usr/bin/python3.12`).

### Erro: `Node.js >= 22 is required, but 'node' was not found in PATH`
- **Causa**: O executável `node` não está disponível no `PATH` do sistema ou não está instalado.
- **Solução**: Instale o Node.js 22 LTS a partir de [nodejs.org](https://nodejs.org/) e adicione-o ao seu `PATH`.

### Erro: `Node.js >= 22 is required (found v18.X.X / v20.X.X)`
- **Causa**: A versão do Node.js instalada é inferior à 22.
- **Solução**: Atualize o Node.js para a versão 22 ou superior (necessária para os recursos modernos de ES Modules e compatibilidade com `@modelcontextprotocol/sdk`).

### Erro: `filepath_required` ou `domain_not_found`
- **Causa**: O SAC opera sob escopo delimitado por domínios. Tentativas de consulta sem `--path` ou com arquivos fora dos domínios mapeados pausam a execução para evitar varreduras desnecessárias.
- **Solução**: Registre os arquivos do seu módulo no manifesto `.sac/domains.md` do seu projeto antes de consultar tags específicas.
