# SAC Release Gate — Critérios para Tag Final 0.1.0

Este documento define formalmente os requisitos obrigatórios e o checklist de release para a publicação da tag final **`0.1.0`** do Semantic Architecture Context (SAC).

O repositório encontra-se atualmente na versão **`0.1.0-rc`** (Release Candidate), consolidando a conclusão de todas as 10 tracks do **Bloco 01** (SAC como MCP Público independente, licenciado MIT, instalador stdlib-only, separação de manifestos owned/managed e CI com matriz pública).

A tag pública final **`0.1.0`** está estritamente condicionada à execução, validação e aprovação independente de todas as 9 tracks do **Bloco 02** listadas abaixo.

---

## Checklist de Liberação do Bloco 02 (Release Gate para 0.1.0)

- [ ] **Track 01**: Truncamento de `verify:` no primeiro ponto (`[^.]+`) corrigido (termina em `;` ou fim de linha, nenhum alvo descartado em silêncio).
- [ ] **Track 02**: Campo `on=` com vocabulário fechado para ARCH e parser dual para tags legadas.
- [ ] **Track 03**: AGENTS.md na raiz como porta de entrada e camada de atalho de dois níveis nas três skills.
- [ ] **Track 04**: `_is_covered` avaliando contra o conjunto completo em dois laços (veredicto independente da ordem alfabética de caminhos).
- [ ] **Track 05**: Registro de linguagens (`.py`, `.js`, `.ts`, `.go`) e dogfooding bloqueante na CI do repositório.
- [ ] **Track 06**: `file` sempre relativo, `_perf.sac_root` removido, orçamento e `payload_bytes` medidos na unidade emitida.
- [ ] **Track 07**: `OVER_SELECT` deixa de contar tags auto-incluídas por política e piso de anchors reportado pelo `assess`.
- [ ] **Track 08**: Marcador de comentário sem whitelist prefixal e vocabulário imperativo aceitando PT e EN (`MUST|NEVER|ONLY|DEVE|NUNCA|SOMENTE|APENAS`).
- [ ] **Track 09**: Promessa honesta de co-edit gate consolidada, política de vetos publicada e liberação da tag final `0.1.0`.

---

## Política de Transição e Veto

1. **Impedimento de Liberação Prematura**:
   Nenhuma tag `0.1.0` (sem o sufixo `-rc`) pode ser criada no repositório antes que todas as caixas acima estejam marcadas como concluídas `[x]` com evidência comprovada por testes e revisão independente.

2. **Natureza do Release Candidate (`0.1.0-rc`)**:
   A versão `0.1.0-rc` atesta a estabilidade da infraestrutura pública e do protocolo MCP. Durante o período de RC, o SAC opera como um **co-edit gate** com suporte a comentários nas linguagens especificadas na documentação corrente (`.dart`, `.ps1`), até a extensão poliglota ser entregue no Bloco 02.
