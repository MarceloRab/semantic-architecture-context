# Track 02 — Campo `on=`: ADR e implementação

[governance]
1. Deliver the goal and DoD literally; do not invent observable behavior.
2. Follow the required approach; choose only mechanically equivalent details.
3. Read only causal dependencies and record mechanically necessary unexpected writes.
4. Replan on any DoD, strategy or authority gap; do not replace it with insight, heuristic or a merely functional result.
5. No silent fallback, masked error, weak critical heuristic, TODO/stub, optional improvement or self-certification.
[/governance]

## Goal

O campo obrigatório da tag passa a carregar a **condição de aplicação** (`on=…`) em vez de severidade inerte, permitindo ao agente sem ferramenta filtrar constraints por `grep` antes de ler o texto — e nenhuma tag já escrita deixa de ser lida.

## Context capsule

- Current flow: forma canônica `<marcador> SAC:<TAG>: <TRIGGER> - <Símbolo>: <Constraint>` @ `src/sac_engine.py:20`, parser canônico @ `src/sac_engine.py:24`, parser legado @ `src/sac_engine.py:32-34`.
- Current flow: `_ALLOWED_TRIGGERS = {"ARCH": ("RULE","CONSTRAINT"), "REGR": ("WARNING","CRITICAL"), "DEPRECATED": ("WARNING","CRITICAL")}` @ `src/sac_engine.py:102-106`.
- Verificado: o campo é **inerte**. `RULE` vs `CONSTRAINT` não é distinguido em nenhum ponto do engine; `WARNING` vs `CRITICAL` não altera comportamento — `diff_check` bloqueia qualquer REGR não coberta independentemente do trigger. São ~10 caracteres do recurso mais escasso do sistema com zero efeito de runtime.
- Owner: `src/sac_engine.py`. Dependentes: `templates/domains.template.md`, `skills/sac-context/`, `skills/sac-onboard/`, `docs/`.
- Contrato herdado: parser dual para tags legadas **já existe** (`src/sac_engine.py:32-34`) e é o padrão da casa para compatibilidade retroativa; tag malformada continua parseável e emite warning, em vez de sumir.

## Semantic authority

- Must: o campo passa a aceitar a forma `on=<cond>`.
- Must: para `ARCH`, `<cond>` é **vocabulário fechado**: `ssot`, `boundary`, `ordering`, `state`, `exclusive`, `ownership`. Valor fora do conjunto ⇒ warning canônico `invalid_trigger`, listando o conjunto permitido; a tag continua parseável e visível.
- Must: para `REGR` e `DEPRECATED`, `<cond>` é token livre em snake_case `[a-z][a-z0-9_]{2,47}`, descrevendo a condição de mudança. Fora do padrão ⇒ `invalid_trigger`, mesma política.
- Must: implementar literalmente esta matriz de estados antigos:

  | Tag existente | Veredicto exigido |
  | --- | --- |
  | `SAC:ARCH: RULE\|CONSTRAINT - Sym: …` | parseada normalmente, `on` vazio, warning `legacy_trigger`; constraint, símbolo e `verify:` preservados integralmente |
  | `SAC:REGR: WARNING\|CRITICAL - Sym: …` | idem, com `legacy_trigger`; comportamento de bloqueio do `diff-check` idêntico ao de hoje |
  | `SAC:DEPRECATED: WARNING\|CRITICAL - Sym: …` | idem, com `legacy_trigger`; `replacement:` continua obrigatório |
  | `on=<valor inválido>` | warning `invalid_trigger`; tag continua parseável e visível |

- Must: escrever a ADR em `docs/adr/` registrando a decisão, o vocabulário fechado de ARCH e a política de compatibilidade.
- Must: atualizar `templates/domains.template.md`, as três skills e `docs/` para a forma nova.
- Must not: remover o campo; criar tag nova; criar campo novo; codificar a condição em prosa dentro da constraint; alongar a linha; tocar `verify:` (é track_01) ou `_is_covered` (é track_04).
- Error behavior: valor inválido gera warning nomeado, nunca rejeição da tag e nunca desaparecimento.

## Required approach

- Owner and boundary: `src/sac_engine.py` é o dono do parsing e da validação; `src/sac_validate.py` reporta.
- Data/control flow: parser canônico tenta `on=<cond>` → se não casar, parser legado tenta o vocabulário antigo e emite `legacy_trigger` → validação do vocabulário conforme `tag_type`.
- Integration rule: usar o mecanismo de parser dual que já existe, não criar um segundo.
- Executor latitude: mechanically equivalent details only

## Focus

- Likely writes: `src/sac_engine.py`, `docs/adr/`, `templates/domains.template.md`, `skills/`, `tests/test_trigger_on.py`
- Essential reads: `src/sac_engine.py:20,24,32-34,102-106`
- Forbidden work: alterar `_KNOWN_TAGS`, `_BASE_SCENARIOS` ou `_OPTIONAL_SCENARIOS`; mexer em fitness; tocar `sac_diff.py`
- Stop if: alguma tag legada alcançável não couber em nenhuma linha da matriz
- Depends on: track_01

## DoD

1. Cada linha da matriz de estados antigos é reproduzida em fixture e produz o veredicto declarado. | Proof: approved-test (`tests/test_trigger_on.py`)
2. Fixture com tag legada e tag nova no mesmo arquivo: ambas parseadas, a legada com `legacy_trigger`, nenhuma perdida. | Proof: approved-test
3. `on=ssot` em ARCH é aceito; `on=qualquer_outra_coisa` em ARCH gera `invalid_trigger` listando o conjunto permitido, e a tag continua no resultado. | Proof: approved-test
4. `on=normalization_order` em REGR é aceito; `on=X` (fora do snake_case) gera `invalid_trigger`. | Proof: approved-test
5. A linha na forma nova não é mais longa que a equivalente na forma antiga, para o mesmo conteúdo. | Proof: inspect (comparação de duas linhas equivalentes)
6. `_KNOWN_TAGS`, `_BASE_SCENARIOS` e `_OPTIONAL_SCENARIOS` têm diff vazio. | Proof: diff
7. ADR existe em `docs/adr/` com a decisão e o vocabulário fechado. | Proof: inspect

## Handoff

- File: .context/docs/pendentes/sac_public_extraction/bloco_02_melhoria_funcional/handoff.md
- Terminal: `EXECUTED`; review requires a separate manual trigger
