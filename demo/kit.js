/* Комплект демо базы блоков: тема от страницы базы, появление, счётчики, нижние листы. Без внешних библиотек. */
(function () {
  var d = document, root = d.documentElement;
  function theme() {
    var t; try { t = localStorage.getItem('tema') } catch (e) {}
    if (!t) { var h = new Date().getHours(); t = (h >= 19 || h < 7 || matchMedia('(prefers-color-scheme: dark)').matches) ? 'dark' : 'light' }
    root.setAttribute('data-theme', t);
  }
  theme(); addEventListener('storage', theme);

  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = matchMedia('(hover:hover) and (pointer:fine)').matches;
  var EXPO = 'cubic-bezier(.16,1,.3,1)';

  var K = window.Kit = {
    reduce: reduce, fine: fine, EXPO: EXPO,
    mob: function () { return innerWidth <= 760 },
    $: function (s, r) { return (r || d).querySelector(s) },
    $$: function (s, r) { return [].slice.call((r || d).querySelectorAll(s)) },
    lock: function (on) { root.style.overflow = on ? 'hidden' : '' },

    /* Появление при прокрутке: сдвиг 34 px + прозрачность, 1,1 с, соседние с шагом 80 мс.
       Элементам со стеклом (backdrop-filter) передать {glass:true}: только сдвиг, иначе размытие «слетает». */
    reveal: function (sel, opt) {
      if (reduce) return;
      var glass = opt && opt.glass, els = K.$$(sel || '.rv');
      els.forEach(function (el) { el.style.transform = 'translateY(' + (glass ? 46 : 34) + 'px)'; if (!glass) el.style.opacity = 0 });
      var io = new IntersectionObserver(function (es) {
        var b = es.filter(function (e) { return e.isIntersecting }).map(function (e) { return e.target });
        b.forEach(function (el, i) {
          io.unobserve(el);
          el.style.transition = 'opacity 1.1s ' + EXPO + ' ' + i * 80 + 'ms,transform 1.1s ' + EXPO + ' ' + i * 80 + 'ms';
          requestAnimationFrame(function () { el.style.opacity = ''; el.style.transform = 'none' });
        });
      }, { rootMargin: '0px 0px -8% 0px' });
      els.forEach(function (el) { io.observe(el) });
    },

    /* Счётчик: [data-n="42"] досчитывает до числа за 1,4 с, когда виден на 60 %. Дробные – через запятую. */
    count: function (sel) {
      K.$$(sel || '[data-n]').forEach(function (el) {
        var n = parseFloat(el.dataset.n), frac = n % 1 !== 0;
        function put(v) { el.textContent = frac ? v.toFixed(1).replace('.', ',') : Math.round(v) }
        if (reduce) { put(n); return }
        put(0);
        var io = new IntersectionObserver(function (es) {
          if (!es[0].isIntersecting) return; io.disconnect();
          var t0 = performance.now();
          (function tick(t) { var k = Math.min(1, (t - t0) / 1400); k = 1 - Math.pow(1 - k, 4); put(n * k); if (k < 1) requestAnimationFrame(tick) })(t0);
        }, { threshold: .6 });
        io.observe(el);
      });
    },

    /* Нижние листы: [data-sheet="call"] открывает #sh-call; [data-close], свайп вниз от 80 px и Esc закрывают. */
    sheets: function () {
      function close() {
        K.$$('.sheet.open').forEach(function (s) { s.classList.remove('open'); s.setAttribute('aria-hidden', 'true') });
        K.lock(false);
      }
      K.$$('[data-sheet]').forEach(function (b) {
        b.addEventListener('click', function (e) {
          e.preventDefault(); var s = K.$('#sh-' + b.dataset.sheet); if (!s) return;
          close(); s.classList.add('open'); s.setAttribute('aria-hidden', 'false'); K.lock(true);
        });
      });
      K.$$('.sheet [data-close]').forEach(function (b) { b.addEventListener('click', close) });
      K.$$('.sh-box').forEach(function (b) {
        var y0 = 0;
        b.addEventListener('touchstart', function (e) { y0 = e.touches[0].clientY }, { passive: true });
        b.addEventListener('touchend', function (e) { if (e.changedTouches[0].clientY - y0 > 80 && b.scrollTop <= 0) close() });
      });
      addEventListener('keydown', function (e) { if (e.key === 'Escape') close() });
      K.closeSheets = close;
    },

    /* Автоперебор: пока блок на экране и человек сам ничего не выбрал, раз в ms вызывает step(). Возвращает stop(). */
    auto: function (el, ms, step) {
      var vis = false, user = false, t = 0;
      function plan() { clearTimeout(t); if (vis && !user && !reduce) t = setTimeout(function () { step(); plan() }, ms) }
      new IntersectionObserver(function (es) { vis = es[0].isIntersecting; plan() }, { threshold: .3 }).observe(el);
      return { stop: function () { user = true; clearTimeout(t) }, active: function () { return vis && !user && !reduce } };
    }
  };
})();
