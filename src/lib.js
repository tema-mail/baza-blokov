/* Библиотека референсов: вкладки «Секции / Страницы», типы, фильтры, просмотр, добавление и удаление.
   Запись – прямо в репо через GitHub API (data/referest.json, data/referest-inbox.json); ключ хранится только в этом браузере.
   После записи GitHub Actions пересобирает сайт (~1–2 мин); до этого правки держатся локально, чтобы не мигали. */
(function () {
  if (!window.LIB) return;
  var d = document, CFG = LIB.cfg, ITEMS = LIB.items, REPO = CFG.repo;
  var $ = function (id) { return d.getElementById(id) };
  var SEK = {}, STR = {};
  CFG.sekcii.forEach(function (s) { SEK[s[0]] = { name: s[1], tip: s[2], tipName: s[3] } });
  CFG.stranicy.forEach(function (s) { STR[s[0]] = s[1] });
  var st = { vid: 'sekcii', type: '', q: '', tem: '', stil: '', cvet: '', shrift: '', otdel: false, limit: 48 };
  var LS = 'lib-izm-v1', KEY = 'lib-gh-token';
  function ls(k, v) { try { if (v === undefined) return JSON.parse(localStorage.getItem(k) || 'null'); localStorage.setItem(k, JSON.stringify(v)) } catch (e) { return null } }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c] }) }
  function dom(u) { try { return new URL(u).hostname.replace(/^www\./, '') } catch (e) { return '' } }

  /* --- локальные правки поверх собранных данных: удалённое и сменённые типы, пока сайт не пересобрался --- */
  var izm = ls(LS) || { del: {}, tip: {} };
  function primenit() {
    ITEMS = LIB.items.filter(function (it) { return !izm.del[it.id] }).map(function (it) {
      var bl = it.bloki.filter(function (b) { return !izm.del[b.img] }).map(function (b) {
        return izm.tip[b.img] !== undefined ? Object.assign({}, b, { tip: izm.tip[b.img] }) : b;
      });
      return Object.assign({}, it, { bloki: bl });
    }).filter(function (it) { return it.bloki.length });
  }
  function chistka() { // правка уже есть в собранных данных – локальная запись больше не нужна
    var ids = {}, imgs = {};
    LIB.items.forEach(function (it) { ids[it.id] = 1; it.bloki.forEach(function (b) { imgs[b.img] = b.tip || '' }) });
    Object.keys(izm.del).forEach(function (k) { if (!ids[k] && imgs[k] === undefined) delete izm.del[k] });
    Object.keys(izm.tip).forEach(function (k) { if (imgs[k] === undefined || imgs[k] === (izm.tip[k] || '')) delete izm.tip[k] });
    ls(LS, izm);
  }

  /* --- записи для текущей вкладки --- */
  function zapisi() {
    var out = [];
    ITEMS.forEach(function (it) {
      if (st.vid === 'stranicy') { if (it.vid === 'stranica') out.push({ it: it, tip: it.tip_ref || '' }); return }
      if (st.otdel && it.vid !== 'sekciya') return;
      it.bloki.forEach(function (b) { out.push({ it: it, b: b, tip: b.tip || '' }) });
    });
    return out;
  }
  function podhodit(z) {
    var t = z.it.tegi || {};
    if (st.tem && (t.tematika || []).indexOf(st.tem) < 0) return false;
    if (st.stil && (t.stil || []).indexOf(st.stil) < 0) return false;
    if (st.cvet && (t.cveta || []).indexOf(st.cvet) < 0) return false;
    if (st.shrift && (t.tipografika || []).indexOf(st.shrift) < 0) return false;
    if (st.q && (z.it.title + ' ' + z.it.site).toLowerCase().indexOf(st.q) < 0) return false;
    return true;
  }
  function imyaTipa(tip) {
    if (st.vid === 'stranicy') return STR[tip] || tip || 'Без вида';
    return SEK[tip] ? SEK[tip].name : (tip || 'Без типа');
  }

  function tipy(vse) {
    var cnt = {}, poryadok = st.vid === 'stranicy' ? CFG.stranicy.map(function (s) { return s[0] }) : CFG.sekcii.map(function (s) { return s[0] });
    vse.forEach(function (z) { cnt[z.tip] = (cnt[z.tip] || 0) + 1 });
    var h = '<button type="button" data-t=""' + (st.type ? '' : ' class="on"') + '>Все <i>' + vse.length + '</i></button>';
    poryadok.concat(Object.keys(cnt).filter(function (k) { return poryadok.indexOf(k) < 0 })).forEach(function (k) {
      if (!cnt[k]) return;
      h += '<button type="button" data-t="' + esc(k) + '"' + (st.type === k ? ' class="on"' : '') + '>' + esc(imyaTipa(k)) + ' <i>' + cnt[k] + '</i></button>';
    });
    $('lib-types').innerHTML = h;
  }

  function opcii() {
    var sets = { tem: {}, stil: {}, cvet: {}, shrift: {} }, map = { tem: 'tematika', stil: 'stil', cvet: 'cveta', shrift: 'tipografika' };
    LIB.items.forEach(function (it) { Object.keys(map).forEach(function (k) { ((it.tegi || {})[map[k]] || []).forEach(function (v) { sets[k][v] = (sets[k][v] || 0) + 1 }) }) });
    Object.keys(map).forEach(function (k) {
      var s = $('lib-' + k), first = s.options[0].outerHTML;
      s.innerHTML = first + Object.keys(sets[k]).sort().map(function (v) { return '<option value="' + esc(v) + '">' + esc(v) + ' · ' + sets[k][v] + '</option>' }).join('');
    });
  }

  function kartochka(z, i) {
    var it = z.it, img = z.b ? z.b.img : it.cover, chast = '';
    if (z.b && it.vid === 'stranica') chast = '<span class="lc-part">блок ' + (it.bloki.indexOf(z.b) + 1) + ' из ' + it.bloki.length + '</span>';
    if (!z.b) chast = '<span class="lc-part">' + it.bloki.length + ' блоков</span>';
    return '<article class="lc" data-i="' + i + '">' +
      '<button type="button" class="lc-img" data-open="' + i + '" aria-label="Открыть ' + esc(it.title) + '"><img src="' + esc(img) + '" alt="" loading="lazy">' + chast + '</button>' +
      '<div class="lc-b"><b>' + esc(it.title) + '</b><small>' + esc(imyaTipa(z.tip)) + ' · ' + esc(dom(it.site)) + '</small></div>' +
      '<button type="button" class="lc-del" data-del="' + i + '" title="Удалить" aria-label="Удалить">×</button></article>';
  }

  var vidno = [];
  function risovat() {
    primenit();
    var vse = zapisi().filter(podhodit);
    tipy(vse);
    vidno = vse.filter(function (z) { return !st.type || z.tip === st.type });
    $('lib-n').textContent = vidno.length;
    $('lib-grid').innerHTML = vidno.slice(0, st.limit).map(kartochka).join('') || '<p class="meta">Ничего не нашлось – снимите фильтр.</p>';
    $('lib-more').hidden = vidno.length <= st.limit;
  }

  /* --- просмотр: справа описание, слева снимок (у страницы – все блоки подряд с типом каждого) --- */
  var ov = d.createElement('div'); ov.className = 'lib-ov'; ov.hidden = true; d.body.appendChild(ov);
  function selTip(img, cur) {
    var h = '<select data-retip="' + esc(img) + '"><option value="">– без типа –</option>';
    CFG.sekcii.forEach(function (s) { h += '<option value="' + s[0] + '"' + (s[0] === cur ? ' selected' : '') + '>' + esc(s[1]) + ' · ' + esc(s[3]) + '</option>' });
    return h + '</select>';
  }
  function otkryt(z) {
    var it = z.it, t = it.tegi || {}, celaya = !z.b || it.vid === 'sekciya';
    var bl = celaya ? it.bloki : [z.b];
    var shots = bl.map(function (b, k) {
      var n = it.bloki.indexOf(b) + 1;
      return '<figure class="ov-b" id="ov-' + esc(b.img) + '">' + (it.vid === 'stranica' ? '<figcaption>Блок ' + n + ' · ' + selTip(b.img, b.tip) + '<button type="button" class="chip" data-delb="' + esc(b.img) + '">Удалить блок</button></figcaption>' : '') +
        '<img src="' + esc(b.img) + '" alt="" loading="' + (k < 3 ? 'eager' : 'lazy') + '"></figure>';
    }).join('');
    var tg = [['Тематика', t.tematika], ['Стиль', t.stil], ['Цвета', t.cveta], ['Типографика', t.tipografika]].filter(function (x) { return x[1] && x[1].length })
      .map(function (x) { return '<dt>' + x[0] + '</dt><dd>' + esc(x[1].join(', ')) + '</dd>' }).join('');
    var tipBlok = z.b ? (SEK[z.b.tip] ? SEK[z.b.tip] : null) : null;
    ov.innerHTML = '<div class="ov-w"><div class="ov-shots">' + shots + '</div><aside class="ov-side">' +
      '<button type="button" class="ov-x" aria-label="Закрыть">×</button>' +
      '<h3>' + esc(it.title) + '</h3><p class="meta">' + (it.vid === 'stranica' ? 'Страница · ' + esc(STR[it.tip_ref] || it.tip_ref_name || '') + ' · ' + it.bloki.length + ' блоков' : 'Секция') + '</p>' +
      (z.b && it.vid === 'sekciya' ? '<p>' + selTip(z.b.img, z.b.tip) + '</p>' : '') +
      (tipBlok ? '<p><span class="chip t">' + esc(tipBlok.tipName) + ' · ' + tipBlok.tip + '</span> <a href="index.html">живые демо</a></p>' : '') +
      '<dl>' + tg + '</dl>' +
      '<p><a href="' + esc(it.site) + '" target="_blank" rel="noopener">Открыть сайт ' + esc(dom(it.site)) + ' ↗</a><br>' +
      (it.istochnik ? '<a href="' + esc(it.istochnik) + '" target="_blank" rel="noopener">Карточка на Referest ↗</a>' : 'Добавлен своим снимком') + '</p>' +
      (!celaya ? '<p><button type="button" class="chip" data-whole>Вся страница целиком →</button></p>' : '') +
      '<p><button type="button" class="chip danger" data-deli>' + (it.vid === 'stranica' ? 'Удалить страницу со всеми блоками' : 'Удалить секцию') + '</button></p>' +
      '</aside></div>';
    ov.hidden = false; d.documentElement.style.overflow = 'hidden'; ov.scrollTop = 0;
    ov.querySelector('.ov-x').onclick = zakryt;
    var w = ov.querySelector('[data-whole]'); if (w) w.onclick = function () { otkryt({ it: it }); var f = d.getElementById('ov-' + z.b.img); if (f) f.scrollIntoView() };
    ov.querySelector('[data-deli]').onclick = function () { udalit(it, null) };
    [].forEach.call(ov.querySelectorAll('[data-delb]'), function (b) { b.onclick = function () { udalit(it, b.dataset.delb); b.closest('figure').remove() } });
    [].forEach.call(ov.querySelectorAll('[data-retip]'), function (s) { s.onchange = function () { smenitTip(it, s.dataset.retip, s.value) } });
  }
  function zakryt() { ov.hidden = true; d.documentElement.style.overflow = '' }
  ov.addEventListener('click', function (e) { if (e.target === ov) zakryt() });
  addEventListener('keydown', function (e) { if (e.key === 'Escape') { zakryt(); dlg.hidden = true } });

  /* --- GitHub: чтение и запись файлов репо по очереди, с повтором при гонке с пересборкой --- */
  function tok() { return ls(KEY) }
  function b64(str) { var u = new TextEncoder().encode(str), s = ''; for (var i = 0; i < u.length; i += 0x8000) s += String.fromCharCode.apply(null, u.subarray(i, i + 0x8000)); return btoa(s) }
  function unb64(s) { var b = atob(s.replace(/\n/g, '')), u = new Uint8Array(b.length); for (var i = 0; i < b.length; i++) u[i] = b.charCodeAt(i); return new TextDecoder().decode(u) }
  function api(path, opt) {
    opt = opt || {};
    opt.headers = { Authorization: 'Bearer ' + tok(), Accept: 'application/vnd.github+json' };
    return fetch('https://api.github.com/repos/' + REPO + path, opt);
  }
  function chitat(file) {
    return api('/contents/' + file + '?ref=main').then(function (r) {
      if (r.status === 404) return { sha: null, text: null };
      if (!r.ok) throw new Error('GitHub ' + r.status);
      return r.json().then(function (m) {
        if (m.content) return { sha: m.sha, text: unb64(m.content) };
        return api('/git/blobs/' + m.sha).then(function (r2) { return r2.json() }).then(function (bl) { return { sha: m.sha, text: unb64(bl.content) } });
      });
    });
  }
  function pisat(file, sha, b64content, msg) {
    var body = { message: msg, content: b64content, branch: 'main' }; if (sha) body.sha = sha;
    return api('/contents/' + file, { method: 'PUT', body: JSON.stringify(body) }).then(function (r) {
      if (r.status === 409 || r.status === 422) { var e = new Error('гонка'); e.race = 1; throw e }
      if (!r.ok) throw new Error('GitHub ' + r.status);
    });
  }
  var ochered = Promise.resolve(), zhdut = 0;
  function sync(t) { $('lib-sync').textContent = t ? '· ' + t : '' }
  function vRepo(file, msg, fn, pustoe) {
    zhdut++; sync('сохраняю… (' + zhdut + ')');
    function raz(n) {
      return chitat(file).then(function (f) {
        var data = f.text ? JSON.parse(f.text) : pustoe;
        fn(data);
        return pisat(file, f.sha, b64(JSON.stringify(data, null, 1)), msg);
      }).catch(function (e) { if (e.race && n < 3) return new Promise(function (ok) { setTimeout(ok, 1500) }).then(function () { return raz(n + 1) }); throw e });
    }
    ochered = ochered.then(function () { return raz(0) }).then(function () {
      zhdut--; sync(zhdut ? 'сохраняю… (' + zhdut + ')' : 'сохранено в репо, сайт обновится через 1–2 минуты');
    }, function (e) { zhdut--; sync('не сохранилось: ' + e.message + ' – проверьте доступ'); });
    return ochered;
  }
  function nuzhenKlyuch() { if (tok()) return false; otkrytDlg('key'); return true }

  function udalit(it, img) {
    if (nuzhenKlyuch()) return;
    var vse = !img || it.bloki.length < 2;
    if (vse && !confirmUdal(it)) return;
    if (vse) izm.del[it.id] = 1; else izm.del[img] = 1;
    ls(LS, izm);
    if (vse) zakryt();
    risovat();
    vRepo('data/referest.json', (vse ? 'Библиотека: удалён референс ' : 'Библиотека: удалён блок ') + it.title, function (baza) {
      if (vse) baza.items = baza.items.filter(function (x) { return x.id !== it.id });
      else baza.items.forEach(function (x) { if (x.id === it.id) x.bloki = x.bloki.filter(function (b) { return b.img !== img }) });
    }, { items: [] });
  }
  var podtv = {};
  function confirmUdal(it) { // без системного окна: первый щелчок предупреждает, второй в течение 4 с удаляет
    if (podtv[it.id] && Date.now() - podtv[it.id] < 4000) return true;
    podtv[it.id] = Date.now(); sync('нажмите «удалить» ещё раз, чтобы удалить «' + it.title + '»'); return false;
  }
  function smenitTip(it, img, tip) {
    if (nuzhenKlyuch()) return;
    izm.tip[img] = tip; ls(LS, izm); risovat();
    vRepo('data/referest.json', 'Библиотека: тип блока ' + it.title + ' → ' + (tip || 'без типа'), function (baza) {
      baza.items.forEach(function (x) { if (x.id === it.id) x.bloki.forEach(function (b) { if (b.img === img) b.tip = tip || null }) });
    }, { items: [] });
  }

  /* --- окно «Добавить» и «Доступ» --- */
  var dlg = d.createElement('div'); dlg.className = 'lib-ov lib-dlg'; dlg.hidden = true; d.body.appendChild(dlg);
  function opts(list) { return list.map(function (s) { return '<option value="' + s[0] + '">' + esc(s[1]) + '</option>' }).join('') }
  function otkrytDlg(chto) {
    var key = chto === 'key';
    dlg.innerHTML = '<div class="dlg"><button type="button" class="ov-x" aria-label="Закрыть">×</button>' + (key ?
      '<h3>Доступ на запись</h3><p class="meta">Добавлять и удалять может только тот, у кого есть ключ GitHub с правом записи в репо ' + REPO + '. Ключ хранится только в этом браузере и уходит только на api.github.com.</p>' +
      '<label>Ключ GitHub<input type="password" id="dk" autocomplete="off" placeholder="github_pat_… или ghp_…" value="' + esc(tok() || '') + '"></label>' +
      '<p class="meta">Лучше отдельный ключ: GitHub → Settings → Developer settings → Fine-grained token, репо ' + REPO + ', Contents: Read and write.</p>' +
      '<div class="dlg-a"><button type="button" class="btn-main" id="dk-ok">Сохранить и проверить</button><button type="button" class="chip" id="dk-del">Убрать ключ</button></div><p class="meta" id="dk-st"></p>'
      :
      '<h3>Добавить референс</h3><div class="lib-tabs sm"><button type="button" class="on" data-m="url">Ссылка Referest</button><button type="button" data-m="file">Свой снимок</button></div>' +
      '<div data-p="url"><label>Ссылка на экран или коллекцию Referest<input id="du" placeholder="https://referest.ru/screens/… или https://referest.ru/имя/12343242"></label>' +
      '<p class="meta">Снимок, тип, теги и нарезку страницы на блоки сделает сборка на GitHub, через 2–4 минуты он появится здесь.</p></div>' +
      '<div data-p="file" hidden><label>Снимок (PNG, JPG, WebP)<input type="file" id="df" accept="image/*"></label>' +
      '<label>Название<input id="dn" placeholder="Например, сайт студии"></label><label>Адрес сайта<input id="ds" placeholder="https://"></label>' +
      '<label>Что это<select id="dv"><option value="sekciya">Секция – один блок</option><option value="stranica">Страница целиком – порезать на блоки</option></select></label>' +
      '<label id="dt-s">Тип секции<select id="dts">' + opts(CFG.sekcii) + '</select></label><label id="dt-p" hidden>Вид страницы<select id="dtp">' + opts(CFG.stranicy) + '</select></label></div>' +
      '<div class="dlg-a"><button type="button" class="btn-main" id="da">Добавить</button></div><p class="meta" id="da-st"></p>') + '</div>';
    dlg.hidden = false;
    dlg.querySelector('.ov-x').onclick = function () { dlg.hidden = true };
    if (key) {
      $('dk-ok').onclick = function () {
        ls(KEY, $('dk').value.trim()); $('dk-st').textContent = 'проверяю…';
        api('').then(function (r) { return r.json().then(function (j) { return [r.status, j] }) }).then(function (x) {
          $('dk-st').textContent = x[0] === 200 && x[1].permissions && x[1].permissions.push ? 'Ключ работает, запись разрешена.' : 'Ключ не даёт записи в ' + REPO + ' (ответ ' + x[0] + ').';
        }).catch(function () { $('dk-st').textContent = 'Нет связи с GitHub.' });
      };
      $('dk-del').onclick = function () { try { localStorage.removeItem(KEY) } catch (e) { } $('dk').value = ''; $('dk-st').textContent = 'Ключ убран.' };
      return;
    }
    var mode = 'url';
    [].forEach.call(dlg.querySelectorAll('[data-m]'), function (b) {
      b.onclick = function () {
        mode = b.dataset.m;
        [].forEach.call(dlg.querySelectorAll('[data-m]'), function (x) { x.classList.toggle('on', x === b) });
        [].forEach.call(dlg.querySelectorAll('[data-p]'), function (p) { p.hidden = p.dataset.p !== mode });
      };
    });
    $('dv').onchange = function () { $('dt-s').hidden = this.value !== 'sekciya'; $('dt-p').hidden = this.value === 'sekciya' };
    $('da').onclick = function () { if (!nuzhenKlyuch()) (mode === 'url' ? poSsylke() : poFaylu()) };
  }
  function poSsylke() {
    var u = $('du').value.trim();
    if (!/referest\.ru\//.test(u)) { $('da-st').textContent = 'Нужна ссылка на referest.ru'; return }
    $('da-st').textContent = 'Отправляю…';
    vRepo('data/referest-inbox.json', 'Библиотека: добавить ' + u, function (q) { q.push({ url: u }) }, []).then(function () {
      $('da-st').textContent = 'Принято. Сборка скачает снимок и порежет его, через 2–4 минуты обновите страницу.'; $('du').value = '';
    });
  }
  function poFaylu() {
    var f = $('df').files[0], name = $('dn').value.trim();
    if (!f || !name) { $('da-st').textContent = 'Нужны снимок и название'; return }
    var vid = $('dv').value, slug = 'svoy-' + Date.now().toString(36);
    $('da-st').textContent = 'Сжимаю снимок…';
    var im = new Image();
    im.onload = function () {
      var k = Math.min(1, 1600 / im.naturalWidth), c = d.createElement('canvas');
      c.width = Math.round(im.naturalWidth * k); c.height = Math.round(im.naturalHeight * k);
      c.getContext('2d').drawImage(im, 0, 0, c.width, c.height);
      var b64img = c.toDataURL('image/webp', 0.85).split(',')[1];
      $('da-st').textContent = 'Загружаю…';
      zhdut++; sync('сохраняю…');
      ochered = ochered.then(function () { return pisat('data/inbox/' + slug + '.webp', null, b64img, 'Библиотека: снимок ' + name) })
        .then(function () { zhdut-- }, function (e) { zhdut--; throw e });
      vRepo('data/referest-inbox.json', 'Библиотека: добавить ' + name, function (q) {
        q.push({ fajl: 'data/inbox/' + slug + '.webp', slug: slug, title: name, site: $('ds').value.trim(), vid: vid, tip: vid === 'sekciya' ? $('dts').value : $('dtp').value });
      }, []).then(function () { $('da-st').textContent = 'Загружено. Через 2–4 минуты появится в библиотеке.' });
    };
    im.onerror = function () { $('da-st').textContent = 'Не получилось открыть картинку' };
    im.src = URL.createObjectURL(f);
  }

  /* --- события --- */
  [].forEach.call(d.querySelectorAll('.lib-tabs [data-vid]'), function (b) {
    b.onclick = function () {
      st.vid = b.dataset.vid; st.type = ''; st.limit = 48;
      [].forEach.call(d.querySelectorAll('.lib-tabs [data-vid]'), function (x) { x.classList.toggle('on', x === b) });
      $('lib-otdel').parentNode.hidden = st.vid !== 'sekcii'; risovat();
    };
  });
  $('lib-types').onclick = function (e) { var b = e.target.closest('[data-t]'); if (!b) return; st.type = b.dataset.t; st.limit = 48; risovat() };
  ['tem', 'stil', 'cvet', 'shrift'].forEach(function (k) { $('lib-' + k).onchange = function () { st[k] = this.value; st.limit = 48; risovat() } });
  $('lib-q').oninput = function () { st.q = this.value.trim().toLowerCase(); st.limit = 48; risovat() };
  $('lib-otdel').onchange = function () { st.otdel = this.checked; risovat() };
  $('lib-more').onclick = function () { st.limit += 48; risovat() };
  $('lib-grid').onclick = function (e) {
    var o = e.target.closest('[data-open]'), x = e.target.closest('[data-del]');
    if (o) otkryt(vidno[+o.dataset.open]);
    if (x) { var z = vidno[+x.dataset.del]; udalit(z.it, z.b && z.it.vid === 'stranica' ? z.b.img : null) }
  };
  $('lib-add').onclick = function () { otkrytDlg('add') };
  $('lib-key').onclick = function () { otkrytDlg('key') };

  chistka(); opcii(); risovat();
})();
