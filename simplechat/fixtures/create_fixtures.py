import os
import sys
import django
import json
from django.contrib.auth.hashers import make_password

# Добавляем корневую директорию проекта в PYTHONPATH
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Устанавливаем переменную окружения DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'simplechat.simplechat.settings')

# Инициализируем Django
django.setup()

from django.contrib.auth import get_user_model
from chat.models import Thread, Message

User = get_user_model()

def create_fixture():
    data = []

    # Создание пользователей
    alice = {
        "model": "auth.user",
        "pk": 1,
        "fields": {
            "username": "alice",
            "password": make_password("test1234"),
            "is_superuser": False,
            "is_staff": False,
            "is_active": True
        }
    }
    data.append(alice)

    bob = {
        "model": "auth.user",
        "pk": 2,
        "fields": {
            "username": "bob",
            "password": make_password("test1234"),
            "is_superuser": False,
            "is_staff": False,
            "is_active": True
        }
    }
    data.append(bob)

    # Создание диалога
    thread = {
        "model": "chat.thread",
        "pk": 1,
        "fields": {
            "participants": [1, 2],
            "created": "2025-06-01T12:00:00Z",
            "updated": "2025-06-01T12:00:00Z"
        }
    }
    data.append(thread)

    # Создание сообщений
    message1 = {
        "model": "chat.message",
        "pk": 1,
        "fields": {
            "thread": 1,
            "sender": 1,
            "text": "Привіт, як справи?",
            "created": "2025-06-01T12:01:00Z",
            "is_read": False
        }
    }
    data.append(message1)

    message2 = {
        "model": "chat.message",
        "pk": 2,
        "fields": {
            "thread": 1,
            "sender": 2,
            "text": "Все добре, дякую! А в тебе?",
            "created": "2025-06-01T12:02:00Z",
            "is_read": False
        }
    }
    data.append(message2)

    # Сохранение в файл
    output_path = os.path.join(BASE_DIR, 'fixtures', 'all_data.json')
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == '__main__':
    create_fixture()