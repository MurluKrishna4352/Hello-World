// Usage: node render.js job1.json [job2.json ...]   (paths relative to stage dir)
//        node render.js --svg in.svg out.png W H     (transparent SVG/HTML -> PNG)
const { chromium } = require('playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const MIME = { '.js': 'text/javascript', '.json': 'application/json', '.html': 'text/html', '.ttf': 'font/ttf',
  '.otf': 'font/otf', '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml' };

function serve() {
  return new Promise((resolve) => {
    const srv = http.createServer((req, res) => {
      const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
      if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); res.end(); return; }
      res.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' });
      fs.createReadStream(p).pipe(res);
    });
    srv.listen(0, '127.0.0.1', () => resolve(srv));
  });
}

(async () => {
  const args = process.argv.slice(2);
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--enable-webgl'] });
  if (args[0] === '--svg') {
    const [, inp, out, w, h] = args;
    const page = await browser.newPage({ viewport: { width: +w, height: +h } });
    const srv = await serve();
    const rel = path.relative(ROOT, path.resolve(inp));
    await page.goto(`http://127.0.0.1:${srv.address().port}/${rel}`);
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(150);
    await page.screenshot({ path: out, omitBackground: true, clip: { x: 0, y: 0, width: +w, height: +h } });
    srv.close(); await browser.close(); return;
  }
  const srv = await serve();
  const port = srv.address().port;
  for (const j of args) {
    const job = JSON.parse(fs.readFileSync(path.join(ROOT, j)));
    const page = await browser.newPage({ viewport: { width: 800, height: 600 } });
    page.on('console', (m) => { if (m.type() === 'error') console.log('console:', m.text()); });
    page.on('pageerror', (e) => console.log('pageerror:', e.message));
    const t0 = Date.now();
    await page.goto(`http://127.0.0.1:${port}/web/index.html?job=/${j}`);
    await page.waitForFunction(() => window.__DONE === true || window.__ERR, null, { timeout: 300000 });
    const err = await page.evaluate(() => window.__ERR);
    if (err) { console.log('ERROR', j, err); await page.close(); continue; }
    const data = await page.evaluate(() => document.querySelector('canvas').toDataURL('image/png'));
    fs.writeFileSync(path.join(ROOT, job.out), Buffer.from(data.split(',')[1], 'base64'));
    console.log('rendered', job.out, ((Date.now() - t0) / 1000).toFixed(1) + 's');
    await page.close();
  }
  srv.close(); await browser.close();
})();
