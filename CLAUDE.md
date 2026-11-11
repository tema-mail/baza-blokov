# baza-blokov – база блоков сайтов (референсы с анимацией и смыслом)

- Ссылка: https://tema-mail.github.io/baza-blokov/ (noindex). Внутренняя база студии, не клиентский сайт.
- Один блок = один файл `demo/<id>.html`: живое демо + карточка в `<script type="application/json" id="meta">`. Комплект – `demo/kit.css`, `demo/kit.js`.
- Разбор сайта-образца – `data/cerus.json` + снимки `img/cerus/` + геометрия `data/geo-cerus-*.json` (снята Playwright).
- Сборка: `python3 build.py` → `site/` (в конце ставит тёмную тему через `tema.py` и валит сборку без неё).
- Проверка демо: `node proverka.mjs [id]` – ошибки консоли, горизонтальная прокрутка на 390, поля карточки.
- В демо – свой нейтральный текст (роль блока), серые заглушки вместо фото, без чужих картинок, текстов и названий.
- Только короткое тире «–». Файл кода до 800 строк. Пуш в main – выкладка на Pages.
- Библиотека (`biblioteka.html`, `build_lib.py`, `src/lib.js`, `src/lib.css`): референсы по разбивке Referest – «Секции» (типы секций) и «Страницы» (виды страниц). Данные `data/referest.json`, снимки `ref/rf/<slug>/<n>.webp` (1000 px), страницы порезаны на блоки.
- Импорт: `python3 tools/referest.py kollekciya <id>` / `ekran <slug>`; перерезать из кэша – `narezat`; разметка блоков агентами – `razmetka otvet*.json`. Кэш полных снимков – `cache/` (вне git).
- Добавить/удалить/сменить тип – с самой страницы: пишет в репо через GitHub API (ключ в браузере владельца). «Добавить» кладёт заявку в `data/referest-inbox.json`, её разбирает шаг в `.github/workflows/pages.yml` (`vhodyashie`, `chistka`) и коммитит сам.
