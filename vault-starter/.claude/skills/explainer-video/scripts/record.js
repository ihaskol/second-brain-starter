// Record frames from an engine page (whiteboard.html, crayon.html, or a player page in ?record mode).
//   PWC=/path/to/playwright-core node record.js <page.html> <timing.json> <framesdir> [fps=25] [width=1920] [height=1080]
// The page must expose build(timing) and render(t). Frames: <framesdir>/00000.jpg …
const {chromium}=require(process.env.PWC||'playwright-core');
const fs=require('fs'),path=require('path');
(async()=>{const [page,timing,out,fps='25',w='1920',h='1080']=process.argv.slice(2); const FPS=+fps;
 fs.mkdirSync(out,{recursive:true}); const T=JSON.parse(fs.readFileSync(timing));
 const b=await chromium.launch(); const p=await b.newPage({viewport:{width:+w,height:+h}});
 const errs=[]; p.on('pageerror',e=>errs.push(e.message));
 await p.goto('file://'+path.resolve(page)); await p.evaluate(()=>document.fonts.ready); await p.evaluate(T=>build(T),T);
 const n=Math.ceil(T.total*FPS);
 if(process.env.STILLS){for(const t of process.env.STILLS.split(',')){await p.evaluate(t=>render(t),+t); await p.screenshot({path:path.join(out,'still-'+t+'.png')});} console.log('stills; errors',errs); await b.close(); return;}
 for(let i=0;i<n;i++){const f=path.join(out,String(i).padStart(5,'0')+'.jpg'); await p.evaluate(t=>render(t),i/FPS); await p.screenshot({path:f,type:'jpeg',quality:92});}
 console.log('frames',n,'errors',errs); await b.close();})();
