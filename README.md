# Telegram Advent Bot (v3, упрощённый webhook)

Эта версия использует встроенный сервер `run_webhook()` из
`python-telegram-bot`, без собственного aiohttp-приложения.

Это:
- убирает ошибку `This Application was not initialized via 'Application.initialize'!`;
- упрощает код;
- остаётся полностью бесплатным на Render (free план).

Для работы нужно задать переменные окружения:
- `TELEGRAM_TOKEN`
- `WEBHOOK_URL` (например, `https://telegram-advent-bot.onrender.com/webhook`)
- `WEBHOOK_SECRET` (опционально)
- `TZ_NAME` (например, `Europe/Amsterdam`)
