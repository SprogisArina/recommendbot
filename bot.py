import logging
import os
import sys
from http import HTTPStatus

import httpx
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv

from constants import GENRES, URL
from exceptions import ResponseStatusException
from utils import make_inline_keyboard

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
    """Получение 10 фильмов по жанру через внешний api"""
    logger.debug('Запрос на внешний api.')
    headers = {
        'X-API-KEY': API_TOKEN,
        'Accept': 'application/json'
    }
    params = {
        'notNullFields': ['name', 'year', 'rating.imdb'],
        'type': 'movie',
        'genres.name': genre
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(URL, headers=headers, params=params)
        response_status = response.status_code
        if response_status != HTTPStatus.OK:
            raise ResponseStatusException(
                f'Статус ответа: {response_status}. Ожидается 200.'
            )
        logger.debug('Успешное завершение получения ответа.')
        return response.json()
    except Exception as e:
        logger.error(f'Ошибка при запросе к API: {e}')


async def check_response(response):
    """Проверка ответа на соответствие документации"""
    logger.debug('Начало проверки ответа API.')
    if not isinstance(response, dict):
        raise TypeError(
            f'Тип данных ответа {type(response)}. Ожидается dict.'
        )

    for key in ('name', 'rating', 'year', 'description'):
        if key not in response:
            raise KeyError(
                f'В отвере нет ключа {key}.'
            )

    logger.debug('Успешное завершение проверки.')


@router.message(Command('start'))
async def start(message: types.Message, state: FSMContext):
    """Начало диалога"""
    await message.answer(
        'Привет, я помогу выбрать фильм!\n'
        'Какой жанр тебя интересует?',
        reply_markup=make_inline_keyboard()
    )
    await state.set_state(MovieForm.choose_genre)


@router.callback_query(MovieForm.choose_genre)
async def handle_genre(callback: types.CallbackQuery, state: FSMContext):
    """Обработка выбора жанра и выдача рекомендаций"""
    try:
        genre = callback.data
        genre_ru = GENRES.get(genre)

        movie_data = await get_movies(genre_ru)
        await check_response(movie_data)

        logger.debug(movie_data)

        rating_imdb = movie_data.get('rating').get('imdb')

        message_text = (
            f'Рекомендую посмотреть в жанре {genre_ru}:\n\n'
            f'{movie_data["name"]}, {movie_data["year"]}\n'
            # f'Страна:{movie_data.get("")}'
            f'★ Рейтинг imdb: {rating_imdb}/10\n\n'
            f'Описание: {movie_data["description"] or "нет описания"}'
        )

        if not (isinstance(callback.message, types.Message)):
            raise TypeError('Сообщение недоступно для редактирования')

        await callback.message.edit_text(text=message_text)
        await callback.answer()
        await state.clear()

    except Exception as e:
        logger.error(f'Ошибка: {e}')
        await callback.answer('Что-то пошло не так...')


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
