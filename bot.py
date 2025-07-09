import logging
import os
import sys

import requests
from aiogram import Bot, Dispatcher, executor, Router, types
from aiogram.filters import Text
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv

from .constants import GENRES, URL
from .utils import make_inline_keyboard

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN', '')
API_TOKEN = os.getenv('API_TOKEN', '')

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler = logging.StreamHandler(stream=sys.stdout)
logger.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(handler)


class MovieForm(StatesGroup):
    choose_genre = State()


async def get_movies(genre):
    """Получение 5 фильмов по жанру через внешний api"""
    headers = {'X-API-KEY': API_TOKEN}
    params = {
        "genres.name": genre,
        "limit": 5,
        "selectFields": ["name", "year", "rating.kp"]
    }
    try:
        response = requests.get(URL, headers=headers, params=params)
        return response.json()
    except Exception as e:
        logging.error(f'Ошибка при запросе к API {e}')
        return []


@router.message(commands=['start'])
async def start(message: types.Message, state: FSMContext):
    """Начало диалога"""
    await message.answer(
        'Привет, я помогу выбрать фильм!'
        'Какие жанры тебя интересуют?',
        reply_markup=make_inline_keyboard()
    )
    await state.set_state(MovieForm.choose_genre)


@router.callback_query(MovieForm.choose_genre)
async def handle_genre(callback: types.CallbackQuery, state: FSMContext):
    """Обработка выбора жанра"""

    genre = callback.data
    genre_ru = GENRES.get(genre)

    movies = get_movies(genre)

    message_text = f'Рекомендую посмотреть в жанре {genre_ru}:\n\n'

    for idx, movie in enumerate(movies):
        rating = movie.get('rating')
        message_text += (
            f'{idx}. {movie["name"]}\n'
            f'★ Рейтинг: {rating}/10\n\n'
        )

    await callback.message.edit_text(
        text=message_text
    )
    await state.clear()
