import json

from app.utils.kafka_helper import get_consumer
from app.cli.producer import *
from app.core.kafka_config import TOPICS
from pydantic import ValidationError
from app.services.event_service import *

TOPIC_LIST = [TOPICS["requests"]]


def process_new_message(action, request_id, message):
    try:
        print(f"📩 Обработка нового сообщения: {json.dumps(message, indent=2)}")

        if "body" in message:
            message = message["body"]

        print("message:", message)

        if action == "create_event":
            result = create_event_service(message["data"], action)
            send_response(request_id, result)
        elif action == "update_event":
            result = update_event_service(message["data"], action)
            send_response(request_id, result)
        elif action == "delete_event":
            result = delete_event_service(message["data"], action)
            send_response(request_id, result)
        elif action == "register_volunteer":
            result = register_volunteer_service(message["data"], action)
            send_response(request_id, result)
        elif action == "unregister_volunteer":
            result = unregister_volunteer_service(message["data"], action)
            send_response(request_id, result)
        elif action == "get_upcoming_events":
            result = get_upcoming_events_service(message.get("data", {}), action)
            send_response(request_id, result)
        elif action == "get_user_events":
            result = get_user_events_service(message.get("data", {}), action)
            send_response(request_id, result)


    except ValidationError as ve:
        print(f"⚠️ Ошибка валидации данных: {ve}")
    except Exception as e:
        print(f"⚠️ Ошибка обработки сообщения: {str(e)}")


def consume_messages():
    consumer = get_consumer(TOPIC_LIST)

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"⚠️ Ошибка Kafka Consumer: {msg.error()}")
                continue

            message = json.loads(msg.value().decode("utf-8"))
            print(f"📩 Получено сообщение из {msg.topic()}:\n{json.dumps(message, indent=2)}")

            request_id = message.get("request_id")
            action = message["message"].get("action")

            process_new_message(action, request_id, message["message"])

    except KeyboardInterrupt:
        print("⏹️ Остановка Consumer")
    finally:
        consumer.close()
