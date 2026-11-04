// Helpers compartilhados dos Reels dinâmicos (render(t) determinístico, sem relógio do navegador)
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const ease=x=>1-Math.pow(1-clamp(x),3);
const back=x=>{x=clamp(x);const c=1.9;return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2)};
const fmt=(x,d=0)=>x.toFixed(d).replace('.',',');
const $=id=>document.getElementById(id);
let SC=[];// [{id,a,b}]
function scenes(list){let a=0;SC=list.map(([id,d])=>{const s={id,a,b:a+d};a+=d;return s});window.DUR=a;return SC}
const T=id=>SC.find(s=>s.id===id).a;
function base(t){
  // câmera sempre viva: respiração + deriva do fundo
  $('cam').style.transform=`scale(${1.012+0.012*Math.sin(t*1.3)}) rotate(${0.25*Math.sin(t*0.7)}deg)`;
  $('grid').style.transform=`translate(${(t*22)%120}px,${(t*34)%120}px)`;
  $('glow').style.transform=`translate(${180*Math.sin(t*0.45)}px,${260*Math.cos(t*0.33)}px)`;
  let fl=0;
  SC.forEach((s,i)=>{const el=$(s.id);const on=t>=s.a&&t<s.b;el.style.visibility=on?'visible':'hidden';
    if(!on)return;const lt=t-s.a;
    const pk=i===0&&lt<0.0001?1:back(lt/0.32);el.style.transform=`scale(${1.12-0.12*pk})`;
    if(i>0)fl=Math.max(fl,0.22*(1-clamp(lt/0.16)));
    el.querySelectorAll('[data-at]').forEach(w=>{const at=+w.dataset.at;const k=at<=0?1:back((lt-at)/0.3);const o=at<=0?1:clamp((lt-at)/0.12);
      w.style.opacity=o;w.style.transform=`translateY(${(1-k)*60}px) scale(${0.9+0.1*k})`;});
  });
  $('flash').style.opacity=fl;
}
function count(el,to,a,d,t,dec=0,from=0){el.textContent=fmt(from+(to-from)*ease((t-a)/d),dec)}
