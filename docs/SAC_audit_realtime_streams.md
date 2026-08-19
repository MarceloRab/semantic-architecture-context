# Auditoria SAC — domínio `realtime_streams`

**Projeto alvo:** `to_de_plantao`  
**Data:** 2026-07-24  
**Veredito:** `INSUFFICIENT` — Etapa 1 permanece em `PAUSA`; nenhuma linha está aprovada para injeção.

## Escopo e métricas

- `sac_scope`: `domain=realtime_streams`
- `context_domains_loaded`: `1` (`3` domínios apenas catalogados)
- `files_listed/files_scanned`: `6/6` — limite do domínio e scan do engine; não significa leitura humana
- arquivos efetivamente abertos:
  - `lib/app/services/institution_scoped_coordinator_service.dart`: assinatura real de `start`, warning de gramática e contrato de `_onMembershipLiveEvent`
  - `sac-context/docs/SAC_domains.md`: comparação de anchors
- `anchors_total/anchors_mapped`: `9/9` (`MCP-measured`)
- `non_anchor_tags`: `3` — `_onMembershipLiveEvent`, `start`, `stop` (`inferred` por comparação entre domínio e Discover)
- `ARCH/REGR/DEPRECATED`: `11/1/0` (`MCP-measured`)
- `REGR verify edges`: `0` (`MCP-measured`)
- `orphans`: `not_measured`; Discover não prova orphan
- `duplicate_constraints`: `not_proven`
- `domain_index_status`: `current` para membership/anchors, mas cobertura semântica insuficiente

## Evidências bloqueantes

1. Linha 284 de `institution_scoped_coordinator_service.dart`: `unsupported_sac_grammar`. O comentário está dentro do corpo do método e não pode ancorar `start`; a assinatura real é `Future<void> start(String userId)`.
2. `_onMembershipLiveEvent` está parseável na linha 820, mas usa trigger `RULE` em `REGR` e não possui `verify` terminal. Após o mirror, o MCP manteve a tag visível e emitiu `invalid_trigger tag=REGR trigger=RULE allowed=WARNING|CRITICAL` e `regr_verify_required`.
3. A tag existente contém a obrigação semântica “MUST enqueue scope mutation ...”. Qualquer proposta substituta deve preservar essa obrigação; apenas trocar trigger ou acrescentar `verify` não autoriza apagá-la.
4. Não existe decisão arquitetural comprovada suficiente para redigir uma tag canônica de `start`. `ARCH` exige `RULE|CONSTRAINT`, ao menos um de `MUST|NEVER|ONLY` e posição imediatamente acima da assinatura real.

## Autoridade de propagação

- Runtime/docs: `C:\Users\Rabelo\projects\rabelo-standards\sac-context`
- Skills: os 3 bundles canônicos em `C:\Users\Rabelo\projects\rabelo-standards\skills\catalog\domains\context-governance`
- Cópias no filho e em `templates/project-base` são artefatos derivados; nunca fonte, fallback ou autoridade do mirror.

## Fechamento da Etapa 1

Não há proposta literal aprovada neste relatório. Antes da Etapa 2, uma nova proposta deve:

- provar a regra arquitetural real de `start` e posicioná-la acima da assinatura;
- preservar integralmente a obrigação atual de `_onMembershipLiveEvent` e justificar alvos `verify` observáveis, incluindo a relação com `hydrateNow` e `_rebindScopedListeners` quando aplicável;
- retornar sem warnings canônicos no lookup de cada símbolo.

**PAUSA:** aguardar nova proposta literal e aprovação humana. É proibido editar código, `SAC_domains.md`, drawer ou índice a partir deste relatório.
