// Проверка демо: node proverka.mjs [id ...] [--shots <папка>]
// Ловит: битую карточку (meta), ошибки консоли, горизонтальную прокрутку, длинное тире, внешние адреса.
import { createRequire } from 'module';
import { readdirSync, readFileSync, mkdirSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const ROOT = dirname(fileURLToPath(import.meta.url));
const DEMO = join(ROOT, 'demo');
const KEYS = ['id', 'nazvanie', 'tip', 'etap', 'vopros', 'smysl', 'setka_d', 'setka_m', 'animaciya', 'kak_rabotaet', 'kogda', 'ne_kogda', 'u_cerusa', 'sled', 'vid', 'vysota'];
const TIPY = ['SYS', 'OFF', 'PROD', 'REL', 'VAL', 'PROOF', 'EXP', 'COM', 'PROC', 'COMP', 'RISK', 'CTA', 'CONV', 'MEDIA', 'NICHE'];
const ETAPY = ['IDENTIFY', 'UNDERSTAND', 'WANT', 'EVALUATE', 'BELIEVE', 'REDUCE RISK', 'ACT', '—'];
const W = { m: 390, d: 1280 };

const args = process.argv.slice(2);
const si = args.indexOf('--shots');
const shots = si > -1 ? args[si + 1] : null;
const ids = args.filter((a, i) => !a.startsWith('--') && i !== si + 1 || (si === -1 && !a.startsWith('--')));
const files = readdirSync(DEMO).filter((f) => f.endsWith('.html')).filter((f) => !ids.length || ids.includes(f.slice(0, -5)));
if (shots) mkdirSync(shots, { recursive: true });

function findPlaywright() {
  const sites = join(process.env.HOME, 'Sites');
  for (const d of [ROOT, ...readdirSync(sites).map((x) => join(sites, x))]) {
    if (existsSync(join(d, 'node_modules', 'playwright'))) return createRequire(d + '/')('playwright');
  }
  throw new Error('Playwright не найден в ~/Sites/*/node_modules');
}

let bad = 0;
const fail = (f, m) => { bad++; console.log(`FAIL ${f}: ${m}`) };
const browser = await findPlaywright().chromium.launch();
try {
  for (const f of files) {
    const src = readFileSync(join(DEMO, f), 'utf8');
    if (src.includes('—')) fail(f, 'длинное тире «—»');
    if (/(src|href)="https?:\/\//.test(src)) fail(f, 'внешний адрес в src/href');
    if (src.split('\n').length > 800) fail(f, 'больше 800 строк');
    const m = src.match(/<script type="application\/json" id="meta">([\s\S]*?)<\/script>/);
    let meta = null;
    try { meta = JSON.parse(m[1]) } catch (e) { fail(f, 'meta не читается: ' + e.message); continue }
    for (const k of KEYS) if (meta[k] === undefined || meta[k] === '') fail(f, 'нет поля ' + k);
    if (meta.id !== f.slice(0, -5)) fail(f, 'id не совпадает с именем файла');
    if (!TIPY.includes(meta.tip)) fail(f, 'tip вне классификатора: ' + meta.tip);
    if (!ETAPY.includes(meta.etap)) fail(f, 'etap вне классификатора: ' + meta.etap);
    for (const v of meta.vid || []) {
      const ctx = await browser.newContext({ viewport: { width: W[v], height: (meta.vysota && meta.vysota[v]) || 700 }, hasTouch: v === 'm', isMobile: v === 'm', deviceScaleFactor: v === 'm' ? 2 : 1 });
      const page = await ctx.newPage(), errs = [];
      page.on('pageerror', (e) => errs.push(e.message));
      page.on('console', (c) => { if (c.type() === 'error') errs.push(c.text()) });
      await page.goto('file://' + join(DEMO, f));
      await page.waitForTimeout(600);
      const H = await page.evaluate(() => document.documentElement.scrollHeight);
      if (shots) await page.screenshot({ path: join(shots, `${meta.id}-${v}-0.png`) });
      for (let y = 0; y < H; y += 400) { await page.evaluate((yy) => scrollTo(0, yy), y); await page.waitForTimeout(140) }
      await page.waitForTimeout(900);
      const over = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
      if (over > 1) fail(f, `горизонтальная прокрутка на ${W[v]}: +${over}px`);
      if (errs.length) fail(f, `ошибки (${v}): ` + errs.slice(0, 3).join(' | '));
      if (shots) { await page.evaluate(() => scrollTo(0, 0)); await page.waitForTimeout(300); await page.screenshot({ path: join(shots, `${meta.id}-${v}-1.png`), fullPage: true }) }
      await ctx.close();
    }
    console.log(`ok   ${f} [${(meta.vid || []).join(',')}]`);
  }
} finally {
  await browser.close();
}
console.log(bad ? `\nИТОГ: ${bad} замечаний` : `\nИТОГ: чисто, демо ${files.length}`);
process.exit(bad ? 1 : 0);
