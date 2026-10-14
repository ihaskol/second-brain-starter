// Serialise a whiteboard engine page for the interactive player (assets/player.js):
//   PWC=… node export_player.js <whiteboard.html> <timing.json> <out.json>
// out.json = {svg, els, scn, caps, total}. Mount it with wfMount(root, WF, {audio}) in any page;
// rough.js is not needed at runtime. Captions come from the timing's lines.
const {chromium}=require(process.env.PWC||'playwright-core');
const fs=require('fs'),path=require('path');
(async()=>{const [page,timing,out]=process.argv.slice(2); const T=JSON.parse(fs.readFileSync(timing));
 const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1920,height:1080}});
 await p.goto('file://'+path.resolve(page)); await p.evaluate(()=>document.fonts.ready);
 const data=await p.evaluate(T=>{build(T); const r1=n=>Math.round(n*10)/10;
  SC.forEach((g,i)=>g.setAttribute('data-sc',i));
  // give clip paths unique ids so several players can share a page
  document.querySelectorAll('#defs clipPath').forEach(c=>{const old=c.id; c.id='wf'+old; document.querySelectorAll(`[clip-path="url(#${old})"]`).forEach(g=>g.setAttribute('clip-path',`url(#wf${old})`));});
  const els=EL.map((e,i)=>{e.g.setAttribute('data-e',i);
    if(e.kind==='draw'){e.paths.forEach((q,j)=>{q.setAttribute('data-l',r1(e.lens[j])); q.removeAttribute('style');}); e.fills.forEach(f=>{f.setAttribute('data-f',''); f.removeAttribute('style');}); return {i,k:'d',t0:+e.t0.toFixed(2),d:e.dur};}
    const bb=e.tx.getBBox(); const cid=e.g.getAttribute('clip-path').match(/#([^)]+)/)[1];
    return {i,k:'t',t0:+e.t0.toFixed(2),d:+e.dur.toFixed(2),c:cid,bb:[r1(bb.x),r1(bb.y),r1(bb.width),r1(bb.height)]};});
  document.querySelectorAll('#stage path').forEach(q=>q.setAttribute('d',q.getAttribute('d').replace(/-?\d+\.\d+/g,m=>String(Math.round(+m*10)/10))));
  const s=document.getElementById('s').cloneNode(true); s.removeAttribute('id'); s.removeAttribute('width'); s.removeAttribute('height');
  const caps=[]; T.scenes.forEach(sc=>sc.seg.forEach(g=>caps.push([g.t,g.text])));
  return {svg:s.outerHTML,els,scn:T.scenes.map(sc=>sc.start),chapters:T.scenes.map((sc,i)=>sc.title||("Part "+(i+1))),caps,total:T.total};},T);
 fs.writeFileSync(out,JSON.stringify(data)); console.log('elements',data.els.length,'svg KB',Math.round(data.svg.length/1024)); await b.close();})();
