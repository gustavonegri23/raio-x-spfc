# Changelog

## 01/11/2026 · local do Majestoso

- São Paulo x Corinthians (R34, 04/11) será na Vila Belmiro, com o Morumbis ocupado por um show. Novo campo opcional `estadio` em `data/escalacoes.js`; o placar da capa e a ficha do jogo usam esse campo quando o mando não é no Morumbis. Textos da capa do diagnóstico (2.3) e da reta final ajustados.

## 01/11/2026 · novo layout: capa e quatro capítulos

- **Estrutura em capítulos**: Capa · 01 Temporada · 02 Diagnóstico · 03 Elenco · 04 Reta final · Método. Cada capítulo abre com numeral, pergunta, introdução e sumário clicável, e termina com a passagem para o próximo.
- **Seções reorganizadas na ordem da história**: o que aconteceu (trajetória, técnicos, copas), por quê (mando, adversários, clássicos, finalização, chutes, janelas, sistema, físico), quem (ataque, duplas, fichas) e o que fazer (prioridades, simulador, escalações). O placar das previsões e a metodologia viraram o epílogo "Método e acerto".
- **Capa**: placar no estilo do antigo letreiro do Morumbi com o próximo jogo, campanha jogo a jogo por mando e aproveitamento em casa e fora (tudo calculado de `dados.js`, atualiza sozinho), KPIs, achados e selo do placar das previsões.
- **Navegação**: barra fixa com progresso de leitura, links diretos para cada seção (ex.: `#s-shots`) e os links antigos (`#gols`, `#jogos`, `#jogadores`, `#j-<jogador>`) continuam funcionando.
- **Compartilhamento**: metatags para WhatsApp/LinkedIn, favicon e `og-card.png` (1200×630) gerado por `ferramentas/gerar-og.js` a partir de `ferramentas/og.html`. Lê só `dados.js`; rodar depois do `gerar-card.js` a cada rodada.
- **Achados da capa**: o título conta os itens sozinho ("Seis achados"); a skill pode escrever de 3 a 6 sem mexer no título.
- **Fim de temporada**: sem próximos jogos, o placar da capa mostra "FIM" e a posição final.
- **README** reescrito como vitrine: imagem de prévia, link do site, capítulos, como é atualizado e estrutura.

## 01/11/2026 · credibilidade, conteúdo novo e card para redes

- **Placar das previsões** (aba Próximos jogos): escalação sugerida e palpite registrados antes do jogo em `data/previsoes.json`; o `montar.py` preenche o resultado, os titulares acertados e o Brier do modelo. Previsões das rodadas 34 a 38 registradas hoje (palpite = favorito do modelo).
- **Checagens automáticas** (`ferramentas/validar.py`): placar × lista de gols, mapa de chutes, tabela × campanha, notas e minutos plausíveis, titulares da rodada nova. Com erro, o `montar.py` para; com `--forcar`, a página mostra o selo de dados incompletos.
- **Plano B do coletor**: 3 tentativas por chamada, `RX.status()` e `RX.retomar()`; o JSON sai marcado com `incompleto` quando algo falhar.
- **Coletor novo na etapa 4**: estatísticas do São Paulo, tabela de mandantes e visitantes e forma dos próximos adversários. Para a R33 esses campos foram coletados à parte em 01/11 e acrescentados ao `rodada-33.json`.
- **Ficha do adversário em números** em cada jogo da aba Próximos jogos.
- **Janelas de 15 minutos com xG e impacto das substituições** (aba Gols, seção nova). O gráfico de gols por faixa passou a ler os dados do `montar.py`.
- **Simulador da reta final** e **ritmo dos vizinhos × média da Série A** (aba Time, seção Reta final).
- **Card da rodada** (`ferramentas/card.html` + `gerar-card.js`): PNG 1080×1350 em `relatorios/`, números de `data/card-base.js` (automático) e textos de `data/card.js`.
- **Contador de visitas** pronto para ligar (GoatCounter, sem cookies): basta preencher `window.RX_CONTADOR` no `index.html`.
- **Modo fim de temporada**: `montar.py --temporada` gera `relatorios/retrospectiva-2026.md`.
- Tabelas que estouravam a largura no celular agora rolam dentro do quadro.

## 01/11/2026 · mapa de finalizações interativo

- Mapa de chutes com filtros por mando, adversário, tipo de jogada e "só gols"; cada chute mostra rodada, placar, minuto, autor, parte do corpo, jogada e xG ao passar o mouse ou tocar.
- Formato do `SHOTMAP` mudou para v2 (17 caracteres por chute, com rodada, minuto e autor). `coletor.js` e `montar.py` já usam o novo formato.
- Mapa dos gols na ficha do jogador maior no desktop (card em largura total quando o jogador tem gol).
- Projeto salvo em Documentos\raio-x-spfc.

## 01/11/2026 · versão base (após a 33ª rodada)

- Relatório separado em página (`index.html`) e dados (`data/`).
- Coletor do SofaScore (`ferramentas/coletor.js`) e gerador de dados e resumo (`ferramentas/montar.py`).
- Primeira foto completa: `data/rodadas/rodada-33.json`. Foi montada a partir das coletas desta sessão; os campos `GOLS` e `CAMPO` vêm da mesma fonte, mas os textos de impacto em campo da aba Gols foram escritos com um cálculo anterior e podem diferir em até 0,1 do resumo.
- Página marcada como análise independente, sem vínculo com o clube.
- Escalações para as rodadas 34 a 38 em `data/escalacoes.js`.
