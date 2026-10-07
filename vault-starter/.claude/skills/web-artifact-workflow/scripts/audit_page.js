// Accessibility + layout audit for a local web page / artifact source.
// Usage: PLAYWRIGHT_CORE=/path/to/node_modules/playwright-core \
//   node audit_page.js <url-without-hash> [routes,comma,separated] [outdir]
// Example: node audit_page.js http://localhost:8765/page.html home,map,w06 ./shots
// Checks, at 1280px light and 390px dark, for each route (#hash):
//   axe-core WCAG 2 A/AA + best-practice violations, console/page errors,
//   horizontal overflow, tap targets < 24px (links inside sentences reported separately).
const { chromium } = require(process.env.PLAYWRIGHT_CORE || 'playwright-core');
const fs = require('fs'), path = require('path'), https = require('https');
const url = process.argv[2], routes = (process.argv[3] || '').split(',').filter(Boolean), out = process.argv[4];
if (!url) { console.error('usage: node audit_page.js <url> [routes] [outdir]'); process.exit(2); }
const AXE = path.join(__dirname, 'axe.min.js');
const get = u => new Promise((ok, no) => https.get(u, r => { let d = ''; r.on('data', c => d += c); r.on('end', () => ok(d)); }).on('error', no));
(async () => {
  if (!fs.existsSync(AXE)) fs.writeFileSync(AXE, await get('https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.2/axe.min.js'));
  const axe = fs.readFileSync(AXE, 'utf8');
  const dir = process.env.HOME + '/Library/Caches/ms-playwright';
  const exe = fs.readdirSync(dir).find(d => d.startsWith('chromium-'));
  const bin = require('child_process').execSync(`ls -d ${dir}/${exe}/*/*.app/Contents/MacOS/* | head -1`).toString().trim();
  const b = await chromium.launch({ executablePath: bin });
  const report = { violations: {}, errors: [], overflow: [], smallTargets: [], inlineSmallLinks: 0 };
  if (out) fs.mkdirSync(out, { recursive: true });
  for (const [w, scheme] of [[1280, 'light'], [390, 'dark']]) {
    const p = await (await b.newContext({ viewport: { width: w, height: 900 }, colorScheme: scheme })).newPage();
    p.on('pageerror', e => report.errors.push(`${w}: ${e.message}`));
    p.on('console', m => { if (m.type() === 'error' && !/favicon|404/.test(m.text())) report.errors.push(`${w}: ${m.text()}`); });
    for (const r of (routes.length ? routes : [''])) {
      await p.goto(url + (r ? '#' + r : '')); await p.waitForTimeout(500);
      await p.addScriptTag({ content: axe });
      const v = await p.evaluate(async () => (await axe.run(document, { runOnly: ['wcag2a', 'wcag2aa', 'best-practice'] })).violations.map(x => ({ id: x.id, impact: x.impact, help: x.help, t: x.nodes.slice(0, 2).map(n => n.target.join(' ')) })));
      v.forEach(x => { const k = report.violations[x.id] ||= { impact: x.impact, help: x.help, where: [] }; k.where.push(`${r || '/'}@${w}: ${x.t.join(' | ')}`); });
      const ov = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth); if (ov > 1) report.overflow.push(`${r || '/'}@${w}: ${ov}px`);
      if (w === 390) {
        const s = await p.evaluate(() => [...document.querySelectorAll('a,button,input,select,summary,[tabindex]')].filter(e => { const b = e.getBoundingClientRect(); return b.width > 0 && (b.height < 24 || b.width < 24); }).map(e => ({ inline: getComputedStyle(e).display === 'inline' && !!e.closest('p,li,label'), d: e.tagName + ':' + (e.textContent || e.getAttribute('aria-label') || '').trim().slice(0, 24) })));
        s.forEach(x => x.inline ? report.inlineSmallLinks++ : report.smallTargets.push(`${r || '/'}: ${x.d}`));
      }
      if (out) await p.screenshot({ path: `${out}/${(r || 'root')}-${w}.png` });
    }
  }
  await b.close();
  console.log(JSON.stringify(report, null, 1));
  process.exit(Object.keys(report.violations).length || report.errors.length || report.overflow.length ? 1 : 0);
})();
