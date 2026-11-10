"""Страница разбора сайта-образца «Церус»: логика сборки, телефон, всплывашки, блоки главной, карта сайта, что берём."""
import json

from build import ROOT, SITE, e, page, ul, wires_cerus

IMG = "img/cerus"


def shot(name, label, cls="shot"):
    return (f'<button class="{cls}" type="button" data-zoom="{IMG}/{name}.webp" aria-label="{e(label)}">'
            f'<img src="{IMG}/{name}.webp" alt="{e(label)}" loading="lazy"></button>')


def sekciya(s, bloki, geo):
    n = s["n"]
    b = next((x for x in bloki if x.get("cerus_blok") == n), None)
    demo = b["id"] if b else s.get("demo", "")
    vopros = b["vopros"] if b else s.get("vopros", "")
    anim = f'<dt>Что движется</dt><dd>{ul(b["animaciya"])}</dd>' if b else ""
    link = f'<p><a href="index.html#{e(demo)}">Живое демо и карточка блока в базе →</a></p>' if demo else ""
    zag = f'<p class="meta">Заголовок у образца: «{e(s["zagolovok"])}»</p>' if s["zagolovok"] != "–" else ""
    return f"""<article class="blok" id="b{n:02d}">
<h3>{n + 1}. {e(s['nazvanie'])}</h3>{zag}
<div class="blok-g">
<div>
<div class="shots">{shot(f'd-{n:02d}', s['nazvanie'] + ' – десктоп')}{shot(f'm-{n:02d}', s['nazvanie'] + ' – телефон')}</div>
<small>Снимки: десктоп 1440 и телефон 390. Нажмите, чтобы открыть.</small>
{wires_cerus(geo, n)}
<small>Композиционная сетка: схема построена по геометрии блока, без цвета и картинок.</small>
</div>
<dl>
<dt>На какой вопрос отвечает</dt><dd class="q">{e(vopros)}</dd>
<dt>Что стоит в блоке</dt><dd>{e(s['sut'])}</dd>
{anim}
</dl>
</div>
{link}
</article>"""


def build(bloki, geo):
    c = json.loads((ROOT / "data" / "cerus.json").read_text(encoding="utf8"))
    s = c["sayt"]
    ids = {b["id"] for b in bloki}

    def demo_link(i, text="демо"):
        return f'<a href="index.html#{e(i)}">{text}</a>' if i in ids else "–"

    logika = "".join(f'<div class="box"><h3>{i}. {e(t)}</h3><p>{e(d)}</p></div>' for i, (t, d) in enumerate(c["logika"], 1))
    mob = "".join(f"<tr><td><b>{e(t)}</b></td><td>{e(d)}</td></tr>" for t, d in c["mobilka"])
    vs = "".join(f"<tr><td><b>{e(a)}</b></td><td>{e(b_)}</td><td>{e(v)}</td><td>{demo_link(dm)}</td></tr>" for a, b_, v, dm in c["vsplyvashki"])
    put = "".join(f'<li><a href="#b{i:02d}">{e(t)}</a></li>' for i, t in enumerate(c["put"]))
    kg = "".join(f"<tr><td><b>{e(a)}</b></td><td>{e(b_)}</td><td>{n}</td></tr>" for a, b_, n in c["karta"]["gruppy"])
    kt = "".join(f"<tr><td><b>{e(a)}</b></td><td>{e(b_)}</td></tr>" for a, b_ in c["karta"]["tipy"])
    ber = "".join(f'<tr><td><span class="pri">{p}</span></td><td><b>{e(a)}</b></td><td>{e(z)}</td><td>{e(k)}</td><td>{demo_link(dm) if dm else "–"}</td></tr>'
                  for p, a, z, k, dm in c["berem"])
    mob_shots = "".join(shot(n, l) for n, l in [
        ("m-s-top", "Первый экран: таб-бара ещё нет"), ("m-s-scroll", "После первого экрана: таб-бар выехал"),
        ("m-s-dark", "Над тёмным блоком таб-бар и шапка темнеют"), ("m-s-sheet-call", "Окно «Связаться»"),
        ("m-s-sheet-all", "Окно «Все разделы»"), ("m-s-top-cookie", "Cookie-плашка"), ("m-s-stories", "Просмотр сторис")])
    desk_shots = "".join(shot(n, l) for n, l in [
        ("d-s-top", "Шапка на первом экране: три пилюли"), ("d-s-scroll", "После прокрутки: одна плашка"),
        ("d-s-mega", "Мега-меню с цифрами разделов"), ("d-s-dark", "Шапка над тёмным блоком"),
        ("d-s-top-cookie", "Cookie-плашка на десктопе"), ("d-s-stories", "Просмотр сторис на десктопе")])

    body = f"""<h1>Разбор: {e(s['nazvanie'])}</h1>
<p class="sub">{e(s['nisha']).capitalize()}. Адрес: <a href="{e(s['adres'])}" rel="noopener nofollow" target="_blank">{e(s['adres'])}</a> – {e(s['status'])}. Разработчик: {e(s['razrabotchik'])}. Снято {e(s['data'])}: код главной, 13 внутренних страниц, карта сайта, 45 снимков на 390 и 1440.</p>
<div class="chips"><a class="chip" href="#logika">Логика сборки</a><a class="chip" href="#mobilka">Телефон и таб-бар</a><a class="chip" href="#vsplyvashki">Всплывашки</a><a class="chip" href="#glavnaya">Главная по блокам</a><a class="chip" href="#karta">Карта сайта</a><a class="chip" href="#berem">Что берём</a></div>

<h2 id="logika">Как собран сайт</h2>
<div class="two">{logika}</div>
<div class="row-m">{desk_shots}</div>

<h2 id="mobilka">Телефон: таб-бар и окна</h2>
<p class="sub">То, что понравилось в мобильной версии. Всё это уже работает в базе: {demo_link('tab-bar', 'живое демо таб-бара и окна «Связаться»')}.</p>
<div class="row-m">{mob_shots}</div>
<div class="tbl"><table><tr><th>Что</th><th>Как устроено</th></tr>{mob}</table></div>

<h2 id="vsplyvashki">Всплывашки и слои поверх страницы</h2>
<p class="sub">Девять слоёв. Сам по себе появляется только один – плашка cookie. Окон «по таймеру», «при уходе» и навязчивых квизов на сайте нет: всё открывает сам человек.</p>
<div class="tbl"><table><tr><th>Слой</th><th>Чем открывается</th><th>Что внутри</th><th>В базе</th></tr>{vs}</table></div>

<h2 id="glavnaya">Главная по блокам</h2>
<p class="sub">Шестнадцать блоков. Логика страницы – цепочка вопросов клиента, каждый блок отвечает на один и подводит к следующему:</p>
<div class="box"><ol>{put}<li><a href="#b15">Подвал</a></li></ol></div>
{''.join(sekciya(x, bloki, geo) for x in c['sekcii'])}

<h2 id="karta">Карта сайта и типы страниц</h2>
<p class="sub">В карте сайта {c['karta']['vsego']} адреса.</p>
<div class="two">
<div class="tbl"><table><tr><th>Группа</th><th>Адреса</th><th>Страниц</th></tr>{kg}</table></div>
<div class="tbl"><table><tr><th>Тип страницы</th><th>Что на ней</th></tr>{kt}</table></div>
</div>

<h2 id="berem">Что берём себе</h2>
<p class="sub">Приоритет 1 – брать в стандарт сейчас, 2 – брать под задачу проекта, 3 – держать как приём.</p>
<div class="tbl"><table><tr><th>№</th><th>Что</th><th>В чём приём</th><th>Куда</th><th>В базе</th></tr>{ber}</table></div>

<h2 id="ostorozhno">Что не копируем</h2>
<div class="box">{ul(c['ostorozhno'])}</div>"""
    (SITE / "cerus.html").write_text(page("cerus.html", "Разбор: Церус", body), encoding="utf8")
