from datetime import date

# Используется только для вычисления цикличного "дня" по текущей дате
ADVENT_START = date(2024, 12, 26)

ADVENT_DAYS = [
    {
        "text": """День 1 💌

12 декабря ты поднимал тропики с колен, а я радовалась
и говорила, что я хакер 😌

Так вот — шёл 10-й день моих попыток сделать чат-бот, и вот он наконец-то заработал!

Я, моё терпение, ChatGPT, Render и GitHub сделали для тебя новогодний адвент 🤍""",
        "media": [
            {"type": "photo", "file_id": "AgACAgIAAxkBAANgaUk0yDGx7IbEvwicBheHBm4uGHsAAjsLaxvKflFKq6ndmEsTD1MBAAMCAAN5AAM2BA"},
        ],
    },
    {
        "text": """День 2 🦀

По этой фотке и не скажешь, что я мастерски владею крабами Массада и
бережно храню в себе Инокентича 😏""",
        "media": [
            {"type": "photo", "file_id": "AgACAgIAAxkBAAOyaUlztu_lDSKmIQIXNPAciLzKqywAAg0OaxvKflFKumfNmzdIvIwBAAMCAAN5AAM2BA"},
        ],
    },
    {
        "text": """День 3 🧡

Не могла оставить тебя без дальневосточной икры в этот Новый год.

Напиши моей сестре и договорись о доставке 🐟
ТГ Ани: @tikhonenchikk""",
        "media": [
            {"type": "photo", "file_id": "AgACAgIAAxkBAAOOaUk84hhMjLDPyVZW-r0G7kH_t6MAAq0LaxvKflFKoyePfBpatZoBAAMCAAN5AAM2BA"},
        ],
    },
    {
        "text": """День 4 ✨

Помнишь, как мы с тобой ровно 4 месяца назад сидели в Зарядье и пели «капалавада»?

Это было лучшее первое свидание.
А на фотке мы ещё не знаем, что вот-вот окажемся в секте 😌""",
        "media": [
            {"type": "photo", "file_id": "AgACAgIAAxkBAAOKaUk75mLJVqtBCDD9PrXFpvYQH0kAAqALaxvKflFKqhzfes1woP0BAAMCAAN5AAM2BA"},
        ],
    },
    {
        "text": """День 5 🍑

Сегодня без лишних слов.
Сегодня — фотка жопы 😌""",
        "media": [
            {"type": "photo", "file_id": "AgACAgIAAxkBAANyaUk5QbehMpRL-R1xH4HeXps4GbIAAoYLaxvKflFKVNWVxcFeR9cBAAMCAAN5AAM2BA"},
        ],
    },
    {
        "text": """День 6 🎄

Если бы ёлка была больше, то подарок я бы спрятала под неё,
а так он лежит в шкафу, рядом с полкой без двери.

С наступающим Новым годом! 🤍""",
        "media": [
            {"type": "photo", "file_id": "AgACAgIAAxkBAAOaaUk-_Ll_6fD2WmRvAXlLsyaUr90AAs0LaxvKflFKKkshEtuacPkBAAMCAAN5AAM2BA"},
        ],
    },
    {
        "text": """День 7 🥗

Вытирай майонез с усов и приходи в себя.
С наступившим Новым годом 😌""",
        "media": [
            {"type": "photo", "file_id": "AgACAgIAAxkBAAN-aUk5wEtL5BUrgFJM1PL16DbuA24AAosLaxvKflFKEZGtUtsBbxsBAAMCAAN5AAM2BA"},
        ],
    },
    {
        "text": """День 8 🔥

Помнишь, как мы 6 часов топили чан и только потом в нём варились и смотрели на звёзды?
А как под тобой скрипел дом? И сколько в этом доме было секса…

Это была хорошая поездка 🤍""",
        "media": [
            {"type": "photo", "file_id": "AgACAgIAAxkBAANqaUk4_DLIbJ6dN6bdc6LSHR5_mVsAAoELaxvKflFKivbAJ4QiN5kBAAMCAAN5AAM2BA"},
            {"type": "photo", "file_id": "AgACAgIAAxkBAANuaUk5Gm_TIfAAAbwmEdztYdzyEeSgAAKFC2sbyn5RSog3PwkXE1GkAQADAgADeQADNgQ"},
        ],
    },
    {
        "text": """День 9 🌲

Помнишь, как мы много болтали, смеялись, ели коврижку, как ты вылетал из трубы,
как я лежала у тебя на коленях и смотрела в небо?

Фотка из Зарайска 🤍""",
        "media": [
            {"type": "video", "file_id": "BAACAgIAAxkBAAO6aUl36tm6r1Y40ytL1VvxIXsuPXwAAlCQAALKflFKSQozhPOw7k42BA"},
        ],
    },
    {
        "text": """День 10 🎤

Чуть не забыла, что ты рэпер 😌""",
        "media": [
            {"type": "video", "file_id": "BAACAgIAAxkBAAOGaUk7noDWIZhEOloy4qMAAce9C8jzAAKuiQACyn5RSrKdkGzlO53NNgQ"},
        ],
    },
    {
        "text": """День 11 🔞

Тебе доступны 5 нюдсов в любой момент 😏""",
        "media": [
            {"type": "photo", "file_id": "AgACAgIAAxkBAAN2aUk5WJaqfLu-WUvv0lqpttprCXwAAogLaxvKflFKbPn901BSE5wBAAMCAAN5AAM2BA"},
        ],
    },
    {
        "text": """День 12 💤

Один здесь отдыхаешь?""",
        "media": [
            {"type": "photo", "file_id": "AgACAgIAAxkBAAO2aUl2Var13J_1nJLPToje7-wOq_0AAi8OaxvKflFKLJizK5b2x74BAAMCAAN5AAM2BA"},
        ],
    },
    {
        "text": """День 13 📊

Немного статистики про нас:

— мы обменялись более чем 957 голосовыми и кружочками
— отправили друг другу более 650 фото и видео
— мы написали друг другу более 10 000 сообщений
— обменялись более 300 рислами

И при этом у нас всего 3 селфи (упущение какое-то) 😌""",
        "media": [
            {"type": "photo", "file_id": "AgACAgIAAxkBAAOeaUlyEowB5Ksq4A8XAAGsKrsP2K5DAALsDWsbyn5RSt1fICmrD-L-AQADAgADeQADNgQ"},
        ],
    },
    {
        "text": """День 14 🎂

Помнишь, как мы отмечали твой день рождения в Королёве?

Мой шок от летящего торта, знакомство с мамой, теннисный мяч, летящий из окна твоей квартиры 😅

Это было познавательно и мне было очень ценно, что ты позвал меня с собой 🤍""",
        "media": [
            {"type": "photo", "file_id": "AgACAgIAAxkBAANmaUk4ugbkfa4BSuCk-AeIZQGGyXoAAn0LaxvKflFKgg-9m8j3RwIBAAMCAAN5AAM2BA"},
            {"type": "photo", "file_id": "AgACAgIAAxkBAAOuaUlzDyl0R0odtTJ7nUqQgemxQOUAAgMOaxvKflFKSCZ8gIejNLgBAAMCAAN5AAM2BA"},
            {"type": "photo", "file_id": "AgACAgIAAxkBAAOqaUlzCHYkJ2pmqjjUmEAU5vf6J1sAAgIOaxvKflFKYReUohJRwScBAAMCAAN5AAM2BA"},
            {"type": "photo", "file_id": "AgACAgIAAxkBAAOmaUlzAf6Kgq8I6MZqjOqS5qzJKysAAgEOaxvKflFKnngLv9jSzrQBAAMCAAN5AAM2BA"},
            {"type": "photo", "file_id": "AgACAgIAAxkBAAOiaUly-uqerOFWgmYZdgRFZh6rByUAAvwNaxvKflFKSl0QugzzqAcBAAMCAAN5AAM2BA"},
        ],
    },
    {
        "text": """День 15 🧘‍♀️

Нужно не забывать радовать друг друга и не забывать,
как сильно тебя бесил голос той женщины в медитации 😌""",
        "media": [
            {"type": "video", "file_id": "BAACAgIAAxkBAAOSaUk9Eb1iGttpIdX8j050KxudQXEAAsGJAALKflFKFegwm6NFPHE2BA"},
        ],
    },
    {
        "text": """День 16 🍷

Уже завтра будет хамон, сыр, портвейн.
Хотя тебе, конечно, больше подойдёт борщ с салом и лагер 🤍""",
        "media": [
            {"type": "video", "file_id": "BAACAgIAAxkBAAOWaUk9cFThjYH2N4OuWxmAQUVD13UAAsqJAALKflFKT56ge6iwqQc2BA"},
        ],
    },
]
