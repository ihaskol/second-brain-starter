// Generic in-page link check for single-file hash-routed pages (ux-redesign skill).
// For every view, clicks every internal "#…" link (reloading between clicks) and checks that
// the target exists, is visible below the sticky header, and that any enclosing <details> is open.
// Also reports page errors and links to a page's own files (which artifact sandboxes block).
//
// Usage (serve the page folder first, e.g. python3 -m http.server 8765):
//   PWC=/path/to/node_modules/playwright-core node link_check.js http://localhost:8765/page.html start,how,build,library [header-selector]
const {chromium}=require(process.env.PWC||"playwright-core");
const [url,routesArg,hdrSel="header"]=process.argv.slice(2);
if(!url||!routesArg){console.error("usage: link_check.js <url> <route1,route2,…> [header-selector]"); process.exit(2)}
(async()=>{
 const b=await chromium.launch(); let bad=0, n=0;
 for(const [W,H] of [[1280,900],[390,844]]){
  const p=await b.newPage({viewport:{width:W,height:H}}); const errs=[]; p.on("pageerror",e=>errs.push(e.message));
  for(const r of routesArg.split(",")){
   await p.goto(url+"#"+r); await p.waitForTimeout(300);
   const hrefs=[...new Set(await p.$$eval('a[href^="#"]',as=>as.map(a=>a.getAttribute("href")).filter(h=>h&&h!=="#")))];
   const selfFiles=await p.$$eval('a[href]:not([href^="#"]):not([href^="http"]):not([href^="mailto"])',as=>as.map(a=>a.getAttribute("href")));
   selfFiles.forEach(f=>{bad++; console.log(`${W} ${r}: link to own file "${f}" (blocked in artifacts)`)});
   for(const h of hrefs){
    n++; await p.goto(url+"#"+r); await p.waitForTimeout(150);
    const loc=p.locator(`a[href="${h}"]`).first(); if(!(await loc.isVisible().catch(()=>false))) continue;   // hidden (e.g. inside closed menus)
    await loc.click(); await p.waitForTimeout(350);
    const res=await p.evaluate(([h,hs])=>{const id=h.slice(1); const el=document.getElementById(id); const hdr=document.querySelector(hs);
      const hb=hdr?hdr.getBoundingClientRect().bottom:0;
      if(!el) return {ok:true,note:"view link"};   // a link to a whole view has no element with that id
      const top=el.getBoundingClientRect().top; const closed=el.closest("details")&&!el.closest("details").open;
      return {ok:top>=hb-2&&top<innerHeight&&!closed,top:Math.round(top),hb:Math.round(hb),closed}},[h,hdrSel]);
    if(!res.ok){bad++; console.log(`${W} ${r}: ${h} → top ${res.top} (header ends ${res.hb})${res.closed?" inside a closed <details>":""}`)}
   }
  }
  if(errs.length){bad+=errs.length; console.log(W,"page errors:",errs)}
  await p.close();
 }
 await b.close(); console.log(`${n} link clicks checked, ${bad} problem(s)`); process.exit(bad?1:0);
})();
