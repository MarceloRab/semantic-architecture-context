Ative sac-execution-overlay. Contrato COR-GATE (tags = SSOT; MCP = cérebro de busca):

0. Qualquer intenção de código/arquitetura → `list_sac_domains()` antes do primeiro Read.
1. Exatamente 1 intent → auto-route + `get_sac_context`; zero → `sac_scope: unmapped` + busca bounded; múltiplos → HALT.
2. Sem domínio: `fd` só em diretórios objetivos, depois `rg` scoped e `bat` por intervalo; sem limite objetivo → HALT.
3. `rg` scoped é permitido; nunca contornar busca ampla bloqueada com PowerShell equivalente.
4. Domínio resolvido → carregar Context uma vez para esse único domínio: anchors + todas `REGR`/`DEPRECATED` + hop1; cachear por sessão.
5. `context_payload_too_large` / `payload_warn=OVER_BUDGET` → zero constraints no Context; MUST `discover_sac` + `get_sac_constraints`; MUST NOT thin `files:`/tags/claims; sem truncar.
6. Alvo conhecido → `get_sac_constraints(symbol, filepath, domain_id)`; erro de rota/membership/path → PARAR.
7. MCP down → CLI+jq anunciado com o mesmo contrato; nunca fingir MCP OK.
8. Reportar `sac_scope`, `context_domains_loaded=1|0`, `search_scope`, `files_scanned` separado de arquivos abertos+motivo, `deprecated_risk`, `domain_index_status`, evidência e `sac_perf`; non-anchor ≠ orphan e inferência ≠ evidência.
9. `domain.files` é limite de busca, não fila: abrir só o alvo primário e arquivos adicionais com motivo objetivo (`verify`/hop1, import/chamada direta ou staleness).
10. Tag parseada pode ser não canônica: warning canônico ou item `REGR verify` fora de `[A-Za-z_][A-Za-z0-9_.$-]*` → `INSUFFICIENT`/HALT; nunca inventar correção.
11. Missing anchor/file ou alvo necessário fora do domínio → `suspected_stale`; encaminhar `sac-onboard mode=ASSESS`, nunca auto-write.
12. REGISTER só indexa; TAG_DELTA é o único modo que altera tag e exige comando+tabela literais. EXECUTE material fora do domínio → HALT.
13. `lookup --pre-onboard` é exclusivo do `sac-onboard` com scope explícito; nesta overlay → HALT.
14. Capillarity **cold path** only — nunca boot READ/EXECUTE; onboard ASSESS ou auditoria explícita; **proibido revert** por capillarity.
15. DoD: get_sac_context missing=[] → responder/editar; sem turno 2 de auditoria de agente.

Pipeline: boot → list_sac_domains → get_sac_context → Verify se alvo → edit/read. Onboard = sac-onboard separado.
15. `domain.files` é limite de busca, não fila; proibido abrir todos os arquivos listados.

Pipeline: boot → Route → Context ou bounded-unmapped → Verify/Discover → Capillarity(on-demand) → Gate.
