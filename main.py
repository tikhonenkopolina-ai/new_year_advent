#!/usr/bin/env python3
"""
Telegram Advent Bot — версия без календарных ограничений.

Кнопка «Распаковать подарок на сегодня» всегда работает:
- берём сегодняшнюю дату;
- считаем количество дней, прошедших с ADVENT_START;
- берём остаток по длине списка ADVENT_DAYS;
- таким образом, дни зациклены, и бот никогда не говорит «ещё рано» или «адвент закончился».
"""

import os
import logging
from datetime import datetime, date
from zoneinfo import ZoneInfo

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from advent_content import ADVENT_DAYS, ADVENT_START, ADVENT_END

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TZ_NAME = os.getenv("TZ_NAME", "Europe/Amsterdam")
TZ = ZoneInfo(TZ_NAME)

UNPACK_CALLBACK = "UNPACK_TODAY"


def get_today_index() -> int:
    """
    Возвращает индекс дня адвента (0..len-1) для текущей даты.

    Без ограничений:
    - считаем разницу между сегодняшним днём и ADVENT_START;
    - берём её по модулю длины ADVENT_DAYS;
    - таким образом, дни зациклены по кругу и работают в любое время года.
    """
    today: date = datetime.now(TZ).date()
    delta_days = (today - ADVENT_START).days
    # на случай, если сегодня раньше ADVENT_START — нормализуем
    index = delta_days % len(ADVENT_DAYS)
    return index


def build_main_keyboard() -> InlineKeyboardMarkup:
    button = InlineKeyboardButton(
        text="🎁 Распаковать подарок на сегодня",
        callback_data=UNPACK_CALLBACK,
    )
    return InlineKeyboardMarkup([[button]])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = build_main_keyboard()

    text = (
        "Привет, любимый! 💌\n\n"
        "Этот бот будет сопровождать тебя с {start} по {end}.\n"
        "Каждый день здесь спрятан маленький подарок: текст, фото или видео.\n\n"
        "Нажимай кнопку «🎁 Распаковать подарок на сегодня», чтобы открывать "
        "по одному сюрпризу в день.\n\n"
        "Всё, что мы уже распаковали, остаётся в чате — можно перечитывать и "
        "пересматривать сколько угодно 🤍"
    ).format(
        start=ADVENT_START.strftime("%d.%m"),
        end=ADVENT_END.strftime("%d.%m"),
    )

    if update.message:
        await update.message.reply_text(text, reply_markup=keyboard)
    elif update.callback_query:
        await update.callback_query.message.reply_text(text, reply_markup=keyboard)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = build_main_keyboard()
    text = (
        "Этот бот создан, чтобы каждый день дарить по одному маленькому сюрпризу 🎁\n\n"
        "1. Нажми «🎁 Распаковать подарок на сегодня».\n"
        "2. Получишь текст, фото или видео.\n"
        "3. Все уже открытые подарки останутся в ленте чата 💫\n\n"
        "Сейчас календарных ограничений нет — можно тестировать в любой день."
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=keyboard)
    elif update.callback_query:
        await update.callback_query.message.reply_text(text, reply_markup=keyboard)


async def handle_unpack_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает нажатие на кнопку «🎁 Распаковать подарок на сегодня».

    В этой версии:
    - не проверяем, наступил ли адвент и закончился ли он;
    - просто определяем индекс по сегодняшней дате (циклически) и отдаём соответствующий день.
    """
    query = update.callback_query
    if not query:
        return

    await query.answer()

    today: date = datetime.now(TZ).date()
    index = get_today_index()

    day_data = ADVENT_DAYS[index]
    media_type = day_data.get("media_type")
    base_text = day_data.get("text", "").strip()
    file_id = day_data.get("file_id")

    text = f"{base_text}\n\n(Сегодня {today.strftime('%d.%m')}, день #{index + 1})"

    if media_type == "photo" and file_id:
        await query.message.reply_photo(photo=file_id, caption=text)
    elif media_type == "video" and file_id:
        await query.message.reply_video(video=file_id, caption=text)
    else:
        await query.message.reply_text(text)

    keyboard = build_main_keyboard()
    await query.message.reply_text("Жду тебя здесь завтра 🤍", reply_markup=keyboard)


def main() -> None:
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError("Нужно задать TELEGRAM_TOKEN в переменных окружения")

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(
        CallbackQueryHandler(handle_unpack_callback, pattern=f"^{UNPACK_CALLBACK}$")
    )

    webhook_url = os.environ.get("WEBHOOK_URL")
    secret_token = os.environ.get("WEBHOOK_SECRET", "") or None
    port = int(os.environ.get("PORT", "8000"))

    if not webhook_url:
        raise RuntimeError(
            "Нужно задать WEBHOOK_URL (например, https://telegram-advent-bot.onrender.com/webhook)"
        )

    logger.info("Запускаю run_webhook на порту %d", port)
    logger.info("WEBHOOK_URL: %s", webhook_url)

    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="webhook",
        webhook_url=webhook_url,
        secret_token=secret_token,
        allowed_updates=["message", "callback_query"],
    )


if __name__ == "__main__":
    main()
