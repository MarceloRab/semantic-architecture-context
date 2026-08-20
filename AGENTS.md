# SAC — entrada para agentes

O Semantic Architecture Context (SAC) existe neste projeto. O manifesto e mapa de fronteiras fica em [`.sac/domains.md`](.sac/domains.md); escolha ali o `domain_id` compatível com a intenção antes de buscar código.

```text
SAC:ARCH: on=<ssot|boundary|ordering|state|exclusive|ownership> - <Symbol>: <MUST|NEVER|ONLY ...>
SAC:REGR: on=<snake_case_condition> - <Symbol>: <obrigação>; MUST verify: <target>[, ...]
SAC:DEPRECATED: on=<snake_case_condition> - <Symbol>: <restrição>; replacement: <symbol|none>
```

`files:` é **limite de busca, não fila de leitura**: abra somente o alvo e arquivos adicionais ligados por evidência objetiva.

Sem MCP, obtenha as constraints do domínio pela CLI:

```bash
python3 src/sac_scan.py context --root . --domain <domain_id> --json
```

Atalhos tool-neutral, estáveis e disjuntos:

- `SAC` → [`skills/sac-execution-overlay/PROMPT.md`](skills/sac-execution-overlay/PROMPT.md) (READ/EXECUTE, sem autorizar Write).
- `SAC ONBOARD <id>` → [`skills/sac-onboard/PROMPT.md`](skills/sac-onboard/PROMPT.md) (`ASSESS` read-only por default).
- `SAC TAG` → [`skills/sac-context/PROMPT.md`](skills/sac-context/PROMPT.md) (consultar a gramática, sem autorizar Write).

O usuário não precisa montar parâmetros internos: basta apontar a skill e declarar a intenção em linguagem natural, por exemplo `criar domínio <id> em <escopo>`, `atualizar domínio <id>`, `implementar <mudança>` ou `corrigir bug <descrição>`. O `PROMPT.md` escolhido deriva o modo, a rota e o contexto; pede somente identificadores ou escopo que realmente estiverem ausentes.

Somente `APROVAR SAC REGISTER <id>` e `APROVAR SAC TAG_DELTA <id>` autorizam os Writes definidos pelo contrato de `sac-onboard`. Se um caminho relativo de atalho não puder ser resolvido a partir da raiz, pare e reporte o caminho ausente; não tente fallback.
