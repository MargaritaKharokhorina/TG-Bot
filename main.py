from aiogram import Bot, Dispatcher, executor, types
import requests
import os 
import json
#from aiogram.types import ParseMode, Message
from aiogram.utils.markdown import text, bold, code
import re 
import random
from dotenv import load_dotenv
load_dotenv()
#import pprint

HEADERS = {
    "X-API-KEY": os.environ.get("KINOPOISK_API_KEY"),
    "accept": "application/json",
}

#PARAMS = {'page': 1, 'limit': 1, 'genres.name': 'комедия', 'selectFields[]': ['name','poster.url', 'watchability.items.url']}
#PARAMS = {'page': 1, 'limit': 1, 'genres.name': 'комедия', 'selectFields': 'watchability.items.url', 'selectFields': 'poster.url', 'selectFields': 'name'}

PARAMS = [('page', 1), ('limit',5), ('genres.name', 'комедия'), ('selectFields', 'watchability.items.url'), ('selectFields', 'watchability.items.name'), ('selectFields', 'poster.url'), ('selectFields', 'name'), ('selectFields', 'description')]

#print(os.environ.get("TELEGRAM_API_TOKEN"))
bot = Bot(token=os.environ.get("TELEGRAM_API_TOKEN"))
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])

async def send_welcome(message: types.Message):
    await bot.send_message(message.chat.id, 'Привет, {0.first_name}!\nЯ бот, который поможет тебе выбрать фильм на вечер.\nВыбери в меню жанр 🎬'.format(message.from_user), reply_markup=markup)

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
buttons = ['🍿 Комедии', '💔 Мелодрама']
markup.add(*buttons)



#markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#item1 = types.KeyboardButton('🍿 Комедии')
#item2 = types.KeyboardButton('💔 Мелодрама')
#item3 = types.KeyboardButton('🤍 Драма')
#item4 = types.KeyboardButton('🔍 Детектив')
#item5 = types.KeyboardButton('🤫 Триллер')
#item6 = types.KeyboardButton('😱 Ужасы')
#item7 = types.KeyboardButton('💣 Боевик')
#item8 = types.KeyboardButton('☄️ Фантастика')
#item9 = types.KeyboardButton('👀 Приключения')
#item10 = types.KeyboardButton('⏳ Исторические')
#item11 = types.KeyboardButton('📝 Документальные')
#item12 = types.KeyboardButton('🏆 Спортивные')
#item13 = types.KeyboardButton('🎥 Артхаус')
#item14 = types.KeyboardButton('🎵 Мюзикл')
#item15 = types.KeyboardButton('🧁 Мультфильмы')

#markup.add(item1, item2, item3, item4, item5, item6, item7, item8, item9, item10, item11, item12, item13, item14, item15)

def get_random_movie(genre):
    HEADERS = {
        "X-API-KEY": os.environ.get("KINOPOISK_API_KEY"),
        "accept": "application/json",
    }

    PARAMS = [
        ("page", 1),
        ("limit", 1),
        ("watchability.items", "!null"),
        ("name", "!null"),
        ("description", "!null"),
        ("rating.kp", "5"),
        ("genres.name", genre),
        ("selectFields", "name"),
    ]

    response = requests.get(
        "https://api.kinopoisk.dev/v1/movie",
        params=PARAMS,
        headers=HEADERS,
    )
    movies = response.json()
    total_pages = movies["total"] // movies["limit"] + (
        1 if movies["total"] % movies["limit"] > 0 else 0
    )

    random_page = random.randint(1, total_pages)

    PARAMS_FIELDS = [
        ("page", random_page),
        ("limit", 1),
        ("genres.name", "комедия"),
        ("watchability.items", "!null"),
        ("name", "!null"),
        ("description", "!null"),
        ("rating.kp", "5"),
        ("selectFields", "watchability.items.url"),
        ("selectFields", "watchability.items.name"),
        ("selectFields", "name"),
        ("selectFields", "description"),
        ("selectFields", "year"),
        ("selectFields", "rating.kp"),
    ]

    response1 = requests.get(
        "https://api.kinopoisk.dev/v1/movie",
        params=PARAMS_FIELDS,
        headers=HEADERS,
    )
    movies = response1.json()
    print(movies)
    return movies["docs"][0]


@dp.message_handler(content_types=["text"])
async def answer(message: types.Message):
    if message.chat.type == "private":
        if message.text == "🍿 Комедии":
            film = get_random_movie("комедия")
            name = film["name"]
            year = str(film["year"])
            rating = str(film["rating"]["kp"])
            description = film["description"]
            #description = "«О, Боже!!!!... Невероятно!!!... Я верила - Снежный Человек существует. Он есть!!!...Он похитил меня!!! Он добрый!!!... Мы идем знакомиться с его родителями!!!... Мне кажется,  я ему нравлюсь. Ваня - дай грибочков!!!» - вот так начинается необычайный видеорепортаж, записанный на камеру, которую случайно нашли в лесу охотники. Что это -  сенсация??? Русский Кинг-Конг??? А может быть пронзительная история  любви??? Полгода назад, где-то на Урале, в тайге, пропала тележурналистика Лариса Дебомонова. Где она  - никому не известно. Давайте досмотрим  до конца этот полуторачасовой сюжет. Возможно, мы узнаем, что же с ней случилось."
            links = film["watchability"]["items"]
            linksFiltered = []
            for link in links:
                if link not in linksFiltered:
                    linksFiltered.append(link)
            linkUrls = list(
                map(lambda l: f'[{l["name"]}]({l["url"]})', linksFiltered)
            )  #TODOfilter repetitive keys

            linkUrlsJoined = "\n".join(linkUrls)
            print(links, linkUrls, linkUrlsJoined)
            msg = f"*{re.escape(name)}, {re.escape(year)}*\n*Рейтинг КиноПоиска: {re.escape(rating)}*\n{re.escape(description)}\n*Просмотр*\:\n{linkUrlsJoined}"
            await message.answer(msg, parse_mode="MarkdownV2")
            #await message.answer(movie)
            #name = "1\\+\\1"
            #md = "*Название фильма:* "
            #fin = ''.join([md, name])
            #msg = f"*Название фильма:* {name.encode('unicode_escape')}"
            #msg = f"*Название фильма:* {re.escape(name)}"
            #await message.answer("Hello, *world*\!", parse_mode= "MarkdownV2")!!!!+
            #await message.answer(msg, parse_mode= "MarkdownV2")

            

#@dp.message_handler(content_types=['text'])

#def 

#async def answer(message: types.Message):
    #await message.answer(message.text)      this is echo

if __name__ == '__main__':
   executor.start_polling(dp, skip_updates=True)

bot.polling(non_stop = True)