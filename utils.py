from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from constants import GENRES


def make_inline_keyboard():
    """Клавиатура с жанрами"""
    builder = InlineKeyboardBuilder()
    builder.add(*[InlineKeyboardButton(
        text=genre, callback_data=f'{slug}'
        ) for slug, genre in GENRES.items()])
    builder.adjust(3)
    return builder.as_markup()


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
