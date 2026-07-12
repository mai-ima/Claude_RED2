#!/usr/bin/env node
/* 主要インタラクションの実地検証(B-G)。 */
function requirePlaywright() { try { return require('playwright'); } catch {} return require('/opt/node22/lib/node_modules/playwright'); }
const { chromium } = requirePlaywright();
const BASE = process.env.AUDIT_BASE || 'http://localhost:8930';

(async () => {
  let browser;
  try { browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' }); }
  catch (e) { browser = await chromium.launch(); }
  const page = await (await browser.newContext()).newPage();
  const results = [];
  function ok(name, cond, detail) { results.push((cond ? 'PASS ' : 'FAIL ') + name + (detail ? ' — ' + detail : '')); }

  // 1) 法人機 カメラトグル + 価格更新
  await page.goto(BASE + '/business/kaname-b1/', { waitUntil: 'networkidle' });
  const img0 = await page.getAttribute('#bizImage', 'src');
  const price0 = (await page.textContent('#bizPrice')) || '';
  await page.click('input[name=bizcam][value="1"]');
  await page.waitForTimeout(200);
  const imgNc = await page.getAttribute('#bizImage', 'src');
  ok('KANAME カメラレスで背面がnc画像に', /-nc-\d/.test(imgNc), imgNc);
  // 正面表示に切替 → nc-front
  await page.click('[data-bizview=front]');
  await page.waitForTimeout(200);
  const front = await page.getAttribute('#bizImage', 'src');
  ok('カメラレス+正面で nc-front 画像', /-nc-front/.test(front), front);
  // ストレージ変更で価格更新
  const opts = await page.$$('input[name=bizstorage]');
  if (opts[2]) { await opts[2].click(); await page.waitForTimeout(150); }
  const price1 = (await page.textContent('#bizPrice')) || '';
  ok('ストレージ変更で価格が上昇', price1 !== price0, price0 + ' -> ' + price1);

  // 2) 比較プリセット + ダッシュボード + 王冠
  await page.goto(BASE + '/products/compare/', { waitUntil: 'networkidle' });
  await page.click('.cmp-preset[data-preset="suzaku-4,zankyo"]');
  await page.waitForTimeout(300);
  const bars = await page.$$('#compareDash .cmp-bar');
  ok('プリセットで実測ダッシュボード描画', bars.length >= 4, bars.length + ' bars');
  const crown = await page.$('#compareResult .cmp-crown');
  ok('最良値に王冠SVG', !!crown);
  const dym = await page.$$('#compareResult td.cmp-best');
  ok('最良セルのハイライト', dym.length >= 1, dym.length + ' cells');

  // 3) 検索「もしかして」
  await page.goto(BASE + '/search/?q=genshin', { waitUntil: 'networkidle' });
  await page.waitForTimeout(200);
  const chip = await page.$('.dym-chip');
  ok('検索もしかしてチップ表示', !!chip);
  if (chip) {
    await chip.click(); await page.waitForTimeout(200);
    const url = page.url();
    ok('チップclickでURL更新(?q=原神)', /q=%E5%8E%9F%E7%A5%9E|q=原神/.test(decodeURI(url)) || /原神/.test(decodeURIComponent(url)), url);
  }

  console.log(results.join('\n'));
  const failed = results.filter(r => r.startsWith('FAIL'));
  await browser.close();
  process.exit(failed.length ? 1 : 0);
})();
