# SAC — atalho de execução

## Sem MCP

```bash
python3 src/sac_scan.py list-domains --root . --json
python3 src/sac_scan.py context --root . --domain <id> --json
```

Use `SAC` para ativar `sac-execution-overlay` em READ/EXECUTE, sem autorização de Write. Leia agora o [`SKILL.md`](./SKILL.md) irmão, que contém o contrato; se o caminho relativo não resolver, pare e reporte.

## Frase do usuário → contrato derivado

| Frase | Contrato derivado |
|---|---|
| `SAC` | `sac-execution-overlay`; READ/EXECUTE sem autorização de Write |
| `Implementar <mudança>` | `mode=EXECUTE`; derivar Route da intenção, carregar Context e verificar o alvo antes de editar |
| `Corrigir bug <descrição>` | `mode=EXECUTE`; derivar Route da descrição, carregar Context e verificar código/teste causal antes de editar |
| `Entender` / `explicar <código ou arquitetura>` | `mode=READ`; derivar Route, carregar Context e responder sem Write |
| Só apontar este `PROMPT.md` sem uma intenção | **PAUSE**; perguntar se deseja implementar, corrigir bug ou consultar código; zero busca até a resposta |
| `Criar domínio <id> em <escopo>` | Encaminhar para `sac-onboard`, `mode=ASSESS` read-only; não implementar nem escrever tags |
| `Atualizar domínio <id>` | Encaminhar para `sac-onboard`, `mode=ASSESS` read-only; não implementar nem escrever tags |
| `SAC ONBOARD <id>` | `sac-onboard`, `mode=ASSESS` read-only por default |
| `SAC TAG` | `sac-context`; consultar gramática, sem autorização de Write |
| `APROVAR SAC REGISTER <id>` | `REGISTER`, somente quando o literal e as pré-condições do contrato existirem |
| `APROVAR SAC TAG_DELTA <id>` | `TAG_DELTA`, somente quando o literal, a tabela e as pré-condições do contrato existirem |

Os três atalhos são disjuntos e nenhum autoriza Write. Somente os dois literais `APROVAR` acima podem autorizá-lo nos limites do contrato.

Não exigir que o usuário forneça `mode`, `domain_id` ou nomes de ferramentas quando a intenção permite derivá-los pelo Route. Perguntar apenas quando a rota for ambígua ou faltar o recorte objetivo exigido pelo contrato.

1. Route antes do primeiro Read; um intent carrega um Context, zero usa `bounded-unmapped`, múltiplos param.
2. `files:` é limite de busca, não fila de leitura; Verify/Discover são focados e Capillarity é somente on-demand.
3. Warning canônico, erro de rota/membership/path ou MCP+CLI indisponíveis em alvo tagueado exigem parada conforme o contrato.
4. Gate e reporte escopo, arquivos abertos com motivo, risco deprecated, staleness e performance.

Pipeline: boot → Route → Context ou bounded-unmapped → Verify/Discover → Capillarity(on-demand) → Gate.
