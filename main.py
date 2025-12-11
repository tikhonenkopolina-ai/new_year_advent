#!/usr/bin/env python3
"""
Главный файл бота-адвента для Telegram.

Функции:
- принимает вебхуки от Telegram через HTTP (aiohttp);
- передаёт апдейты в python-telegram-bot;
- обрабатывает команды /start и /help;
- показывает кнопку «Распаковать подарок на сегодня»;
- по нажатию на кнопку проверяет текущую дату и отдаёт контент для этого дня;
- все уже отправленные сообщения остаются в чате (лента воспоминаний).

Запускается как обычный web-сервис (для Render.com или любого другого хостинга).
"""

import os
import logging
from datetime import datetime, date
from zoneinfo import ZoneInfo

from aiohttp import web
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

# Импортируем данные адвента (даты и контент по дням)
from advent_content import ADVENT_DAYS, ADVENT_START, ADVENT_END

# -------------------- НАСТРОЙКА ЛОГИРОВАНИЯ --------------------

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# -------------------- НАСТРОЙКИ ЧАСОВОГО ПОЯСА --------------------

# Часовой пояс можно задать через переменную окружения TZ_NAME
# (по умолчанию — Europe/Amsterdam)
TZ_NAME = os.getenv("TZ_NAME", "Europe/Amsterdam")
TZ = ZoneInfo(TZ_NAME)

# callback_data для inline-кнопки
UNPACK_CALLBACK = "UNPACK_TODAY"


# -------------------- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ --------------------

def get_today_index() -> int | None:
    """
    Возвращает индекс дня адвента (0..len(ADVENT_DAYS)-1), если сегодня входит
    в диапазон адвента, иначе None.

    Логика:
    - Берём сегодняшнюю дату в нужном часовом поясе.
    - Если она меньше даты начала или больше даты конца — возвращаем None.
    - Иначе считаем разницу в днях от даты старта и получаем индекс.
    """
    today: date = datetime.now(TZ).date()

    if today < ADVENT_START or today > ADVENT_END:
        return None

    delta_days = (today - ADVENT_START).days
    if 0 <= delta_days < len(ADVENT_DAYS):
        return delta_days

    return None


def build_main_keyboard() -> InlineKeyboardMarkup:
    """
    Создаёт главную inline-клавиатуру с кнопкой «Распаковать подарок на сегодня».
    """
    button = InlineKeyboardButton(
        text="🎁 Распаковать подарок на сегодня",
        callback_data=UNPACK_CALLBACK,
    )
    return InlineKeyboardMarkup([[button]])


# -------------------- ХЕНДЛЕРЫ КОМАНД --------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает команду /start.
    Показывает приветственный текст и кнопку для распаковки подарка.
    """
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
        # На случай, если кто-то вызовет /start из callback (редко, но бывает)
        await update.callback_query.message.reply_text(text, reply_markup=keyboard)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает команду /help.
    Кратко объясняет, как пользоваться ботом.
    """
    keyboard = build_main_keyboard()
    text = (
        "Этот бот создан, чтобы каждый день в период адвента "
        "дарить по одному маленькому сюрпризу 🎁\n\n"
        "1. Нажми «🎁 Распаковать подарок на сегодня».\n"
        "2. Если нужный день наступил — получишь текст, фото или видео.\n"
        "3. Все уже открытые подарки останутся в ленте чата 💫\n\n"
        "Если день ещё не наступил или адвент уже закончился — "
        "бот честно сообщит об этом."
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=keyboard)
    elif update.callback_query:
        await update.callback_query.message.reply_text(text, reply_markup=keyboard)


# -------------------- ХЕНДЛЕР КНОПКИ «РАСПАКОВКА» --------------------

async def handle_unpack_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает нажатие на кнопку «🎁 Распаковать подарок на сегодня».

    Логика:
    1. Проверяем текущую дату:
       - если до начала адвента — говорим «ещё рано»;
       - если после конца — говорим, что адвент завершён;
    2. Если дата внутри диапазона:
       - определяем индекс дня;
       - берём соответствующий объект из ADVENT_DAYS;
       - в зависимости от типа медиа отправляем текст, фото или видео;
       - затем снова показываем кнопку на будущее (на следующий день).
    """
    query = update.callback_query
    if not query:
        return

    await query.answer()  # закрываем «часики» у кнопки

    today: date = datetime.now(TZ).date()

    # 1. Проверка — ещё не началось
    if today < ADVENT_START:
        await query.message.reply_text(
            "Ещё рано распаковывать 🎁\n\n"
            f"Наш адвент начинается {ADVENT_START.strftime('%d.%m')}.\n"
            "Обещаю, ожидание того стоит 🤍"
        )
        return

    # 2. Проверка — уже закончилось
    if today > ADVENT_END:
        await query.message.reply_text(
            "Наш адвент уже закончился 🎆\n\n"
            "Но все подарки остались в этом чате — "
            "можно пролистать вверх и пересматривать, когда захочется 🥺🤍"
        )
        return

    # 3. Сегодня внутри диапазона — получаем индекс
    index = get_today_index()
    if index is None:
        await query.message.reply_text(
            "Кажется, что-то не так с датой…\n"
            "Попробуй позже или напиши моей создательнице 🙈"
        )
        return

    # 4. Достаём данные для сегодняшнего дня
    day_data = ADVENT_DAYS[index]
    media_type = day_data.get("media_type")
    base_text = day_data.get("text", "").strip()
    file_id = day_data.get("file_id")

    text = f"{base_text}\n\n(Сегодня {today.strftime('%d.%m')})"

    # 5. Отправляем контент
    if media_type == "photo" and file_id:
        await query.message.reply_photo(photo=file_id, caption=text)
    elif media_type == "video" and file_id:
        await query.message.reply_video(video=file_id, caption=text)
    else:
        # Текстовый день или файл ещё не настроен
        await query.message.reply_text(text)

    # 6. Повторно показываем кнопку, чтобы завтра можно было снова нажать
    keyboard = build_main_keyboard()
    await query.message.reply_text("Жду тебя здесь завтра 🤍", reply_markup=keyboard)


# -------------------- ВЕБХУК-СЕРВЕР (AIOHTTP) --------------------

async def handle_root(request: web.Request) -> web.Response:
    """
    Простой GET-обработчик для корня сервиса.
    Удобно для проверки, что сервис запущен (Render health-check и т.п.).
    """
    return web.Response(text="Telegram Advent Bot is running.")


async def handle_webhook(request: web.Request) -> web.Response:
    """
    Обработчик POST-запроса от Telegram на путь /webhook.

    Логика:
    - читаем JSON из тела запроса;
    - превращаем его в объект Update;
    - передаём в Application для обработки хендлерами.
    """
    app: Application = request.app["bot_app"]

    try:
        data = await request.json()
    except Exception:
        logger.exception("Не удалось прочитать JSON от Telegram")
        return web.Response(status=400, text="bad request")

    update = Update.de_json(data, app.bot)

    # Обрабатываем апдейт внутри PTB-приложения
    await app.process_update(update)

    return web.Response(text="ok")


async def on_startup(web_app: web.Application) -> None:
    """
    Хук, который вызывается при старте aiohttp-приложения.

    Здесь мы:
    - инициализируем приложение python-telegram-bot (Application.initialize);
    - читаем WEBHOOK_URL из переменных окружения;
    - регистрируем вебхук в Telegram (bot.set_webhook).
    """
    bot_app: Application = web_app["bot_app"]

    # ОБЯЗАТЕЛЬНО: инициализируем приложение PTB перед process_update
    await bot_app.initialize()

    webhook_url = os.environ.get("WEBHOOK_URL")
    secret_token = os.environ.get("WEBHOOK_SECRET", "")

    if not webhook_url:
        logger.warning(
            "WEBHOOK_URL не задан — вебхук не будет установлен автоматически. "
            "Установи его вручную через BotFather или окружение."
        )
        return

    logger.info("Устанавливаю вебхук на %s", webhook_url)
    await bot_app.bot.set_webhook(
        url=webhook_url,
        secret_token=secret_token or None,
        allowed_updates=["message", "callback_query"],
    )


def main() -> None:
    """
    Точка входа в приложение.

    Логика:
    1. Читаем токен бота из переменной окружения TELEGRAM_TOKEN.
    2. Создаём Application из python-telegram-bot.
    3. Регистрируем хендлеры команд и callback-кнопок.
    4. Создаём aiohttp-приложение, привязываем к нему Application.
    5. Настраиваем маршруты:
       - GET /         — health-check
       - POST /webhook — приём апдейтов от Telegram
    6. Запускаем web-сервер на указанном порту (по умолчанию 8000).
    """
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError("Нужно задать TELEGRAM_TOKEN в переменных окружения")

    # 1. Создаём PTB-приложение
    application = Application.builder().token(token).build()

    # 2. Регистрируем хендлеры
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(
        CallbackQueryHandler(handle_unpack_callback, pattern=f"^{UNPACK_CALLBACK}$")
    )

    # 3. Создаём aiohttp-приложение
    web_app = web.Application()
    web_app["bot_app"] = application

    # маршруты:
    #   GET  /        -> handle_root
    #   POST /webhook -> handle_webhook
    web_app.router.add_get("/", handle_root)
    web_app.router.add_post("/webhook", handle_webhook)

    # Регистрируем хук на старт сервера
    web_app.on_startup.append(on_startup)

    port = int(os.environ.get("PORT", "8000"))
    logger.info("Starting web server on port %d", port)

    # Запускаем aiohttp-приложение (блокирующий вызов)
    web.run_app(web_app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
