# Track 08 — Skills públicas e governança

[governance]
1. Deliver the goal and DoD literally; do not invent observable behavior.
2. Follow the required approach; choose only mechanically equivalent details.
3. Read only causal dependencies and record mechanically necessary unexpected writes.
4. Replan on any DoD, strategy or authority gap; do not replace it with insight, heuristic or a merely functional result.
5. No silent fallback, masked error, weak critical heuristic, TODO/stub, optional improvement or self-certification.
[/governance]

## Goal

As três skills públicas do SAC existem em `skills/`, sem nenhum caminho de máquina e sem gatilho ambíguo, e o repositório documenta como o padrão evolui e como um estranho propõe uma mudança.

## Context capsule

- Current flow (origem): `skills/catalog/domains/context-governance/sac-context/SKILL.md` (12,3K, sem entrada curta); `.../sac-onboard/` (`prompt_resumido.md` 3,2K → `PROMPT.md` 9,3K → `SKILL.md` 15,3K, cadeia de 3 níveis); `.../sac-execution-overlay/` (`PROMPT.md` 2,5K → `SKILL.md` 16,3K).
- Defeito verificado (a): `sac-onboard/prompt_resumido.md` abre instruindo o agente a resolver `C:\Users\Rabelo\projects\rabelo-standards\skills\...`. É a **primeira instrução que o agente lê** e é irresolúvel em qualquer consumidor. O mesmo defeito está em `sac-onboard/PROMPT.md`.
- Defeito verificado (b): as descrições de frontmatter colidem — `sac-context` diz "Gate de contexto para qualquer pergunta, plano, review ou implementação…" e `sac-execution-overlay` diz "Gate obrigatório para qualquer pergunta, plano, review ou implementação…". O roteador de skills não tem como escolher.
- Owner: `skills/` no repositório público.

## Semantic authority

- Must: publicar `sac-context`, `sac-onboard` e `sac-execution-overlay` sob `skills/`.
- Must: remover todo caminho absoluto de máquina e toda menção a `rabelo-standards` dos artefatos; a resolução de artefato irmão passa a ser sempre relativa.
- Must: desambiguar as duas descrições de frontmatter com gatilhos disjuntos — `sac-context` = *gramática e escrita de tag*; `sac-execution-overlay` = *gate de execução*.
- Must: `sac-evolution` **não** é publicada. Em seu lugar, `GOVERNANCE.md` descreve como o padrão evolui (issue → ADR → PR) e `docs/adr/` recebe as ADRs.
- Must: `CONTRIBUTING.md` descreve como abrir PR e o que a CI exige.
- Must not: renomear `prompt_resumido.md` para `PROMPT.md`, criar a tabela frase→contrato nas outras skills, adicionar bloco "sem MCP", ou corrigir o item `15.` duplicado do overlay — **todo o restante do M9 é Bloco 02**, track_03 daquele bloco.
- Must not: exportar topologia de monorepo (`mirror`, `propagation_status`, `skills_registry.json`, `.cursorrules` do pai).
- Error behavior: se um artefato depender de um irmão que não existe no layout público, isso é parado e reportado, não contornado.

## Required approach

- Owner and boundary: `skills/` contém as três skills; `GOVERNANCE.md`, `CONTRIBUTING.md` e `docs/adr/` ficam na raiz.
- Data/control flow: copiar → varrer caminhos absolutos → reescrever resolução de irmão como relativa → editar os dois frontmatter.
- Integration rule: o gate de higiene de track_02 é o verificador; ele já falha em `C:\Users\` e em `rabelo-standards`.
- Executor latitude: mechanically equivalent details only

## Focus

- Likely writes: `skills/sac-context/`, `skills/sac-onboard/`, `skills/sac-execution-overlay/`, `GOVERNANCE.md`, `CONTRIBUTING.md`
- Essential reads: as três skills na origem `C:\Users\Rabelo\projects\rabelo-standards\skills\catalog\domains\context-governance\`
- Forbidden work: qualquer item do M9 além de (a) e (b); publicar `sac-evolution`; reescrever contrato de skill
- Stop if: um artefato de skill não puder funcionar sem o caminho absoluto removido
- Depends on: track_07

## DoD

1. O gate de higiene de track_02 passa sobre `skills/`. | Proof: manual
2. Nenhum artefato em `skills/` contém `C:\Users\` ou `rabelo-standards`. | Proof: inspect
3. As descrições de frontmatter de `sac-context` e `sac-execution-overlay` não compartilham gatilho, e cada uma nomeia um escopo distinto. | Proof: inspect (leitura comparada das duas)
4. `sac-evolution` não existe no repositório público; `GOVERNANCE.md` e `docs/adr/` existem. | Proof: inspect
5. `prompt_resumido.md` ainda existe (sua absorção é Bloco 02) e não contém caminho de máquina. | Proof: inspect

## Handoff

- File: .context/docs/pendentes/sac_public_extraction/bloco_01_mcp_publico/handoff.md
- Terminal: `EXECUTED`; review requires a separate manual trigger
