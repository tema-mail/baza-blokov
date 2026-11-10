/* Страницы базы блоков: фреймы с живыми демо, фильтры, увеличение снимков. */
(function () {
  var d = document, $$ = function (s, r) { return [].slice.call((r || d).querySelectorAll(s)) };
  var W = { m: 390, d: 1280 };

  /* --- живое демо: фрейм фиксированной ширины, ужатый под колонку; грузится, когда карточка рядом с экраном --- */
  function fit(st) {
    var f = st.querySelector('iframe'); if (!f) return;
    var v = st.dataset.v, w = W[v], h = +st.dataset['h' + v] || 680;
    var box = st.parentNode.clientWidth, k = Math.min(1, (v === 'm' ? Math.min(box - 16, 390) : box - 2) / w);
    f.style.width = w + 'px'; f.style.height = h + 'px'; f.style.transform = 'scale(' + k + ')';
    st.style.width = (v === 'm' ? Math.round(w * k) + 16 : '') + (v === 'm' ? 'px' : '');
    st.style.height = Math.round(h * k) + (v === 'm' ? 16 : 2) + 'px';
  }
  function load(st) {
    var w = st.querySelector('.wait'); if (w) w.remove();
    var f = st.querySelector('iframe');
    if (!f) { f = d.createElement('iframe'); f.title = 'Живое демо блока'; st.appendChild(f) }
    f.src = st.dataset.src + '?v=' + st.dataset.v + '&t=' + Date.now();
    st.classList.toggle('m', st.dataset.v === 'm'); fit(st);
  }
  var io = 'IntersectionObserver' in window ? new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { io.unobserve(e.target); load(e.target) } });
  }, { rootMargin: '300px 0px' }) : null;
  $$('.stage').forEach(function (st) { if (io) io.observe(st); else load(st) });
  addEventListener('resize', function () { $$('.stage').forEach(fit) });
  $$('.demo').forEach(function (dm) {
    var st = dm.querySelector('.stage');
    $$('[data-v]', dm.querySelector('.demo-bar')).forEach(function (b) {
      b.addEventListener('click', function () {
        $$('[data-v]', dm.querySelector('.demo-bar')).forEach(function (x) { x.classList.toggle('on', x === b) });
        st.dataset.v = b.dataset.v; load(st);
      });
    });
    var re = dm.querySelector('[data-re]'); if (re) re.addEventListener('click', function () { load(st) });
  });

  /* --- фильтры карточек: по типу блока и этапу решения --- */
  var cur = { tip: '', etap: '' };
  function apply() {
    var n = 0;
    $$('.blok[data-tip]').forEach(function (b) {
      var ok = (!cur.tip || b.dataset.tip === cur.tip) && (!cur.etap || b.dataset.etap === cur.etap);
      b.hidden = !ok; if (ok) n++;
    });
    var c = d.getElementById('found'); if (c) c.textContent = n;
  }
  $$('[data-f]').forEach(function (b) {
    b.addEventListener('click', function () {
      var k = b.dataset.f, v = b.dataset.val;
      cur[k] = cur[k] === v ? '' : v;
      $$('[data-f="' + k + '"]').forEach(function (x) { x.classList.toggle('on', x.dataset.val === cur[k]) });
      apply();
    });
  });

  /* --- снимки: открыть во весь экран, крестик, листание --- */
  var shots = $$('[data-zoom]'), z = d.getElementById('zoom'), zi = z && z.querySelector('img'), at = 0;
  function show(i) { at = (i + shots.length) % shots.length; zi.src = shots[at].dataset.zoom; zi.alt = shots[at].getAttribute('aria-label') || ''; z.classList.add('on'); z.scrollTop = 0; d.documentElement.style.overflow = 'hidden' }
  function hide() { z.classList.remove('on'); d.documentElement.style.overflow = '' }
  if (z) {
    shots.forEach(function (s, i) { s.addEventListener('click', function () { show(i) }) });
    z.querySelector('.zoom-x').addEventListener('click', hide);
    z.querySelector('.p').addEventListener('click', function (e) { e.stopPropagation(); show(at - 1) });
    z.querySelector('.n').addEventListener('click', function (e) { e.stopPropagation(); show(at + 1) });
    z.addEventListener('click', function (e) { if (e.target === z) hide() });
    addEventListener('keydown', function (e) { if (!z.classList.contains('on')) return; if (e.key === 'Escape') hide(); if (e.key === 'ArrowRight') show(at + 1); if (e.key === 'ArrowLeft') show(at - 1) });
  }

  /* --- классификатор: таблица из данных страницы, поиск и отборы --- */
  var kt = d.getElementById('kl-body');
  if (kt && window.KL) {
    var q = d.getElementById('kl-q'), fc = d.getElementById('kl-cat'), fs = d.getElementById('kl-st'), fk = d.getElementById('kl-cl'), cnt = d.getElementById('kl-n');
    function esc(s) { return String(s).replace(/[&<>]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c] }) }
    function draw() {
      var t = q.value.trim().toLowerCase(), c = fc.value, s = fs.value, k = fk.value, out = [], n = 0;
      KL.forEach(function (r) {
        if (c && r[2] !== c) return; if (s && r[7] !== s) return; if (k && r[6] !== k) return;
        if (t && (r[5] + ' ' + r[4] + ' ' + r[10] + ' ' + r[11]).toLowerCase().indexOf(t) < 0) return;
        n++; if (n > 400) return;
        out.push('<tr><td>' + esc(r[0]) + '</td><td><b>' + esc(r[5]) + '</b></td><td>' + esc(r[4]) + '</td><td>' + esc(r[6]) + '</td><td>' + esc(r[7]) + '</td><td>' + esc(r[9]) + '</td><td>' + esc(r[10]) + '</td></tr>');
      });
      kt.innerHTML = out.join(''); cnt.textContent = n + (n > 400 ? ' (показаны первые 400)' : '');
    }
    [q, fc, fs, fk].forEach(function (el) { el.addEventListener('input', draw) }); draw();
  }
})();
