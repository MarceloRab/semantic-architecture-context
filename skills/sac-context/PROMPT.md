# SAC TAG — atalho

## Sem MCP

```bash
python3 src/sac_scan.py lookup <symbol> --root . --path <arquivo> --json
```

Use `SAC TAG` para consultar a gramática: este atalho não autoriza Write. Leia agora o [`SKILL.md`](./SKILL.md) irmão, que contém o contrato; se o caminho relativo não resolver, pare e reporte.

## Frase do usuário → contrato derivado

| Frase | Contrato derivado |
|---|---|
| `SAC` | `sac-execution-overlay`; READ/EXECUTE sem autorização de Write |
| `Implementar <mudança>` | Encaminhar para `sac-execution-overlay`, `mode=EXECUTE`; esta skill fornece apenas a gramática |
| `Corrigir bug <descrição>` | Encaminhar para `sac-execution-overlay`, `mode=EXECUTE`; esta skill fornece apenas a gramática |
| `Criar domínio <id> em <escopo>` | Encaminhar para `sac-onboard`, `mode=ASSESS` read-only |
| `Atualizar domínio <id>` | Encaminhar para `sac-onboard`, `mode=ASSESS` read-only |
| `SAC ONBOARD <id>` | `sac-onboard`, `mode=ASSESS` read-only por default |
| `SAC TAG` | `sac-context`; consultar gramática, sem autorização de Write |
| `APROVAR SAC REGISTER <id>` | `REGISTER`, somente quando o literal e as pré-condições do contrato existirem |
| `APROVAR SAC TAG_DELTA <id>` | `TAG_DELTA`, somente quando o literal, a tabela e as pré-condições do contrato existirem |

Os três atalhos são disjuntos e nenhum autoriza Write. Somente os dois literais `APROVAR` acima podem autorizá-lo nos limites do contrato.
