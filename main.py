#!/usr/bin/env python3
"""
Telegram Advent Bot (Render Free) — финальная версия + /getid.

✅ Вебхуки через python-telegram-bot.run_webhook()
✅ Без календарных ограничений (дни циклично по кругу)
✅ Не падает на "Query is too old" (Render может просыпаться долго)
✅ /getid — выдаёт file_id последнего присланного фото/видео

ENV:
- TELEGRAM_TOKEN (обязательно)
- WEBHOOK_URL (обязательно)  -> https://<your-service>.onrender.com/webhook
- TZ_NAME (опционально)      -> Europe/Amsterdam
- WEBHOOK_SECRET (опционально)
"""

import os
import logging
from datetime import datetime, date
from zoneinfo import ZoneInfo

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.error import BadRequest

from advent_content import ADVENT_DAYS, ADVENT_START

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TZ = ZoneInfo(os.getenv("TZ_NAME", "Europe/Amsterdam"))
UNPACK_CALLBACK = "UNPACK_TODAY"


def get_index_for_today() -> int:
    """Цикличный индекс дня по текущей дате."""
    today: date = datetime.now(TZ).date()
    return (today - ADVENT_START).days % len(ADVENT_DAYS)


def main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🎁 Распаковать подарок на сегодня", callback_data=UNPACK_CALLBACK)]]
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "Привет, любимый! 💌\n\n"
        "Этот бот каждый день дарит маленький подарок: текст, фото или видео.\n\n"
        "Нажимай кнопку «🎁 Распаковать подарок на сегодня».\n\n"
        "Всё, что мы уже распаковали, остаётся в чате — можно возвращаться и пересматривать 🤍\n\n"
        "Если хочешь добавить фото/видео в контент:\n"
        "1) пришли сюда фото или видео\n"
        "2) напиши /getid — я верну file_id"
    )
    await update.message.reply_text(text, reply_markup=main_keyboard())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "Команды:\n"
        "• /start — приветствие\n"
        "• /help — помощь\n"
        "• /getid — получить file_id последнего фото/видео, которое ты прислала боту\n\n"
        "Как получить file_id:\n"
        "1) Отправь фото или видео\n"
        "2) Напиши /getid\n"
    )
    await update.message.reply_text(text, reply_markup=main_keyboard())


async def capture_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Запоминаем file_id последнего фото/видео от пользователя.
    Это нужно для команды /getid.
    """
    msg = update.message
    if not msg:
        return

    if msg.photo:
        # Берём самое большое по размеру (последний элемент)
        fid = msg.photo[-1].file_id
        context.user_data["last_media_type"] = "photo"
        context.user_data["last_file_id"] = fid
        await msg.reply_text("Фото принято ✅\nТеперь напиши /getid, и я пришлю file_id.")
        return

    if msg.video:
        fid = msg.video.file_id
        context.user_data["last_media_type"] = "video"
        context.user_data["last_file_id"] = fid
        await msg.reply_text("Видео принято ✅\nТеперь напиши /getid, и я пришлю file_id.")
        return


async def getid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Отдаём file_id последнего сохранённого фото/видео для этого пользователя.
    """
    fid = context.user_data.get("last_file_id")
    mtype = context.user_data.get("last_media_type")

    if not fid or not mtype:
        await update.message.reply_text(
            "Я пока не вижу последнего фото/видео.\n\n"
            "Сделай так:\n"
            "1) отправь мне фото или видео\n"
            "2) потом снова напиши /getid"
        )
        return

    await update.message.reply_text(
        f"Готово! ✨\n\n"
        f"Тип: {mtype}\n"
        f"file_id:\n{fid}\n\n"
        f"Скопируй его и вставь в advent_content.py в нужный день."
    )


async def unpack(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    if not q:
        return

    # Render Free может проснуться не сразу -> Telegram иногда считает callback "протухшим"
    try:
        await q.answer()
    except BadRequest as e:
        logger.warning("Callback query too old / invalid: %s", e)

    idx = get_index_for_today()
    item = ADVENT_DAYS[idx]

    media_type = item.get("media_type", "text")
    file_id = item.get("file_id")
    base_text = (item.get("text") or "").strip()
    today = datetime.now(TZ).date()
    text = f"{base_text}\n\n(Сегодня {today.strftime('%d.%m')}, день #{idx+1})"

    if media_type == "photo" and file_id:
        await q.message.reply_photo(photo=file_id, caption=text)
    elif media_type == "video" and file_id:
        await q.message.reply_video(video=file_id, caption=text)
    else:
        await q.message.reply_text(text)

    await q.message.reply_text("Жду тебя здесь снова 🤍", reply_markup=main_keyboard())


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

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("getid", getid))

    # Media capture (photo/video)
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, capture_media))

    # Button callback
    app.add_handler(CallbackQueryHandler(unpack, pattern=f"^{UNPACK_CALLBACK}$"))

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
