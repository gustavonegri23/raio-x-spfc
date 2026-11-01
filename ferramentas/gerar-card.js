/*
  Raio-X SPFC · gerar-card.js
  Gera relatorios/card-rodada-NN.png (1080×1350) a partir de ferramentas/card.html.
  Uso:  node ferramentas/gerar-card.js
  Precisa do Playwright com Chromium (já instalado no ambiente de trabalho do Claude).
  Fontes: se as fontes do Google não carregarem, use os pacotes @fontsource
  (npm i @fontsource/big-shoulders-display @fontsource/archivo @fontsource/ibm-plex-mono)
  e passe a pasta node_modules em FONTES=/caminho/node_modules.
*/
const path = require('path'), fs = require('fs');
const { chromium } = require('playwright');
const RAIZ = path.resolve(__dirname, '..');

function cssLocal(dir) {
  if (!dir) return null;
  const f = (pkg, file) => path.join(dir, '@fontsource', pkg, 'files', file);
  const faces = [
    ['Big Shoulders Display', 'big-shoulders-display', [700, 800, 900]],
    ['Archivo', 'archivo', [400, 500, 600, 700]],
    ['IBM Plex Mono', 'ibm-plex-mono', [400, 500, 700]]
  ];
  let css = '';
  for (const [fam, pkg, ws] of faces) for (const w of ws) {
    const p = f(pkg, `${pkg}-latin-${w}-normal.woff2`);
    if (fs.existsSync(p)) css += `@font-face{font-family:"${fam}";font-weight:${w};src:url(data:font/woff2;base64,${fs.readFileSync(p).toString('base64')}) format("woff2")}\n`;
  }
  return css || null;
}

(async () => {
  const base = fs.readFileSync(path.join(RAIZ, 'data', 'card-base.js'), 'utf8');
  const rd = (base.match(/"rodada":\s*(\d+)/) || [])[1] || 'xx';
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  const css = cssLocal(process.env.FONTES);
  if (css) {
    await p.route('**/fonts.googleapis.com/**', r => r.fulfill({ status: 200, contentType: 'text/css', body: css }));
  }
  await p.goto('file://' + path.join(RAIZ, 'ferramentas', 'card.html'));
  await p.waitForSelector('body[data-pronto="1"]');
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300);
  const out = path.join(RAIZ, 'relatorios', `card-rodada-${String(rd).padStart(2, '0')}.png`);
  fs.mkdirSync(path.dirname(out), { recursive: true });
  await p.screenshot({ path: out, clip: { x: 0, y: 0, width: 1080, height: 1350 } });
  await b.close();
  console.log('ok:', out);
})();
