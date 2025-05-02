import json

from app.utils.kafka_helper import get_producer
from app.core.kafka_config import TOPICS


def send_response(request_id, message):
    producer = get_producer()

    response_message = {
        "request_id": request_id,
        "message": message
    }

    producer.produce(TOPICS["responses"], key="user", value=json.dumps(response_message))
    producer.flush()
    print(f"✅ Ответ отправлен в {TOPICS['responses']}:\n{json.dumps(response_message, indent=2)}")

