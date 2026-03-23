# config/celery.py
import os
import sys
from pathlib import Path
from celery import Celery

# Добавляем корень проекта в PATH
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Загружаем .env вручную
from dotenv import load_dotenv
env_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=env_path)

# Принудительно устанавливаем SECRET_KEY для Django
if not os.getenv('SECRET_KEY'):
    # Если нет в .env, используем временный (только для разработки)
    os.environ['SECRET_KEY'] = 'django-insecure-temporary-key-for-celery'

# Устанавливаем настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Создаем экземпляр Celery
app = Celery('config')

# Загружаем настройки из Django settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находим задачи в приложениях
app.autodiscover_tasks()