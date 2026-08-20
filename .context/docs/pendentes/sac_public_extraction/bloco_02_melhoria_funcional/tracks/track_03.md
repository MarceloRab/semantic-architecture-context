# Track 03 — Porta de entrada e camada de atalho

[governance]
1. Deliver the goal and DoD literally; do not invent observable behavior.
2. Follow the required approach; choose only mechanically equivalent details.
3. Read only causal dependencies and record mechanically necessary unexpected writes.
4. Replan on any DoD, strategy or authority gap; do not replace it with insight, heuristic or a merely functional result.
5. No silent fallback, masked error, weak critical heuristic, TODO/stub, optional improvement or approval without literal evidence for every DoD item.
[/governance]

## Goal

Um agente que abre apenas `AGENTS.md` descobre que o SAC existe, onde está o manifesto, como a tag se lê, que `files:` é limite de busca, e qual comando rodar quando não há MCP — sem nunca precisar de ferramenta.

## Context capsule

- Current flow: `AGENTS.md` na raiz — o arquivo que todo agente lê por convenção — tem **zero** menções a SAC. A única referência de raiz é `.cursorrules`, específico de um host, e seu conteúdo trata de governança de mirror, não de como usar SAC. Resultado: o agente sem ferramenta só encontra uma tag por acidente, e Route, boundary e `files:` como limite de busca são inexistentes para ele.
- Current flow (skills, após Bloco 01 track_08): caminhos absolutos já removidos e frontmatter já desambiguado. Permanecem: `sac-onboard` com cadeia de 3 níveis (`prompt_resumido.md` → `PROMPT.md` → `SKILL.md`); `sac-context` sem entrada curta; `sac-execution-overlay/PROMPT.md` com o item `15.` **duplicado** e duas linhas `Pipeline:` divergentes.
- Fato de ergonomia: a tabela *frase do usuário → contrato derivado* existe apenas em `sac-onboard/prompt_resumido.md` e é o mecanismo que faz uma frase virar contrato sem heurística.
- Owner: `AGENTS.md` na raiz; `skills/*/PROMPT.md`.

## Semantic authority

- Must: `AGENTS.md` ganha um bloco SAC tool-neutral contendo, no mínimo: onde está o manifesto (`.sac/domains.md`); a gramática da tag em até três linhas; a afirmação explícita de que `files:` é **limite de busca**, não fila de leitura; e o comando de CLI equivalente para quando não há MCP.
- Must: nome único de entrada nas três skills: `PROMPT.md`. O conteúdo de `sac-onboard/prompt_resumido.md` é **absorvido** no `PROMPT.md` e o arquivo é removido — sem redirect e sem stub. A cadeia passa a ter dois níveis: `PROMPT.md` (atalho, ≤ 1 tela) → `SKILL.md` (contrato).
- Must: a tabela *frase → contrato derivado* passa a existir nas três skills.
- Must: verbos de atalho estáveis e disjuntos — `SAC` → `sac-execution-overlay`; `SAC ONBOARD <id>` → `sac-onboard` (ASSESS default, read-only); `SAC TAG` → `sac-context`. Os literais que autorizam Write (`APROVAR SAC REGISTER <id>`, `APROVAR SAC TAG_DELTA <id>`) continuam sendo os **únicos** que o fazem.
- Must: bloco "sem MCP" no topo de cada `PROMPT.md`, com o comando de CLI equivalente em duas linhas.
- Must: corrigir o item `15.` duplicado e a linha `Pipeline:` divergente em `sac-execution-overlay/PROMPT.md`, mantendo a versão completa do pipeline (`boot → Route → Context ou bounded-unmapped → Verify/Discover → Capillarity(on-demand) → Gate`).
- Must not: adicionar artefato novo; introduzir terceiro nível de indireção; criar verbo que autorize Write; alterar o contrato de qualquer `SKILL.md`.
- Error behavior: se um atalho não puder ser resolvido de forma relativa, parar e reportar.

## Required approach

- Owner and boundary: `AGENTS.md` é a porta; `PROMPT.md` de cada skill é o atalho; `SKILL.md` continua sendo o contrato e não é reescrito.
- Data/control flow: agente lê `AGENTS.md` → chega ao manifesto ou ao atalho da skill → o atalho lhe dá o comando de CLI quando não há MCP.
- Integration rule: a camada de atalho é **subtrativa** — remove um nível de indireção e uma duplicação; o único conteúdo novo é replicação da tabela que já existe e funciona.
- Executor latitude: mechanically equivalent details only

## Focus

- Likely writes: `AGENTS.md`, `skills/sac-context/PROMPT.md`, `skills/sac-onboard/PROMPT.md`, `skills/sac-execution-overlay/PROMPT.md`
- Essential reads: `skills/sac-onboard/prompt_resumido.md`, `skills/sac-execution-overlay/PROMPT.md`
- Forbidden work: reescrever `SKILL.md`; publicar `sac-evolution`; tocar código do engine
- Stop if: a absorção de `prompt_resumido.md` perder conteúdo que só existe nele
- Depends on: track_02

## DoD

1. Partindo **apenas** de `AGENTS.md`, sem MCP, é possível chegar ao manifesto e executar o comando de CLI que devolve constraints. | Proof: manual (leitura dirigida, passos registrados)
2. `AGENTS.md` afirma explicitamente que `files:` é limite de busca, não fila de leitura. | Proof: inspect
3. `prompt_resumido.md` não existe mais e nenhum conteúdo dele se perdeu. | Proof: diff
4. As três skills têm `PROMPT.md`, com a tabela frase→contrato e o bloco "sem MCP" no topo. | Proof: inspect
5. `sac-execution-overlay/PROMPT.md` tem numeração sem duplicata e uma única linha `Pipeline:`, na versão completa. | Proof: inspect
6. Os três verbos de atalho são disjuntos, e nenhum deles autoriza Write. | Proof: inspect

## Handoff

- File: .context/docs/pendentes/sac_public_extraction/bloco_02_melhoria_funcional/handoff.md
- Terminal: record `EXECUTED` + `APPROVED` after the executor checks every DoD item in this chat; then return the robust prompt for `track_04` in a new chat
