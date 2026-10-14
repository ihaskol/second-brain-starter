/* Animation player (explainer-video skill). wfMount(root, WF, opts) draws the board from WF (scripts/export_player.js)
   and adds Play/Pause, Restart, chapter buttons, a position slider, live captions and a transcript.
   opts: {chapters:[names], label:'screen-reader description', audio:url, fetchAudio:true, start:t, noTranscript:true}
   Pure SVG + JS; no libraries. Used by the standalone page, the hub and the MP4 recorder. */
const WF_CSS=`.wf{display:flex;flex-direction:column;gap:10px}
.wf-board{background:#efeee9;border:1px solid var(--line,#d8d6cf);border-radius:12px;overflow:hidden;aspect-ratio:16/9}
.wf-board svg{display:block;width:100%;height:100%}
.wf-board text{font-family:"Patrick Hand",cursive}
.wf-cap{min-height:3.2em;font-size:1rem;line-height:1.45;color:var(--ink,#1d1d1b)}
.wf-ctl{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.wf-ctl button{font:inherit;font-size:.92rem;min-height:36px;padding:4px 12px;border:1px solid var(--line,#c9c6bd);border-radius:8px;background:var(--paper,#fff);color:var(--ink,#1d1d1b);cursor:pointer}
.wf-ctl button[aria-pressed="true"]{border-color:var(--blue,#1f5fbf);box-shadow:inset 0 -3px 0 var(--blue,#1f5fbf)}
.wf-ctl input[type=range]{flex:1 1 160px;min-width:140px;height:28px;accent-color:var(--blue,#1f5fbf)}
.wf-time{font-variant-numeric:tabular-nums;font-size:.85rem;color:var(--muted,#666)}
.wf-tr ol{margin:.5em 0 0 1.2em;padding:0;font-size:.92rem;line-height:1.5}`;
function wfMount(root,WF,opts={}){
  if(!document.getElementById("wf-css")){const st=document.createElement("style"); st.id="wf-css"; st.textContent=WF_CSS; document.head.appendChild(st);}
  const CH=opts.chapters||WF.chapters||WF.scn.map((_,i)=>"Part "+(i+1)), fmt=s=>Math.floor(s/60)+":"+String(Math.floor(s%60)).padStart(2,"0");
  root.classList.add("wf");
  root.innerHTML=`<div class="wf-board" role="img" aria-label="${(opts.label||"Animated explainer. The captions below describe every step.").replace(/"/g,"&quot;")}">${WF.svg}</div>
  <p class="wf-cap" aria-live="polite"></p>
  <div class="wf-ctl"><button type="button" data-a="play">▶ Play</button><button type="button" data-a="restart">↺ Restart</button>${opts.audio?'<button type="button" data-a="sound" aria-pressed="true">🔊 Sound on</button>':''}
  ${CH.map((c,i)=>`<button type="button" data-ch="${i}" aria-pressed="false">${i+1} · ${c}</button>`).join("")}
  <input type="range" min="0" max="${WF.total}" step="0.1" value="0" aria-label="Position in the animation"><span class="wf-time"></span></div>
  ${opts.noTranscript?"":`<details class="wf-tr"><summary>Transcript</summary><ol>${WF.caps.map(c=>`<li>${c[1].replace(/&/g,"&amp;").replace(/</g,"&lt;")}</li>`).join("")}</ol></details>`}`;
  const svg=root.querySelector("svg"), cap=root.querySelector(".wf-cap"), rng=root.querySelector("input"), tm=root.querySelector(".wf-time"), pb=root.querySelector('[data-a="play"]');
  const SCG=[...svg.querySelectorAll("[data-sc]")];
  const E=WF.els.map(d=>{const g=svg.querySelector(`[data-e="${d.i}"]`), o=Object.assign({g},d);
    if(d.k==="d"){o.P=[...g.querySelectorAll("path[data-l]")]; o.L=o.P.map(p=>+p.dataset.l); o.T=o.L.reduce((a,b)=>a+b,0)||1; o.F=[...g.querySelectorAll("path[data-f]")];
      o.P.forEach((p,i)=>{p.style.strokeDasharray=o.L[i]+" "+o.L[i]; p.style.strokeLinecap="round";});}
    if(d.k==="t"){o.r=svg.querySelector(`#${d.c} rect`); const b=d.bb; o.r.setAttribute("x",b[0]-10); o.r.setAttribute("y",b[1]-12); o.r.setAttribute("height",b[3]+24);}
    return o;});
  let t=0, playing=false, last=0, shown=-1, au=null, auOK=false;
  if(opts.audio){au=new Audio(); au.preload="auto";
    const set=u=>{au.src=u; au.addEventListener("canplay",()=>{auOK=true},{once:true}); au.addEventListener("error",()=>{auOK=false},{once:true});};
    if(opts.fetchAudio) fetch(opts.audio).then(r=>{if(!r.ok) throw 0; return r.blob();}).then(b=>set(URL.createObjectURL(b))).catch(()=>{}); else set(opts.audio);
    const sb=root.querySelector('[data-a="sound"]'); sb.onclick=()=>{au.muted=!au.muted; sb.setAttribute("aria-pressed",String(!au.muted)); sb.textContent=au.muted?"🔇 Sound off":"🔊 Sound on";};}
  const useAu=()=>au&&auOK&&!au.error;
  function render(T){t=Math.max(0,Math.min(WF.total,T));
    WF.scn.forEach((s,i)=>{const nx=i+1<WF.scn.length?WF.scn[i+1]:1e9; let o=0; if(t>=s&&t<nx){o=Math.min(1,(t-s)/0.3+(s===0?1:0)); if(t>nx-0.45) o=Math.max(0,(nx-t)/0.45);} if(t>=WF.total&&i===WF.scn.length-1) o=1; SCG[i].style.opacity=o; SCG[i].style.display=o>0?"":"none";});
    for(const e of E){
      if(e.k==="m"){const k=e.keys; if(t<k[0][0]||(e.end!=null&&t>=e.end)){e.g.style.opacity=0; continue;} e.g.style.opacity=1; let x=k[k.length-1][1], y=k[k.length-1][2];
        for(let i=0;i<k.length-1;i++) if(t<k[i+1][0]){const u=(t-k[i][0])/(k[i+1][0]-k[i][0]), s=u*u*(3-2*u); x=k[i][1]+(k[i+1][1]-k[i][1])*s; y=k[i][2]+(k[i+1][2]-k[i][2])*s; break;}
        e.g.setAttribute("transform",`translate(${x.toFixed(1)},${y.toFixed(1)})`); continue;}
      const u=Math.max(0,Math.min(1,(t-e.t0)/e.d)); e.g.style.opacity=u>0?1:0;
      if(e.k==="d"){let left=u*e.T; e.P.forEach((p,i)=>{const L=e.L[i], d=Math.max(0,Math.min(L,left)); left-=L; p.style.strokeDashoffset=L-d;}); e.F.forEach(f=>f.style.opacity=u>=1?1:0);}
      else e.r.setAttribute("width",(e.bb[2]+20)*u);}
    let ci=0; WF.caps.forEach((c,i)=>{if(c[0]<=t+0.05) ci=i;}); if(ci!==shown){shown=ci; cap.textContent=WF.caps[ci][1];}
    const ch=WF.scn.reduce((a,s,i)=>t>=s?i:a,0); root.querySelectorAll("[data-ch]").forEach(b=>b.setAttribute("aria-pressed",String(+b.dataset.ch===ch)));
    rng.value=t; tm.textContent=fmt(t)+" / "+fmt(WF.total);}
  function frame(now){if(!playing) return; if(!root.isConnected){playing=false; return;}
    const dt=Math.min(0.1,(now-last)/1000); last=now;
    if(useAu()&&au.paused&&!au._tried){au._tried=true; try{au.currentTime=t;}catch(e){} au.play().catch(()=>{});}
    if(useAu()&&!au.paused&&Math.abs(au.currentTime-t)<1.5) render(au.currentTime); else render(t+dt);
    if(t>=WF.total){pause(); return;} requestAnimationFrame(frame);}
  function play(){if(t>=WF.total-0.05) t=0; playing=true; pb.textContent="❚❚ Pause"; last=performance.now(); if(au) au._tried=true;
    if(useAu()){try{au.currentTime=t;}catch(e){} au.play().catch(()=>{});} requestAnimationFrame(frame);}
  function pause(){playing=false; pb.textContent="▶ Play"; if(au) au.pause();}
  pb.onclick=()=>playing?pause():play();
  root.querySelector('[data-a="restart"]').onclick=()=>{render(0); play();};
  root.querySelectorAll("[data-ch]").forEach(b=>b.onclick=()=>{render(WF.scn[+b.dataset.ch]+0.01); play();});
  rng.oninput=()=>{pause(); render(+rng.value);};
  render(opts.start!=null?opts.start:(WF.scn.length>1?WF.scn[1]-0.6:WF.total));   // poster: the end of the first scene
  if(opts.start==null){t=0; shown=0; rng.value=0; tm.textContent=fmt(0)+" / "+fmt(WF.total); cap.textContent=WF.caps[0][1];}   // Play still starts from the beginning
  return {render, play, pause, audio:()=>au};
}
