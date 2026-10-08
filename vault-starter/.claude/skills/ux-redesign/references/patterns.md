# UX patterns that worked (explainer hub redesign, 2026-10-07)

Copy, adapt the selectors, keep the behaviour. Every snippet below ran in a published explainer hub and was tested at 1280 px and 390 px.
`$` is `(s,r=document)=>r.querySelector(s)`.

## 1. Hash router with old-link aliases

Views are `V.start`, `V.how`, … ; sections inside a view use ids like `how-blocks`. Old hashes map to new places,
and every enclosing `<details>` opens.

```js
const ALIAS={understand:"how","understand-session":"how-session",setup:"build",prompts:"build-work",visuals:"library-figures"};
function resolve(){let h=(location.hash||"#start").slice(1); if(ALIAS[h]) h=ALIAS[h];
 const base=h.split("-")[0]; const key=V[h]?h:(V[base]?base:"start"); return [key,h]}
function render(o={}){const [key,h]=resolve();
 document.querySelectorAll("nav.tabs a").forEach(a=>a.setAttribute("aria-current",a.getAttribute("href")==="#"+key?"page":"false"));
 $("#main").innerHTML=V[key](); wire();
 if(h!==key){const el=document.getElementById(h); if(el){let d=el; while(d){if(d.tagName==="DETAILS") d.open=true; d=d.parentElement}
   setTimeout(()=>el.scrollIntoView({block:"start"}),0)}} else if(!o.keep) window.scrollTo(0,0)}
window.addEventListener("hashchange",()=>render());
// a link to the hash you are already on still works:
document.addEventListener("click",e=>{const a=e.target.closest('a[href^="#"]'); if(a&&a.getAttribute("href")===(location.hash||"#start")){e.preventDefault(); render()}});
```

## 2. Anchors land below the sticky header (measured, not guessed)

```css
[id]{scroll-margin-top:var(--hdr,96px)}
header.top{position:sticky; top:env(safe-area-inset-top,0px)}
```
```js
const setHdr=()=>document.documentElement.style.setProperty("--hdr",(document.querySelector("header.top").offsetHeight+12)+"px");
setHdr(); window.addEventListener("resize",setHdr);   // call setHdr() again when a header panel (search, settings) opens
```

## 3. Progressive disclosure: "Go deeper"

```html
<section class="chapter" id="how-jev"><span class="num">CHAPTER 3</span><h2>…</h2>
  <p class="short">Two or three plain sentences.</p>
  …one key visual…
  <details class="deeper"><summary>Go deeper: the decision gate and where it sits</summary><div>…tables, extra figures…</div></details>
</section>
```
```css
details.deeper>summary{cursor:pointer; list-style:none; padding:14px 0; font-weight:700; display:flex; gap:10px}
details.deeper>summary::-webkit-details-marker{display:none}
details.deeper>summary::before{content:"+"; width:24px; height:24px; border:1px solid var(--line); border-radius:6px; display:grid; place-items:center}
details.deeper[open]>summary::before{content:"−"}
```

## 4. Back-to-top button

```html
<button type="button" id="toTop" class="totop" hidden aria-label="Back to top">↑ Top</button>
```
```css
.totop{position:fixed; right:16px; bottom:calc(16px + env(safe-area-inset-bottom,0px)); z-index:25; min-height:44px;
  border:1px solid var(--line); background:var(--paper); color:var(--ink); border-radius:999px; padding:10px 16px; font:inherit; font-weight:600}
```
```js
const toTop=$("#toTop"); const showTop=()=>{toTop.hidden=window.scrollY<500};
window.addEventListener("scroll",showTop,{passive:true}); showTop();
toTop.onclick=()=>{const calm=matchMedia("(prefers-reduced-motion: reduce)").matches;
  window.scrollTo({top:0,behavior:calm?"auto":"smooth"}); setTimeout(()=>$(".brand").focus(),calm?0:400)};
```

## 5. Figure viewer: Prev/Next, counter, arrow keys, click outside closes

```js
let lbList=[], lbIdx=0;
function showFig(){const f=lbList[lbIdx]; $("#lbImg").src="img/"+f; $("#lbPos").textContent=(lbIdx+1)+" / "+lbList.length;
  $("#lbPrev").disabled=lbIdx<=0; $("#lbNext").disabled=lbIdx>=lbList.length-1}
function openFig(file,list){lbList=list&&list.length?list:ALL_FIGS; lbIdx=lbList.indexOf(file); showFig(); const d=$("#lb"); if(!d.open) d.showModal()}
// open from a gallery → step through what is currently shown (respects the active filter):
b.onclick=()=>openFig(b.dataset.fig, b.closest(".gal")?[...document.querySelectorAll(".gal [data-fig]")].map(x=>x.dataset.fig):null);
$("#lb").addEventListener("keydown",e=>{if(e.key==="ArrowRight") $("#lbNext").click(); if(e.key==="ArrowLeft") $("#lbPrev").click()});
["#lb","#viewer"].forEach(id=>$(id).addEventListener("click",e=>{if(e.target===e.currentTarget) e.currentTarget.close()}));  // backdrop click
```
```css
/* never let a flex box stretch an image or canvas */
dialog.lb .lbimg{display:flex; align-items:flex-start; overflow:auto}
dialog.lb img{flex:none; margin:0 auto; max-width:100%; max-height:calc(94vh - 130px); width:auto; height:auto}
```

## 6. Clickable step cards (story or animation)

Cards that look like stations are `<button>`s. A click stops autoplay and jumps to that card's step; a card that appears twice
(start and end) toggles between its two steps.

```js
document.querySelectorAll(".st").forEach(c=>c.onclick=()=>{stopStory(); const k=c.dataset.st;
  let i=STORY.findIndex(x=>x[0]===k); if(k==="mem"&&storyI===0) i=STORY.length-1; storyI=i; showStory()});
```
```css
button.st{font:inherit; color:var(--ink); text-align:left; cursor:pointer; width:100%}
button.st:hover{border-color:var(--c)}
```

## 7. Alternatives as tabs (for example prompts)

```js
document.querySelectorAll("[data-prompt]").forEach(b=>b.onclick=()=>{promptSel=b.dataset.prompt; render({keep:true}); $("#pt-"+promptSel).focus()});
const tabs=[...document.querySelectorAll("[data-prompt]")];
tabs.forEach((b,i)=>b.onkeydown=e=>{if(e.key==="ArrowRight"||e.key==="ArrowLeft"){e.preventDefault();
  tabs[(i+(e.key==="ArrowRight"?1:-1)+tabs.length)%tabs.length].click()}});
```
Markup: `role="tablist"` on the row, `role="tab"` and `aria-selected` on each button, `role="tabpanel"` with `aria-labelledby` on the panel.

## 8. Copy button that works on every click

```js
b.onclick=e=>{e.preventDefault(); const txt=[...b.parentElement.childNodes].filter(n=>n!==b).map(n=>n.textContent).join("");
  (navigator.clipboard?navigator.clipboard.writeText(txt):Promise.reject()).then(()=>{b.textContent="Copied"})
  .catch(()=>{const r=document.createRange(); r.selectNodeContents(b.parentElement); const s=getSelection(); s.removeAllRanges(); s.addRange(r); b.textContent="Selected"})};
```
(Stripping a leading "Copy" from `textContent` breaks on the second click, when the button already says "Copied".)

```css
pre.cmd{position:relative; padding:36px 12px 10px}   /* room for the button: it must not cover the command */
pre.cmd button{position:absolute; top:4px; right:4px}
```

## 9. Phone layout

```css
@media (max-width:760px){
  .topbar{justify-content:space-between}
  nav.tabs{order:3; flex:0 0 100%}                    /* tabs get their own row */
  nav.tabs a{padding:8px 9px; font-size:.9rem}        /* all tabs fit at 375 px */
}
```
Wide diagram: `<div class="mg-diagram" tabindex="0" role="region" aria-label="Diagram …, scrollable">` with `overflow-x:auto`,
an inner `svg{min-width:720px}`, and a "Swipe sideways to see the whole diagram" hint shown only under 760 px.

## 10. Dark hero inside a light page

```css
.hero{background:var(--hero); color:var(--hero-ink);
  /* scoped dark tokens: anything inside renders dark in both themes */
  --paper:#131f38; --ink:#e8ecf0; --muted:#9aa5b1; --line:#2a3e66; --navy-soft:#1d2840; --aqua:#4fc79a; …}
```
A static copy of an interactive diagram can live in the hero (ids renamed, `role="img"`), with a link to the interactive version.

## Artifact pitfalls hit during the redesign

| Pitfall | Fix |
|---|---|
| An "Open PDF" link to `pdfs/x.pdf` opens the sandbox frame URL (`claude.ai/code/frame/…`) and shows ERR_BLOCKED_BY_RESPONSE | Show files in-page only (viewer with zoom); artifacts also block downloads |
| PDF pages squashed in the viewer | The flex container stretched the canvas: `align-items:flex-start`, explicit canvas CSS height |
| Blurry slides | Keynote export `PDF image quality:Good` = 72 ppi; use `Best` |
| Publish refused: "supporting file carries a DOCTYPE" | Strip `<!DOCTYPE …>` from matplotlib SVGs before publishing |
| Publish refused: "file not read in this session" | Read the live file with the Artifact tool, compare its hash to the local backup, then publish |
| `scrollable-region-focusable` after adding a wide hero diagram | Give the scroll container `tabindex="0"`, `role="region"`, `aria-label` |
| Anchor targets hidden under the sticky header | Pattern 2 |
