# Бот для рекомендации фильмов

Телеграм-бот, который рекомендует фильмы по жанрам.

Выбор жанров происходит с помощью inline-клавиатуры.
Кроме названия фильма также приводится дополнительная информация для удобства пользователя.

## Технологический стек
- Python 3.9
- Aiogram 3.20
- API Кинопоиска (kinopoisk.dev)
- Logging для системного журналирования

Автор [Arina](https://github.com/SprogisArina)

### Как запустить проект:

1. Клонировать репозиторий:

```
git clone git@github.com:SprogisArina/recommendbot.git
cd recommendbot
```

2. Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

- для Windows:

```
source venv/Scripts/activate
```

- для Linux/MacOS:

```
source venv/bin/activate
```

4. Обновить pip и установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

5. Создать файл .env:

```
BOT_TOKEN=токен_тг_бота
API_TOKEN=токен_для доступа_к_api_кинопоиска
```

6. Запустить бота:

```
python bot.py
```
