from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.types.inline_keyboard_button import InlineKeyboardButton

from constants import GENRES


def make_inline_keyboard():
    """Клавиатура с жанрами"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=genre, callback_data=f'{key}'
            ) for key, genre in GENRES.items()]
        ])


def format_countries(countries):
    if not countries:
        return 'не указаны'

    countries_names = []

    for country in countries:
        name = country.get('name')
        if name:
            countries_names.append(name)

    if not countries_names:
        return 'не указаны'

    return ', '.join(countries_names)
