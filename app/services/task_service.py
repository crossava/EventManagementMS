import json
from datetime import datetime

from app.models.volunteer_task import VolunteerTask, VolunteerTaskUpdate
from app.core.mongo_config import db
from pydantic import ValidationError
from bson import ObjectId, errors


def assign_task_service(task_data: dict, action: str):
    try:
        now = datetime.utcnow()

        # Добавляем timestamps
        task_data["created_at"] = now
        task_data["updated_at"] = now

        # Валидируем данные через модель
        task = VolunteerTask(**task_data)
        task_dict = task.dict(by_alias=True)

        # Вставляем в MongoDB
        inserted = db.volunteer_tasks.insert_one(task_dict)
        inserted_id = str(inserted.inserted_id)

        print(f"✅ Задача успешно создана с _id: {inserted_id}")

        task_dict["_id"] = inserted_id

        forward_to_user = task_dict.get("assigned_to")
        return {
            "action": action,
            "message": {
                "status": "success",
                "task": task_dict,
                "forward_to": [forward_to_user] if forward_to_user else []
            }
        }

    except ValidationError as e:
        print(f"❌ Ошибка валидации при назначении задачи: {e}")
        return {
            "action": action,
            "message": {
                "status": "error",
                "details": str(e)
            }
        }
    except Exception as e:
        print(f"❌ Ошибка создания задачи: {e}")
        return {
            "action": action,
            "message": {
                "status": "error",
                "details": str(e)
            }
        }


def update_task_service(task_data: dict, action: str):
    try:
        task_id = task_data.get("_id")
        if not task_id:
            raise ValueError("Не передан _id задачи")

        update_fields = {k: v for k, v in task_data.items() if k != "_id"}

        update_model = VolunteerTaskUpdate(
            **{**update_fields})  # заглушка
        validated = update_model.dict(exclude_unset=True, exclude={"created_at", "comments", "created_by"})

        validated["updated_at"] = datetime.utcnow()

        result = db.volunteer_tasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": validated}
        )

        if result.matched_count == 0:
            raise ValueError(f"Задача с _id {task_id} не найдена")

        print(f"🔄 Задача {task_id} успешно обновлена")

        return {
            "action": action,
            "status": "success",
            "message": {
                "updated_task": {
                    "_id": task_id,
                    **validated
                }
            }
        }

    except (ValidationError, ValueError) as e:
        print(f"❌ Ошибка обновления задачи: {e}")
        return {
            "action": action,
            "status": "error",
            "message": {
                "details": str(e)
            }
        }
    except Exception as e:
        print(f"❌ Общая ошибка обновления задачи: {e}")
        return {
            "action": action,
            "status": "error",
            "message": {
                "details": str(e)
            }
        }


def delete_task_service(task_data: dict, action: str):
    try:
        task_id = task_data.get("_id")
        if not task_id:
            raise ValueError("Не передан _id задачи")

        try:
            object_id = ObjectId(task_id)
        except errors.InvalidId:
            raise ValueError("Невалидный формат _id")

        result = db.volunteer_tasks.delete_one({"_id": object_id})

        if result.deleted_count == 0:
            raise ValueError(f"Задача с _id {task_id} не найдена")

        return {
            "action": action,
            "status": "success",
            "message": {
                "_id": task_id
            }
        }

    except ValueError as e:
        print(f"❌ Ошибка удаления задачи: {e}")
        return {
            "status": "error",
            "action": action,
            "message": {
                "details": str(e)
            }
        }
    except Exception as e:
        print(f"❌ Общая ошибка удаления задачи: {e}")
        return {
            "status": "error",
            "action": action,
            "message": {
                "details": str(e)
            }
        }


def serialize_task(task: dict) -> dict:
    task["_id"] = str(task["_id"])
    task["assigned_to"] = str(task["assigned_to"])
    if task.get("event_id"):
        task["event_id"] = str(task["event_id"])

    if "created_by" in task:
        task["created_by"] = str(task["created_by"])

    for dt_field in ["created_at", "updated_at", "deadline"]:
        if dt_field in task and isinstance(task[dt_field], datetime):
            task[dt_field] = task[dt_field].isoformat()

    # сериализация комментариев
    for comment in task.get("comments", []):
        comment["user_id"] = str(comment["user_id"])
        if "created_at" in comment and isinstance(comment["created_at"], datetime):
            comment["created_at"] = comment["created_at"].isoformat()

    return task


def get_tasks_by_user_service(task_data: dict, action: str):
    try:
        user_id = task_data.get("user_id")
        if not user_id:
            raise ValueError("Не передан user_id")

        cursor = db.volunteer_tasks.find({"assigned_to": user_id}).sort("deadline", 1)
        tasks = [serialize_task(task) for task in cursor]

        return {
            "action": action,
            "status": "success",
            "data": {
                "tasks": tasks
            }
        }

    except Exception as e:
        print(f"❌ Ошибка при получении задач по user_id: {e}")
        return {
            "action": action,
            "message": {
                "status": "error",
                "details": str(e)
            }
        }


def get_tasks_by_event_service(task_data: dict, action: str):
    try:
        event_id = task_data.get("event_id")
        if not event_id:
            raise ValueError("Не передан event_id")

        object_id = ObjectId(event_id)

        cursor = db.volunteer_tasks.find({"event_id": object_id}).sort("deadline", 1)
        tasks = [serialize_task(task) for task in cursor]

        return {
            "action": action,
            "message": {
                "status": "success",
                "tasks": tasks
            }
        }

    except Exception as e:
        print(f"❌ Ошибка при получении задач по event_id: {e}")
        return {
            "action": action,
            "message": {
                "status": "error",
                "details": str(e)
            }
        }


def get_task_by_id_service(task_data: dict, action: str):
    try:
        task_id = task_data.get("task_id")
        if not task_id:
            raise ValueError("Не передан task_id")

        task = db.volunteer_tasks.find_one({"_id": ObjectId(task_id)})
        if not task:
            raise ValueError("Задача не найдена")

        serialized = serialize_task(task)

        return {
            "action": action,
            "message": {
                "status": "success",
                "task": serialized
            }
        }

    except Exception as e:
        print(f"❌ Ошибка при получении задачи по id: {e}")
        return {
            "action": action,
            "message": {
                "status": "error",
                "details": str(e)
            }
        }


def add_task_comment_service(data: dict, action: str):
    try:
        task_id = data.get("task_id")
        user_id = data.get("user_id")
        text = data.get("text", "")
        attachments = data.get("attachments", [])

        if not task_id or not user_id or not text:
            raise ValueError("Необходимы поля: task_id, user_id, text")

        task = db.volunteer_tasks.find_one({"_id": ObjectId(task_id)})
        if not task:
            raise ValueError("Задача не найдена")

        comment = {
            "user_id": ObjectId(user_id),
            "text": text,
            "attachments": attachments,
            "created_at": datetime.utcnow(),
            "task_id": task_id
        }

        # Определяем, кому форвардить (только в питоне, не в БД)
        forward_to_user = None
        if str(user_id) == task.get("assigned_to"):
            forward_to_user = task.get("created_by")
        else:
            forward_to_user = task.get("assigned_to")

        # Добавляем комментарий в MongoDB
        result = db.volunteer_tasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$push": {"comments": comment}}
        )

        if result.modified_count == 0:
            raise ValueError("Комментарий не был добавлен")

        return {
            "action": action,
            "status": "success",
            "message": {
                "comment": comment,
                "forward_to": [forward_to_user] if forward_to_user else [],
            }
        }

    except Exception as e:
        print(f"❌ Ошибка при добавлении комментария: {e}")
        return {
            "action": action,
            "message": {
                "status": "error",
                "details": str(e)
            }
        }


def add_task_attachment_service(data: dict, action: str):
    try:
        task_id = data.get("task_id")
        user_id = data.get("user_id")
        attachments = data.get("attachments", [])

        if not task_id or not attachments:
            raise ValueError("Необходимы поля: task_id и attachments")

        # Добавление вложений
        result = db.volunteer_tasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$push": {"attachments": {"$each": attachments}}}
        )

        if result.modified_count == 0:
            raise ValueError("Задача не найдена")

        # Получение обновлённой задачи
        task = db.volunteer_tasks.find_one({"_id": ObjectId(task_id)})
        if not task:
            raise ValueError("Задача не найдена после обновления")

        current_attachments = task.get("attachments", [])

        # Определение, кому переслать сообщение
        forward_to_user = None
        if str(user_id) == task.get("assigned_to"):
            forward_to_user = task.get("created_by")
        else:
            forward_to_user = task.get("assigned_to")

        return {
            "action": action,
            "message": {
                "status": "success",
                "task_id": task_id,
                "details": f"{len(attachments)} вложений добавлено",
                "attachments": attachments,
                "forward_to": [forward_to_user] if forward_to_user else [],
            }
        }

    except Exception as e:
        print(f"❌ Ошибка при добавлении вложений: {e}")
        return {
            "action": action,
            "message": {
                "status": "error",
                "details": str(e)
            }
        }


def change_task_status_service(data: dict, action: str):
    try:
        task_id = data.get("task_id")
        new_status = data.get("status")

        if not task_id or not new_status:
            raise ValueError("Необходимы поля: task_id и status")

        result = db.volunteer_tasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {"status": new_status}}
        )

        if result.modified_count == 0:
            raise ValueError("Задача не найдена или статус уже установлен")

        return {
            "action": action,
            "message": {
                "status": "success",
                "task_id": task_id,
                "new_status": new_status
            }
        }

    except Exception as e:
        print(f"❌ Ошибка при смене статуса: {e}")
        return {
            "action": action,
            "message": {
                "status": "error",
                "details": str(e)
            }
        }


def remove_task_attachment_service(data: dict, action: str):
    try:
        task_id = data.get("task_id")
        attachments_to_remove = data.get("attachments", [])

        if not task_id or not attachments_to_remove:
            raise ValueError("Нужны task_id и список attachments")

        result = db.volunteer_tasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$pull": {"attachments": {"$in": attachments_to_remove}}}
        )

        return {
            "action": action,
            "message": {
                "status": "success",
                "removed": attachments_to_remove
            }
        }

    except Exception as e:
        print(f"❌ Ошибка при удалении вложений: {e}")
        return {
            "action": action,
            "message": {
                "status": "error",
                "details": str(e)
            }
        }


def get_task_comments_service(data: dict, action: str):
    try:
        task_id = data.get("task_id")

        if not task_id:
            raise ValueError("Не указан task_id")

        task = db.volunteer_tasks.find_one({"_id": ObjectId(task_id)}, {"comments": 1})

        if not task:
            raise ValueError("Задача не найдена")

        return {
            "action": action,
            "status": "success",
            "data": {
                "comments": task.get("comments", [])
            }
        }

    except Exception as e:
        print(f"❌ Ошибка при получении комментариев: {e}")
        return {
            "action": action,
            "message": {
                "status": "error",
                "details": str(e)
            }
        }


def get_tasks_assigned_by_user_service(data: dict, action: str):
    try:
        user_id = data.get("user_id")
        if not user_id:
            raise ValueError("user_id is required")

        tasks = list(db.volunteer_tasks.find({"created_by": user_id}))
        for task in tasks:
            task["_id"] = str(task["_id"])

        return {
            "action": action,
            "status": "success",
            "data": {
                "tasks": tasks
            }
        }

    except Exception as e:
        print(f"❌ Ошибка при получении задач по user_id: {e}")
        return {
            "action": action,
            "status": "error",
            "message": {
                "details": str(e)
            }
        }


def get_task_attachments_service(data: dict, action: str):
    try:
        task_id = data.get("task_id")
        if not task_id:
            raise ValueError("Необходимо указать task_id")

        task = db.volunteer_tasks.find_one({"_id": ObjectId(task_id)}, {"attachments": 1})
        if not task:
            raise ValueError("Задача не найдена")

        return {
            "action": action,
            "status": "success",
            "message": {
                "attachments": task.get("attachments", [])
            }
        }

    except Exception as e:
        print(f"❌ Ошибка при получении вложений задачи: {e}")
        return {
            "action": action,
            "message": {
                "status": "error",
                "details": str(e)
            }
        }


def delete_tasks_by_event_id_service(data: dict, action: str):
    try:
        event_id = data.get("_id")
        if not event_id:
            raise ValueError("Не передан event_id")

        result = db.volunteer_tasks.delete_many({"event_id": event_id})
        deleted_count = result.deleted_count

        return {
            "action": action,
            "message": {
                "status": "success",
                "deleted_count": deleted_count,
                "event_id": event_id
            }
        }

    except Exception as e:
        return {
            "action": action,
            "message": {
                "status": "error",
                "error": str(e)
            }
        }