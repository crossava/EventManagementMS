import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/event_db")
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "94.241.138.149:9092,94.241.138.149:9094")
KAFKA_TOPIC_REQUESTS = os.getenv("KAFKA_TOPIC_REQUESTS", "event_requests")
KAFKA_TOPIC_RESPONSES = os.getenv("KAFKA_TOPIC_RESPONSES", "event_responses")
