# Track 02 — Esqueleto público e gates de higiene

[governance]
1. Deliver the goal and DoD literally; do not invent observable behavior.
2. Follow the required approach; choose only mechanically equivalent details.
3. Read only causal dependencies and record mechanically necessary unexpected writes.
4. Replan on any DoD, strategy or authority gap; do not replace it with insight, heuristic or a merely functional result.
5. No silent fallback, masked error, weak critical heuristic, TODO/stub, optional improvement or self-certification.
[/governance]

## Goal

`semantic-architecture-context` é um repositório git com histórico próprio iniciado do zero, licenciado MIT, e com um workflow de higiene que **falha** quando um arquivo rastreado contém caminho de máquina, nome de monorepo privado ou bytecode compilado.

## Context capsule

- Current flow: o diretório hoje não é repositório git (`git rev-parse` falha) e contém apenas `.context/`, `.claude/`, `.github/PULL_REQUEST_TEMPLATE.md`, `.cursorrules`, `.antigravityignore`.
- Owner: nenhum código de produto existe ainda. Esta track cria só o invólucro.
- Dependency: track_01 (a classificação de `AUDIT.md` justifica os gates).

## Semantic authority

- Must: `git init` com histórico próprio. Nenhum commit é importado de `rabelo-standards`.
- Must: `LICENSE` = MIT, ano corrente, titular = o autor do repositório.
- Must: `.gitignore` cobre `__pycache__/`, `*.pyc`, `node_modules/`, `.sac/symbol_index.json`.
- Must: o workflow de higiene falha (exit ≠ 0) se qualquer arquivo rastreado contiver a string `C:\Users\`, a string `rabelo-standards`, ou se qualquer `*.pyc` / diretório `__pycache__` estiver rastreado. A varredura cobre também o histórico (`git log -p`).
- Must not: criar README, installer, workflow de CI de produto, ou copiar qualquer arquivo de `sac-context/`. Isso é track_03 e seguintes.
- Error behavior: o gate falha de forma dura, nomeando o arquivo e a string encontrada. Nunca avisa e continua.

## Required approach

- Owner and boundary: `.github/workflows/hygiene.yml` é o dono único do gate. Ele roda em `push` e em `pull_request`.
- Data/control flow: checkout → varredura sobre arquivos rastreados → varredura sobre histórico → falha nomeando a ocorrência.
- Integration rule: `permissions: contents: read` explícito; sem segredos; sem `pull_request_target`.
- Executor latitude: mechanically equivalent details only

## Focus

- Likely writes: `.gitignore`, `LICENSE`, `CODE_OF_CONDUCT.md`, `.github/workflows/hygiene.yml`
- Essential reads: `AUDIT.md` (achado dos `.pyc` e dos caminhos de máquina)
- Forbidden work: copiar `src/`, `mcp/`, `ci/`, `docs/`; escrever README ou CONTRIBUTING; criar tag
- Stop if: o gate não conseguir varrer o histórico de forma determinística
- Depends on: track_01

## DoD

1. `git log` do repositório existe e não contém nenhum commit cuja mensagem ou conteúdo venha de `rabelo-standards`. | Proof: inspect
2. Plantar um arquivo `.pyc` rastreado faz o workflow de higiene falhar; removê-lo o faz passar. | Proof: manual (execução do workflow nos dois estados)
3. Plantar um arquivo com a string `C:\Users\` faz o workflow falhar nomeando o arquivo. | Proof: manual
4. `LICENSE` é MIT e `.gitignore` cobre as quatro entradas exigidas. | Proof: inspect
5. Nenhum arquivo de `sac-context/` foi copiado nesta track. | Proof: diff

## Handoff

- File: .context/docs/pendentes/sac_public_extraction/bloco_01_mcp_publico/handoff.md
- Terminal: `EXECUTED`; review requires a separate manual trigger
