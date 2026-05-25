# VoxPop

Учебный Django-проект сервиса вопросов и ответов.

Проект содержит основные страницы сайта:
- список новых вопросов;
- список популярных вопросов;
- список вопросов по тегу;
- страницу одного вопроса со списком ответов;
- форму входа;
- форму регистрации;
- форму редактирования профиля;
- форму создания вопроса.

На текущем этапе данные используются как заглушки и передаются из view в шаблоны.

## Технологии

- Python
- Django
- HTML
- CSS
- Bootstrap
- Docker
- Docker Compose

## Локальный запуск

1. Создать и активировать виртуальное окружение:

```bash
python -m venv .venv
```

Windows PowerShell:

```bash
.\.venv\Scripts\Activate.ps1
```

2. Установить зависимости:

```bash
pip install -r requirements.txt
```

3. Создать файл `.env` на основе примера:

```bash
copy .env.example .env
```

4. Применить миграции:

```bash
python manage.py migrate
```

5. Запустить сервер:

```bash
python manage.py runserver
```

После запуска проект будет доступен по адресу:

```text
http://127.0.0.1:8000/
```

## Запуск через Docker Compose

1. Создать файл `.env` на основе примера:

```bash
copy .env.example .env
```

2. Собрать и запустить контейнер:

```bash
docker compose up --build
```

После запуска проект будет доступен по адресу:

```text
http://127.0.0.1:8000/
```

## Основные маршруты

- `/` — список новых вопросов;
- `/hot/` — список популярных вопросов;
- `/tag/<tag_name>/` — вопросы по тегу;
- `/question/<question_id>/` — страница одного вопроса;
- `/ask/` — форма создания вопроса;
- `/login/` — форма входа;
- `/signup/` — форма регистрации;
- `/profile/` — форма редактирования профиля.

## Структура проекта

```text
application/                  настройки Django-проекта
core/                         приложение для страниц пользователя
questions/                    приложение для страниц вопросов
templates/                    общие шаблоны проекта
questions/static/questions/   статические файлы приложения questions
manage.py                     скрипт управления Django
requirements.txt              зависимости проекта
Dockerfile                    сборка Docker-образа
docker-compose.yml            запуск проекта через Docker Compose
.env.example                  пример переменных окружения
```

## Переменные окружения

Для запуска проекта нужен файл `.env`.

Пример содержимого указан в `.env.example`:

```env
SECRET_KEY=django-secret-key-example
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

Файл `.env` не должен попадать в Git.