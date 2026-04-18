# DRF_project - LMS система на Django REST Framework

## Описание проекта
LMS (Learning Management System) - система для управления курсами и уроками. Проект представляет собой REST API для создания и управления образовательным контентом.

## Функциональность

### 1. Управление курсами
- Создание курса
- Просмотр списка всех курсов
- Просмотр детальной информации о курсе
- Редактирование курса
- Удаление курса

### 2. Управление уроками
- Создание урока с привязкой к курсу
- Просмотр списка всех уроков
- Просмотр детальной информации об уроке
- Редактирование урока
- Удаление урока

## Технологии
- Python 3.13
- Django 6.0.2
- Django REST Framework 3.14.0
- PostgreSQL
- Pillow (для работы с изображениями)

## Установка и запуск

### 1. Клонирование репозитория
git clone <ссылка на репозиторий>
cd DRF_project

### 2. Создание и активация виртуального окружения
python -m venv venv
venv\Scripts\activate  # для Windows
source venv/bin/activate  # для Mac/Linux

### 3. Установка зависимостей
pip install -r requirements.txt

### 4. Настройка базы данных PostgreSQL
Создай базу данных в PostgreSQL:
CREATE DATABASE drf_db;

В файле .env в корне проекта пропиши:
DATABASE_NAME=drf_db
DATABASE_USER=postgres
DATABASE_PASSWORD=твой_пароль
DATABASE_HOST=localhost
DATABASE_PORT=5432
SECRET_KEY=твой_секретный_ключ
DEBUG=True

### 5. Применение миграций
python manage.py makemigrations
python manage.py migrate

### 6. Создание суперпользователя
python manage.py createsuperuser

### 7. Запуск сервера
python manage.py runserver

## API Endpoints

### Курсы
GET /api/courses/ - список всех курсов
POST /api/courses/ - создать новый курс
GET /api/courses/{id}/ - получить курс по ID
PUT /api/courses/{id}/ - полностью обновить курс
PATCH /api/courses/{id}/ - частично обновить курс
DELETE /api/courses/{id}/ - удалить курс

### Уроки
GET /api/lessons/ - список всех уроков
POST /api/lessons/create/ - создать новый урок
GET /api/lessons/{id}/ - получить урок по ID
PUT /api/lessons/{id}/update/ - обновить урок
DELETE /api/lessons/{id}/delete/ - удалить урок

## Примеры запросов

### Создание курса
POST /api/courses/
{
    "title": "Python для начинающих",
    "description": "Полный курс по Python"
}

### Создание урока
POST /api/lessons/create/
{
    "title": "Введение в Python",
    "description": "Первый урок курса",
    "video_link": "https://youtube.com/watch?v=12345",
    "course": 1
}

## Структура проекта
````
DRF_project/
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── courses/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── media/
├── manage.py
├── requirements.txt
└── .env
````

## Модели данных

### Course (Курс)
- title - название курса
- description - описание курса
- preview - изображение (опционально)
- created_at - дата создания
- updated_at - дата обновления

### Lesson (Урок)
- title - название урока
- description - описание урока
- preview - изображение (опционально)
- video_link - ссылка на видео
- course - курс (внешний ключ)
- created_at - дата создания
- updated_at - дата обновления

## Зависимости (requirements.txt)
Django==6.0.2
djangorestframework==3.14.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
Pillow==10.2.0
<!-- homework branch -->