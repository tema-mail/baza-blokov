#!/usr/bin/env python3
"""Сборка базы блоков: demo/*.html (живое демо + карточка meta) и data/* → site/.
Последним шагом ставит тёмную тему (tema.py) и падает, если страница осталась без неё."""
import html
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SITE = ROOT / "site"
FIGMA = "https://www.figma.com/design/xiCcUceHSqkiG26eZzDFS3"
OBRAZEC = "http://87.242.100.185/"

TIP = {"SYS": "Системный", "OFF": "Оффер", "PROD": "Продукт", "REL": "Релевантность", "VAL": "Ценность",
       "PROOF": "Доказательства", "EXP": "Экспертность", "COM": "Условия и цена", "PROC": "Процесс",
       "COMP": "Компания", "RISK": "Возражения и риск", "CTA": "Действие", "CONV": "Механики",
       "MEDIA": "Форматы", "NICHE": "Нишевые"}
ETAP = {"UNDERSTAND": "Понять", "IDENTIFY": "Узнать себя", "WANT": "Захотеть", "BELIEVE": "Поверить",
        "EVALUATE": "Оценить", "REDUCE RISK": "Снять риск", "ACT": "Действовать", "—": "вне этапов"}
NAV = [("index.html", "База блоков"), ("cerus.html", "Разбор Церуса"),
       ("setki.html", "Сетки из Figma"), ("referensy.html", "Референсы"), ("klassifikator.html", "Классификатор")]
VID = {"m": "Телефон 390", "d": "Десктоп 1280"}
# порядок карточек: сначала системные, дальше – как блоки идут на странице-образце
PERVYE = ["tab-bar", "shapka-pilyuli"]


def e(s):
    return html.escape(str(s), quote=True)


def ul(items):
    return "<ul>" + "".join(f"<li>{e(i)}</li>" for i in items) + "</ul>"


def load_bloki():
    out = []
    for f in sorted((ROOT / "demo").glob("*.html")):
        m = re.search(r'<script type="application/json" id="meta">(.*?)</script>', f.read_text(encoding="utf8"), re.S)
        if not m:
            sys.exit(f"нет карточки meta: {f.name}")
        b = json.loads(m.group(1))
        if b["id"] != f.stem:
            sys.exit(f"id карточки не совпадает с файлом: {f.name}")
        out.append(b)

    def key(b):
        if b["id"] in PERVYE:
            return (0, PERVYE.index(b["id"]))
        return (1, b["cerus_blok"] if b.get("cerus_blok") is not None else 99)
    return sorted(out, key=key)


def wire(w, h, els):
    """Композиционная сетка: схема блока из геометрии его частей. els – (тип, x, y, ширина, высота)."""
    big = w > 600
    p = [f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="Схема блока">']
    for t, x, y, ww, hh in sorted(els, key=lambda q: -(q[3] * q[4])):
        if ww <= 2 or hh <= 2:
            continue
        if t == "card":
            p.append(f'<rect class="w-card" x="{x}" y="{y}" width="{ww}" height="{hh}" rx="{min(18, hh / 2):.0f}"/>')
        elif t == "img":
            p.append(f'<rect class="w-img" x="{x}" y="{y}" width="{ww}" height="{hh}" rx="10"/>'
                     f'<path class="w-x" d="M{x} {y}L{x + ww} {y + hh}M{x + ww} {y}L{x} {y + hh}"/>')
        elif t in ("h", "txt"):
            unit = (40 if big else 26) if t == "h" else (24 if big else 20)
            n = max(1, round(hh / unit))
            lh = hh / n
            th = max(3, lh * (0.6 if t == "h" else 0.3))
            for i in range(n):
                lw = ww * (0.7 if (i == n - 1 and n > 1) else 1)
                p.append(f'<rect class="w-{t}" x="{x}" y="{y + i * lh + (lh - th) / 2:.1f}" width="{lw:.0f}" height="{th:.1f}" rx="2"/>')
        elif t == "btn":
            p.append(f'<rect class="w-btn" x="{x}" y="{y}" width="{ww}" height="{hh}" rx="10"/>')
        elif t == "inp":
            p.append(f'<rect class="w-inp" x="{x}" y="{y}" width="{ww}" height="{hh}" rx="10"/>')
    p.append("</svg>")
    return "".join(p)


def load_geo():
    """Геометрия блоков образца: {'d': [секции], 'm': [секции]}, у секции w, h, els."""
    out = {}
    for v in ("d", "m"):
        secs = json.loads((ROOT / "data" / f"geo-cerus-{v}.json").read_text(encoding="utf8"))
        out[v] = [(s["w"], s["h"], [(x["t"], x["x"], x["y"], x["w"], x["h"]) for x in s["els"]]) for s in secs]
    return out


def wires_cerus(geo, n):
    d, m = geo["d"][n], geo["m"][n]
    return ('<div class="wires">'
            f'<figure class="wire">{wire(*d)}<figcaption>Десктоп 1440</figcaption></figure>'
            f'<figure class="wire">{wire(*m)}<figcaption>Телефон 390</figcaption></figure></div>')


def page(fname, title, body, head=""):
    cur = ' aria-current="page"'
    nav = "".join(f'<a href="{h}"{cur if h == fname else ""}>{t}</a>' for h, t in NAV)
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>{e(title)}</title>
<link rel="stylesheet" href="page.css">
{head}</head>
<body>
<div class="page">
<nav class="nav">{nav}</nav>
{body}
</div>
<div class="zoom" id="zoom"><button class="zoom-x" type="button" aria-label="Закрыть">×</button><button class="zoom-n p" type="button" aria-label="Назад">‹</button><button class="zoom-n n" type="button" aria-label="Дальше">›</button><img alt=""></div>
<script src="page.js"></script>
</body>
</html>
"""


def card(b, geo):
    vids = b["vid"]
    btns = "".join(f'<button class="chip{" on" if i == 0 else ""}" type="button" data-v="{v}">{VID[v]}</button>' for i, v in enumerate(vids))
    hs = " ".join(f'data-h{v}="{b["vysota"].get(v, 680)}"' for v in vids)
    n = b.get("cerus_blok")
    setka = ""
    if n is not None:
        setka = (f'<dt style="margin-top:18px">Композиционная сетка – снята с блока-образца</dt>{wires_cerus(geo, n)}')
    obr = f' <a href="cerus.html#b{n:02d}">Снимки в разборе</a>' if n is not None else ' <a href="cerus.html#mobilka">Снимки в разборе</a>'
    return f"""<article class="blok" id="{e(b['id'])}" data-tip="{e(b['tip'])}" data-etap="{e(b['etap'])}">
<div class="blok-top"><div><h3>{e(b['nazvanie'])}</h3>
<div class="chips"><span class="chip t">{TIP[b['tip']]} · {b['tip']}</span><span class="chip">Этап: {ETAP[b['etap']].lower()}</span></div></div></div>
<div class="blok-g">
<div>
<div class="demo">
<div class="demo-bar">{btns}<button class="chip" type="button" data-re>↻ Заново</button><a href="demo/{e(b['id'])}.html" target="_blank" rel="noopener">Открыть отдельно</a></div>
<div class="stage" data-src="demo/{e(b['id'])}.html" data-v="{vids[0]}" {hs}><div class="wait">Демо включится, когда карточка окажется на экране</div></div>
</div>
<dl>{setka}</dl>
</div>
<dl>
<dt>На какой вопрос отвечает</dt><dd class="q">{e(b['vopros'])}</dd>
<dt>Смысл</dt><dd>{e(b['smysl'])}</dd>
<dt>Сетка – десктоп</dt><dd>{e(b['setka_d'])}</dd>
<dt>Сетка – телефон</dt><dd>{e(b['setka_m'])}</dd>
<dt>Анимация</dt><dd>{ul(b['animaciya'])}</dd>
<dt>Как работает</dt><dd>{ul(b['kak_rabotaet'])}</dd>
<dt>Когда ставить</dt><dd>{e(b['kogda'])}</dd>
<dt>Когда не ставить</dt><dd>{e(b['ne_kogda'])}</dd>
<dt>Что сделали у образца</dt><dd>{e(b['u_cerusa'])}{obr}</dd>
<dt>Что дальше по странице</dt><dd>{e(b['sled'])}</dd>
</dl>
</div>
</article>"""


def build_index(bloki, geo):
    tips = sorted({b["tip"] for b in bloki}, key=list(TIP).index)
    etaps = sorted({b["etap"] for b in bloki}, key=list(ETAP).index)
    f_tip = "".join(f'<button class="chip" type="button" data-f="tip" data-val="{t}">{TIP[t]} · {sum(1 for b in bloki if b["tip"] == t)}</button>' for t in tips)
    f_et = "".join(f'<button class="chip" type="button" data-f="etap" data-val="{t}">{ETAP[t]} · {sum(1 for b in bloki if b["etap"] == t)}</button>' for t in etaps)
    voice = ('<div class="voice"><small>Послушать итог голосом</small><audio controls preload="none" src="itog.mp3"></audio></div>'
             if (ROOT / "itog.mp3").exists() else "")
    anim = sum(len(b["animaciya"]) for b in bloki)
    n_kl = len(json.loads((ROOT / "data" / "klassifikator.json").read_text(encoding="utf8"))["rows"])
    n_fg = sum(len(f["blocks"]) for f in json.loads((ROOT / "data" / "figma-tf.json").read_text(encoding="utf8")))
    body = f"""<h1>База блоков</h1>
<p class="sub">Наши референсы блоков сайта: у каждого живое демо с анимацией, композиционная сетка на десктопе и телефоне и смысл – на какой вопрос клиента блок отвечает и что ставить следом. Первый источник – разбор сайта «Церус».</p>
{voice}
<div class="stat">
<div><b>{len(bloki)}</b><span>блоков с живым демо</span></div>
<div><b>{anim}</b><span>описанных движений и механик</span></div>
<div><b>{len(tips)} из {len(TIP)}</b><span>типов блоков по классификатору</span></div>
<div><b>{n_kl}</b><span>блока в <a href="klassifikator.html">классификаторе</a></span></div>
<div><b>{n_fg}</b><span>сеток блоков из <a href="setki.html">Figma</a></span></div>
</div>
<div class="box"><b>Как читать карточку.</b> Слева блок работает по-настоящему: его можно листать, нажимать и переключать «Телефон / Десктоп». Под ним схема – сетка, снятая с блока-образца. Справа: вопрос клиента, смысл, сетка словами, что и как движется, когда блок ставить и что идёт следом. В демо текст нейтральный: он называет роль места, а не продаёт.</div>
<h2 id="bloki">Блоки</h2>
<small>Тип блока</small><div class="chips">{f_tip}</div>
<small>Этап решения клиента</small><div class="chips">{f_et}</div>
<p class="meta">Показано: <b id="found">{len(bloki)}</b> из {len(bloki)}</p>
{''.join(card(b, geo) for b in bloki)}
<h2>Откуда собрано</h2>
<div class="box"><ul>
<li><a href="cerus.html">Разбор сайта «Церус»</a> – живой сайт-образец: код, снимки 390 и 1440, геометрия блоков.</li>
<li><a href="setki.html">Сетки из Figma</a> – ч/б сетки нашего проекта: {n_fg} схем, TargetFactory (12 колонок на десктопе, 4 на телефоне).</li>
<li><a href="referensy.html">Референсы из Figma</a> – файл «Блоки примеры стандартизация»: чужие сайты по типам блоков, снятые по страницам и связанные с нашими демо.</li>
<li><a href="klassifikator.html">Классификатор смысловых блоков</a> – наша таблица на {n_kl} блока: тип, класс, этап решения.</li>
</ul></div>"""
    (SITE / "index.html").write_text(page("index.html", "База блоков", body), encoding="utf8")


def main():
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()
    shutil.copytree(ROOT / "demo", SITE / "demo")
    shutil.copytree(ROOT / "img", SITE / "img")
    for f in ("page.css", "page.js"):
        shutil.copy(ROOT / "src" / f, SITE / f)
    if (ROOT / "itog.mp3").exists():
        shutil.copy(ROOT / "itog.mp3", SITE / "itog.mp3")
    (SITE / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf8")
    (SITE / ".nojekyll").write_text("", encoding="utf8")

    bloki, geo = load_bloki(), load_geo()
    build_index(bloki, geo)
    import build_cerus
    import build_dop
    build_cerus.build(bloki, geo)
    build_dop.build(bloki)
    import build_ref
    print(f"референсов из Figma: {build_ref.build(bloki)}")
    print(f"страниц: {len(list(SITE.glob('*.html')))}, блоков: {len(bloki)}")
    import tema
    tema.main()


if __name__ == "__main__":
    main()
