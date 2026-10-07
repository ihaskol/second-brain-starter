const { chromium } = require(process.env.PLAYWRIGHT_CORE || 'playwright-core');
const fs=require('fs'); const out=process.argv[2];
(async()=>{
  const dir=process.env.HOME+'/Library/Caches/ms-playwright'; const exe=fs.readdirSync(dir).find(d=>d.startsWith('chromium-'));
  const bin=require('child_process').execSync(`ls -d ${dir}/${exe}/*/*.app/Contents/MacOS/* | head -1`).toString().trim();
  const b=await chromium.launch({executablePath:bin});
  const routes=['home','map','weeks','w03','w05','w06','w08','w17','w18','workshops','exam','methods','assignments','support'];
  for(const [w,scheme] of [[1280,'light'],[390,'dark']]){
    const ctx=await b.newContext({viewport:{width:w,height:900},colorScheme:scheme}); const p=await ctx.newPage();
    const errs=[]; p.on('pageerror',e=>errs.push(e.message)); p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
    await p.goto('http://localhost:8765/' + (process.argv[3]||'index.html') + '#home'); await p.waitForTimeout(800);
    for(const r of routes){ await p.evaluate(r=>location.hash=r,r); await p.waitForTimeout(250);
      const ov=await p.evaluate(()=>document.documentElement.scrollWidth-window.innerWidth);
      if(ov>1) errs.push(`overflow ${ov}px on #${r} @${w}`);
      if(['home','map','w06','w17','exam'].includes(r)) await p.screenshot({path:`${out}/${r}-${w}.png`,fullPage:r!=='home'?false:false});
    }
    // exam subtabs
    await p.evaluate(()=>location.hash='exam'); await p.waitForTimeout(200);
    for(const k of ['flash','design','mist','synth','plan']){ await p.click(`[data-et="${k}"]`); await p.waitForTimeout(150);}
    await p.click('[data-et="design"]'); await p.locator('#dList .opt').first().click();
    // map thread
    await p.evaluate(()=>location.hash='map'); await p.waitForTimeout(200); await p.click('[data-thread="t2"]'); await p.waitForTimeout(150); await p.screenshot({path:`${out}/map-thread-${w}.png`});
    // viewer
    await p.evaluate(()=>location.hash='w06'); await p.waitForTimeout(200); await p.locator('[data-pdf]').first().click(); await p.waitForTimeout(5000);
    const vtxt=await p.locator('#vPage').textContent(); errs.push('viewer page label: '+vtxt);
    await p.screenshot({path:`${out}/viewer-${w}.png`});
    console.log(w,scheme,JSON.stringify(errs,null,1));
    await ctx.close();
  }
  await b.close();
})();
