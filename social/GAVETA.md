# Gaveta do @data_tricolor

Regras que a tarefa agendada diária segue para manter conteúdo pronto. Editar aqui muda o comportamento das próximas execuções.

## Fluxo
1. Ler `social/gaveta.json` (o que já foi gerado) e os dados do Raio-X (`data/dados.js`, `data/notas.js`, `data/escalacoes.js`, textos de `index.html`).
2. Manter sempre **os próximos 2 dias** preenchidos (hoje não conta). Só gerar o que falta.
3. Renderizar com os moldes de `social/moldes/` (carrossel 1080×1350 em PNG; Reels 1080×1920 em MP4, ~35 s, ritmo atual do `reels-jogador.html`).
4. Subir em `social/AAAA-MM-DD/`, commitar e criar no Metricool como **rascunho** (`draft: true`), com horário sugerido. Mídia por `https://raw.githubusercontent.com/gustavonegri23/raio-x-spfc/<commit>/social/...`.
5. Registrar em `gaveta.json` e commitar.

## Grade
- **Todo dia, Reels "Elenco em números"** (um jogador). Horário sugerido 19h (18h em dia de jogo). Instagram REEL, `autoPublish: false` (o Gustavo põe música em alta pelo app do Metricool).
- **Terça e sexta, carrossel tático** às 12h: esquemas e o que funciona/não funciona (3-4-2-1 casa × fora, janelas de 15 min, substituições, bola parada, etc.).
- **Dia de jogo, carrossel pré-jogo** às 10h: adversário em números (forma, mando, desfalques, pontos fortes e fracos de `escalacoes.js`).
- **Pós-jogo NÃO entra na gaveta**: depende da coleta no SofaScore ("atualizar Raio-X").

## Ordem dos jogadores
Gancho com o próximo jogo: priorizar quem pesa no adversário da próxima rodada (duelos, escalação sugerida em `escalacoes.js`, pontos fracos do rival). Não repetir jogador já publicado no ciclo, a não ser que haja dado novo de rodada.

## Estilo
- Identidade do Raio-X: fundo #121214, vermelho #E0102F, faixa tricolor no topo, Big Shoulders Display + Archivo + IBM Plex Mono.
- Rodapé: fonte (SofaScore · Série A 2026 · rodada) e "Não oficial".
- Só números que estão nos dados do Raio-X. Nada inventado ou estimado.
- **Não citar "link da bio" / relatório completo** até o domínio próprio estar no ar.
- Legenda em PT-BR, 4 a 7 linhas, gancho na primeira linha, pergunta para comentário quando couber, hashtags: #SPFC #SaoPaulo #Brasileirao #DataTricolor (+ nome do jogador/tema).
- Local de jogo: usar o campo `estadio` de `escalacoes.js` quando existir (R34 × Corinthians é na Vila Belmiro).
