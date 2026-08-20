# SAC Release Gate — Critérios para Tag Final 0.1.0

Este documento define formalmente os requisitos obrigatórios e o checklist de release para a publicação da tag final **`0.1.0`** do Semantic Architecture Context (SAC).

O release candidate **`0.1.0-rc`** consolidou as 10 tracks do **Bloco 01** (SAC como MCP Público independente, licenciado MIT, instalador stdlib-only, separação de manifestos owned/managed e CI com matriz pública).

A tag pública final **`0.1.0`** está estritamente condicionada à execução, validação e aprovação de todas as 9 tracks do **Bloco 02** listadas abaixo.

---

## Checklist de Liberação do Bloco 02 (Release Gate para 0.1.0)

- [x] **Track 01**: Truncamento de `verify:` corrigido. Evidência: Track 01, Attempt 1, approved-test `python3 -m unittest tests/test_verify_parse.py` e smoke MCP com os alvos pontuados preservados.
- [x] **Track 02**: Campo `on=` com vocabulário fechado para ARCH e parser dual. Evidência: Track 02, Attempt 1, approved-test `python3 -m unittest tests/test_trigger_on.py -v` com matriz legada e canônica.
- [x] **Track 03**: AGENTS.md e atalhos de dois níveis. Evidência: Track 03, Attempt 1, inspeção dirigida dos três `PROMPT.md` e prova CLI sem MCP.
- [x] **Track 04**: `_is_covered` avaliado contra o conjunto completo. Evidência: Track 04, Attempt 1, approved-test `python3 -m unittest tests/test_is_covered.py -v` e fixture Git manual com ordens de caminho equivalentes.
- [x] **Track 05**: Registro poliglota e dogfooding bloqueante. Evidência: Track 05, Attempt 2, approved-test `python3 -m unittest tests/test_symbol_registry.py -v` e execuções reais vermelha `87779759659` e verde `32381711142` da CI na PR #6.
- [x] **Track 06**: Caminhos relativos e medição na unidade emitida. Evidência: Track 06, Attempt 1, smoke de paridade byte a byte entre roots e medições manuais de `payload_bytes` e budget.
- [x] **Track 07**: Seleção por anchor e piso reportado. Evidência: Track 07, Attempt 1, approved-test `python3 -m unittest tests/test_fitness.py -v`, fixture manual de `assess` e paridade SHA-256 do Context.
- [x] **Track 08**: Marcadores de comentário e imperativos PT+EN. Evidência: Track 08, Attempt 1, approved-test `python3 -m unittest tests/test_markers.py -v`, prova manual do fechamento HTML e smoke MCP.
- [x] **Track 09**: Promessa honesta, política de vetos e liberação. Evidência: Track 09, Attempt 1, inspeção de `README.md`, `docs/PROJECT_POLICY.md`, `CHANGELOG.md` e deste checklist; diff de cenários e de arquivos de código vazio; gates completos registrados no handoff.

---

## Política de Transição e Veto

1. **Impedimento de Liberação Prematura**:
   Nenhuma tag `0.1.0` (sem o sufixo `-rc`) pode ser criada no repositório antes que todas as caixas acima estejam marcadas como concluídas `[x]` com a evidência citada pela track correspondente.

2. **Conclusão do Release Candidate (`0.1.0-rc`)**:
   O RC atestou a infraestrutura pública e o protocolo MCP. O checklist acima registra a conclusão do Bloco 02 e autoriza a tag final somente no commit aprovado, sem mover ou recriar uma tag que já tenha sido publicada.
