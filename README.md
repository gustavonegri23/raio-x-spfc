# Raio-X Tricolor 2026

Análise de desempenho independente do São Paulo FC no Brasileirão Série A 2026, com dados públicos do SofaScore e probabilidades do Modelo ValorFinal. O projeto não é oficial e não tem vínculo com o clube.

Feito por Gustavo Negri Tavares.

## Onde fica

`C:\Users\gusta\Documents\raio-x-spfc` no computador do Gustavo.

## Estrutura

```
raio-x-spfc/
├── index.html               página do relatório (quatro abas: Time, Jogadores, Gols, Próximos jogos)
├── data/
│   ├── dados.js             dados da rodada atual (gerado pelo montar.py; não editar à mão)
│   ├── notas.js             "leitura do analista" de cada jogador (texto, editado a cada rodada)
│   ├── escalacoes.js        escalações sugeridas para os próximos jogos e atualizações pré-jogo
│   └── rodadas/
│       └── rodada-NN.json   foto completa de cada rodada, como saiu do coletor
├── relatorios/
│   ├── resumo-rodada-NN.md  números-chave e o que mudou, base para reescrever os textos
│   └── prejogo-rodada-NN.md notícias do dia do jogo e impacto na escalação
├── ferramentas/
│   ├── coletor.js           roda no navegador, numa aba do sofascore.com
│   └── montar.py            transforma a coleta em data/dados.js e no resumo
├── ideias.md                backlog de upgrades, em ordem de prioridade
└── CHANGELOG.md             o que mudou em cada atualização
```

## Atualização depois de cada rodada

1. Abrir uma aba em `https://www.sofascore.com` no navegador do app do Claude.
2. Executar `ferramentas/coletor.js` na aba, depois `await RX.tudo()`.
3. Ler o resultado com `RX.partes()` e `RX.parte(i)` e salvar em `data/rodadas/rodada-NN.json`.
4. Rodar `python3 ferramentas/montar.py`.
5. Ler `relatorios/resumo-rodada-NN.md` e atualizar os textos de `index.html`, `data/notas.js` e `data/escalacoes.js`.
6. Fazer um upgrade de `ideias.md`, registrar em `CHANGELOG.md` e publicar.

O passo a passo completo está na skill "Atualizar Raio-X SPFC".

## Abrir localmente

Basta abrir `index.html` no navegador. A página carrega os arquivos de `data/` pelo caminho relativo, então a pasta precisa ficar inteira.

## Fontes e crédito

Estatísticas, notas, mapas de calor, GPS e chutes: SofaScore. Probabilidades: Modelo ValorFinal (CC BY 4.0). Os dados pertencem às fontes; este projeto apenas os analisa.
