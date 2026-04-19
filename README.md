
# DRF_project - LMS система на Django REST Framework

## Описание проекта

LMS (Learning Management System) - система для управления курсами и уроками. Проект представляет собой REST API для создания и управления образовательным контентом.

## Функциональность

- Регистрация и авторизация пользователей (JWT)
- Создание, редактирование и удаление курсов
- Создание, редактирование и удаление уроков
- Привязка уроков к курсам
- Пагинация списков
- Документация API (Swagger/ReDoc)
- Асинхронные задачи (Celery + Redis)
- Отправка уведомлений в Telegram
- Тесты (покрытие 80%)
- CI/CD (GitHub Actions)

## Технологии

- Python 3.13
- Django 6.0.2
- Django REST Framework 3.16.1
- JWT аутентификация
- PostgreSQL
- Redis (брокер сообщений)
- Celery (отложенные задачи)
- Celery Beat (периодические задачи)
- Telegram Bot API
- Gunicorn (WSGI сервер)
- Nginx (веб-сервер)
- GitHub Actions (CI/CD)

## Установка и запуск (локально)

### 1. Клонирование репозитория
git clone https://github.com/rahimzhanov/DRF_project.git
cd DRF_project

### 2. Создание виртуального окружения
````
python -m venv venv
venv\Scripts\activate  # для Windows
source venv/bin/activate  # для Mac/Linux
````
### 3. Установка зависимостей
pip install -r requirements.txt

### 4. Настройка переменных окружения
````
Создайте файл .env в корне проекта:
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_NAME=drf_db
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
````
### 5. Создание базы данных
В PostgreSQL:
CREATE DATABASE drf_db;

### 6. Применение миграций
python manage.py migrate

### 7. Создание суперпользователя
python manage.py createsuperuser

### 8. Запуск Redis
redis-server

### 9. Запуск Celery Worker
celery -A config worker --loglevel=info --pool=solo

### 10. Запуск Celery Beat
celery -A config beat --loglevel=info

### 11. Запуск Django сервера
python manage.py runserver

## API Эндпоинты

### Пользователи
````
POST /api/users/register/ - регистрация
POST /api/users/token/ - получение JWT токена
POST /api/users/token/refresh/ - обновление токена
````
### Курсы
````
GET /api/courses/ - список всех курсов
POST /api/courses/ - создание курса
GET /api/courses/{id}/ - детали курса
PUT /api/courses/{id}/ - обновление курса
PATCH /api/courses/{id}/ - частичное обновление
DELETE /api/courses/{id}/ - удаление курса
````
### Уроки
````
GET /api/lessons/ - список всех уроков
POST /api/lessons/create/ - создание урока
GET /api/lessons/{id}/ - детали урока
PUT /api/lessons/{id}/update/ - обновление урока
DELETE /api/lessons/{id}/delete/ - удаление урока
````
## Документация API
````
Swagger UI: http://127.0.0.1:8000/swagger/
ReDoc: http://127.0.0.1:8000/redoc/
````
## Развертывание на сервере

### Настройка сервера (Yandex Cloud / Ubuntu)
````
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv nginx postgresql redis-server -y
````
### Клонирование проекта
````
sudo mkdir -p /var/www/drf_project
sudo git clone https://github.com/rahimzhanov/DRF_project.git /var/www/drf_project
````
### Настройка Gunicorn
Создайте файл /etc/systemd/system/gunicorn.service

### Настройка Nginx
Создайте файл /etc/nginx/sites-available/drf_project

## CI/CD (GitHub Actions)

Проект настроен на автоматическое тестирование и деплой при каждом push в ветку main.

Workflow файл: .github/workflows/deploy.yml

Этапы:
1. Установка зависимостей
2. Запуск тестов
3. Деплой на сервер (при успешных тестах)

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
├── .env
└── .github/workflows/      # CI/CD конфигурация
````
## Автор
Аман Рахимжанов

## Лицензия
MIT
