import os

from dotenv import load_dotenv

load_dotenv()

KAFKA_BROKERS = os.getenv("KAFKA_BROKERS")
REQUESTS_TOPIC = os.getenv("KAFKA_TOPIC_REQUESTS")
RESPONSES_TOPIC = os.getenv("KAFKA_TOPIC_RESPONSES")
BROKERS = KAFKA_BROKERS

KAFKA_CONFIG = {
    "bootstrap.servers": BROKERS,
}

CONSUMER_CONFIG = {
    **KAFKA_CONFIG,
    "group.id": "event_ms",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": True,
    "session.timeout.ms": 10000,
}

PRODUCER_CONFIG = {
    **KAFKA_CONFIG,
}

TOPICS = {
    "requests": REQUESTS_TOPIC,
    "responses": RESPONSES_TOPIC
}
