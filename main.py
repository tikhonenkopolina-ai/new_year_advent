#!/usr/bin/env python3
"""
Telegram Advent Bot (Render Free) — финальная версия.

- Webhooks (python-telegram-bot[webhooks])
- Кнопка: «Что сегодня?»
- Дни открываются по порядку с Дня 1 (прогресс запоминается для каждого чата)
- ОГРАНИЧЕНИЕ: 1 подарок в день на чат (по TZ_NAME)
- На день: 1 текстовое сообщение, затем медиа подряд БЕЗ подписей
- Обработана ошибка Telegram: "Query is too old..." (Render Free может просыпаться долго)

ENV:
- TELEGRAM_TOKEN (обязательно)
- WEBHOOK_URL (обязательно)  -> https://<your-service>.onrender.com/webhook
- TZ_NAME (опционально, напр. Europe/Amsterdam)
- WEBHOOK_SECRET (опционально)
"""

import os
import logging
import sqlite3
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import BadRequest

from advent_content import ADVENT_DAYS

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TZ = ZoneInfo(os.getenv("TZ_NAME", "Europe/Amsterdam"))

BUTTON_TEXT = "Что сегодня?"
CALLBACK = "TODAY"
DB_PATH = Path(os.getenv("STATE_DB_PATH", "state.db"))

LIMIT_TEXT = "Я знаю, что ты запойный, но наберись терпения — завтра ты всё узнаешь ❤️"


def _db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS progress (
            chat_id INTEGER PRIMARY KEY,
            idx INTEGER NOT NULL,
            last_open_date TEXT
        )
        """
    )
    return conn


def get_state(chat_id: int) -> tuple[int, str | None]:
    conn = _db()
    try:
        cur = conn.execute("SELECT idx, last_open_date FROM progress WHERE chat_id = ?", (chat_id,))
        row = cur.fetchone()
        if row is None:
            return 0, None
        return int(row[0]), row[1]
    finally:
        conn.close()


def set_state(chat_id: int, idx: int, last_open_date: str | None) -> None:
    conn = _db()
    try:
        conn.execute(
            "INSERT INTO progress(chat_id, idx, last_open_date) VALUES(?, ?, ?) "
            "ON CONFLICT(chat_id) DO UPDATE SET idx=excluded.idx, last_open_date=excluded.last_open_date",
            (chat_id, idx, last_open_date),
        )
        conn.commit()
    finally:
        conn.close()


def today_key() -> str:
    return datetime.now(TZ).date().isoformat()


def keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton(BUTTON_TEXT, callback_data=CALLBACK)]])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "Привет, Пшеничка 🌾\n"
        "Это адвент-бот, который будет дарить тебе подарки \n"
        "и напоминать о приятных моментах,\n"
        "пока между нами несколько тысяч километров 🧡"
    )
    await update.message.reply_text(text, reply_markup=keyboard())


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Сброс прогресса (для теста)."""
    chat_id = update.effective_chat.id
    set_state(chat_id, 0, None)
    await update.message.reply_text("Прогресс сброшен. Начинаем с Дня 1 ❤️", reply_markup=keyboard())


async def today(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    if not q:
        return

    # Render Free может проснуться не сразу -> Telegram иногда считает callback "протухшим"
    try:
        await q.answer()
    except BadRequest as e:
        logger.warning("Callback query too old/invalid: %s", e)

    chat_id = q.message.chat_id
    idx, last_open = get_state(chat_id)

    # лимит: 1 раз в день
    tk = today_key()
    if last_open == tk:
        await q.message.reply_text(LIMIT_TEXT, reply_markup=keyboard())
        return

    if idx >= len(ADVENT_DAYS):
        await q.message.reply_text("Наш адвент закончился ❤️", reply_markup=keyboard())
        return

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

    # сохранить прогресс + дату открытия
    set_state(chat_id, idx + 1, tk)

    await q.message.reply_text("❤️", reply_markup=keyboard())


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
    app.add_handler(CommandHandler("reset", reset))
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
