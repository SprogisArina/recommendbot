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
    """Получение 5 фильмов по жанру через внешний api"""
    logger.debug('Запрос на внешний api.')
    headers = {
        'X-API-KEY': API_TOKEN,
        'accept': 'application/json'
    }
    params = {
        'page': 1,
        'limit': 5,
        'selectFields': 'name',
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
        return []


async def check_response(response):
    """Проверка ответа на соответствие документации"""
    logger.debug('Начало проверки ответа API.')
    if not isinstance(response, dict):
        raise TypeError(
            f'Тип данных ответа {type(response)}. Ожидается dict.'
        )

    if 'docs' not in response:
        raise KeyError('В ответе нет ключа "docs".')

    if not isinstance(response['docs'], list):
        raise TypeError(
            f'Тип данных ответа {type(response["docs"])}. Ожидается list.'
        )

    logger.debug('Успешное завершение проверки.')


@router.message(Command('start'))
async def start(message: types.Message, state: FSMContext):
    """Начало диалога"""
    await message.answer(
        'Привет, я помогу выбрать фильм!'
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

        movies = await get_movies(genre)
        await check_response(movies)

        message_text = f'Рекомендую посмотреть в жанре {genre_ru}:\n\n'

        for idx, movie in enumerate(movies['docs'], 1):
            # rating = movie.get('rating', {}).get('kp')
            message_text += (
                f'{idx}. {movie["name"]}, {movie["year"]}\n'
                # f'★ Рейтинг: {rating}/10\n\n'
            )

        if not (isinstance(callback.message, types.Message)):
            raise TypeError('Сообщение недоступно для редактированиияю')

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
