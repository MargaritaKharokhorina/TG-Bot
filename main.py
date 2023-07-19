from aiogram import Bot, Dispatcher, executor, types
import requests
import os 
from aiogram.utils.markdown import text, bold, code
#import re 
import random
from aiogram import md
from dotenv import load_dotenv
load_dotenv()


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
def get_genres_list():
    PARAMS = [("field", "genres.name")]
    response = requests.get(
        "https://api.kinopoisk.dev/v1/movie/possible-values-by-field",
        params=PARAMS,
        headers=HEADERS,
    )
    genres_list = response.json()
    return genres_list

genres = get_genres_list()
buttons = map(lambda l: l["name"], genres)
#buttons = list(map(str.title, buttons))
#for elem in buttons:
    #print(elem)
markup.add(*buttons)



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
        ("rating.kp", "5-10"),
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
        ("genres.name", genre),
        ("watchability.items", "!null"),
        ("name", "!null"),
        ("description", "!null"),
        ("rating.kp", "5-10"),
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
    #print(movies)
    return movies["docs"][0]


@dp.message_handler(content_types=["text"])
async def answer(message: types.Message):
    if message.chat.type == "private":
        #print(genres)
        film = get_random_movie(message.text)
        name = md.escape_md(film["name"])
        year = md.escape_md(str(film["year"]))
        rating = md.escape_md(round(film["rating"]["kp"], 1))
        description = md.escape_md(film["description"])
        links = film["watchability"]["items"]
        linksFiltered = []
        for link in links:
                if link not in linksFiltered:
                    linksFiltered.append(link)
        linkUrls = list(map(lambda l: f'[{md.escape_md(l["name"])}]({l["url"]})', linksFiltered))
        linkUrlsJoined = "\n".join(linkUrls)

        msg = f"*{(name)}, {year}*\n*Рейтинг КиноПоиска: {(rating)}*\n{(description)}\n*Просмотр*\:\n{linkUrlsJoined}"
        try:
                await message.answer(msg, parse_mode= "MarkdownV2")
        except Exception as inst:
                await message.answer(
                    "Кина не будет", parse_mode= "MarkdownV2"

                )
                print('message', msg, "\nlinks", linkUrlsJoined)
                print(inst)
                raise


if __name__ == '__main__':
   executor.start_polling(dp, skip_updates=True)

bot.polling(non_stop = True)