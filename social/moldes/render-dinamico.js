// Igual ao render-reels.js, mas embute reels-dinamico-base.css/.js e dados (/*SHOTS*/) antes de renderizar.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),fontCss=require('./fonts'),{execSync}=require('child_process');
(async()=>{const [src,out,shots]=process.argv.slice(2);const FPS=30;const fr=path.join(path.dirname(out),'frames-'+path.basename(out,'.mp4'));fs.rmSync(fr,{recursive:true,force:true});fs.mkdirSync(fr,{recursive:true});
let html=fs.readFileSync(src,'utf8').replace('/*BASE*/',fs.readFileSync(path.join(__dirname,'reels-dinamico-base.css'),'utf8')).replace('/*BASEJS*/',fs.readFileSync(path.join(__dirname,'reels-dinamico-base.js'),'utf8'));
html=html.replace('/*FONTS*/',fontCss());if(shots)html=html.replace('/*SHOTS*/',fs.readFileSync(shots,'utf8'));
const b=await chromium.launch({executablePath:'/usr/bin/google-chrome'});const p=await b.newPage({viewport:{width:1080,height:1920}});
p.on('pageerror',e=>{console.error('ERRO',e.message);process.exit(1)});
await p.setContent(html);await p.evaluate(()=>document.fonts.ready);const dur=await p.evaluate(()=>window.DUR);
const only=process.env.FRAMES?process.env.FRAMES.split(',').map(Number):null;
if(only){for(const s of only){await p.evaluate(t=>render(t),s);await p.screenshot({path:out.replace('.mp4',`-t${s}.png`)});}await b.close();return console.log('previews ok');}
const n=Math.round(dur*FPS);for(let i=0;i<n;i++){await p.evaluate(t=>render(t),i/FPS);await p.screenshot({path:path.join(fr,`f${String(i).padStart(5,'0')}.jpg`),type:'jpeg',quality:92});}
await b.close();
execSync(`ffmpeg -loglevel error -y -framerate ${FPS} -i ${fr}/f%05d.jpg -f lavfi -i anullsrc=r=44100:cl=stereo -shortest -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart ${out}`);
fs.rmSync(fr,{recursive:true,force:true});console.log('ok',n,'frames',dur+'s')})();
