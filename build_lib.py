"""Страница «Библиотека»: референсы по разбивке Referest – вкладки «Секции / Страницы», ряд типов, фильтры.
Страницы целиком режутся на блоки (tools/referest.py), блоки размечены типом секции и попадают во вкладку «Секции».
Данные – data/referest.json; добавление и удаление с самой страницы пишут в репо через GitHub API (src/lib.js)."""
import json
import shutil

from build import ROOT, SITE, TIP, e, page

# типы секций – как у Referest (/inspiration/web/sections), плюс меню и квиз; справа – тип по нашему классификатору
SEKCII = [
    ("menu", "Меню", "SYS"), ("header", "Первый экран", "OFF"), ("advantages", "Преимущества", "VAL"),
    ("target-audience", "Для кого", "REL"), ("services", "Услуги", "PROD"), ("product-cards", "Товары", "PROD"),
    ("product-details", "О продукте", "PROD"), ("prices", "Цены", "COM"), ("stages", "Этапы", "PROC"),
    ("schedule", "Расписание", "PROC"), ("cases", "Кейсы", "PROOF"), ("portfolio", "Портфолио", "PROOF"),
    ("reviews", "Отзывы", "PROOF"), ("statistics", "Статистика", "PROOF"), ("partners", "Партнеры", "PROOF"),
    ("awards", "Награды", "PROOF"), ("about", "О компании", "COMP"), ("team", "Команда", "COMP"),
    ("author-bio", "Об авторе", "COMP"), ("faq", "FAQ", "RISK"), ("help-center", "Помощь", "RISK"),
    ("quiz", "Квиз", "CONV"), ("cta", "Призыв к действию", "CTA"), ("form", "Форма", "CTA"),
    ("contacts", "Контакты", "CTA"), ("maps", "Карты", "SYS"), ("video", "Видео", "MEDIA"),
    ("content", "Контент", "EXP"), ("blog", "Блог", "EXP"), ("news", "Новости", "EXP"),
    ("social-media", "Соц. сети", "SYS"), ("footer", "Футер", "SYS"),
]
# типы страниц – как у Referest (/inspiration/web/pages)
STRANICY = [
    ("landing-page", "Лендинги"), ("home", "Главные"), ("multi-page", "Многостраничные"), ("catalog", "Каталог"),
    ("product", "Продукт"), ("services", "Услуги"), ("about", "О компании"), ("portfolio", "Портфолио"),
    ("reviews", "Отзывы"), ("blog", "Блог"), ("news", "Новости"), ("career", "Карьера"), ("contacts", "Контакты"),
    ("card", "Заказ карты"), ("loyalty", "Программа лояльности"), ("help", "База знаний"),
    ("coming-soon", "Coming Soon"), ("404", "404-страница"),
]
REPO = "tema-mail/baza-blokov"


def build():
    p = ROOT / "data" / "referest.json"
    if not p.exists():
        return 0
    baza = json.loads(p.read_text(encoding="utf8"))
    items = baza["items"]
    # у Referest в карточках секций бывают свои слаги – приводим к нашему списку по названию
    po_imeni = {n: s for s, n, _ in SEKCII}
    for it in items:
        if it["vid"] == "sekciya" and it["bloki"] and it["bloki"][0]["tip"] not in {s for s, _, _ in SEKCII}:
            it["bloki"][0]["tip"] = po_imeni.get(it.get("tip_ref_name"), it["bloki"][0]["tip"])
    if (ROOT / "ref" / "rf").exists():
        shutil.copytree(ROOT / "ref" / "rf", SITE / "ref" / "rf", ignore=shutil.ignore_patterns("*.json"))
    for f in ("lib.js", "lib.css"):
        shutil.copy(ROOT / "src" / f, SITE / f)
    n_sek = sum(len(it["bloki"]) for it in items)
    n_str = sum(1 for it in items if it["vid"] == "stranica")
    nerazob = sum(1 for it in items for b in it["bloki"] if not b.get("tip"))
    cfg = {"repo": REPO, "sekcii": [[s, n, t, TIP[t]] for s, n, t in SEKCII], "stranicy": STRANICY}
    data = json.dumps({"cfg": cfg, "items": items}, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    body = f"""<div class="lib-head">
<div><h1>Библиотека референсов</h1>
<p class="sub">Сайты, которые нам понравились, разложены как на Referest: «Секции» – отдельные блоки по типам, «Страницы» – страницы целиком по видам. Каждая страница порезана на блоки, и её блоки лежат в «Секциях» рядом с отдельными. Тип блока связан с нашим <a href="klassifikator.html">классификатором</a>.</p></div>
<div class="lib-act"><button class="btn-main" type="button" id="lib-add">＋ Добавить</button><button class="chip" type="button" id="lib-key" title="Ключ GitHub для записи">⚙ Доступ</button></div>
</div>
<div class="stat"><div><b>{n_sek}</b><span>секций и блоков</span></div><div><b>{n_str}</b><span>страниц целиком</span></div><div><b>{len(items)}</b><span>референсов</span></div><div><b>{nerazob}</b><span>блоков без типа</span></div></div>
<div class="lib-tabs" role="tablist"><button type="button" class="on" data-vid="sekcii">Секции</button><button type="button" data-vid="stranicy">Страницы</button></div>
<div class="lib-types" id="lib-types"></div>
<div class="lib-f">
<input type="search" id="lib-q" placeholder="Поиск по названию и сайту">
<select id="lib-tem"><option value="">Тематика</option></select>
<select id="lib-stil"><option value="">Стиль</option></select>
<select id="lib-cvet"><option value="">Цвет</option></select>
<select id="lib-shrift"><option value="">Типографика</option></select>
<label class="lib-chk"><input type="checkbox" id="lib-otdel"> только отдельные секции</label>
</div>
<p class="meta">Показано: <b id="lib-n">0</b> <span id="lib-sync"></span></p>
<div class="lib-grid" id="lib-grid"></div>
<button class="chip lib-more" type="button" id="lib-more" hidden>Показать ещё</button>
<script>window.LIB={data};</script>"""
    head = '<link rel="stylesheet" href="lib.css">'
    html = page("biblioteka.html", "Библиотека референсов", body, head).replace(
        '<script src="page.js"></script>', '<script src="page.js"></script>\n<script src="lib.js"></script>')
    (SITE / "biblioteka.html").write_text(html, encoding="utf8")
    return len(items)
