#!/usr/bin/env node
/* 指定URLのスクリーンショットを撮る簡易ツール。
   使い方: node scripts/shot.js <outdir> <width> <path1> [path2 ...] */
function requirePlaywright() {
  try { return require('playwright'); } catch {}
  return require('/opt/node22/lib/node_modules/playwright');
}
const { chromium } = requirePlaywright();
const path = require('path');

(async () => {
  const [outdir, widthArg, ...paths] = process.argv.slice(2);
  const width = parseInt(widthArg, 10) || 1440;
  const base = process.env.AUDIT_BASE || 'http://localhost:8930';
  const exe = '/opt/pw-browsers/chromium';
  let browser;
  try {
    browser = await chromium.launch({ executablePath: exe });
  } catch (e) {
    browser = await chromium.launch();
  }
  // reduced-motion にするとカウントアップ演出がスキップされ、統計値が最終値で描画される
  const ctx = await browser.newContext({ viewport: { width, height: 900 }, deviceScaleFactor: 2, reducedMotion: 'reduce' });
  const page = await ctx.newPage();
  for (const p of paths) {
    const url = base + p;
    const name = (p.replace(/[^a-z0-9]+/gi, '_').replace(/^_|_$/g, '') || 'home') + '_' + width + '.png';
    const file = path.join(outdir, name);
    try {
      await page.goto(url, { waitUntil: 'networkidle', timeout: 20000 });
      // スクロール連動の reveal 演出を全展開してからフルページ撮影する
      await page.evaluate(() => {
        document.querySelectorAll('.reveal, .reveal-l, .reveal-r, .reveal-scale, .reveal-stagger')
          .forEach(el => el.classList.add('is-inview'));
      });
      await page.waitForTimeout(500);
      await page.screenshot({ path: file, fullPage: true });
      console.log('OK  ' + p + ' -> ' + file);
    } catch (e) {
      console.log('ERR ' + p + ' : ' + e.message);
    }
  }
  await browser.close();
})();
