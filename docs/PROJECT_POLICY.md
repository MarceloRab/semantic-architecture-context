# Política do Projeto e Limites de Implementação

## Não implementar

Os itens abaixo são vetados no escopo do produto:

- code graph;
- AST como requisito;
- geração dinâmica de contexto pelo MCP;
- provenance no hot path;
- documentação causal paralela.

Provenance é explicitamente permitido **fora** do hot path, como campo opcional
fora do payload de Context ou como sinal derivado. Essa possibilidade continua
não implementada; a permissão apenas a retira da lista de vetos quando respeita
essa fronteira.

## Cenário de benchmark

`DIAGNOSE` é somente um cenário de benchmark documentado. Ele mede, em uma
avaliação externa, se uma falha pode ser reduzida a um slice inicial sem busca
global. Ele fica fora do schema porque essa propriedade pertence ao comportamento
do boundary `files:` e dos anchors, não a um tipo de tag. Promovê-lo ao schema
acrescentaria uma claim ARCH satisfeita pelas mesmas tags de cenários existentes,
sem criar requisito estrutural novo. A harness desse benchmark não faz parte do
produto e não é implementada aqui.
