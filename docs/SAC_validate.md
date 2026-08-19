# SAC Validate — Operacionalidade e Critérios de Avaliação

> Este documento define como avaliar, operar e manter a feature `validate`
> do SAC V2.1 em projetos downstream.

## O que é validate

`validate` detecta **orphan tags** — tags SAC cuja linha não coincide com
uma declaração real de símbolo no arquivo-fonte, via parse AST — e inconsistências entre `anchor_symbols` e as tags físicas dos `files:` de cada domínio.

```
python sac-context/src/sac_scan.py validate --root .
```

### validate vs capillarity (não confundir)

| Superfície | Pergunta | Entrada | Status / saída |
|---|---|---|---|
| **validate** | A tag física casa com declaração AST? Anchor listado tem tag? | Scan AST nos `files:` | Orphans, `UNMAPPED_ANCHOR_SYMBOL`; exit 0/1 |
| **capillarity** | Claims humanos aprovados cobrem tags canônicas? Domínio fit para Context? Payload cabe? | `context_scenarios` + `coverage_claims` no domínio | (A) `status` `UNRATED` \| `INVALID_CONTRACT` \| `INSUFFICIENT` \| `SUFFICIENT`; (B) `fitness_status` `null` \| `TOO_THIN` \| `UNFIT` \| `OVER_SELECT` \| `FIT`; (C) `payload_status` `OK` \| `OVER_BUDGET` + `payload_warn`; `quality_status=PASS` com `SUFFICIENT`+`FIT`+(`OK`\|`OVER_BUDGET`); campos `uncovered_scenarios`, `missing_roles`, `context_unfit_claims`, `uncontracted_context_tag_count`, `context_selected_tag_count`, `payload_warn` |
| **scan (motor)** | Quantos arquivos/tags o engine leu? | Context/Discover/capillarity | `files_scanned`, `files_listed` — telemetria |
| **open (agente)** | Quais arquivos o agente abriu na sessão? | Handoff manual | Motivo por arquivo; ≠ `files_scanned` |

- **coverage_claims** = rastreabilidade no manifesto; **não** substituem tags no código.
- **minimum_source_tag_lines** = tuples físicos únicos exigidos; pode ser menor que contagem de claims (N claims → 1 linha).
- **tags físicas** = SSOT semântica; constraints vêm só delas.
- Capillarity é **on-demand** (`capillarity --domain` / `assess_sac_capillarity`); **nunca** no boot Route→Context.
- Domínio legado sem metadata capillarity ⇒ assessor `UNRATED`; validate continua independente.
- **Overflow de Context / eixo C:** `context_payload_too_large` ou `payload_status=OVER_BUDGET` / `payload_warn=OVER_BUDGET` → **MUST** `discover_sac(domain_id)` depois `get_sac_constraints(symbol, filepath∈files:)`; Context **não** trunca constraints. **MUST NOT** reduzir `files:`/tags/claims aprovados só para caber no budget ou “passar” capillarity. `OVER_BUDGET` com `SUFFICIENT`+`FIT` é WARN de payload, não FAIL de cobertura.

## Exit codes

| Code | Significado | Ação CI |
|---|---|---|
| 0 | Nenhum orphan encontrado | PASS |
| 1 | Orphans detectados | FAIL hard |
| 2 | Erro de uso ou I/O (root inválido, etc.) | FAIL hard |

> Use `--warning-only` para adotção gradual (VAL-2): o CI não falha mesmo com orphans, permitindo corrigir a dívida incrementalmente.

## Métricas de Qualidade

### Precisão

| Métrica | Definição | Limiar mínimo |
|---|---|---|
| False positive rate | Tags reportadas como órfãs que não são órfãs | ≤ 1% |
| False negative rate | Orphans não detectados pelo parser | 0% (obrigatório) |
| Unknown-language recall | Arquivos em linguagem sem parser são warning, não erro | N/A |

### Performance

| Cenário | SLA |
|---|---|
| 1 arquivo Dart (~500 LOC) | < 200ms |
| 1 arquivo Python (~500 LOC) | < 50ms |
| Repositório médio Dart (~500 arquivos) | < 30s |
| Repositório Python (~500 arquivos) | < 10s |

>Performance medida em hardware padrão CI (2 vCPU, 4GB RAM).

### Coverage Matrix — Dart

| Construct | Detectado como declaração? | Notas |
|---|---|---|
| `class Foo` | ✅ | |
| `abstract class Foo` | ✅ | |
| `mixin Foo` | ✅ | |
| `extension Foo` | ✅ | |
| `enum Foo` | ✅ | |
| `interface class Foo` | ✅ | |
| `function de retorno explícito` | ✅ | |
| `function void foo()` | ✅ | |
| `Future<T> foo()` | ✅ | |
| `method` em classe | ✅ | |
| `getter` | ✅ | |
| `setter` | ✅ | |
| `field declaration` | ✅ | |
| `type alias` | ✅ | |
| `function de retorno implícito` | ❌ | Gaps conhecidos |
| `variable local` | ❌ | Fora do escopo V2.1 |
| `callable` (lambda) | ❌ | Fora do escopo V2.1 |

### Coverage Matrix — Python

| Construct | Detectado como declaração? | Notas |
|---|---|---|
| `class Foo` | ✅ | |
| `def foo():` | ✅ | |
| `async def foo():` | ✅ | |
| Assignment top-level (`x = ...`) | ✅ | |
| Assignment em método | ❌ | Fora do escopo |
| `lambda` | ❌ | Fora do escopo |

## Critérios de Opt-in para Projetos

### Adoção gradual (recomendado)

1. **Fase 1 — dry-run**: rodar `validate` sem fail no CI; coletar orphans existentes.
2. **Fase 2 — warning-only**: manter o CI passando com `--warning-only` enquanto resolve orphans documentados via `SAC-ACK` nas linhas correspondentes.
3. **Fase 3 — hard-fail**: remover `--warning-only` do `sac_guard.yml` após 0 orphans.

```bash
# Fase 1 e 2: observar sem fail
python sac-context/src/sac_scan.py validate --root . --json | jq '.orphans'

# Fase 2 no CI: warning-only
python sac-context/src/sac_scan.py validate --root . --warning-only

# Fase 3: hard-fail (remover --warning-only)
python sac-context/src/sac_scan.py validate --root .
```

### Pré-requisitos para hard-fail

- [ ] Tree-sitter + tree-sitter-dart instalados no CI
- [ ] 0 orphans no baseline do projeto
- [ ] Equipe sabe usar `SAC-ACK` por linha

## Critérios de Avaliação de Feature

Para declarar `validate` pronto para produção em um projeto:

| Critério | Pergunta | Resposta esperada |
|---|---|---|
| Correctness | O parser não emite false negatives em fixtures conhecidos? | ✅ SIM |
| Correctness | False positives em comentários de documentação são aceitos? | ⚠️ Documentar gaps |
| Performance | CI total (diff-check + validate) < 60s? | ✅ SIM ou plano de otimização |
| Operacional | Equipe sabe interpretar warnings de `unsupported_language`? | ✅ Treinamento fatto |
| Operacional | `SAC-ACK` por linha é suficiente para liberar orphans residuais? | ✅ SIM |
| Propagação | Mirror usa a fonte canônica `rabelo-standards/sac-context/`, rejeita fonte alternativa e preserva `SAC_domains.md` do filho? | ✅ SIM |
| Manutenção | Quem mantém os parsers quando a linguagem evolui? | Processo definido |

## Edge Cases Conhecidos

### Tag em doc comment

```dart
/// SAC:ARCH: WARNING - Foo: ...
class Foo {}
```

**Comportamento atual**: a linha do doc comment não coincide com a declaração → reported as orphan. Isso é **intencional** — tags em doc comments não são verificação de símbolo.

**Recomendação**: mover tag para a linha anterior à declaração. Se houver múltiplas tags, usar bloco contíguo `ARCH` → `REGR` → `DEPRECATED` → assinatura; todas são associadas à mesma declaração.

### Tag em string ou literal

```dart
var example = '// SAC:ARCH: WARNING - Foo: ...';
```

**Comportamento atual**: se a tag está dentro de uma string/literal, não é parseada como tag (sac_engine faz filtering). Validate verifica só linhas com tag real.

### Heritage forms (legado)

```dart
// SAC:REGR: WARNING - If modifying Foo, verify: Bar.
```

Forma legada é reconhecida pelo `sac_engine` mas **não é validada** pelo `validate` (V2.1 só valida forma canônica `SAC:<TAG>: <TRIGGER> - <Symbol>:`).

## Manutenção de Parsers

### Quando atualizar parser Dart

- Nova versão da linguagem Dart adiciona novos constructos de declaração
- Testes fixtures revelam false negatives
- Release notes do Dart indicam mudança em AST

### Quando atualizar parser Python

- Nova versão Python altera AST (e.g. `match...case` patterns)
- Testes fixtures revelam false negatives

### Processo de atualização parser

1. Adicionar construct ao `_get_declarations_dart` ou `_get_declarations_python`
2. Adicionar fixture em `sac-context/fixtures/validate/`
3. Executar `python sac-context/src/sac_scan.py validate --root sac-context/fixtures/validate/`
4. Verificar exit 0 e contagem esperada de orphans
5. Propagar para template

## Warnings e seus Significados

| Warning | Causa | Ação |
|---|---|---|
| `unsupported_language dart (tree-sitter not installed)` | tree-sitter não está no environment | Instalar `tree-sitter` + `tree-sitter-dart` |
| `unsupported_language dart (tree-sitter-dart not available)` | Parse falhou | Verificar compatibilidade de versão |
| `read_error <exc>` | Arquivo não pode ser lido | Verificar permissões |
| `decode_error <exc>` | Encoding inválido | Arquivo corrompido ou binário |
| `unknown_tag SAC:FOO` | Tag com tipo desconhecido | Corrigir gramática ou adicionar ao registry |
| `invalid_trigger tag=<tipo> trigger=<valor> allowed=<lista>` | Tag parseável usa trigger fora da matriz canônica | HALT; corrigir por proposta literal aprovada |
| `arch_imperative_required` | `SAC:ARCH` não contém `MUST`, `NEVER` ou `ONLY` | HALT; tornar a invariante imperativa sem inventar semântica |
| `regr_verify_required` | `SAC:REGR` não possui alvos terminais `verify:` | HALT; preservar a constraint existente e propor alvos concretos |
| `deprecated_replacement_required` | `SAC:DEPRECATED` sem `replacement:<símbolo|none>` terminal | Corrigir a tag; uso novo permanece bloqueado |
| `UNMAPPED_ANCHOR_SYMBOL domain=<id> symbol=<nome>` | `anchor_symbols` lista símbolo sem tag física correspondente nos `files:` do domínio | HALT no closeout do onboard; injetar somente linha literal aprovada ou remover/corrigir o anchor por decisão humana |

## Dependências

```txt
# Para validate completo (Dart + Python)
tree-sitter>=0.23
tree-sitter-dart>=3.0

# Para Python-only (Python, sem Dart AST)
# Nenhuma dependência adicional (stdlib only)
```

## Referências

- `sac-context/docs/SAC_V2.md` — gramática e usage
- `sac-context/src/sac_validate.py` — implementação do parser
- `sac-context/ci/sac_guard.yml` — fonte canônica; cópia em template é snapshot derivado de bootstrap
- `skills/catalog/domains/context-governance/sac-context/SKILL.md`
