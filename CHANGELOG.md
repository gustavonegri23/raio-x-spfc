# Changelog

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
