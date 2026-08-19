# Handoff — Bloco 02: melhoria funcional da feature

## Plan

- Design: .context/docs/pendentes/sac_public_extraction/bloco_02_melhoria_funcional/design.md
- Approved by: usuário, 2026-08-19 — autorização explícita para ativar o builder
- Current: track_01

## Tracks

| Track | Goal | Depends on | Status | Attempt |
| --- | --- | --- | --- | --- |
| track_01 | verify: termina em `;` ou fim de linha; nenhum alvo descartado em silêncio | none | PENDING | 0 |
| track_02 | Campo `on=` com vocabulário fechado para ARCH e parser dual para tags legadas | track_01 | PENDING | 0 |
| track_03 | AGENTS.md como porta de entrada e camada de atalho de dois níveis nas três skills | track_02 | PENDING | 0 |
| track_04 | `_is_covered` avalia contra o conjunto completo; veredicto independente da ordem de caminhos | track_03 | PENDING | 0 |
| track_05 | Registro de linguagens com Python, JS/TS e Go, e dogfooding bloqueante na CI | track_04 | PENDING | 0 |
| track_06 | file relativo, `_perf.sac_root` removido, orçamento e payload_bytes na unidade emitida | track_05 | PENDING | 0 |
| track_07 | OVER_SELECT deixa de contar tags auto-incluídas; piso de anchors reportado pelo assess | track_06 | PENDING | 0 |
| track_08 | Marcador de comentário sem whitelist e vocabulário imperativo PT+EN | track_07 | PENDING | 0 |
| track_09 | Promessa honesta, política de vetos publicada, RELEASE_GATE satisfeito e tag 0.1.0 | track_08 | PENDING | 0 |

Status: `PENDING` -> `EXECUTED` | `FAILED` | `REPLAN` -> `APPROVED` | `CHANGES_REQUIRED` | `REPLAN`.
Execution writes its own row status and attempt number. Review writes the post-verdict status and moves `Current` on `APPROVED`. Nobody edits another row.

## Attempts

Append entries; never rewrite history.

## Pré-condição do bloco

Este bloco inicia somente após `track_10` do Bloco 01 estar `APPROVED`. A ordem interna é ditada por princípio, não por custo: as quatro primeiras tracks são as únicas de toda a coleção de relatórios que **aumentam** o benefício ao agente cego; as demais defendem os outros dois pilares.

## Fora de escopo, posterior ao bloco

Nenhum consumidor existente é migrado por este bloco. `api_robot` e `to_de_plantao` continuam rodando suas cópias congeladas de `sac-context/`, e `rabelo-standards` — base propagadora, não consumidora — não é tocado. A transferência para esses projetos é decisão do usuário, posterior a testes estáveis pós-Bloco 02.
