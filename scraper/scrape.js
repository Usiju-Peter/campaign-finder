// Scrape Content Rewards Discover: step "list" saves every campaign card, step "details" opens each candidate page.
// usage: node scraper/scrape.js list | details
// Browser: installed Edge when BROWSER_CHANNEL=msedge (Windows laptop), else Playwright's own Chromium (CI).
const { chromium } = require('playwright-core');
const fs = require('fs'); const path = require('path');
const WORK = path.join(__dirname, '..', 'work'); fs.mkdirSync(WORK, { recursive: true });
const step = process.argv[2];

async function browser() {
  return chromium.launch({ headless: true, ...(process.env.BROWSER_CHANNEL ? { channel: process.env.BROWSER_CHANNEL } : {}) });
}

async function list() {
  const b = await browser();
  const page = await (await b.newContext({ viewport: { width: 1600, height: 1000 } })).newPage();
  await page.goto('https://contentrewards.com/c/discover?section=all', { waitUntil: 'load', timeout: 90000 });
  await page.waitForTimeout(6000);
  const seen = new Map(); let still = 0;
  for (let round = 0; round < 250 && still < 6; round++) {
    const cards = await page.$$eval('a[href^="/c/campaigns/"]', (as) => as.map((a) => ({ href: a.getAttribute('href'), text: a.innerText.replace(/\s+/g, ' ').trim() })));
    const before = seen.size;
    cards.forEach((c) => { if (!seen.has(c.href) || seen.get(c.href).text.length < c.text.length) seen.set(c.href, c); });
    still = seen.size === before ? still + 1 : 0;
    await page.mouse.wheel(0, 2500); await page.waitForTimeout(1200);
    const more = page.getByRole('button', { name: /load more|show more/i }).first();
    if (await more.isVisible().catch(() => false)) { await more.click().catch(() => {}); await page.waitForTimeout(2000); still = 0; }
  }
  const out = [...seen.values()];
  if (out.length < 300) throw new Error(`only ${out.length} campaigns found; the page may have changed`);
  fs.writeFileSync(path.join(WORK, 'list.json'), JSON.stringify(out));
  console.log('list:', out.length, 'campaigns');
  await b.close();
}

async function details() {
  const hrefs = JSON.parse(fs.readFileSync(path.join(WORK, 'candidates.json'), 'utf8'));
  const OUT = path.join(WORK, 'details'); fs.rmSync(OUT, { recursive: true, force: true }); fs.mkdirSync(OUT, { recursive: true });
  const b = await browser();
  const ctx = await b.newContext({ viewport: { width: 1400, height: 1000 } });
  await ctx.route(/\.(png|jpe?g|webp|gif|mp4|webm|woff2?)(\?|$)/i, (r) => r.abort());
  let i = 0, done = 0, failed = 0;
  const worker = async () => {
    const page = await ctx.newPage();
    while (i < hrefs.length) {
      const h = hrefs[i++];
      let ok = false;
      for (let attempt = 0; attempt < 3 && !ok; attempt++) {
        try {
          await page.goto('https://contentrewards.com' + h, { waitUntil: 'load', timeout: 60000 });
          await page.waitForTimeout(3000 + attempt * 2000);
          const text = await page.innerText('body');
          if (!text.includes('\nBack\n')) throw new Error('page not ready');
          fs.writeFileSync(path.join(OUT, h.split('/').pop() + '.txt'), text); ok = true;
        } catch (e) { await page.waitForTimeout(2000); }
      }
      if (!ok) failed++;
      if (++done % 50 === 0) console.log('details:', done, '/', hrefs.length);
    }
  };
  await Promise.all([worker(), worker(), worker()]);
  console.log('details:', done - failed, 'saved,', failed, 'failed');
  await b.close();
}

(step === 'list' ? list() : step === 'details' ? details() : Promise.reject(new Error('step must be list or details')))
  .catch((e) => { console.error(e); process.exit(1); });
