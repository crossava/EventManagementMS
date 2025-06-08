from datetime import datetime

from bson import ObjectId

from app.models.events import Event, EventUpdate
from pydantic import ValidationError, HttpUrl
from app.core.mongo_config import db
from copy import deepcopy
from bson import ObjectId, errors


def serialize_event(event: dict) -> dict:
    event["_id"] = str(event["_id"])

    if "created_at" in event and isinstance(event["created_at"], datetime):
        event["created_at"] = event["created_at"].isoformat()

    if "updated_at" in event and isinstance(event["updated_at"], datetime):
        event["updated_at"] = event["updated_at"].isoformat()

    if "start_datetime" in event and isinstance(event["start_datetime"], datetime):
        event["start_datetime"] = event["start_datetime"].isoformat()

    if "end_datetime" in event and isinstance(event.get("end_datetime"), datetime):
        event["end_datetime"] = event["end_datetime"].isoformat()

    # Преобразуем ObjectId внутри volunteers если есть
    if "volunteers" in event and isinstance(event["volunteers"], list):
        event["volunteers"] = [str(v) for v in event["volunteers"]]

    return event


def serialize_for_mongo(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, HttpUrl):
        return str(obj)
    return obj  # datetime и другие типы оставить как есть


def create_event_service(event_data: dict, action: str):
    try:
        event = Event(**event_data)
        print(f"✅ Событие успешно создано: {event}")

        event_dict = event.dict()  # не использовать mode="json"
        event_dict.setdefault("status", "Новое")

        now = datetime.utcnow()
        event_dict["created_at"] = now
        event_dict["updated_at"] = now
        event_dict["created_by"] = event_data.get("created_by")
        event_dict["updated_by"] = event_data.get("created_by")

        event_to_insert = {k: serialize_for_mongo(v) for k, v in event_dict.items()}
        inserted = db.events.insert_one(event_to_insert)

        inserted_id = str(inserted.inserted_id)

        print(f"🗂️ Событие сохранено с _id: {inserted_id}")
        event_to_insert["_id"] = inserted_id

        return {
            "action": action,
            "message": {
                "status": "success",
                "event": event_to_insert
            }
        }

    except ValidationError as e:
        print(f"❌ Ошибка валидации события: {e}")
        return {
            "action": action,
            "message": {
                "status": "error",
                "details": str(e)
            }
        }


def update_event_service(event_data: dict, action: str):
    try:
        event_id = event_data.get("_id")
        if not event_id:
            raise ValueError("Не указан _id события для обновления")

        update_fields = {k: v for k, v in event_data.items() if k != "_id"}
        update_model = EventUpdate(**update_fields)
        update_dict = update_model.dict(exclude_unset=True)

        update_dict["updated_at"] = datetime.utcnow()

        # Сериализация всех значений в подходящий вид
        update_serialized = {k: serialize_for_mongo(v) for k, v in update_dict.items()}

        result = db.events.update_one(
            {"_id": ObjectId(event_id)},
            {"$set": update_serialized}
        )

        if result.matched_count == 0:
            raise ValueError(f"Событие с _id {event_id} не найдено")

        update_serialized["_id"] = event_id

        print(f"🔄 Событие {event_id} успешно обновлено")

        return {
            "action": action,
            "message": {
                "status": "success",
                "event": update_serialized
            }
        }

    except (ValidationError, ValueError) as e:
        print(f"❌ Ошибка при обновлении события: {e}")
        return {
            "action": action,
            "message": {
                "status": "error",
                "details": str(e)
            }
        }


def delete_event_service(event_data: dict, action: str):
    try:
        event_id = event_data.get("_id")
        if not event_id:
            raise ValueError("Не указан _id события для удаления")

        result = db.events.delete_one({"_id": ObjectId(event_id)})

        if result.deleted_count == 0:
            raise ValueError(f"Событие с _id {event_id} не найдено")

        print(f"🗑️ Событие {event_id} успешно удалено")

        return {
            "action": action,
            "message": {
                "status": "success",
                "_id": event_id
            }
        }

    except ValueError as e:
        print(f"❌ Ошибка при удалении события: {e}")
        return {
            "action": action,
            "message": {
                "status": "error",
                "details": str(e)
            }
        }


def register_volunteer_service(event_data: dict, action: str):
    try:
        event_id = event_data.get("_id")
        user_id = event_data.get("user_id")

        if not event_id or not user_id:
            raise ValueError("Требуется _id мероприятия и user_id")

        try:
            event_oid = ObjectId(event_id)
        except (errors.InvalidId, TypeError):
            raise ValueError(f"_id '{event_id}' — невалидный ObjectId")

        event = db.events.find_one({"_id": event_oid})
        if not event:
            raise ValueError(f"Событие с _id {event_id} не найдено")

        volunteers = event.get("volunteers", [])
        max_volunteers = event.get("required_volunteers", 0)

        # Уже записан?
        if user_id in volunteers:
            return {
                "action": action,
                "message": {
                    "status": "error",
                    "details": "Пользователь уже записан на мероприятие"
                }
            }

        # Достигнут лимит?
        if len(volunteers) >= max_volunteers:
            return {
                "action": action,
                "message": {
                    "status": "error",
                    "details": "Достигнут лимит волонтёров для мероприятия"
                }
            }

        # Обновляем
        result = db.events.update_one(
            {"_id": event_oid},
            {
                "$addToSet": {"volunteers": user_id},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

        if result.modified_count == 0:
            raise ValueError("Ошибка при добавлении волонтёра")

        print(f"🤝 Пользователь {user_id} записан на событие {event_id}")

        return {
            "action": action,
            "message": {
                "status": "success",
                "_id": event_id,
                "user_id": user_id
            }
        }

    except ValueError as e:
        print(f"❌ Ошибка записи волонтёра: {e}")
        return {
            "action": action,
            "message": {
                "status": "error",
                "details": str(e)
            }
        }


def unregister_volunteer_service(event_data: dict, action: str):
    try:
        event_id = event_data.get("_id")
        user_id = event_data.get("user_id")

        if not event_id or not user_id:
            raise ValueError("Требуется _id мероприятия и user_id")

        try:
            event_oid = ObjectId(event_id)
        except (errors.InvalidId, TypeError):
            raise ValueError(f"_id '{event_id}' — невалидный ObjectId")

        event = db.events.find_one({"_id": event_oid})
        if not event:
            raise ValueError(f"Событие с _id {event_id} не найдено")

        if user_id not in event.get("volunteers", []):
            return {
                "action": action,
                "message": {
                    "status": "error",
                    "details": "Пользователь не записан на мероприятие"
                }
            }

        result = db.events.update_one(
            {"_id": event_oid},
            {
                "$pull": {"volunteers": user_id},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

        if result.modified_count == 0:
            raise ValueError("Ошибка при удалении волонтёра")

        print(f"🚫 Пользователь {user_id} удалён из события {event_id}")

        return {
            "action": action,
            "message": {
                "status": "success",
                "_id": event_id,
                "user_id": user_id
            }
        }

    except ValueError as e:
        print(f"❌ Ошибка при удалении волонтёра: {e}")
        return {
            "action": action,
            "message": {
                "status": "error",
                "details": str(e)
            }
        }


def get_upcoming_events_service(event_data: dict, action: str):
    try:
        limit = event_data.get("limit", 10)
        category = event_data.get("category", "all")
        now = datetime.utcnow()

        query = {
            "start_datetime": {"$gt": now}
        }

        if category != "all":
            query["category"] = category

        events_cursor = (
            db.events
            .find(query)
            .sort("start_datetime", 1)
            .limit(limit)
        )

        events = []
        for event in events_cursor:
            event["_id"] = str(event["_id"])
            if "created_at" in event:
                event["created_at"] = event["created_at"].isoformat()
            if "updated_at" in event:
                event["updated_at"] = event["updated_at"].isoformat()
            if "start_datetime" in event:
                event["start_datetime"] = event["start_datetime"].isoformat()
            events.append(event)

        return {
            "action": action,
            "message": {
                "status": "success",
                "events": events
            }
        }

    except Exception as e:
        print(f"❌ Ошибка при получении ближайших событий: {e}")
        return {
            "action": action,
            "message": {
                "status": "error",
                "details": str(e)
            }
        }


def get_event_by_id_service(data: dict, action: str) -> dict:
    event_id = data.get("_id")
    if not event_id:
        return {"status": "error", "message": "ID мероприятия не передан"}

    event = db.events.find_one({"_id": ObjectId(event_id)})
    if not event:
        return {"status": "error", "message": "Мероприятие не найдено"}

    serialized_event = serialize_event(event)

    return {
        "status": "success",
        "action": action,
        "event": serialized_event
    }

def convert_datetime_fields(event: dict):
    for field in ["start_datetime", "created_at", "updated_at"]:
        if field in event and isinstance(event[field], datetime):
            event[field] = event[field].isoformat()
    return event

def get_user_events_service(event_data: dict, action: str):
    try:
        user_id = event_data.get("user_id")
        if not user_id:
            raise ValueError("Не передан user_id")

        # Мероприятия, созданные пользователем
        created_cursor = db.events.find({"created_by": user_id})
        created_events = []
        for event in created_cursor:
            event["_id"] = str(event["_id"])
            created_events.append(convert_datetime_fields(event))

        # Мероприятия, где он волонтер
        volunteer_cursor = db.events.find({"volunteers": user_id})
        volunteer_events = []
        for event in volunteer_cursor:
            event["_id"] = str(event["_id"])
            volunteer_events.append(convert_datetime_fields(event))

        return {
            "action": action,
            "message": {
                "status": "success",
                "created_events": created_events,
                "volunteer_events": volunteer_events
            }
        }

    except Exception as e:
        print(f"❌ Ошибка при получении событий пользователя: {e}")
        return {
            "action": action,
            "message": {
                "status": "error",
                "details": str(e)
            }
        }

def get_event_by_title_service(data: dict, action: str) -> dict:
    try:
        title = data.get("title")
        if not title:
            raise ValueError("Не передано название мероприятия (title)")

        events_cursor = db.events.find({"title": {"$regex": title, "$options": "i"}})

        events = []
        for event in events_cursor:
            serialized = serialize_event(event)
            events.append(serialized)

        return {
            "action": action,
            "message": {
                "status": "success",
                "events": events
            }
        }

    except Exception as e:
        print(f"❌ Ошибка при поиске события по title: {e}")
        return {
            "action": action,
            "message": {
                "status": "error",
                "details": str(e)
            }
        }


def get_user_volunteer_count_service(event_data: dict, action: str):
    try:
        user_id = event_data.get("user_id")
        if not user_id:
            raise ValueError("Не передан user_id")

        count = db.events.count_documents({"volunteers": user_id})

        return {
            "action": action,
            "status": "success",
            "data": {
                "volunteer_count": count
            }
        }

    except Exception as e:
        print(f"❌ Ошибка при получении количества волонтёрских событий: {e}")
        return {
            "action": action,
            "message": {
                "status": "error",
                "details": str(e)
            }
        }

