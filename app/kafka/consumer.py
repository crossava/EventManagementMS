from aiokafka import AIOKafkaConsumer
import asyncio
import json
from app.events.service import EventService
from app.kafka.producer import send_kafka_message
from app.config import KAFKA_BROKERS, KAFKA_TOPIC_REQUESTS


async def consume_kafka_messages():
    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC_REQUESTS,
        bootstrap_servers=KAFKA_BROKERS,
        value_deserializer=lambda v: json.loads(v.decode("utf-8"))
    )
    await consumer.start()
    try:
        async for message in consumer:
            command = message.value
            print(f"📩 Получена команда: {command}")

            # Обрабатываем команду
            response = EventService.handle_command(command)

            # Отправляем ответ в Kafka (event_responses) с request_id
            await send_kafka_message(response)
    finally:
        await consumer.stop()
