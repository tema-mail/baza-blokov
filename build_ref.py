"""Страница «Референсы из Figma»: файл «Блоки примеры стандартизация», снятый по страницам."""
import json

from build import ROOT, SITE, TIP, e, page

FILE = "https://www.figma.com/design/ah1brW9rmCqBwZnAhmzGvG"
PUSTO = 15_000  # снимок легче 15 КБ – пустая заготовка в файле, не показываем

# раздел файла → тип блока по классификатору и наши живые демо того же назначения (по началу названия страницы)
RAZDEL = [
    ("Меню", "SYS", ["shapka-pilyuli", "tab-bar"]), ("0. Меню", "SYS", ["shapka-pilyuli"]),
    ("0. Футер", "SYS", []), ("! Виджеты ОС", "SYS", ["tab-bar"]),
    ("1. Главная", "OFF", ["pervyy-ekran-rama"]), ("2. Описание", "PROD", []),
    ("3. Прем", "VAL", ["fakty-garantii"]), ("4. Квиз", "CONV", []),
    ("5. СTA", "CTA", ["forma-razgovor"]), ("5. CTA", "CTA", ["forma-razgovor"]),
    ("6. Этапы", "PROC", ["put-lenta"]), ("Этапы работы", "PROC", ["put-lenta"]),
    ("7. Целевая", "REL", []), ("8. Услуги", "PROD", ["katalog-vkladki"]),
    ("Услуги / Товары", "PROD", ["katalog-vkladki"]), ("Каталог", "PROD", ["katalog-vkladki"]),
    ("9. Портфолио", "PROOF", ["karta-obektov", "slozhnye-vkladki"]), ("10. Тарифы", "COM", ["sostav-ceny", "dvoynoy-blok"]),
    ("11. Галерея", "MEDIA", ["storis"]), ("12. Отзывы", "PROOF", ["otzyvy-citata"]), ("Отзывы", "PROOF", ["otzyvy-citata"]),
    ("13. О нас", "COMP", ["direktor"]), ("14. Команда", "COMP", ["direktor"]), ("15. Основатель", "COMP", ["direktor"]),
    ("16. Видео", "MEDIA", ["storis", "otzyvy-citata"]), ("17. Контакты", "CTA", ["forma-razgovor"]),
    ("18. Фактойды", "PROOF", ["fakty-garantii", "karta-obektov"]), ("Соц доказательства", "PROOF", ["otzyvy-citata"]),
    ("19. Награды", "PROOF", []), ("20. FAQ", "RISK", ["faq-akkordeon"]), ("21. Клиенты", "PROOF", []),
    ("22. Блог", "EXP", []), ("23. Карта", "SYS", ["karta-obektov"]), ("24. Pop up", "CONV", []),
    ("28. Конверсионные", "CONV", ["forma-razgovor"]), ("! Маркетинговые", "CONV", []),
    ("! Блоки уселит", "VAL", ["sposoby-proverit"]), ("Карточка товара", "PROD", []), ("Фильтр каталога", "PROD", ["katalog-vkladki"]),
    ("Страница оплаты", "CTA", []), ("27. Программа", "PROC", []), ("28. Кому", "REL", []), ("29. До/после", "VAL", []),
    ("Кобрендинг", "COMP", []),
]


def razdel(name):
    best = None
    for k, t, d in RAZDEL:
        if name.strip().startswith(k) and (best is None or len(k) > len(best[0])):
            best = (k, t, d)
    return best


def img(src, w, h, label):
    return (f'<button class="shot" type="button" data-zoom="{e(src)}" aria-label="{e(label)}">'
            f'<img src="{e(src)}" alt="{e(label)}" width="{w}" height="{h}" loading="lazy"></button>')


def build(bloki):
    p = ROOT / "data" / "figma-bloki.json"
    if not p.exists():
        return 0
    stranicy = json.loads(p.read_text(encoding="utf8"))
    names = {b["id"]: b["nazvanie"] for b in bloki}
    cards, toc, n_img = [], [], 0
    for s in stranicy:
        r = razdel(s["nazvanie"])
        chip = f'<span class="chip t">{TIP[r[1]]} · {r[1]}</span>' if r else ""
        demos = " ".join(f'<a class="chip" href="index.html#{d}">▶ {e(names[d])}</a>' for d in (r[2] if r else []) if d in names)
        demos = f'<div class="chips"><small>Живые демо этого типа:</small> {demos}</div>' if demos else ""
        pics = []
        if s.get("stranica") and s.get("vsego_obektov") and (ROOT / s["stranica"]).stat().st_size >= PUSTO:
            pics.append(img(s["stranica"], s["w"], s["h"], s["nazvanie"] + " – страница целиком"))
        for u in s.get("uzly", []):
            if not u.get("img") or (ROOT / u["img"]).stat().st_size < PUSTO:
                continue
            label = f'{s["nazvanie"].strip()} – {u["nazvanie"]}'
            if u.get("polosy"):
                ps = u["polosy"]
                strips = "".join(img(q["img"], q["w"], q["h"], f"{label}, часть {i} из {len(ps)}") for i, q in enumerate(ps, 1))
                pics.append(f'<div class="strip" title="{e(label)}">{strips}<small>{e(u["nazvanie"])} · {len(ps)} частей, листайте</small></div>')
            else:
                pics.append(img(u["img"], u["w"], u["h"], label))
        n_img += len(pics)
        if not pics:
            continue
        txt = "".join(f"<li>{e(t)}</li>" for t in s.get("tekst", []) if t.strip())
        txt = f'<details><summary>Пометки в файле ({len(s["tekst"])})</summary><ul>{txt}</ul></details>' if txt else ""
        aid = "f" + s["id"].replace(":", "-")
        toc.append(f'<a class="chip" href="#{aid}">{e(s["nazvanie"].strip())}</a>')
        cards.append(f"""<article class="blok" id="{aid}">
<div class="blok-top"><div><h3>{e(s['nazvanie'].strip())}</h3><small>Объектов на странице: {s.get('vsego_obektov', '–')} · снимков: {len(pics)}</small></div><div class="chips">{chip}</div></div>
{demos}
<div class="ref-g">{''.join(pics)}</div>
{txt}
</article>""")
    body = f"""<h1>Референсы из Figma</h1>
<p class="sub">Файл «Блоки примеры стандартизация» – подборка чужих сайтов по типам блоков: первый экран, преимущества, квиз, формы, этапы, отзывы, каталог, тапбары и другие. Здесь он снят по страницам, без правок. Каждый раздел размечен типом блока по <a href="klassifikator.html">классификатору</a> и связан с нашими <a href="index.html">живыми демо</a> того же назначения. Оригинал – в <a href="{FILE}" target="_blank" rel="noopener">Figma</a>.</p>
<div class="stat"><div><b>{len(cards)}</b><span>разделов файла</span></div><div><b>{n_img}</b><span>снимков</span></div></div>
<div class="chips">{''.join(toc)}</div>
{''.join(cards)}"""
    (SITE / "referensy.html").write_text(page("referensy.html", "Референсы из Figma", body), encoding="utf8")
    return n_img
