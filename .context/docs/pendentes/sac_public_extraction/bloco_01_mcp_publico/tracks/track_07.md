# Track 07 — Installer e quickstart

[governance]
1. Deliver the goal and DoD literally; do not invent observable behavior.
2. Follow the required approach; choose only mechanically equivalent details.
3. Read only causal dependencies and record mechanically necessary unexpected writes.
4. Replan on any DoD, strategy or authority gap; do not replace it with insight, heuristic or a merely functional result.
5. No silent fallback, masked error, weak critical heuristic, TODO/stub, optional improvement or self-certification.
[/governance]

## Goal

Uma pessoa desconhecida, numa máquina limpa, clona o repositório, roda `python install.py` no seu próprio projeto e obtém um projeto que responde a `list_sac_domains`, sem que o installer jamais sobrescreva conteúdo que ela tenha escrito.

## Context capsule

- Current flow: hoje a distribuição ao consumidor é cópia de arquivos por `scripts/mirror-sac-tooling.ps1` a partir de `rabelo-standards` (base propagadora, não consumidora), com exclusão por nome para preservar o manifesto — mecanismo que congela schema, template e manual na versão do bootstrap. `install.py` substitui esse mecanismo para quem instalar a partir do repositório público; os consumidores atuais (`api_robot`, `to_de_plantao`) não são migrados por esta track nem por nenhuma outra destes blocos.
- Current flow: após track_05, `managed` = árvore copiada + `templates/domains.template.md`; `owned` = `<root>/.sac/domains.md`.
- Owner: `install.py` na raiz é o dono único da instalação.
- Dependency: Python é requisito duro do engine, logo o installer em Python não adiciona runtime nenhum.

## Semantic authority

- Must: `install.py` usa **apenas** a stdlib e é o único installer. Não existe `install.ps1` nem `install.sh`.
- Must: o installer valida Python ≥ 3.11 e Node ≥ 22, falhando com erro nomeado quando abaixo.
- Must: o installer instala/atualiza integralmente a árvore `managed` (sem exclusão por nome).
- Must: o installer cria `<root>/.sac/domains.md` a partir de `templates/domains.template.md` **somente quando ausente**. Se presente, não é tocado — nem lido para comparar, nem mesclado.
- Must: o installer **imprime** o bloco de configuração do host MCP para o usuário colar.
- Must not: editar arquivo de configuração de host MCP; escrever em qualquer caminho `owned`; instalar dependência; criar arquivo fora da árvore `managed` e de `.sac/domains.md`.
- Error behavior: versão de runtime abaixo do piso, ou destino não gravável, falham explicitamente nomeando a causa. Nunca prosseguir em modo degradado.

## Required approach

- Owner and boundary: `install.py` escreve; `README.md` e `docs/INSTALL.md` documentam.
- Data/control flow: validar runtimes → instalar árvore `managed` → criar `.sac/domains.md` se ausente → imprimir bloco de config.
- Integration rule: `README.md` traz o quickstart em no máximo cinco passos; `docs/INSTALL.md` traz o detalhe.
- Executor latitude: mechanically equivalent details only

## Focus

- Likely writes: `install.py`, `README.md`, `docs/INSTALL.md`
- Essential reads: `templates/domains.template.md`, `.sac/domains.md`, `src/sac_domains.py` (caminho resolvido)
- Forbidden work: declarar o gate como prevenção de regressão no README (a promessa honesta é Bloco 02); criar tag; publicar em registry; escrever CI
- Stop if: a árvore `managed` não puder ser distinguida de `owned` sem exclusão por nome
- Depends on: track_06

## DoD

1. Em diretório limpo, `python install.py` produz um projeto que responde a `list_sac_domains`. | Proof: manual
2. Reexecutar o installer sobre um `.sac/domains.md` modificado deixa o arquivo **byte a byte idêntico**. | Proof: manual (hash antes/depois)
3. Python abaixo de 3.11 ou Node abaixo de 22 fazem o installer falhar com erro nomeado. | Proof: manual
4. O installer não escreve em nenhum arquivo de configuração de host MCP. | Proof: inspect
5. `install.py` não importa nada fora da stdlib. | Proof: inspect
6. O quickstart do README foi executado literalmente, do zero, e funcionou. | Proof: manual

## Handoff

- File: .context/docs/pendentes/sac_public_extraction/bloco_01_mcp_publico/handoff.md
- Terminal: `EXECUTED`; review requires a separate manual trigger
