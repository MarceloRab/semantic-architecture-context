## Resumo

<!-- Descreva o que mudou e por quê. Mantenha entre 1-3 parágrafos. -->

## SAC-ACK (SAC override)

<!-- Apague esta seção se não houver símbolos SAC:REGR afetados. -->

Esta PR altera símbolos protegidos por SAC. Para cada símbolo explicitamente liberado, inclua uma linha exata:

```text
SAC-ACK: <symbol_name>
```

- `SAC-ACK: all` é **ignorado**.
- Só libera o símbolo explicitamente nomeado.
- Ver detalhes em `sac-context/docs/SAC_V2.md`.

## Checklist

- [ ] A mudança está no escopo aprovado.
- [ ] Símbolos SAC:REGR afetados foram consultados via MCP/CLI ou explicitamente liberados acima.
- [ ] Não há over-tagging ou tags em locais proibidos.
- [ ] CI local `sac-context/ci/sac_ci_guard.ps1` passou (ou warnings são esperados e documentados).

## Reviewers

<!-- Opcional: @mencione revisores. -->
