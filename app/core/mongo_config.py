import os

from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Получаем логин и пароль из .env
username = os.getenv("mongo_username")
password = os.getenv("mongo_password")

# Формируем строку подключения
MONGO_URI = f"mongodb://{username}:{password}@77.232.135.48:27017"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()  # Проверяем соединение
    print("✅ Подключение к MongoDB установлено")
except Exception as e:
    print(f"⚠️ Ошибка подключения к MongoDB: {e}")

db = client["events"]


