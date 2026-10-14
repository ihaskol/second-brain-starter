// Smoke test for a project hub built from project-hub-template.html.
//   python3 -m http.server 8790   (in the page's folder)
//   PWC=/path/to/playwright-core node smoke_test.js http://localhost:8790/<page>.html
// Checks at 1280 px light and 390 px dark: every view renders, no console errors, no horizontal overflow;
// search finds something; a copy button responds; the PDF viewer draws a sharp canvas (if there are PDFs);
// the video loads as a Blob and can seek (if there is a video). Exit code 1 on any failure.
const {chromium}=require(process.env.PWC||'playwright-core');
(async()=>{const U=process.argv[2]; let fail=0; const b=await chromium.launch();
 for(const [w,h,scheme] of [[1280,900,'light'],[390,844,'dark']]){
  const p=await b.newPage({viewport:{width:w,height:h},colorScheme:scheme}); const errs=[]; p.on('pageerror',e=>errs.push(e.message)); p.on('console',m=>{if(m.type()==='error'&&!/favicon/.test(m.text())) errs.push(m.text())});
  for(const v of ['start','how','build','library']){await p.goto(U+'#'+v); await p.waitForTimeout(500);
   const r=await p.evaluate(()=>({h1:!!document.querySelector('main h1'),over:document.documentElement.scrollWidth>innerWidth}));
   const ok=r.h1&&!r.over; if(!ok) fail++; console.log(w,v,ok?'ok':'FAIL',JSON.stringify(r));}
  await p.goto(U+'#start'); await p.click('#searchBtn'); await p.fill('#q','gu'); await p.waitForTimeout(200);
  const hits=await p.$$eval('#searchResults [data-go]',a=>a.length); console.log(w,'search hits',hits); if(!hits) fail++;
  await p.goto(U+'#build-work'); await p.waitForTimeout(300); const cb=await p.$('[data-copy]'); if(cb){await cb.click(); await p.waitForTimeout(200); console.log(w,'copy button →',await cb.textContent())}
  if(await p.evaluate(()=>DECKS.length+DOCS.length)){await p.goto(U+'#library'); await p.waitForTimeout(300); await p.click('[data-pdf]'); await p.waitForSelector('#vStage canvas',{timeout:15000}).catch(()=>{});
   const c=await p.evaluate(()=>{const c=document.querySelector('#vStage canvas'); return c?{px:c.width,css:Math.round(c.getBoundingClientRect().width)}:null}); console.log(w,'viewer',JSON.stringify(c)); if(!c||c.px<c.css*1.9) fail++; await p.click('#vClose');}
  if(await p.evaluate(()=>!!VIDEO)){await p.goto(U+'#library-video'); await p.waitForTimeout(2500);
   const v=await p.evaluate(async()=>{const v=document.querySelector('video[data-src]'); await new Promise(r=>{if(v.readyState>=1) r(); else {v.addEventListener('loadedmetadata',r,{once:true}); setTimeout(r,5000)}}); v.currentTime=Math.min(5,v.duration/2||0); await new Promise(r=>setTimeout(r,500)); return {blob:v.src.startsWith('blob:'),seek:v.seekable.length?v.seekable.end(0):0,t:v.currentTime}});
   console.log(w,'video',JSON.stringify(v)); if(!v.blob||!v.seek) fail++;}
  if(errs.length){fail++; console.log(w,'errors',errs)} await p.close();}
 await b.close(); console.log(fail?'FAIL ('+fail+')':'PASS'); process.exit(fail?1:0);})();
