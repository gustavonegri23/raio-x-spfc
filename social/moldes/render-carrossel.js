const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),fontCss=require('./fonts');
(async()=>{const [src,out]=process.argv.slice(2);fs.mkdirSync(out,{recursive:true});
const html=fs.readFileSync(src,'utf8').replace('/*FONTS*/',fontCss());
const b=await chromium.launch({executablePath:'/usr/bin/google-chrome'});const p=await b.newPage({viewport:{width:1080,height:1350}});
await p.setContent(html);await p.evaluate(()=>document.fonts.ready);
const ids=await p.$$eval('section.s',a=>a.map(e=>e.id));
for(const [i,id] of ids.entries()){await (await p.$('#'+id)).screenshot({path:path.join(out,`slide-${String(i+1).padStart(2,'0')}.png`)});}
await b.close();console.log(ids.length,'slides')})();
