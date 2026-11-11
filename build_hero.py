"""Страница «Первый экран»: варианты композиции, собранные из разбора 112 референсов Figma, с живыми демо."""
import json
from collections import Counter

from build import ROOT, SITE, e, page

# порядок вариантов и подсказка выбора: (id демо, код композиции, коротко, трафик, ниша)
VARIANTY = [
    ("hero-split", "A", "Текст + фото или объект", "поиск, реклама на горячий спрос", "услуги с результатом, который видно: стройка, ремонт, студии, авто"),
    ("hero-ekspert", "E", "Человек-эксперт", "реклама, соцсети, тёплый трафик", "услуги, где покупают человека: юрист, врач, консультант, мастер"),
    ("hero-centr", "D", "По центру", "бренд, тёплый трафик, продукт", "сервисы и продукты с коротким сильным обещанием"),
    ("hero-foto-fon", "C", "Фото или видео во весь экран", "бренд, поиск по дорогим услугам", "интерьер, архитектура, недвижимость, где продаёт картинка"),
    ("pervyy-ekran-rama", "I", "Рама-карточка с подбором", "поиск и каталог", "каталоги с параметрами: дома, авто, недвижимость"),
    ("hero-bento", "H", "Бенто из плиток", "тёплый трафик, B2B", "консалтинг, эксперты, B2B: много доводов в одном экране"),
    ("hero-forma", "F", "С формой в первом экране", "реклама с одной целью – заявка", "лендинги под рекламу: расчёт, консультация, запись"),
]
EL = {"h1": "заголовок", "sub": "подзаголовок", "btn1": "одна кнопка", "btn2": "две кнопки", "foto_cheloveka": "фото человека", "cifry": "цифры и факты",
      "tag": "надзаголовок-плашка", "kontakty": "телефон и мессенджеры", "akciya": "скидка, подарок, таймер", "bul": "выгоды списком",
      "foto_obekt": "фото объекта", "video": "видео", "slayder": "слайдер", "produkt": "товар крупно", "foto_fon": "фото на фон",
      "reyting": "рейтинг и отзывы", "navigaciya_kategoriy": "категории", "badge": "круглый значок", "forma": "форма", "logo_klientov": "логотипы клиентов"}


def build(bloki, geo):
    from build import card
    cards = json.loads((ROOT / "ref" / "hero" / "vse.json").read_text(encoding="utf8"))
    n = len(cards)
    ib = sum(1 for c in cards if c["sekciya"] == "ИНФОБИЗ")
    kod = Counter(c["kompoziciya"] for c in cards)
    by_id = {b["id"]: b for b in bloki}
    el_c = Counter(x for c in cards for x in c["elementy"])
    pc = lambda v: f"{round(v * 100 / n)} %"
    dok = {"cifry", "reyting", "logo_klientov", "badge"}
    bez_l = [c["ocenka"] for c in cards if not dok & set(c["elementy"])]
    s_l = [c["ocenka"] for c in cards if dok & set(c["elementy"])]
    bez = len(bez_l)
    sr_bez = f"{sum(bez_l) / len(bez_l):.1f}".replace(".", ",")
    sr_s = f"{sum(s_l) / len(s_l):.1f}".replace(".", ",")

    rows = "".join(
        f'<tr><td><a href="#{v}"><b>{e(nm)}</b></a>{"" if v in by_id else " <small>(демо готовится)</small>"}</td><td>{kod.get(k, 0)}</td><td>{e(tr)}</td><td>{e(ni)}</td></tr>'
        for v, k, nm, tr, ni in VARIANTY)
    kart = "".join(card(by_id[v], geo) for v, *_ in VARIANTY if v in by_id)

    el = Counter(x for c in cards for x in c["elementy"])
    el_rows = "".join(f"<tr><td>{e(EL.get(k, k))}</td><td>{v}</td><td>{round(v * 100 / n)} %</td></tr>" for k, v in el.most_common() if k in EL and v >= 5)

    best = sorted([c for c in cards if c["ocenka"] >= 4 and c["sekciya"] != "ИНФОБИЗ" and c.get("formula")], key=lambda c: -c["ocenka"])[:18]
    zag = "".join(
        f'<tr><td><button class="shot" type="button" data-zoom="ref/hero/{c["id"].replace(":", "-")}.webp" aria-label="Образец {c["id"]}" style="width:120px">'
        f'<img src="ref/hero/{c["id"].replace(":", "-")}.webp" alt="" loading="lazy"></button></td>'
        f'<td><b>{e(c["formula"])}</b><br><small>«{e(c["zagolovok"])}»</small></td><td>{e(c["cta"] or "–")}</td><td>{e(c["priem"])}</td></tr>'
        for c in best)

    body = f"""<h1>Первый экран</h1>
<p class="sub">Разобрали {n} первых экранов из Figma-файла «Блоки примеры стандартизация» (страница «1. Главная/Hero», дубли убраны, из них {ib} – инфобиз). У каждого кадра записали сетку, элементы, формулу заголовка, кнопку и приём. Повторяющихся композиций семь – ниже каждая живым демо с анимацией, схемой и образцами из файла.</p>

<h2 id="vybor">Какой вариант брать</h2>
<div class="tbl"><table><tr><th>Вариант</th><th>Кадров в файле</th><th>Трафик</th><th>Ниша и задача</th></tr>{rows}</table></div>
<div class="note">Из разбора: цифры или факты стоят в {pc(el_c['cifry'])} первых экранов, фото человека – в {pc(el_c['foto_cheloveka'])}. Без цифр, рейтинга, значков и логотипов – {bez} из {n} экранов, и оценка у них в среднем ниже: {sr_bez} против {sr_s}.</div>

<h2 id="varianty">Варианты</h2>
{kart}

<h2 id="zagolovki">Как написан заголовок и кнопка – лучшие образцы</h2>
<p class="sub">Формула – как устроен заголовок, своими словами. Инфобиз в таблицу не брали. Нажмите на кадр, чтобы открыть.</p>
<div class="tbl"><table><tr><th>Кадр</th><th>Формула и заголовок</th><th>Кнопка</th><th>Приём</th></tr>{zag}</table></div>

<h2 id="elementy">Что ставят в первый экран</h2>
<p class="sub">Сколько из {n} первых экранов содержат элемент.</p>
<div class="tbl"><table><tr><th>Элемент</th><th>Экранов</th><th>Доля</th></tr>{el_rows}</table></div>"""
    (SITE / "pervyy-ekran.html").write_text(page("pervyy-ekran.html", "Первый экран", body), encoding="utf8")
