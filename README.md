# 2026-VK-EDU-WEB-11-Solovev-R
# VoxPop

Учебный проект по вёрстке сервиса вопросов и ответов для домашнего задания №1.

## Описание проекта

VoxPop — это статический макет сайта вопросов и ответов.  
Проект выполнен с использованием HTML, CSS и Bootstrap с локальным подключением всех статических файлов.

## Некоторые ссылки

Для оформления проекта были позаимствованы вопросы и ответы с сайта "Ответы Mail.ru": 
https://otvet.mail.ru/question/269583256,
https://otvet.mail.ru/question/269583268,
https://otvet.mail.ru/question/269583196,
а также картинки из интернета, сохраненные в папке public/static/img

## Как открыть проект

Так как проект на данном этапе является статической вёрсткой, сервер запускать не требуется.

Чтобы открыть проект:

1. перейти в папку `public/`
2. открыть файл `index.html` в браузере

Также страницы можно открывать напрямую.

## Страницы проекта

- `index.html` — список вопросов
- `question.html` — страница одного вопроса и ответов
- `ask.html` — форма добавления вопроса
- `login.html` — форма входа
- `signup.html` — форма регистрации
- `profile.html` — страница профиля пользователя
- `base.html` — базовый шаблон общей структуры страницы

## Структура проекта

```text
public/
    base.html
    index.html
    question.html
    ask.html
    login.html
    signup.html
    profile.html
    static/
        css/
            bootstrap.min.css
            style.css
        js/
            bootstrap.bundle.min.js
        img/
            logo.png
            favicon.png
            anime1.jpg
            anime2.jpg
            anime3.jpg
            anime4.jpg
            anime5.jpg
