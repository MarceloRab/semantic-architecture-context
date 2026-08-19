# Track 05 — Relocação do manifesto: managed × owned

[governance]
1. Deliver the goal and DoD literally; do not invent observable behavior.
2. Follow the required approach; choose only mechanically equivalent details.
3. Read only causal dependencies and record mechanically necessary unexpected writes.
4. Replan on any DoD, strategy or authority gap; do not replace it with insight, heuristic or a merely functional result.
5. No silent fallback, masked error, weak critical heuristic, TODO/stub, optional improvement or self-certification.
[/governance]

## Goal

O manifesto Route do projeto (`owned`) reside em `<root>/.sac/domains.md`, fora de qualquer árvore que o installer sobrescreve, e o template/schema (`managed`) vive em `templates/domains.template.md`.

## Context capsule

- Current flow: `_DOMAINS_REL = os.path.join("sac-context","docs","SAC_domains.md")` @ `src/sac_domains.py:14`, resolvido por `sac_domains_path(root)` @ `src/sac_domains.py:44`. O mesmo arquivo serve simultaneamente como schema, template (`## _template`), manual COR-3 e manifesto do projeto.
- Current flow: `_SKIP_DOMAIN_IDS = {"como usar", "_template", "example_domain"}` @ `src/sac_domains.py:23-29` — é o mecanismo que distingue bloco de domínio real de bloco de template.
- Owner: `sac_domains_path` é o ponto único de resolução. Dependentes: todos os subcomandos de `src/sac_scan.py`, `docs/SAC_BOOTSTRAP.md`, e as três skills.
- Dependency: `parse_sac_domains(root)` @ `src/sac_domains.py:58` consome o caminho resolvido.

## Semantic authority

- Must: `_DOMAINS_REL` passa a `.sac/domains.md`.
- Must: `sac-context/docs/SAC_domains.md` é movido para `templates/domains.template.md` (schema + template + manual COR-3), classificado `managed`.
- Must: implementar literalmente esta matriz de estados antigos, sem exceção e sem precedência silenciosa:

  | Estado detectado | Veredicto exigido |
  | --- | --- |
  | `.sac/domains.md` presente, legado ausente | usar `.sac/domains.md` |
  | `.sac/domains.md` ausente, legado presente com ≥1 bloco `##` fora de `_SKIP_DOMAIN_IDS` | erro `sac.environment.domains_manifest_legacy_layout`, com a instrução de mover para `.sac/domains.md` |
  | `.sac/domains.md` ausente, legado presente só com template/howto | tratar como ausência de manifesto: o comportamento hoje já definido para manifesto ausente |
  | ambos presentes | erro `sac.environment.domains_manifest_ambiguous`, exigindo remoção do legado |
  | nenhum presente | o comportamento hoje já definido para manifesto ausente |

- Must: criar `.sac/domains.md` do próprio repositório público, com ao menos um domínio real onboardado.
- Must not: ler o legado quando `.sac/domains.md` existe; escolher por precedência; converter formato; silenciar; usar crash como política.
- Error behavior: os dois códigos de erro acima são explícitos, nomeiam o caminho encontrado e a ação de recuperação. Nunca fallback.

## Required approach

- Owner and boundary: `src/sac_domains.py` é o dono único da resolução e da detecção de estado antigo. `src/sac_scan.py` apenas propaga o erro.
- Data/control flow: `sac_domains_path(root)` → detecção do estado → veredicto da matriz → parse ou erro.
- Integration rule: os códigos de erro usam a família `sac.environment.*`, coerente com track_06.
- Executor latitude: mechanically equivalent details only

## Focus

- Likely writes: `src/sac_domains.py`, `src/sac_scan.py`, `templates/domains.template.md`, `.sac/domains.md`, `docs/SAC_BOOTSTRAP.md`
- Essential reads: `src/sac_domains.py:14,23-29,44,58`
- Forbidden work: tocar gramática de tag; alterar fitness; mexer em `_BASE_SCENARIOS`; escrever installer (é track_07); escrever fora de `semantic-architecture-context` — `api_robot`, `to_de_plantao` e `rabelo-standards` não são migrados por nenhuma track destes blocos
- Stop if: um estado alcançável não couber em nenhuma linha da matriz
- Depends on: track_04

## DoD

1. Cada uma das cinco linhas da matriz é reproduzida em fixture e produz o veredicto declarado. | Proof: manual (cinco execuções da CLI, saídas registradas)
2. Com `.sac/domains.md` presente, o arquivo legado nunca é lido. | Proof: manual (legado com conteúdo divergente; resultado vem do novo)
3. `.sac/domains.md` do repositório público existe e `list-domains` o devolve. | Proof: manual
4. `templates/domains.template.md` contém schema, template e manual COR-3; `sac-context/docs/SAC_domains.md` não existe mais. | Proof: inspect
5. As três skills e `docs/SAC_BOOTSTRAP.md` não citam mais o caminho antigo. | Proof: inspect
6. `mcp/smoke.mjs` verde. | Proof: manual

## Handoff

- File: .context/docs/pendentes/sac_public_extraction/bloco_01_mcp_publico/handoff.md
- Terminal: `EXECUTED`; review requires a separate manual trigger
