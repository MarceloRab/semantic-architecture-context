# Design — Bloco 01: SAC como MCP público

## Objective

`C:\Users\Rabelo\projects\semantic-architecture-context` passa a ser um repositório git público, autocontido e licenciado, em que uma pessoa desconhecida, numa máquina limpa, consegue: clonar, rodar um installer, registrar o servidor MCP no seu host, obter constraints do seu próprio projeto, e abrir PR com CI verde executando a partir de um fork.

Ao fim do bloco o repositório está em `0.1.0-rc`, com tag anotada e release **bloqueado** por `RELEASE_GATE.md`. A tag pública `0.1.0` é ato do Bloco 02.

Estado observável final:

1. `git log` do repositório público não contém nenhum commit importado de `rabelo-standards`, nenhum `.pyc`, nenhuma string `C:\Users\` e nenhuma menção a `rabelo-standards` em arquivo rastreado.
2. Existe exatamente **uma** superfície MCP.
3. Existe exatamente **uma** fonte de versão.
4. O manifesto do projeto do consumidor (`owned`) reside fora de toda árvore que o installer escreve (`managed`).
5. Todo payload que tenha operado com um HALT relaxado declara isso explicitamente.
6. Falha de uso/ambiente da CLI chega ao agente como erro de ambiente, não como falha de lookup.
7. `mcp/smoke.mjs` passa no repositório público com paridade CLI ≡ MCP preservada.

## Non-goals

- Qualquer correção funcional dos pilares: F1 (ordem em `_is_covered`), truncamento de `verify:` no ponto, ADR do campo `trigger` (`on=…`), `_SYMBOL_REGISTRY` além de `.dart`/`.ps1`, path relativo no payload (F4), unidade de bytes (F5), `AGENTS.md` como porta de entrada (F7/A3), marcadores de comentário (F10). **Todos são Bloco 02.**
- M9 além dos dois itens que impedem publicação (caminho absoluto no artefato de atalho; colisão de gatilho no frontmatter). Nome único `PROMPT.md`, tabela frase→contrato, bloco "sem MCP", item 15 duplicado: Bloco 02.
- Migração para MCP SDK v2 (T5). Fora do bloco e, após D12, sem custo de breaking change para justificar pressa.
- Streamable HTTP, worker persistente, cap global de concorrência, ceilings físicos de stdout/stderr. Permanecem `DEFERRED`/`GATED`.
- Publicação em npm ou PyPI.
- Layer A de testes unitários do engine. É pré-requisito declarado do Bloco 02, não deste.
- Qualquer reescrita do engine. O transplante do Bloco 01 é verbatim por contrato (ver O2).
- Publicação da skill `sac-evolution` (ver D9).
- **Migração de qualquer consumidor existente** (`api_robot`, `to_de_plantao`) e qualquer alteração em `rabelo-standards`. Decisão do usuário: a transferência ocorre só após testes estáveis pós-Bloco 02. Ver D15.

## Closed decisions

- **D1 — Destino e histórico.** O repositório público é `semantic-architecture-context`, inicializado com `git init` e **histórico do zero**. Os 52 commits de `rabelo-standards` não são importados. | Why: V3 §1.8 exige varredura de segredos e de artefatos de build sobre histórico não auditado; iniciar limpo elimina o custo inteiro em vez de pagá-lo, e é subtrativo. `rabelo-standards` permanece privado e continua existindo.

- **D2 — Licença e contribuição.** MIT, sem CLA. `CONTRIBUTING.md` + `GOVERNANCE.md` + `.github/PULL_REQUEST_TEMPLATE.md`. | Why: decisão do usuário; máxima adoção, coerente com o objetivo "qualquer um pode baixar e abrir PR".

- **D3 — Distribuição.** `git clone` + `python install.py` local. Nenhum registry na 0.1.0. | Why: decisão do usuário; menor superfície de release, coerente com ADR-008/ADR-010 (0.x antes do hardening).

- **D4 — Installer único em Python stdlib.** `install.py` na raiz, um arquivo, sem `install.ps1`/`install.sh`. | Why: Python já é requisito duro do engine, então o installer não adiciona runtime nenhum; um arquivo cobre Windows, Linux e macOS, contra dois dialetos de shell divergentes. O installer **não edita** arquivos de configuração do host MCP — ele valida o ambiente, cria `.sac/domains.md` a partir do template quando ausente, e **imprime** o bloco de config para o usuário colar.

- **D5 — Superfície MCP única: deletar `src/sac_mcp_server.py`.** | Why: sua semântica diverge do adapter Node (sem gate de membership, sem PAUSE de `filepath_required`, `root=os.getcwd()`), de modo que a paridade CLI≡MCP **já é falsa hoje** para um dos dois adapters. Marcação "LEGACY" em docstring não é gate. É também o único arquivo Python com dependência de terceiros: deletá-lo restaura o contrato stdlib-only integralmente e remove uma superfície de release Python inteira. A CLI já é o fallback de debug documentado. | Rejeitada: manter e submeter aos mesmos gates — contradiz C2/DP-1 e duplica todo o custo de gate por um caminho que ninguém usa em produção.

- **D6 — SSOT de versão: `mcp/package.json` → `version`.** `server.mjs` passa a ler esse valor em vez do literal `"1.6.0"`. `sac_scan.py --version` lê o mesmo arquivo com `json` da stdlib. A versão pública **reinicia em `0.1.0`**. | Why: rung "já existe no repositório" — `package.json` já carrega um campo `version` canônico para o ecossistema Node, e ler um JSON custa uma linha em Python. Criar um `VERSION` novo adicionaria arquivo sem remover nenhum. Os números `1.0.0`/`1.6.0` eram identidade interna e não descrevem nenhum contrato público.

- **D7 — Separação `managed` / `owned` por mudança de caminho.**
  - `templates/domains.template.md` — template + schema + manual COR-3. `managed`, sempre atualizado pelo installer.
  - `<root>/.sac/domains.md` — manifesto do projeto. `owned`, o installer nunca sobrescreve depois de criado.
  - `_DOMAINS_REL` passa a `.sac/domains.md`.
  | Why: hoje o único arquivo `owned` mora dentro da árvore `managed`, e a resolução por exclusão de nome no mirror congela schema, template e manual na versão do dia do bootstrap, em todo projeto filho, permanentemente. É regressão silenciosa já em produção, e é o que impede o dogfooding. Depois de publicar, o custo multiplica pelo número de consumidores — logo é agora ou nunca. | Rejeitada: manter o caminho e resolver por exclusão de nome — é exatamente o mecanismo que produz a regressão.

- **D8 — Atestação de gates no payload.** Toda resposta que operou com pelo menos um `SAC_ALLOW_*` ativo inclui `gates_bypassed: [<nome>, …]` e um warning correspondente. Quando nenhum escape está ativo o campo é **omitido**, custo zero de bytes no caminho normal. Vale para CLI e MCP identicamente (paridade). `mcp/smoke.mjs` cobre cada escape ligado. | Why: com host semi-confiável, os três escapes são configuráveis pelo bloco `env` do arquivo de config do host e valem para todas as chamadas; hoje o payload permissivo é indistinguível do gated e o agente não tem como saber se a resposta respeitou o contrato de domínio. Omitir quando vazio evita que uma correção de segurança vire imposto no pilar 1. | Rejeitada: remover os escapes — eles têm uso legítimo de CI/debug; o defeito é a ausência de atestação, não a existência.

- **D9 — `sac-evolution` não é publicada na 0.1.0.** O repositório público ganha `GOVERNANCE.md` (como o padrão evolui, como propor mudança via issue → ADR → PR) e `docs/adr/`. A skill permanece privada em `rabelo-standards`. | Why: sua matriz de impacto e o contrato "Propagação" (`templates/project-base`, `mirror`, `propagation_status`, `.cursorrules` do pai, `skills_registry.json`) são estruturalmente sobre topologia de monorepo, não sobre governança de padrão; publicá-la exporta a topologia privada e reescrevê-la é reautoria, não remoção. A necessidade pública real — "como proponho uma mudança" — é atendida por `GOVERNANCE.md` + ADR. Reautoria fica fora do caminho crítico.

- **D10 — Skills publicadas: `sac-context`, `sac-onboard`, `sac-execution-overlay`.** Do M9, o Bloco 01 aplica **apenas** os dois itens que impedem publicação: (a) remoção de todo caminho absoluto de máquina e de toda menção a `rabelo-standards` nos artefatos de atalho, com resolução de irmão sempre relativa; (b) desambiguação das descrições de frontmatter de `sac-context` (*gramática e escrita de tag*) e `sac-execution-overlay` (*gate de execução*), hoje quase idênticas. | Why: (a) é a primeira instrução que o agente lê e é irresolúvel em qualquer consumidor — mesma classe dos `.pyc`, em lugar pior. (b) publicar duas skills que disputam o mesmo gatilho entrega ao usuário externo um roteador que adivinha. O resto do M9 é ergonomia e vai ao Bloco 02.

- **D11 — Terceira classe de erro.** Todo caminho que hoje retorna exit 2 escrevendo só em stderr passa a emitir JSON estruturado em stdout com `code` da família `sac.environment.*` (root inexistente, root não é diretório, uso inválido, python ausente). O adapter mapeia para `sac.environment_error` em vez de `lookup_failed`/`context_failed`. | Why: o modelo de duas classes (`sac.` semântica / `mcp.` transporte) descreve um sistema que tem três; a terceira é justamente a mais provável na primeira instalação de um usuário desconhecido, que é o cenário central de um projeto público.

- **D12 — Pisos de runtime declarados: Python ≥ 3.11, Node ≥ 22.** Matriz de CI prova ambos. | Why: nenhum módulo usa sintaxe acima de 3.9 (verificado: sem `match`, sem `tomllib`, sem `removeprefix`; `from __future__ import annotations` em todos), logo 3.11 é escolha de política de suporte, não restrição técnica — e 3.9/3.10 estão fora de suporte. Node 18 (declarado hoje) está fora de suporte. Fixar Node 22 na 0.1.0 custa zero porque não existe base pública instalada, e **remove por completo** a objeção que travava a ordem T5/T6: a migração de SDK deixa de arrastar um MAJOR de Node.

- **D13 — CI pública endurecida por recurso nativo, não por número inventado.** `pull_request` (nunca `pull_request_target`), `permissions: contents: read` explícito, sem segredos, `timeout-minutes` no job, e o corpo da PR entregue ao processo por passo intermediário com `env:` em vez de interpolação de expressão. | Why: publicar cria um ator novo — "autor de fork PR" — que executa parsing próprio sobre conteúdo hostil. `timeout-minutes` limita ReDoS de forma determinística e nativa; inventar um cap de bytes por arquivo seria heurística sem medição. Endurecimento de regex fica condicionado a medição, no Bloco 02.

- **D14 — Nenhum job de `diff-check` na CI do Bloco 01.** A CI pública roda `validate`, `index-build` e os gates de higiene. O job de `diff-check` entra no Bloco 02, junto com F1 e F3. | Why: hoje `diff-check` faz `FAIL CLOSED` em Python e produz falso positivo sistemático quando o alvo `verify:` está em `test/`. Ligá-lo agora publicaria um gate que bloqueia mudanças corretas; ligá-lo "não-bloqueante" seria fallback silencioso. Ausência explícita é a única forma honesta.

- **D15 — Nenhum consumidor existente é migrado neste bloco nem no Bloco 02.** Os consumidores reais do SAC hoje são `api_robot` e `to_de_plantao`, cada um com sua própria cópia de `sac-context/` e seu manifesto no layout legado (`sac-context/docs/SAC_domains.md`). `rabelo-standards` **não** é consumidor: é base propagadora de recursos operacionais, e não possui manifesto de projeto. Nenhum dos três é tocado. | Why: decisão do usuário — a transferência para os consumidores acontece só depois de testes estáveis pós-Bloco 02. Migrar agora acoplaria a estabilização do produto público à correção de dois projetos em produção, sem ganho para nenhum dos dois. Consequência aceita e desejada: os consumidores continuam rodando sua cópia congelada, isolados de tudo que estes dois blocos fazem. O que este bloco entrega para eles é o caminho de migração pronto e explícito — a linha `domains_manifest_legacy_layout` da matriz de D7 é exatamente o erro que cada um receberá, com a ação de recuperação, quando o dono decidir migrar.
  | Corolário sobre dogfooding: como `rabelo-standards` nunca foi consumidor, "o SAC não faz dogfooding" deixa de ser dívida dele e passa a ser responsabilidade do repositório público sobre si mesmo — coberto pelo Bloco 02, que liga o `diff-check` bloqueante na CI do próprio repositório.

## Selected solution

- **Approach.** Transplante fiel seguido de correções cirúrgicas, nesta ordem, sem reescrita. O repositório público nasce como cópia verbatim de `sac-context/` (menos `sac_mcp_server.py` e menos `__pycache__/`), com `mcp/smoke.mjs` verde como prova de equivalência comportamental **antes** de qualquer mudança de comportamento. Só então entram as sete correções de publicação: superfície MCP única, SSOT de versão, relocação do manifesto, atestação de gates, terceira classe de erro, installer e CI de fork. A arquitetura de camadas (semântica em Python, adapter Node fino, paridade CLI≡MCP) é preservada integralmente.

- **Why best.** O risco dominante identificado pelos três relatórios é transformar a publicação numa reescrita prematura; o risco simétrico, identificado pelo V3, é publicar sem auditar e congelar defeitos privados como contratos públicos. Transplante-verbatim-primeiro ataca os dois: o smoke verde no repo novo isola "mudei de lugar" de "mudei de comportamento", e cada correção subsequente é um diff pequeno com um gate próprio. As sete correções escolhidas são exatamente as que a publicação torna irreversíveis — caminho do manifesto, identidade de versão, número de superfícies MCP, semântica de erro, licença, histórico. Depois de existir um consumidor externo, cada uma delas passa a custar um MAJOR.

- **Rejected viable alternative 1: publicar depois de corrigir os pilares (ordem do V4 §9).** | Reason: o V4 coloca F1/F4/F5/F8/F3/Layer A antes de T2/T3. Isso funciona como ordem de engenharia, mas colapsa a divisão em dois blocos pedida pelo usuário e mantém o veículo de entrega bloqueado por trabalho funcional de custo aberto. A decisão tomada preserva a intenção do V4 sem colapsar os blocos: o veículo é construído inteiro no Bloco 01 e o **release** — não a construção — fica gateado pelos P0 do Bloco 02 via `RELEASE_GATE.md`.

- **Rejected viable alternative 2: publicar 0.1.0 já, com limitações documentadas.** | Reason: o defeito de ordenação do `_is_covered` produz falso positivo sistemático no layout `lib/` + `test/`, cuja única saída é `SAC-ACK` no corpo da PR. Publicar isso ensina o bypass ao primeiro contributor externo e corrói a disciplina que o pilar 2 existe para criar. Documentar não neutraliza um gate que treina o hábito contra si mesmo.

- **Rejected viable alternative 3: manter o manifesto em `sac-context/docs/` e resolver por exclusão de nome no installer.** | Reason: é o mecanismo atual, e é a causa da regressão silenciosa em produção (consumidor congelado no schema do dia do bootstrap). Preserva o defeito e o exporta para todo consumidor público.

- **Executor latitude:** apenas escolhas mecânicas. Nenhuma abordagem alternativa, nenhuma heurística, nenhuma decisão semântica.

## Contracts and prohibitions

- **C1** — Must: após O2, `mcp/smoke.mjs` passa no repositório público com o mesmo veredicto que no de origem. | Must not: nenhuma alteração de comportamento dentro de O2. | Evidence: execução do smoke nos dois repositórios, saídas comparadas.
- **C2** — Must: a semântica permanece exclusivamente em Python; `mcp/server.mjs` continua fino. | Must not: mover regra, parsing ou decisão de gate para o Node. | Evidence: diff de `server.mjs` limitado a versão, mapeamento de erro e atestação.
- **C3** — Must: engine e CLI permanecem stdlib-only. | Must not: qualquer import de terceiros em `src/`. | Evidence: gate de CI que falha em import fora da stdlib em `src/`.
- **C4** — Must: paridade CLI ≡ MCP vale também para os campos novos (`gates_bypassed`, erros `sac.environment.*`). | Must not: campo que exista em um adapter e não no outro. | Evidence: casos novos em `mcp/smoke.mjs`.
- **C5** — Must: `.sac/domains.md` é `owned` e nunca é sobrescrito por `install.py` depois de existir. | Must not: installer escrever em qualquer caminho `owned`. | Evidence: teste do installer com manifesto pré-existente modificado; conteúdo inalterado após reexecução.
- **C6** — Must: nenhum arquivo rastreado contém `C:\Users\`, nome de máquina, ou `rabelo-standards`. | Must not: `.pyc`, `__pycache__/`, `node_modules/` rastreados. | Evidence: gate de higiene na CI, falha dura.
- **C7** — Must: existe exatamente uma fonte de versão e a CI a verifica. | Must not: literal de versão em `server.mjs` ou em qualquer skill. | Evidence: gate de CI comparando `package.json` com o que o servidor anuncia e com `--version` da CLI.
- **C8** — Must: existe exatamente um servidor MCP no repositório público. | Must not: reintroduzir adapter Python. | Evidence: inventário no `AUDIT.md` + ausência de `FastMCP` em qualquer arquivo rastreado.
- **C9** — Must: o README declara o `diff-check` como **co-edit gate** e lista as linguagens suportadas (`.dart`, `.ps1`) como limitação corrente conhecida. | Must not: prometer "prevenção de regressão" como prova de teste. | Evidence: revisão do README contra o `RELEASE_GATE.md`.
- **C10** — Must: `RELEASE_GATE.md` enumera nominalmente os P0 do Bloco 02 que liberam a tag `0.1.0`. | Must not: tag `0.1.0` (sem `-rc`) criada dentro deste bloco. | Evidence: `git tag` mostra apenas `0.1.0-rc`.

## Risk-specific requirements

- **R1** — Risk: o transplante altera comportamento sem que ninguém perceba, porque não existe Layer A de testes unitários (`test_*.py` sob `sac-context/`: zero). | Required protection: O2 é verbatim e sua aceitação é o smoke verde; nenhuma outra alteração compartilha commit com o transplante. | Proof: diff de O2 contém apenas movimentação de arquivos e remoções declaradas; smoke executado antes e depois.
- **R2** — Risk: a relocação do manifesto (D7) é breaking para `sac_domains.py`, `sac_scan.py`, `sac-onboard`, `sac-execution-overlay` e docs dentro do repositório público — e será breaking para `api_robot` e `to_de_plantao` no dia em que eles migrarem. | Required protection: mapa de estados antigos fechado (seção seguinte), erro explícito e recuperável, zero fallback silencioso. Como nenhum consumidor é migrado agora (D15), a proteção que importa é a **qualidade da mensagem de recuperação**: ela é o único artefato que o dono de `api_robot`/`to_de_plantao` receberá quando migrar. | Proof: execução contra fixture em layout legado devolve o código de erro com a ação de recuperação literal; execução contra layout novo devolve o manifesto.
- **R3** — Risk: publicar cria o ator "autor de fork PR", que executa parsing próprio do repositório sobre conteúdo hostil. | Required protection: D13 integralmente. | Proof: PR de fork executada de ponta a ponta com CI verde e sem acesso a segredo; workflow inspecionado por ausência de `pull_request_target` e de interpolação de expressão em `run:`.
- **R4** — Risk: um host MCP com bug ou config herdada ativa um `SAC_ALLOW_*` e o agente consome respostas fora do contrato de domínio acreditando estarem gated. | Required protection: D8. | Proof: caso de smoke por escape, com o campo presente quando ligado e ausente quando desligado.
- **R5** — Risk: `install.py` sobrescreve o manifesto de um projeto que já usa SAC, destruindo contexto gravado do usuário. | Required protection: C5 — criação só quando ausente; nunca sobrescrita; nenhuma escrita fora de `.sac/` e da árvore `managed`. | Proof: reexecução do installer sobre manifesto modificado, conteúdo comparado byte a byte.
- **R6** — Risk: a extração leva os caminhos de máquina do autor para o histórico público de forma irreversível. | Required protection: D1 (histórico do zero) + C6 (gate de higiene) + O1 antes de qualquer commit de conteúdo. | Proof: `git log -p` do repositório público varrido pelo mesmo gate de higiene.
- **R7** — Risk: o bloco entrega um veículo correto para um produto cujo gate de regressão bloqueia mudanças corretas, e alguém publica assim mesmo. | Required protection: C9 + C10; a tag é `0.1.0-rc` e o `RELEASE_GATE.md` é o único caminho para `0.1.0`. | Proof: inspeção de tags e do README.

## Old reachable states

O contrato quebrado é a **localização do manifesto Route**. Estados antigos alcançáveis e caminho explícito de cada um:

| Estado antigo alcançável | Detecção | Caminho explícito |
|---|---|---|
| `sac-context/docs/SAC_domains.md` contendo domínios de projeto (consumidor onboardado no layout legado) | ausência de `.sac/domains.md` **e** presença do arquivo legado com ao menos um bloco `##` fora de `_SKIP_DOMAIN_IDS` | **Rejeitar com ação de recuperação**: erro `sac.environment.domains_manifest_legacy_layout`, com a instrução de mover o arquivo para `.sac/domains.md`. Sem leitura, sem conversão adivinhada, sem crash. |
| `sac-context/docs/SAC_domains.md` contendo apenas template/howto (repositório SAC de origem, ou consumidor nunca onboardado) | presença do arquivo legado sem nenhum bloco de domínio real | **Migrar sem intervenção**: o arquivo é o template; `install.py` o instala como `templates/domains.template.md` e cria `.sac/domains.md` a partir dele. |
| `.sac/domains.md` já existente | presença | **Preservar**: `owned`, nunca tocado. |
| Ambos presentes | presença dupla | **Rejeitar com ação de recuperação**: erro `sac.environment.domains_manifest_ambiguous`, exigindo que o usuário remova o legado. Não escolher por precedência silenciosa. |
| Índice `sac-context/.sac/symbol_index.json` gerado no layout antigo | caminho antigo presente | **Regenerar**: o índice é derivado e não versionado; `index-build` o reconstrói no caminho novo. Sem migração de conteúdo. |
| Cópia congelada de `sac-context/` em `api_robot` e em `to_de_plantao`, com manifesto no layout legado | fora do escopo destes blocos | **Preservar intocado** (D15): nenhum dos dois é migrado agora. Quando o dono migrar, receberá `sac.environment.domains_manifest_legacy_layout` com a ação de recuperação — a linha 2 desta matriz. |

Nenhum estado antigo tem caminho de fallback silencioso. Nenhum tem crash como política.

## Planned outcomes

1. **Consolidar a auditoria de estado real em `AUDIT.md`.**
   Registrar cada achado de V3/V4/V5 com arquivo:linha e reprodução, classificado em `corrigir antes da extração` | `corrigir antes da 0.1.0` | `aceitar e documentar`, incluindo o inventário de superfícies MCP (duas), de cobertura por camada (Layer A = 0) e do eixo linguagem.
   | Acceptance: nenhum achado sem classificação; nenhuma decisão deste design contradita por achado não classificado. | Verify: inspeção cruzada contra os três relatórios. | Likely owners: `AUDIT.md`

2. **Esqueleto público + gates de higiene, antes de qualquer conteúdo.**
   `git init`, `.gitignore` (`__pycache__/`, `*.pyc`, `node_modules/`, `.sac/symbol_index.json`), `LICENSE` (MIT), `CODE_OF_CONDUCT.md`, workflow de higiene que falha em `.pyc` rastreado, em `C:\Users\`, em nome de máquina e em `rabelo-standards`.
   | Acceptance: o gate de higiene falha propositalmente ao se plantar um `.pyc` e passa após removê-lo. | Verify: execução do workflow com e sem o arquivo plantado. | Likely owners: `.gitignore`, `LICENSE`, `.github/workflows/hygiene.yml`

3. **Transplante verbatim.**
   Copiar `src/` (sem `sac_mcp_server.py`, sem `__pycache__/`), `mcp/`, `ci/`, `docs/` para o repositório público, sem nenhuma alteração de comportamento.
   | Acceptance: `mcp/smoke.mjs` verde no repositório público, mesmo veredicto do de origem; gate de higiene verde. | Verify: execução do smoke nos dois repositórios com saídas comparadas. | Likely owners: `src/`, `mcp/`, `ci/`, `docs/`

4. **Superfície MCP única + SSOT de versão.**
   Remover referências a `sac_mcp_server.py` em docs e skills; `mcp/package.json` → `0.1.0` e `node >= 22`; `server.mjs` lê a versão do `package.json`; `sac_scan.py --version` lê o mesmo arquivo; gate de CI contra literal de versão duplicado.
   | Acceptance: `FastMCP` não aparece em nenhum arquivo rastreado; as três fontes de versão anunciam `0.1.0`; o gate falha ao se reintroduzir um literal. | Verify: busca no repositório + execução do gate + `initialize` do servidor. | Likely owners: `mcp/package.json`, `mcp/server.mjs`, `src/sac_scan.py`, `.github/workflows/`

5. **Relocação do manifesto: `managed` × `owned`.**
   `_DOMAINS_REL` → `.sac/domains.md`; `sac-context/docs/SAC_domains.md` → `templates/domains.template.md`; implementar a matriz de estados antigos acima com os dois códigos de erro explícitos; atualizar as três skills e os docs de bootstrap; criar o `.sac/domains.md` do próprio repositório público.
   | Acceptance: cada linha da matriz de estados antigos reproduzida em fixture, com o veredicto declarado; smoke verde. | Verify: execução da CLI contra seis fixtures (uma por linha da matriz). | Likely owners: `src/sac_domains.py`, `src/sac_scan.py`, `templates/domains.template.md`, `.sac/domains.md`, `docs/SAC_BOOTSTRAP.md`

6. **Atestação de gates + terceira classe de erro.**
   `gates_bypassed` presente somente quando não vazio, com warning correspondente, em CLI e MCP; caminhos de exit 2 passam a emitir JSON `sac.environment.*` em stdout; adapter mapeia para `sac.environment_error`; casos novos em `mcp/smoke.mjs`.
   | Acceptance: para cada um dos três escapes, payload com o campo quando ligado e sem o campo quando desligado; root inexistente devolve `sac.environment.*` e não `lookup_failed`. | Verify: `mcp/smoke.mjs` estendido, executado nos dois adapters. | Likely owners: `src/sac_scan.py`, `src/sac_domains.py`, `mcp/server.mjs`, `mcp/smoke.mjs`

7. **Installer + quickstart.**
   `install.py` (stdlib-only): valida Python ≥ 3.11 e Node ≥ 22, instala/atualiza a árvore `managed`, cria `.sac/domains.md` a partir do template só quando ausente, imprime o bloco de config do host MCP. Nunca edita config de host. `README.md` com quickstart, `docs/INSTALL.md`.
   | Acceptance: em diretório limpo, o installer produz um projeto que responde a `list_sac_domains`; reexecutado sobre manifesto modificado, o manifesto permanece byte a byte idêntico. | Verify: execução em fixture limpa e em fixture com manifesto modificado. | Likely owners: `install.py`, `README.md`, `docs/INSTALL.md`

8. **Skills públicas.**
   Publicar `sac-context`, `sac-onboard`, `sac-execution-overlay` sob `skills/`, com resolução de irmão relativa, zero caminho absoluto, zero menção ao monorepo, e frontmatter desambiguado entre `sac-context` (gramática de tag) e `sac-execution-overlay` (gate de execução). `sac-evolution` não é publicada; `GOVERNANCE.md` e `docs/adr/` cobrem a evolução do padrão.
   | Acceptance: gate de higiene verde sobre `skills/`; as duas descrições de frontmatter não compartilham gatilho. | Verify: gate de higiene + leitura comparada dos dois frontmatter. | Likely owners: `skills/`, `GOVERNANCE.md`, `CONTRIBUTING.md`, `docs/adr/`

9. **CI pública para PR de fork.**
   `pull_request` com `permissions: contents: read`, sem segredos, `timeout-minutes` no job, corpo da PR entregue por `env:` em passo intermediário; matriz OS × Python (3.11/3.12/3.13) × Node (22/24). Jobs: higiene, `validate`, `index-build`, smoke. **Sem** `diff-check` (D14).
   | Acceptance: PR aberta de um fork completa a CI verde; workflow não contém `pull_request_target` nem interpolação de expressão dentro de `run:`. | Verify: PR de fork real + inspeção do workflow. | Likely owners: `.github/workflows/ci.yml`, `ci/sac_guard.yml`

10. **`0.1.0-rc` + porta de release.**
    `RELEASE_GATE.md` enumerando nominalmente os P0 do Bloco 02 que liberam `0.1.0`; README declarando o `diff-check` como co-edit gate e as linguagens suportadas como limitação corrente; tag anotada `0.1.0-rc`.
    | Acceptance: `git tag` lista apenas `0.1.0-rc`; cada item do `RELEASE_GATE.md` é rastreável a um outcome do Bloco 02. | Verify: inspeção cruzada com o design do Bloco 02. | Likely owners: `RELEASE_GATE.md`, `README.md`, `CHANGELOG.md`

## Open decisions

none

## Approval

status: AWAITING_APPROVAL
