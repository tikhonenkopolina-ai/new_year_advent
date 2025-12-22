#!/usr/bin/env python3
"""
Telegram Advent Bot (Render Free) — финальная версия.

- Вебхуки через python-telegram-bot.run_webhook()
- Кнопка: «Что там сегодня?»
- Без дат и без календарных ограничений: дни крутятся по кругу
- На день: 1 текстовое сообщение, затем медиа подряд БЕЗ подписей
- Обработана ошибка Telegram: "Query is too old..."
"""

import os
import logging
from datetime import datetime, date
from zoneinfo import ZoneInfo

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import BadRequest

from advent_content import ADVENT_DAYS, ADVENT_START

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TZ = ZoneInfo(os.getenv("TZ_NAME", "Europe/Amsterdam"))
BUTTON_TEXT = "Что там сегодня?"
CALLBACK = "TODAY"


def day_index() -> int:
    """Цикличный индекс дня по текущей дате."""
    today: date = datetime.now(TZ).date()
    return (today - ADVENT_START).days % len(ADVENT_DAYS)


def keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton(BUTTON_TEXT, callback_data=CALLBACK)]])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "Привет, Пшеничка 🤍\n"
        "Это адвент-бот, который будет дарить тебе подарки\n"
        "и напоминать о приятных моментах,\n"
        "пока между нами несколько тысяч километров.\n"
        "Кнопка: что там сегодня?"
    )
    await update.message.reply_text(text, reply_markup=keyboard())


async def today(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    if not q:
        return

    try:
        await q.answer()
    except BadRequest as e:
        logger.warning("Callback query too old/invalid: %s", e)

    idx = day_index()
    day = ADVENT_DAYS[idx]

    # 1) один текст
    await q.message.reply_text(day["text"])

    # 2) медиа подряд без подписей
    for item in day.get("media", []):
        t = item.get("type")
        fid = item.get("file_id")
        if not t or not fid:
            continue

        if t == "photo":
            await q.message.reply_photo(photo=fid)
        elif t == "video":
            await q.message.reply_video(video=fid)
        elif t == "animation":
            await q.message.reply_animation(animation=fid)
        elif t == "document":
            await q.message.reply_document(document=fid)

    await q.message.reply_text("🤍", reply_markup=keyboard())


def main() -> None:
    token = os.environ.get("TELEGRAM_TOKEN")
    webhook_url = os.environ.get("WEBHOOK_URL")
    secret_token = os.environ.get("WEBHOOK_SECRET", "") or None
    port = int(os.environ.get("PORT", "10000"))

    if not token:
        raise RuntimeError("TELEGRAM_TOKEN не задан")
    if not webhook_url:
        raise RuntimeError("WEBHOOK_URL не задан (пример: https://<service>.onrender.com/webhook)")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(today, pattern=f"^{CALLBACK}$"))

    logger.info("Starting webhook on port %s", port)
    logger.info("WEBHOOK_URL=%s", webhook_url)

    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="webhook",
        webhook_url=webhook_url,
        secret_token=secret_token,
        allowed_updates=["message", "callback_query"],
    )


if __name__ == "__main__":
    main()
