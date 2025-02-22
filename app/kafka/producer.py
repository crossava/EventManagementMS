from aiokafka import AIOKafkaProducer
import json
import asyncio
from app.config import KAFKA_BROKERS, KAFKA_TOPIC_RESPONSES


async def send_kafka_message(message):
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BROKERS)
    await producer.start()
    try:
        await producer.send_and_wait(KAFKA_TOPIC_RESPONSES, json.dumps(message).encode("utf-8"))
    finally:
        await producer.stop()
