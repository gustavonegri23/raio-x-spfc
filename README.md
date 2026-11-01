# Raio-X Tricolor 2026

Análise de desempenho independente do São Paulo FC no Brasileirão Série A 2026, com dados públicos do SofaScore e probabilidades do Modelo ValorFinal. O projeto não é oficial e não tem vínculo com o clube.

Feito por Gustavo Negri Tavares.

## Onde fica

Site público: https://gustavonegri23.github.io/raio-x-spfc/ (GitHub Pages, repositório gustavonegri23/raio-x-spfc, branch main). A coleta bruta (`data/rodadas/`) e os resumos (`relatorios/`) não vão para o repositório.

Pasta local: `C:\Users\gusta\Documents\raio-x-spfc` no computador do Gustavo.

## Estrutura

```
raio-x-spfc/
├── index.html               página do relatório (quatro abas: Time, Jogadores, Gols, Próximos jogos)
├── data/
│   ├── dados.js             dados da rodada atual (gerado pelo montar.py; não editar à mão)
│   ├── notas.js             "leitura do analista" de cada jogador (texto, editado a cada rodada)
│   ├── escalacoes.js        escalações sugeridas para os próximos jogos e atualizações pré-jogo
│   ├── previsoes.json       previsões registradas antes de cada jogo (fonte; editar só para registrar novas)
│   ├── previsoes.js         placar das previsões (gerado pelo montar.py)
│   ├── card-base.js         números do card da rodada (gerado pelo montar.py)
│   ├── card.js              textos do card da rodada (manchete e 3 destaques)
│   └── rodadas/
│       └── rodada-NN.json   foto completa de cada rodada, como saiu do coletor
├── relatorios/
│   ├── resumo-rodada-NN.md  números-chave e o que mudou, base para reescrever os textos
│   ├── prejogo-rodada-NN.md notícias do dia do jogo e impacto na escalação
│   └── card-rodada-NN.png   card para as redes (não vai para o GitHub)
├── ferramentas/
│   ├── coletor.js           roda no navegador, numa aba do sofascore.com
│   ├── montar.py            checa a coleta e gera data/dados.js, previsões, card-base e o resumo
│   ├── validar.py           checagens automáticas (o montar.py chama sozinho)
│   ├── extras.py            janelas, substituições, vizinhos, previsões e retrospectiva
│   ├── card.html            molde do card da rodada (1080×1350)
│   └── gerar-card.js        gera relatorios/card-rodada-NN.png
├── ideias.md                backlog de upgrades, em ordem de prioridade
└── CHANGELOG.md             o que mudou em cada atualização
```

## Atualização depois de cada rodada

1. Abrir uma aba em `https://www.sofascore.com` no navegador do app do Claude.
2. Executar `ferramentas/coletor.js` na aba, depois `await RX.tudo()`.
3. Ler o resultado com `RX.partes()` e `RX.parte(i)` e salvar em `data/rodadas/rodada-NN.json`.
4. Rodar `python3 ferramentas/montar.py` (para se as checagens acharem erro).
5. Ler `relatorios/resumo-rodada-NN.md` e atualizar os textos de `index.html`, `data/notas.js` e `data/escalacoes.js`.
6. Escrever `data/card.js` e rodar `node ferramentas/gerar-card.js`.
7. Fazer um upgrade de `ideias.md`, registrar em `CHANGELOG.md` e publicar.

O passo a passo completo está na skill "Atualizar Raio-X SPFC".

## Abrir localmente

Basta abrir `index.html` no navegador. A página carrega os arquivos de `data/` pelo caminho relativo, então a pasta precisa ficar inteira.

## Fontes e crédito

Estatísticas, notas, mapas de calor, GPS e chutes: SofaScore. Probabilidades: Modelo ValorFinal (CC BY 4.0). Os dados pertencem às fontes; este projeto apenas os analisa.
