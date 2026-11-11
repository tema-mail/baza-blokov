#!/usr/bin/env python3
"""Импорт референсов с Referest в базу: коллекция или отдельные экраны → data/referest.json + ref/rf/<slug>/*.webp.

Целые страницы режутся на блоки по сменам фона и пустым полосам (нарезка), каждый блок потом размечается типом.
Разметку (tip) повторный запуск не трогает: блоки существующей записи сохраняются как есть.

  python3 tools/referest.py kollekciya 12343242     – вся коллекция
  python3 tools/referest.py ekran kirpich           – один экран (slug или ссылка referest.ru/screens/…)
  python3 tools/referest.py vhodyashie              – обработать data/referest-inbox.json (кнопка «Добавить» на сайте)
  python3 tools/referest.py razmetka otvet*.json     – типы блоков из разметки: {slug: [{n, tip, slit, dva}]}; slit – склеить с предыдущим
"""
import io
import json
import re
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "referest.json"
INBOX = ROOT / "data" / "referest-inbox.json"
OUT = ROOT / "ref" / "rf"
CACHE = ROOT / "cache" / "referest"
API = "https://referest.ru/api/v1/interactions/collections/{}/items"
W = 1000            # ширина блоков в базе
Q = 68              # качество WebP
MIN_BLOK = 260      # блок ниже – склеивается со следующим (обычно это заголовок над содержимым)
PUSTO_POLOSA = 45   # ровная полоса фона выше – граница между блоками
Image.MAX_IMAGE_PIXELS = None


def get(url, binary=False):
    for i in range(3):
        r = subprocess.run(["curl", "-sfL", "--max-time", "90", "-A", "Mozilla/5.0 baza-blokov", url], capture_output=True)
        if r.returncode == 0:
            return r.stdout if binary else r.stdout.decode("utf8")
        time.sleep(2 + i * 3)
    raise RuntimeError(f"не скачалось: {url}")


def kollekciya(cid):
    items, cur = [], None
    while True:
        q = {"rows": 48} | ({"cursor": cur} if cur else {})
        r = json.loads(get(API.format(cid) + "?" + urllib.parse.urlencode(q)))
        items += r["items"]
        if not r["cursor"]["hasMore"]:
            return items
        cur = r["cursor"]["nextCursor"]
        time.sleep(0.4)


def ekran(slug):
    """Карточка одного экрана со страницы referest.ru/screens/<slug>: полноразмерный снимок и подпись из JSON-LD."""
    h = get(f"https://referest.ru/screens/{slug}")
    m = re.search(r'"contentUrl":"(https://storage\.referest\.ru/[^"]+)","width":(\d+),"height":(\d+),"name":"([^"]*)","caption":"([^"]*)"', h)
    if not m:
        raise RuntimeError(f"нет снимка на странице экрана {slug}")
    site = re.search(r'"targetUrl":"([^"]+)"', h.replace('\\"', '"'))
    return {"full": m.group(1), "w": int(m.group(2)), "h": int(m.group(3)), "alt": m.group(4),
            "title": m.group(5), "site": site.group(1) if site else ""}


def tegi(alt):
    out = {}
    for k, name in (("tematika", "тематика"), ("cveta", "цвета"), ("stil", "стиль"), ("tipografika", "типографика")):
        m = re.search(name + r" — (.*?)(?:, (?:тематика|цвета|стиль|типографика) — |$)", alt)
        if m:
            out[k] = [s.strip() for s in m.group(1).split(",") if s.strip()]
    return out


def narezka(a):
    """Границы блоков по строкам картинки шириной W. a – массив (h, W, 3)."""
    h = a.shape[0]
    med = np.median(a, axis=1)
    # строка «ровная», если почти все её точки – цвет фона (мелкий шум и тонкие линии не мешают)
    flat = (np.abs(a - med[:, None, :]).max(2) < 14).mean(1) > 0.985
    mean = med
    cand = []  # (вес, y)
    y = 0
    while y < h:
        if not flat[y]:
            y += 1
            continue
        s = y
        while y + 1 < h and flat[y + 1] and np.abs(mean[y + 1] - mean[y]).max() < 6:
            y += 1
        run = y - s + 1
        if run >= PUSTO_POLOSA:
            cand.append((run, (s + y) // 2))
        # смена фона: ровная полоса фона начинается или кончается на строке другого цвета (секция с фото/цветом → белая)
        if run >= 16 and s > 0 and np.abs(mean[s - 1] - mean[s]).max() > 7:
            cand.append((300, s))
        if run >= 16 and y + 1 < h and np.abs(mean[y + 1] - mean[y]).max() > 7:
            cand.append((300, y + 1))
        y += 1
    cuts = []
    for wgt, cy in sorted(cand, reverse=True):
        if cy < MIN_BLOK or h - cy < MIN_BLOK // 2:
            continue
        if all(abs(cy - c) >= MIN_BLOK for c in cuts):
            cuts.append(cy)
    edges = [0] + sorted(cuts) + [h]
    return [(edges[i], edges[i + 1]) for i in range(len(edges) - 1)]


def zapis(item, raw, vid):
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    k = W / im.width
    im = im.resize((W, max(1, round(im.height * k))), Image.LANCZOS)
    d = OUT / item["slug"]
    d.mkdir(parents=True, exist_ok=True)
    for f in d.glob("*.webp"):
        f.unlink()
    kuski = narezka(np.asarray(im, dtype=np.int16)) if vid == "stranica" else [(0, im.height)]
    bloki = []
    for n, (y0, y1) in enumerate(kuski):
        p = d / f"{n}.webp"
        im.crop((0, y0, W, y1)).save(p, "WEBP", quality=Q, method=5)
        bloki.append({"n": n, "img": str(p.relative_to(ROOT)), "w": W, "h": y1 - y0, "y": y0, "tip": None})
    oblozhka = d / "cover.webp"
    im.crop((0, 0, W, min(im.height, 750))).resize((480, round(min(im.height, 750) * 0.48)), Image.LANCZOS).save(oblozhka, "WEBP", quality=70)
    return bloki, str(oblozhka.relative_to(ROOT)), im.height


def zapisat_item(baza, it, kollekciya_id=None, renarezat=False):
    slug = it["slug"]
    old = next((x for x in baza["items"] if x["slug"] == slug), None)
    if old and not renarezat:
        if kollekciya_id and kollekciya_id not in old.setdefault("kollekcii", []):
            old["kollekcii"].append(kollekciya_id)
        return "есть"
    e = ekran(slug)
    cache = CACHE / (slug + ".webp")
    if cache.exists():
        raw = cache.read_bytes()
    else:
        raw = get(e["full"], binary=True)
        CACHE.mkdir(parents=True, exist_ok=True)
        cache.write_bytes(raw)
    vid = "sekciya" if it.get("contentType", {}).get("slug") == "sections" else "stranica"
    bloki, cover, h = zapis(it, raw, vid)
    pt = it.get("pageType") or {}
    if vid == "sekciya":
        bloki[0]["tip"] = pt.get("slug")  # у секции тип уже дал Referest
    rec = {"id": "rf-" + str(it.get("id", slug)), "slug": slug, "title": it.get("title") or e["title"],
           "site": it.get("targetUrl") or e["site"], "vid": vid, "tip_ref": pt.get("slug"), "tip_ref_name": pt.get("name"),
           "tegi": tegi(e["alt"]), "istochnik": f"https://referest.ru/screens/{slug}", "cover": cover, "h": h,
           "kollekcii": [kollekciya_id] if kollekciya_id else [], "dobavleno": time.strftime("%Y-%m-%d"), "bloki": bloki}
    if old:
        old.update({k: v for k, v in rec.items() if k != "bloki"} | {"bloki": bloki})
    else:
        baza["items"].append(rec)
    return f"{vid}, блоков {len(bloki)}"


def razmetka(baza, otvety):
    """Применить разметку: тип каждого блока, склейка кусков одного блока (slit) по исходному снимку из кэша."""
    po_slug = {x["slug"]: x for x in baza["items"]}
    n_tip = n_slit = 0
    for slug, spisok in otvety.items():
        x = po_slug.get(slug)
        if not x or not spisok or len(spisok) != len(x["bloki"]):
            print("пропуск", slug, "– нет записи или не совпало число блоков")
            continue
        im = None
        c = CACHE / (slug + ".webp")
        if c.exists():
            im = Image.open(c).convert("RGB")
            im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
        novye = []
        for b, r in zip(x["bloki"], sorted(spisok, key=lambda q: q["n"])):
            b["tip"] = r.get("tip") or None
            if r.get("dva"):
                b["dva"] = True
            if r.get("slit") and novye and im is not None and novye[-1]["tip"] == b["tip"]:
                pr = novye[-1]
                pr["h"] = b["y"] + b["h"] - pr["y"]
                im.crop((0, pr["y"], W, pr["y"] + pr["h"])).save(ROOT / pr["img"], "WEBP", quality=Q, method=5)
                (ROOT / b["img"]).unlink(missing_ok=True)
                n_slit += 1
                continue
            novye.append(b)
            n_tip += 1
        x["bloki"] = novye
    print(f"размечено блоков: {n_tip}, склеено кусков: {n_slit}")


def load():
    return json.loads(DATA.read_text(encoding="utf8")) if DATA.exists() else {"items": []}


def save(baza):
    DATA.write_text(json.dumps(baza, ensure_ascii=False, indent=1), encoding="utf8")


def slug_iz(s):
    m = re.search(r"referest\.ru/screens/([\w-]+)", s)
    return m.group(1) if m else s.strip().strip("/")


def api_item(slug):
    """Экран вне коллекции: вид и тип берём из карточки экрана на его странице."""
    h = get(f"https://referest.ru/screens/{slug}").replace('\\"', '"')
    m = re.search(r'"slug":"' + re.escape(slug) + r'","link":"([^"]*)".*?"contentType":\{"id":\d+,"slug":"(\w+)".*?"pageTypes":\[(\{[^\]]*?\})\]', h)
    if not m:
        raise RuntimeError(f"нет карточки экрана {slug}")
    return {"slug": slug, "targetUrl": m.group(1), "contentType": {"slug": m.group(2)},
            "pageType": json.loads(m.group(3).split("},{")[0].rstrip("}") + "}")}


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    baza = load()
    if cmd == "kollekciya":
        cid = sys.argv[2]
        items = kollekciya(cid)
        print(f"в коллекции {cid}: {len(items)}")
        for i, it in enumerate(items, 1):
            try:
                print(i, it["slug"], zapisat_item(baza, it, cid, "--renarezat" in sys.argv), flush=True)
            except Exception as ex:  # один битый экран не валит весь импорт
                print(i, it["slug"], "ОШИБКА", ex, flush=True)
            if i % 10 == 0:
                save(baza)
            time.sleep(0.3)
    elif cmd == "narezat":  # перерезать страницы из кэша без сети (после правки нарезки); разметка страниц сбрасывается
        for x in baza["items"]:
            c = CACHE / (x["slug"] + ".webp")
            if x["vid"] == "stranica" and c.exists():
                x["bloki"], x["cover"], x["h"] = zapis(x, c.read_bytes(), "stranica")
                print(x["slug"], len(x["bloki"]), flush=True)
    elif cmd == "chistka":  # снимки удалённых с сайта референсов
        zhivye = {x["slug"] for x in baza["items"]}
        for d in OUT.iterdir() if OUT.exists() else []:
            if d.is_dir() and d.name not in zhivye:
                for f in d.iterdir():
                    f.unlink()
                d.rmdir()
                print("убран", d.name)
    elif cmd == "razmetka":
        otvety = {}
        for f in sys.argv[2:]:
            otvety |= json.loads(Path(f).read_text(encoding="utf8"))
        razmetka(baza, otvety)
    elif cmd == "ekran":
        it = api_item(slug_iz(sys.argv[2]))
        print(it["slug"], zapisat_item(baza, it, None, "--renarezat" in sys.argv))
    elif cmd == "vhodyashie":
        zayavki = json.loads(INBOX.read_text(encoding="utf8")) if INBOX.exists() else []
        ostalos = []
        for z in zayavki:
            try:
                if z.get("fajl"):  # свой снимок, загруженный с сайта
                    f = ROOT / z["fajl"]
                    bloki, cover, h = zapis(z, f.read_bytes(), z["vid"])
                    if z["vid"] == "sekciya":
                        bloki[0]["tip"] = z.get("tip")
                    baza["items"].append({"id": "my-" + z["slug"], "slug": z["slug"], "title": z["title"], "site": z.get("site", ""),
                                          "vid": z["vid"], "tip_ref": z.get("tip") if z["vid"] == "stranica" else None,
                                          "tip_ref_name": None, "tegi": {}, "istochnik": "", "cover": cover, "h": h,
                                          "kollekcii": [], "dobavleno": time.strftime("%Y-%m-%d"), "bloki": bloki})
                    f.unlink()
                    print(z["slug"], "свой снимок, блоков", len(bloki))
                    continue
                u = z["url"]
                m = re.search(r"referest\.ru/[\w-]+/(\d+)", u)
                if m and "/screens/" not in u:
                    for it in kollekciya(m.group(1)):
                        print(it["slug"], zapisat_item(baza, it, m.group(1)))
                else:
                    it = api_item(slug_iz(u))
                    print(it["slug"], zapisat_item(baza, it))
            except Exception as ex:
                print("ОШИБКА", z, ex)
                ostalos.append(z | {"oshibka": str(ex)})
        INBOX.write_text(json.dumps(ostalos, ensure_ascii=False, indent=1), encoding="utf8")
    else:
        sys.exit(__doc__)
    save(baza)
    print("записей в базе:", len(baza["items"]), "блоков:", sum(len(x["bloki"]) for x in baza["items"]))


if __name__ == "__main__":
    main()
