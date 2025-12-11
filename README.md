# Telegram Advent Bot — финальная версия без ограничений по датам

- Вся логика в `main.py` использует встроенный `run_webhook()` из `python-telegram-bot`.
- Проверок `адвент не начался` / `адвент закончился` нет вообще.
- Индекс дня считается как `(today - ADVENT_START) % len(ADVENT_DAYS)`, поэтому дни идут по кругу.
- Все тексты и структура адвента лежат в `advent_content.py`.
- Конфигурация для Render — в `render.yaml` (free план).
