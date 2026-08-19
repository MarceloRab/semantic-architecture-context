# SAC — Report de Melhoria: Gate de Injeção de Tags em Código Fonte (`sac-onboard`)

**Data:** 2026-07-24  
**Origem:** auditoria do delta `realtime_streams` em `to_de_plantao`  
**Destino canônico:** `rabelo-standards/sac-context` + bundles SAC canônicos do catalog; template é snapshot derivado  
**Status:** IMPLEMENTADO, VALIDADO E ESPELHADO NO PILOTO  

## 1. Causa raiz confirmada

O agente fechou o manifesto (`SAC_domains.md`), drawer e índice sem injetar tags físicas no fonte. O MCP/CLI funcionou como projetado: é read-only e deriva constraints exclusivamente de comentários SAC existentes no código. A skill destacava o closeout, mas não bloqueava a Etapa 3 quando a Etapa 2 não havia produzido evidência física.

## 2. Correção canônica

1. **Autoria controlada:** o agente pode propor apenas linhas ARCH/REGR/DEPRECATED sob a gramática existente. O humano aprova o texto literal; o agente não cria tipos/triggers nem reformula a linha durante a injeção.
2. **HARD GATE:** delta estrutural exige tabela exata `Arquivo | Assinatura do Símbolo | Linha de Tag Proposta | Justificativa`, aprovação literal, injeção física e lookup `found=true` antes de editar domínio, drawer ou índice.
3. **Arquivo novo:** `lookup --pre-onboard --path <arquivo>` é CLI-only e bounded ao arquivo explícito. Rejeita `--domain`, path ausente e path fora da raiz; não pode ser usado em READ/EXECUTE.
4. **Consistência:** `validate` emite `UNMAPPED_ANCHOR_SYMBOL` quando um `anchor_symbols` não possui tag física correspondente nos `files:` do domínio.
5. **Delta administrativo:** não cria tags e só fecha sem `UNMAPPED_ANCHOR_SYMBOL` para anchors remanescentes.

## 3. Escopo deliberado

`EMPTY_DOMAIN_FILE` não foi implementado nesta trilha: um arquivo de domínio pode ser suporte legítimo sem tag própria, e essa regra não constava nas ações explicitamente aprovadas. Adicioná-la exigiria contrato separado para evitar falso positivo.

## 4. Definition of Done

1. Skill e prompts de `sac-onboard` bloqueiam Etapa 3 até `injection_gate: PASS`.
2. CLI valida arquivo novo sem relaxar membership normal.
3. `validate` reporta anchor declarado sem tag física.
4. `SAC_V2`, `SAC_validate`, `sac-context`, overlay e `sac-evolution` descrevem o mesmo contrato.
5. Smoke cobre o caminho positivo, anti-bypass e warning.
6. Mirror usa somente a fonte canônica do pai, rejeita template/fonte alternativa e preserva `SAC_domains.md` do filho.
7. Nenhuma tag de aplicação é criada sem aprovação literal humana.

## 5. Fechamento observado

- Smoke do pai: PASS.
- O template foi sincronizado naquela execução como snapshot derivado; isso não lhe confere autoridade. O contrato atual fixa o mirror em `rabelo-standards/sac-context` + bundles canônicos.
- Mirror `to_de_plantao`: idempotente (`0 changed`, `27 unchanged`) e `SAC_domains.md` preservado pelo hash `4F3FEE323A2ED6C14E72152C448A08CBA0B621D347B320A60AA6BD5723864A72`.
- Smoke do filho: PASS.
- Auditoria do filho: `0` orphans e `15` warnings `UNMAPPED_ANCHOR_SYMBOL`; 7 pertencem a `realtime_streams`. Nenhuma tag de aplicação foi criada ou alterada.
- Riscos adicionais observados, fora desta correção: uma linha `unsupported_sac_grammar` e validação AST Dart indisponível sem tree-sitter no host.
