// Проверка собранного сайта: node proverka_site.mjs [--shots <папка>] [--url <адрес>]
// Без --url поднимает site/ на локальном порту. Ловит: ошибки консоли, ответы 4xx/5xx, горизонтальную прокрутку
// на 390 и 1440, незагруженные демо во фреймах, страницу без тёмной темы.
import { createRequire } from 'module';
import { spawn } from 'child_process';
import { readdirSync, mkdirSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const ROOT = dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const opt = (k) => { const i = args.indexOf(k); return i > -1 ? args[i + 1] : null };
const shots = opt('--shots'), ext = opt('--url');
const PORT = 8765, BASE = ext || `http://127.0.0.1:${PORT}/`;
const PAGES = ['index.html', 'cerus.html', 'setki.html', 'referensy.html', 'klassifikator.html'];
const VIEWS = [{ k: 'm', w: 390, h: 844 }, { k: 'd', w: 1440, h: 900 }];
if (shots) mkdirSync(shots, { recursive: true });

function findPlaywright() {
  const sites = join(process.env.HOME, 'Sites');
  for (const d of [ROOT, ...readdirSync(sites).map((x) => join(sites, x))]) {
    if (existsSync(join(d, 'node_modules', 'playwright'))) return createRequire(d + '/')('playwright');
  }
  throw new Error('Playwright не найден в ~/Sites/*/node_modules');
}

let bad = 0;
const fail = (m) => { bad++; console.log('FAIL ' + m) };
const srv = ext ? null : spawn('python3', ['-m', 'http.server', String(PORT), '--bind', '127.0.0.1'], { cwd: join(ROOT, 'site'), stdio: 'ignore' });
await new Promise((r) => setTimeout(r, 900));
const browser = await findPlaywright().chromium.launch();
try {
  for (const p of PAGES) for (const v of VIEWS) {
    const ctx = await browser.newContext({ viewport: { width: v.w, height: v.h }, isMobile: v.k === 'm', hasTouch: v.k === 'm', colorScheme: 'light' });
    const page = await ctx.newPage(), errs = [];
    page.on('pageerror', (e) => errs.push(e.message));
    page.on('console', (c) => { if (c.type() === 'error') errs.push(c.text()) });
    page.on('response', (r) => { if (r.status() >= 400) errs.push(r.status() + ' ' + r.url()) });
    await page.goto(BASE + p, { waitUntil: 'load' });
    const H = await page.evaluate(() => document.documentElement.scrollHeight);
    for (let y = 0; y < H; y += 700) { await page.evaluate((yy) => scrollTo(0, yy), y); await page.waitForTimeout(90) }
    await page.waitForTimeout(1200);
    const over = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    if (over > 1) fail(`${p} ${v.w}: горизонтальная прокрутка +${over}px`);
    if (!(await page.evaluate(() => !!document.getElementById('tema-btn')))) fail(`${p}: нет кнопки темы`);
    if (p === 'index.html') {
      const st = await page.evaluate(() => [...document.querySelectorAll('.stage')].map((s) => { const f = s.querySelector('iframe'); let ok = false; try { ok = !!(f && f.contentDocument && f.contentDocument.getElementById('meta')) } catch (e) {} return [s.dataset.src, ok] }));
      st.filter((x) => !x[1]).forEach((x) => fail(`${p} ${v.w}: демо не загрузилось: ${x[0]}`));
      console.log(`     демо во фреймах: ${st.filter((x) => x[1]).length} из ${st.length}`);
    }
    if (errs.length) fail(`${p} ${v.w}: ` + [...new Set(errs)].slice(0, 4).join(' | '));
    if (shots) {
      await page.evaluate(() => scrollTo(0, 0)); await page.waitForTimeout(300);
      await page.screenshot({ path: join(shots, `${p.replace('.html', '')}-${v.k}-top.png`) });
      const sel = p === 'index.html' ? '.blok' : p === 'cerus.html' ? '#b03' : (p === 'setki.html' || p === 'referensy.html') ? '.blok:nth-of-type(3)' : '#kl-body';
      const el = page.locator(sel).first();
      if (await el.count()) { await el.scrollIntoViewIfNeeded(); await page.waitForTimeout(1500); await page.screenshot({ path: join(shots, `${p.replace('.html', '')}-${v.k}-blok.png`) }) }
    }
    console.log(`ok   ${p} ${v.w}`);
    await ctx.close();
  }
} finally {
  await browser.close();
  if (srv) srv.kill();
}
console.log(bad ? `\nИТОГ: ${bad} замечаний` : '\nИТОГ: сайт чистый');
process.exit(bad ? 1 : 0);
