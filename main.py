#!/usr/bin/env python3
"""
Telegram Advent Bot (Render Free) — финальная версия.

- Webhooks (python-telegram-bot[webhooks])
- Кнопка: «Что сегодня?»
- 1 подарок в день (по TZ_NAME)
- ДЕНЬ определяется по календарю: от ADVENT_START_DATE (не зависит от перезапусков Render)
- На день: 1 текстовое сообщение, затем медиа подряд БЕЗ подписей
- Обработана ошибка Telegram: "Query is too old..." (Render Free может просыпаться долго)

ENV:
- TELEGRAM_TOKEN (обязательно)
- WEBHOOK_URL (обязательно)  -> https://<your-service>.onrender.com/webhook
- TZ_NAME (опционально, напр. Europe/Amsterdam)
- WEBHOOK_SECRET (опционально)
- ADVENT_START_DATE (опционально) -> YYYY-MM-DD (для теста можно поставить сегодняшнюю дату)
"""

import os
import logging
import sqlite3
from pathlib import Path
from datetime import datetime, date
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


def parse_start_date() -> date:
    s = os.getenv("ADVENT_START_DATE", "2025-12-26")
    try:
        y, m, d = s.split("-")
        return date(int(y), int(m), int(d))
    except Exception:
        # fallback
        return date(2025, 12, 26)


ADVENT_START = parse_start_date()


def _db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS progress (
            chat_id INTEGER PRIMARY KEY,
            last_open_date TEXT
        )
        """
    )
    return conn


def get_last_open(chat_id: int) -> str | None:
    conn = _db()
    try:
        cur = conn.execute("SELECT last_open_date FROM progress WHERE chat_id = ?", (chat_id,))
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def set_last_open(chat_id: int, last_open_date: str) -> None:
    conn = _db()
    try:
        conn.execute(
            "INSERT INTO progress(chat_id, last_open_date) VALUES(?, ?) "
            "ON CONFLICT(chat_id) DO UPDATE SET last_open_date=excluded.last_open_date",
            (chat_id, last_open_date),
        )
        conn.commit()
    finally:
        conn.close()


def today_key() -> str:
    return datetime.now(TZ).date().isoformat()


def calendar_index() -> int:
    today = datetime.now(TZ).date()
    return (today - ADVENT_START).days  # 0..N


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
    """Для теста: сброс дневного лимита в этом чате."""
    chat_id = update.effective_chat.id
    set_last_open(chat_id, "1970-01-01")
    await update.message.reply_text("Ок, сбросила лимит на сегодня ❤️", reply_markup=keyboard())


async def today(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    if not q:
        return

    try:
        await q.answer()
    except BadRequest as e:
        logger.warning("Callback query too old/invalid: %s", e)

    chat_id = q.message.chat_id

    # дневной лимит
    tk = today_key()
    if get_last_open(chat_id) == tk:
        await q.message.reply_text(LIMIT_TEXT, reply_markup=keyboard())
        return

    idx = calendar_index()

    if idx < 0:
        await q.message.reply_text("Пока рано 🙂 Завтра будет ближе ❤️", reply_markup=keyboard())
        set_last_open(chat_id, tk)
        return

    if idx >= len(ADVENT_DAYS):
        await q.message.reply_text("Наш адвент закончился ❤️", reply_markup=keyboard())
        set_last_open(chat_id, tk)
        return

    day = ADVENT_DAYS[idx]

    await q.message.reply_text(day["text"])

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

    set_last_open(chat_id, tk)
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
    logger.info("ADVENT_START_DATE=%s", ADVENT_START.isoformat())

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
