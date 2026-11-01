/*
  Raio-X SPFC · gerar-og.js
  Gera og-card.png (1200×630) na raiz do projeto a partir de ferramentas/og.html.
  É a imagem que aparece quando o link do site é compartilhado (WhatsApp, LinkedIn, X)
  e no topo do README. Lê só data/dados.js, então basta rodar depois do montar.py.
  Uso:  node ferramentas/gerar-og.js
  Fontes: igual ao gerar-card.js. Se as fontes do Google não carregarem, instale
  @fontsource/big-shoulders-display @fontsource/archivo @fontsource/ibm-plex-mono @fontsource/doto
  e passe FONTES=/caminho/node_modules.
*/
const path = require('path'), fs = require('fs');
const { chromium } = require('playwright');
const RAIZ = path.resolve(__dirname, '..');

function cssLocal(dir) {
  if (!dir) return null;
  const faces = [
    ['Big Shoulders Display', 'big-shoulders-display', [800, 900]],
    ['Archivo', 'archivo', [400, 600]],
    ['IBM Plex Mono', 'ibm-plex-mono', [500]],
    ['Doto', 'doto', [900]]
  ];
  let css = '';
  for (const [fam, pkg, ws] of faces) for (const w of ws) {
    const p = path.join(dir, '@fontsource', pkg, 'files', `${pkg}-latin-${w}-normal.woff2`);
    if (fs.existsSync(p)) css += `@font-face{font-family:"${fam}";font-weight:${w};src:url(data:font/woff2;base64,${fs.readFileSync(p).toString('base64')}) format("woff2")}\n`;
  }
  return css || null;
}

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
  const css = cssLocal(process.env.FONTES);
  if (css) await p.route('**/fonts.googleapis.com/**', r => r.fulfill({ status: 200, contentType: 'text/css', body: css }));
  await p.goto('file://' + path.join(RAIZ, 'ferramentas', 'og.html'));
  await p.waitForSelector('body[data-pronto="1"]');
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300);
  const out = path.join(RAIZ, 'og-card.png');
  await p.screenshot({ path: out, clip: { x: 0, y: 0, width: 1200, height: 630 } });
  await b.close();
  console.log('ok:', out);
})();
