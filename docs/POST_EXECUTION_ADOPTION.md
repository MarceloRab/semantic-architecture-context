# Report pós-execução: adoção e atualização segura

## Objetivo e ordem obrigatória

Este report define duas etapas separadas:

1. testar o SAC `0.1.0` em um projeto novo e representativo;
2. somente depois de cumprir os critérios de estabilidade deste documento,
   atualizar um consumidor que ainda usa uma cópia antiga, como
   `to_de_plantao` ou `api_robot`.

Passar nos testes do repositório SAC não garante sozinho a estabilidade de um
consumidor. A promoção depende das evidências do piloto, de uma janela de
observação e de rollback ensaiado. Os consumidores legados não devem ser
atualizados em paralelo com o piloto.

## 1. Preparar uma versão imutável

Use a tag anotada e confirme o commit antes de qualquer teste externo:

```bash
git fetch --tags <remote-sac>
git -C /caminho/para/semantic-architecture-context cat-file -t 0.1.0
git -C /caminho/para/semantic-architecture-context rev-list -n 1 0.1.0
```

O tipo deve ser `tag` e o commit esperado para esta release é
`5645b2171c0adf65165acdc3fad7dbed738729b6`. Não mova nem recrie a tag. Se o
remote apontar para outro commit, interrompa a adoção.

## 2. Testar em um projeto novo

### 2.1 Criar o piloto

Escolha um projeto descartável, mas representativo das linguagens e do CI dos
consumidores. Comece em um repositório limpo e registre o baseline:

```bash
mkdir sac-pilot && cd sac-pilot
git init
printf '# SAC pilot\n' > README.md
git add README.md && git commit -m 'baseline before SAC'
git rev-parse HEAD > ../sac-pilot.baseline
```

No checkout imutável do SAC `0.1.0`, valide os runtimes e inicialize o piloto:

```bash
cd /caminho/para/semantic-architecture-context
git checkout 0.1.0
python3 install.py --check-only --json
python3 install.py --target /caminho/para/sac-pilot --json
```

O instalador deve criar apenas o bootstrap ausente e nunca sobrescrever um
`.sac/domains.md` owned preexistente. Revise e versione o diff antes de seguir.

### 2.2 Criar o primeiro domínio com aprovação explícita

No piloto, invoque `SAC ONBOARD <domain_id>` em modo ASSESS, informando o menor
escopo causal. ASSESS é read-only. Somente depois de revisar a proposta, autorize
o registro com a frase literal:

```text
APROVAR SAC REGISTER <domain_id>
```

Se forem necessárias tags, revise a tabela `ADD|REPLACE|REMOVE` e autorize
separadamente:

```text
APROVAR SAC TAG_DELTA <domain_id>
```

Não substitua essas aprovações por “ok”, aceite implícito ou escrita manual
automatizada.

### 2.3 Executar o protocolo do piloto

```bash
SAC=/caminho/para/semantic-architecture-context
PILOT=/caminho/para/sac-pilot

python3 "$SAC/src/sac_scan.py" list-domains --root "$PILOT" --json
python3 "$SAC/src/sac_scan.py" validate --root "$PILOT"
python3 "$SAC/src/sac_scan.py" index-build --root "$PILOT"
python3 "$SAC/src/sac_scan.py" context --root "$PILOT" --domain <domain_id> --json
python3 "$SAC/src/sac_scan.py" capillarity --root "$PILOT" --domain <domain_id> --json
```

Depois, produza dois commits de fixture no piloto:

1. altere um símbolo protegido sem coeditar o alvo de `verify:` e confirme que
   `diff-check` bloqueia;
2. coedite exatamente o alvo declarado, sem `SAC-ACK`, e confirme que o mesmo
   comando passa.

```bash
python3 "$SAC/src/sac_scan.py" diff-check --root "$PILOT" --base HEAD^
```

Repita o fluxo no CI real do piloto. Guarde links para uma execução bloqueada e
uma execução aprovada, junto com os SHAs e os payloads JSON dos comandos acima.

## 3. Critérios para declarar o piloto estável

Todos os itens são obrigatórios:

- tag e commit do SAC verificados e imutáveis;
- instalação repetida idempotente, com diff vazio na segunda execução;
- `.sac/domains.md` preservado byte a byte pela reinstalação;
- `validate`, `index-build`, `context` e smoke do host MCP sem erro inesperado;
- fixture negativa bloqueada e fixture positiva aprovada localmente e no CI;
- nenhuma ocorrência de fallback silencioso ou `continue-on-error` no gate;
- sete dias corridos ou dez PRs reais do piloto, o que for maior, sem falso
  negativo conhecido nem incidente bloqueante;
- tempos e tamanho de payload dentro dos limites acordados para o consumidor;
- equipe capaz de explicar o co-edit gate e usar `SAC-ACK` por símbolo;
- rollback executado uma vez em ensaio e restauração do baseline confirmada.

Falha em qualquer item mantém os projetos legados congelados. Registre o defeito,
corrija-o primeiro no SAC, gere nova versão imutável e reinicie a janela de
observação; não abra exceção silenciosa.

## 4. Atualizar `to_de_plantao` ou `api_robot`

Atualize um consumidor por vez. Comece pelo de menor risco e use uma PR dedicada,
sem mudança funcional da aplicação no mesmo diff.

### 4.1 Inventário e backup verificável

```bash
TARGET=/caminho/para/to_de_plantao   # ou /caminho/para/api_robot
cd "$TARGET"
git switch -c chore/upgrade-sac-0.1.0
git status --short
git rev-parse HEAD > ../sac-upgrade.baseline
find . -maxdepth 4 -type d -name 'sac-context' -print
find . -maxdepth 4 -type f \( -name 'domains.md' -o -name 'SAC_domains.md' \) -print
sha256sum .sac/domains.md > ../sac-domains.before.sha256
```

Adapte o último caminho se o projeto ainda usar o nome legado. Pare se o
worktree não estiver limpo, se houver mais de uma fonte SAC sem owner definido ou
se não for possível identificar o manifesto owned.

### 4.2 Atualização controlada

Execute primeiro `install.py --check-only`. Depois atualize os arquivos managed a
partir do checkout verificado de `0.1.0`; preserve o manifesto owned e qualquer
configuração do host como decisão explícita do consumidor:

```bash
SAC=/caminho/para/semantic-architecture-context
python3 "$SAC/install.py" --check-only --json
python3 "$SAC/install.py" --target "$TARGET" --json
sha256sum -c ../sac-domains.before.sha256
git diff --check
git diff --stat
```

Não copie o manifesto template sobre o manifesto do consumidor. Tags legadas
continuam visíveis pelo parser dual; migre-as para `on=` somente por delta revisado
e pela autorização literal `APROVAR SAC TAG_DELTA <domain_id>`, nunca como efeito
colateral do upgrade.

### 4.3 Validação antes do merge

Rode no consumidor os mesmos comandos do piloto para cada domínio e compare com o
baseline antigo:

```bash
python3 "$SAC/src/sac_scan.py" list-domains --root "$TARGET" --json
python3 "$SAC/src/sac_scan.py" validate --root "$TARGET"
python3 "$SAC/src/sac_scan.py" index-build --root "$TARGET"
python3 "$SAC/src/sac_scan.py" context --root "$TARGET" --domain <domain_id> --json
python3 "$SAC/src/sac_scan.py" diff-check --root "$TARGET" --base <baseline-sha>
```

Exija CI verde, revisão do owner do projeto, manifesto com hash preservado e a
mesma prova negativa/positiva do co-edit gate. Se o projeto usar MCP, valide ainda
uma consulta real no host configurado; teste de CLI não substitui o teste do host.

### 4.4 Rollout e rollback

Faça merge em janela observada. Não atualize o segundo consumidor até o primeiro
cumprir novamente a janela de estabilidade definida na seção 3.

Vetos de rollout: manifesto owned alterado sem aprovação, domínio ausente,
warning novo sem classificação, divergência CLI↔MCP, fixture negativa passando,
fixture positiva bloqueada, CI mascarado ou rollback não ensaiado.

Em caso de veto ou incidente, reverta a PR inteira para o SHA salvo em
`sac-upgrade.baseline`; não misture arquivos managed novos com o engine antigo.
Confirme depois do rollback o hash do manifesto, os testes do consumidor e o
estado do host MCP. O owner de `to_de_plantao` ou `api_robot` decide o rollback;
o mantenedor do SAC diagnostica o produto, sem alterar silenciosamente o projeto
consumidor.

## Evidência final por consumidor

O report da PR de atualização deve conter: versão e commit exatos do SAC, SHA do
baseline do consumidor, hash do manifesto antes/depois, lista de arquivos managed,
comandos e resultados, links da CI negativa e positiva, resultado do teste MCP,
janela observada, responsáveis por rollout/rollback e decisão final `GO` ou `NO-GO`.
