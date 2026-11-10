"""Дополнительные страницы базы: сетки блоков из Figma и классификатор смысловых блоков."""
import json
from collections import Counter

from build import ETAP, FIGMA, ROOT, SITE, TIP, e, page, wire

# тип блока по классификатору для сеток главной страницы из Figma (по названию блока)
TIP_FIGMA = {"Маркетинг для цветочных магазинов": "OFF", "Поток заказов": "VAL", "Боли владельца": "REL", "Кейсы": "PROOF",
             "Почему мы": "COMP", "Что меняется": "VAL", "Видео-отзывы": "PROOF", "Праздники": "NICHE", "Было / стало": "VAL",
             "Этапы работы": "PROC", "Бонусы": "COM", "Делаем интернет-магазины": "PROD", "Интернет-магазины, которые": "PROOF",
             "6 причин": "VAL", "У вас уже есть сайт": "REL", "План роста": "CTA", "Этот блок для Вас": "RISK",
             "Шапка": "SYS", "Подвал": "SYS", "Прозрачность": "RISK", "Отзывы": "PROOF", "Цены на продвижение": "COM",
             "Разбор отзыва": "PROOF", "Обещания и факты": "PROOF", "Все отзывы": "PROOF"}


def tip_of(name):
    for k, v in TIP_FIGMA.items():
        if name.startswith(k):
            return v
    return ""


def build_setki():
    frames = json.loads((ROOT / "data" / "figma-tf.json").read_text(encoding="utf8"))
    pages = {}
    for f in frames:
        pages.setdefault(f["page"], {})[f["view"]] = f
    order = ["Главная", "Почему мы", "Цены", "Видео-отзывы", "Разборы"]
    out, total = [], 0
    for title in order:
        d, m = pages[title].get("d"), pages[title].get("m")
        mob = {b["name"]: b for b in (m["blocks"] if m else [])}
        cards = []
        for b in d["blocks"]:
            total += 1 + (b["name"] in mob)
            t = tip_of(b["name"])
            chip = f'<span class="chip t">{TIP[t]} · {t}</span>' if t else ""
            wd = wire(b["w"], b["h"], [tuple(x[:5]) for x in b["els"]])
            mb = mob.get(b["name"])
            wm = (f'<figure class="wire">{wire(mb["w"], mb["h"], [tuple(x[:5]) for x in mb["els"]])}<figcaption>Телефон 390 · 4 колонки</figcaption></figure>'
                  if mb else "")
            cards.append(f'<article class="blok"><div class="blok-top"><h3>{e(b["name"])}</h3><div class="chips">{chip}</div></div>'
                         f'<div class="wires"><figure class="wire">{wd}<figcaption>Десктоп 1440 · 12 колонок</figcaption></figure>{wm}</div></article>')
        out.append(f'<h2 id="p-{order.index(title)}">{e(title)} <small>· блоков: {len(d["blocks"])}</small></h2>' + "".join(cards))
    nav = "".join(f'<a class="chip" href="#p-{i}">{e(t)}</a>' for i, t in enumerate(order))
    body = f"""<h1>Сетки из Figma</h1>
<p class="sub">Композиционные сетки блоков нашего проекта TargetFactory (маркетинг для цветочных): страница «Сетка» в <a href="{FIGMA}" target="_blank" rel="noopener">файле Figma</a> – ч/б прототип без цвета и картинок, 12 колонок на десктопе и 4 на телефоне. Здесь {total} сеток: каждый блок на 1440 и на 390. Схемы построены из размеров слоёв Figma. Движения в этих блоках нет – живые демо с анимацией лежат в <a href="index.html">базе блоков</a>.</p>
<div class="chips">{nav}</div>
{''.join(out)}"""
    (SITE / "setki.html").write_text(page("setki.html", "Сетки из Figma", body), encoding="utf8")
    return total


def build_klass(bloki):
    k = json.loads((ROOT / "data" / "klassifikator.json").read_text(encoding="utf8"))
    rows = k["rows"]
    cats = Counter((r[2], r[3]) for r in rows)
    nashi = Counter(b["tip"] for b in bloki)
    svod = "".join(
        f'<tr><td><b>{TIP.get(code, name)}</b> <small>{e(code)}</small></td><td>{e(name)}</td><td>{n}</td>'
        f'<td>{("<a href=\"index.html#bloki\">" + str(nashi[code]) + "</a>") if nashi.get(code) else "–"}</td></tr>'
        for (code, name), n in sorted(cats.items(), key=lambda x: list(TIP).index(x[0][0]) if x[0][0] in TIP else 99))
    taks = {"LEVEL": [], "CLASS": [], "STAGE": []}
    for t, code, name, mean in k["taks"]:
        taks.setdefault(t, []).append((code, name, mean))

    def tt(key, title):
        return (f'<div class="tbl"><table><tr><th>{title}</th><th>Название</th><th>Смысл</th></tr>'
                + "".join(f"<tr><td>{e(c)}</td><td><b>{e(n)}</b></td><td>{e(m)}</td></tr>" for c, n, m in taks[key]) + "</table></div>")

    opt_c = "".join(f'<option value="{e(code)}">{TIP.get(code, name)} ({n})</option>' for (code, name), n in sorted(cats.items()))
    opt_s = "".join(f'<option value="{e(s)}">{ETAP.get(s, s)} ({n})</option>' for s, n in Counter(r[7] for r in rows).most_common())
    opt_k = "".join(f'<option value="{e(s)}">{e(s)} ({n})</option>' for s, n in Counter(r[6] for r in rows).most_common())
    data = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    body = f"""<h1>Классификатор смысловых блоков</h1>
<p class="sub">Наша таблица MASTER на {len(rows)} блока: что это за блок, к какому типу относится, на каком этапе решения клиента работает и для каких страниц подходит. База блоков с живыми демо размечена этими же кодами. Поле «тип бизнеса» в исходной таблице не заполнено – в отбор не вынесено.</p>
<h2>Типы блоков</h2>
<div class="tbl"><table><tr><th>Тип</th><th>Категория в таблице</th><th>Блоков</th><th>С живым демо</th></tr>{svod}</table></div>
<h2>Как размечен блок</h2>
<div class="two">{tt('STAGE', 'Этап решения')}{tt('CLASS', 'Класс')}</div>
{tt('LEVEL', 'Уровень')}
<h2>Все блоки</h2>
<div class="tools"><input type="search" id="kl-q" placeholder="Найти блок: гарантия, калькулятор, отзывы…" aria-label="Поиск по блокам">
<select id="kl-cat" aria-label="Тип"><option value="">Все типы</option>{opt_c}</select>
<select id="kl-st" aria-label="Этап"><option value="">Все этапы</option>{opt_s}</select>
<select id="kl-cl" aria-label="Класс"><option value="">Все классы</option>{opt_k}</select></div>
<p class="meta">Найдено: <b id="kl-n"></b></p>
<div class="tbl"><table><thead><tr><th>Код</th><th>Блок</th><th>Подкатегория</th><th>Класс</th><th>Этап</th><th>Страницы</th><th>Ниша</th></tr></thead><tbody id="kl-body"></tbody></table></div>"""
    head = f"<script>window.KL={data};</script>\n"
    (SITE / "klassifikator.html").write_text(page("klassifikator.html", "Классификатор блоков", body, head), encoding="utf8")


def build(bloki):
    n = build_setki()
    build_klass(bloki)
    print(f"сеток из Figma: {n}")
