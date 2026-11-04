// Gera o arquivo de chutes do São Paulo para o reels-dinamico-chutes.html.
// Uso: node exportar-chutes.js ../../data/dados.js /caminho/shots.js
//      node render-dinamico.js reels-dinamico-chutes.html ../AAAA-MM-DD/reels.mp4 /caminho/shots.js
const fs=require('fs'),path=require('path');const [src,out]=process.argv.slice(2);
global.window={};require(path.resolve(src));const M=window.SHOTMAP,o=[];
for(let i=0;i<M.length;i+=17){const q=M.substr(i,17);if(q[3]!=='1')continue;const x=+q.substr(4,2),y=+q.substr(6,2);
  o.push([+q.substr(0,2),+q.substr(11,2),q[2]==='1'?1:0,Math.max(1.5,Math.min(98.5,y)),Math.max(1.5,Math.min(64.5,x*1.25)),+q.substr(8,2)/100,q[10]]);}
o.sort((a,b)=>a[0]-b[0]||a[1]-b[1]);fs.writeFileSync(out,'const SHOTS='+JSON.stringify(o.map(s=>s.slice(2)))+';');console.log(o.length,'chutes');
