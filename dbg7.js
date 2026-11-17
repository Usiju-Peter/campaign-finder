const { chromium } = require('playwright-core');
(async () => {
  const b = await chromium.launch({ channel: 'msedge', headless: true }); const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('http://localhost:8765/s/07-hallmark/', { waitUntil: 'load' }); await p.waitForTimeout(2500);
  const rest = await p.evaluate(() => getComputedStyle(document.getElementById('pop-sort')).visibility);
  await p.click('[data-pop="pop-budget"]'); await p.waitForTimeout(400);
  const open = await p.evaluate(() => getComputedStyle(document.getElementById('pop-budget')).visibility);
  await p.screenshot({ path: 'C:/Users/DELL/tools/screenrec/out/v-07-hallmark-menu.png' });
  await p.keyboard.press('Escape'); await p.waitForTimeout(300);
  const closed = await p.evaluate(() => getComputedStyle(document.getElementById('pop-budget')).visibility);
  console.log({ rest, open, closed, errs }); await b.close();
})();
