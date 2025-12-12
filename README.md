# Telegram Advent Bot — обработка "Query is too old"

Эта версия:
- без привязки к датам;
- использует run_webhook();
- в `handle_unpack_callback` оборачивает `query.answer()` в try/except BadRequest,
  чтобы не падать на ошибке "Query is too old and response timeout expired or query id is invalid"
  (она появляется, когда Render долго просыпается и Telegram считает нажатие устаревшим).
