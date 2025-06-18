import json
from datetime import datetime

from bson import ObjectId

from app.utils.kafka_helper import get_producer
from app.core.kafka_config import TOPICS


def default_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def send_response(request_id, message):
    producer = get_producer()

    forward_to = message.get("message", {}).get("forward_to")
    only_forward = message.get("message", {}).get("only_forward")

    response_message = {
        "request_id": request_id,
        "message": message
    }

    if forward_to:
        response_message["forward_to"] = forward_to

    if only_forward is not None:
        response_message["only_forward"] = only_forward

    producer.produce(
        TOPICS["responses"],
        key="user",
        value=json.dumps(response_message, cls=MongoJSONEncoder)
    )

    producer.flush()

    # Для логирования покажем все, что отправили
    print(f"✅ Ответ отправлен в {TOPICS['responses']}:\n{json.dumps(response_message, indent=2, cls=MongoJSONEncoder)}")
    if forward_to:
        for target_id in forward_to:
            print(f"↪️ Также переслано пользователю {target_id}:\n{json.dumps(message, indent=2, cls=MongoJSONEncoder)}")


