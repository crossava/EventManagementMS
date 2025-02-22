import asyncio
from app.kafka.consumer import consume_kafka_messages
from mongoengine import connect
from app.config import MONGO_URI

if __name__ == "__main__":
    print("🚀 Event Management Service запущен...")

    # Подключаем MongoDB
    connect(host=MONGO_URI)

    # Запускаем Kafka-консьюмер
    asyncio.run(consume_kafka_messages())
