const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),fontCss=require('./fonts'),{execSync}=require('child_process');
(async()=>{const [src,out]=process.argv.slice(2);const FPS=30;const fr=path.join(path.dirname(out),'frames');fs.rmSync(fr,{recursive:true,force:true});fs.mkdirSync(fr,{recursive:true});
const html=fs.readFileSync(src,'utf8').replace('/*FONTS*/',fontCss());
const b=await chromium.launch({executablePath:'/usr/bin/google-chrome'});const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.setContent(html);await p.evaluate(()=>document.fonts.ready);const dur=await p.evaluate(()=>window.DUR);
const n=Math.round(dur*FPS);for(let i=0;i<n;i++){await p.evaluate(t=>render(t),i/FPS);await p.screenshot({path:path.join(fr,`f${String(i).padStart(5,'0')}.jpg`),type:'jpeg',quality:92});}
await b.close();
execSync(`ffmpeg -loglevel error -y -framerate ${FPS} -i ${fr}/f%05d.jpg -f lavfi -i anullsrc=r=44100:cl=stereo -shortest -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart ${out}`);
fs.rmSync(fr,{recursive:true,force:true});console.log('ok',n,'frames')})();
