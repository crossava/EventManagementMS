from datetime import datetime

from bson import ObjectId

from app.core.mongo_config import db
from app.models.chats import Chat, ChatMessage


def get_chat_messages_service(data: dict, action: str):
    chat_id = data.get("chat_id")
    if not chat_id:
        return {"status": "error", "message": "chat_id is required", "action": action}

    chat = db.chats.find_one({"_id": ObjectId(chat_id)})
    if not chat:
        return {
            "action": action,
            "message": {
                "status": "success",
                "messages": []
            }
            }

    return {
        "action": action,
        "message": {
            "status": "success",
            "messages": chat.get("messages", [])
        }
    }


def add_chat_message_service(data: dict, action: str):
    chat_id = data.get("chat_id")
    author = data.get("author")
    message = data.get("message")

    if not all([chat_id, author, message]):
        return {
            "action": action,
            "message": {
                "status": "error",
                "message": "chat_id, author, and message are required"
            }
        }

    new_message = {
        "author": author,
        "message": message,
        "timestamp": datetime.utcnow(),
    }

    # Обновляем чат
    chat = db.chats.find_one({"_id": ObjectId(chat_id)})
    if chat:
        db.chats.update_one(
            {"event_id": chat_id},
            {"$push": {"messages": new_message}}
        )
    else:
        new_chat = Chat(event_id=chat_id, messages=[ChatMessage(**new_message)])
        db.chats.insert_one(new_chat.dict())

    try:
        event = db.events.find_one({"chat_id": chat_id})
    except Exception:
        return {
            "action": action,
            "message": {
                "status": "error",
                "message": "Invalid chat_id format (should be ObjectId)"
            }
        }

    volunteers = event.get("volunteers", []) if event else []
    volunteers = [v for v in volunteers if v != author]
    volunteers.append(event.get("created_by"))

    return {
        "action": action,
        "message": {
            "status": "success",
            "new_message": new_message,
            "forward_to": volunteers
        }
    }
