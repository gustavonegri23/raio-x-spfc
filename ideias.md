# Backlog de upgrades

Regra: a cada atualização de rodada, fazer **um** item da lista (o primeiro que couber no tempo), marcar como feito com a data e registrar no CHANGELOG. Ideias novas que surgirem dos dados entram aqui, no lugar certo da prioridade, com uma linha explicando por que importam.

## Prioridade alta

- [ ] **Tirar os números fixos da aba Time.** Os textos da aba Time (KPIs, trajetória, mando, sistema, GPS, técnicos, reta final) ainda têm números escritos no HTML. Mover os números para `data/` e deixar só a interpretação no texto, para a atualização não depender de procurar valores no código.
- [ ] **Carga física e risco.** Minutos acumulados e jogos seguidos por jogador, queda de distância e sprints nas últimas 3 rodadas contra a média da temporada. Sinalizar quem está no limite antes da sequência de 4 jogos em 14 dias.
- [ ] **Recalcular a aba Gols com o montar.py.** Os números da aba Gols e do impacto em campo foram calculados antes do montar.py e diferem levemente (método de minuto final). Alinhar os textos com o resumo.

## Prioridade média

- [ ] **Comparação com os rivais diretos em xG e bola parada.** Pontos e gols por jogo já estão na aba Time; falta xG e bola parada, que exigem coletar os jogos dos rivais.
- [ ] **Bola parada defensiva em detalhe.** Mapa só dos gols e chutes sofridos de escanteio e falta, por zona de origem e marcação.
- [ ] **Histórico rodada a rodada da nota de cada jogador** usando os arquivos de `data/rodadas/` (tendência das últimas 5).

## Novas (01/11)

- [ ] **Palpite de placar do analista.** Hoje o palpite é o favorito do modelo; registrar um palpite próprio (resultado e placar) em `data/previsoes.json` deixa o placar de credibilidade mais interessante.
- [ ] **Card de pré-jogo.** Mesmo molde do card da rodada, com a escalação sugerida e a ficha do adversário, para postar no dia do jogo.
- [ ] **Painel de visitas.** Depois de ativar o GoatCounter, mostrar na mensagem pós-rodada as visitas da semana.

## Para 2027

- [ ] Planejamento: contratos que terminam, idade por posição, perfil de reforço por setor.
- [ ] Trocar o ID de temporada no coletor (`SEASON`) e abrir `data/rodadas/2027/`.

## Feito

- 01/11/2026 · Impacto das substituições (aba Gols), placar das previsões (aba Próximos jogos), checagens automáticas no montar.py, plano B do coletor, ficha do adversário em números, janelas de 15 minutos com xG, simulador da reta final, vizinhos e média da liga, card da rodada e modo fim de temporada.

- 01/11/2026 · Estrutura do projeto, coletor, montar.py, skill e tarefas agendadas.
