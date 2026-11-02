// Embeds the report fonts (Big Shoulders Display, Archivo, IBM Plex Mono) as base64 @font-face CSS.
const fs = require('fs'), path = require('path');
module.exports = function fontCss() {
  const dir = path.join(__dirname, 'node_modules', '@fontsource');
  const faces = [
    ['Big Shoulders Display', 'big-shoulders-display', [600, 700, 800, 900]],
    ['Archivo', 'archivo', [400, 500, 600, 700, 800]],
    ['IBM Plex Mono', 'ibm-plex-mono', [400, 500, 700]],
  ];
  let css = '';
  for (const [fam, pkg, ws] of faces) for (const w of ws) {
    const p = path.join(dir, pkg, 'files', `${pkg}-latin-${w}-normal.woff2`);
    if (fs.existsSync(p)) css += `@font-face{font-family:"${fam}";font-weight:${w};src:url(data:font/woff2;base64,${fs.readFileSync(p).toString('base64')}) format("woff2")}\n`;
  }
  return css;
};
