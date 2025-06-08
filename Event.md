# 📘 Документация по Kafka-сообщениям для управления мероприятиями

Все сообщения отправляются в Kafka-топик: event_requests


---

## 🔹 create_event

### Описание

Создание нового мероприятия.

### Пример запроса

```json
{
  "topic": "event_requests",
  "message": {
    "action": "create_event",
    "data": {
      "title": "Эко-субботник",
      "description": "Уборка мусора в парке",
      "start_datetime": "2025-05-12T10:00:00",
      "location": "Центральный парк",
      "required_volunteers": 10,
      "photo_url": null,
      "category": "Экология",
      "created_by": "user1"
    }
  }
}
```


---

## 🔹 update_event

### Описание

Обновление одного или нескольких полей мероприятия.

### Пример запроса

```json
{
  "topic": "event_requests",
  "message": {
    "action": "update_event",
    "data": {
      "_id": "EVENT_OBJECT_ID",
      "title": "Новое название",
      "updated_by": "user1"
    }
  }
}
```


---

## 🔹 delete_event

### Описание

Удаление мероприятия по его _id.

### Пример запроса

```json
{
  "topic": "event_requests",
  "message": {
    "action": "delete_event",
    "data": {
      "_id": "EVENT_OBJECT_ID"
    }
  }
}
```


---

## 🔹 register_volunteer

### Описание

Запись пользователя в волонтёры на мероприятие.

### Пример запроса

```json
{
  "topic": "event_requests",
  "message": {
    "action": "register_volunteer",
    "data": {
      "_id": "EVENT_OBJECT_ID",
      "user_id": "user1"
    }
  }
}
```


---

## 🔹 unregister_volunteer

### Описание

Удаление пользователя из списка волонтёров.

### Пример запроса

```json
{
  "topic": "event_requests",
  "message": {
    "action": "unregister_volunteer",
    "data": {
      "_id": "EVENT_OBJECT_ID",
      "user_id": "user1"
    }
  }
}
```


---

## 🔹 get_upcoming_events

### Описание

Получение списка ближайших (будущих) мероприятий.

### Пример запроса

```json
{
  "topic": "event_requests",
  "message": {
    "action": "get_upcoming_events",
    "data": {
      "limit": 10
    }
  }
}
```


---

## 🔹 get_user_events

### Описание

Получение всех мероприятий, связанных с пользователем:

* `created_events` — созданные им;
* `volunteer_events` — где он записан как волонтёр.

### Пример запроса

```json
{
  "topic": "event_requests",
  "message": {
    "action": "update_event",
    "data": {
      "user_id": "USER_ID"
    }
  }
}
```

## 🔹 assign_task

### Описание

Создание задачи к мероприятию

### Пример запроса

```json
{
  "topic": "event_requests",
  "message": {
    "action": "assign_task",
    "data": {
      "title": "Подготовить зону регистрации",
      "description": "Установить стол, разложить бейджи и ручки",
      "deadline": "2025-06-09T10:00:00Z",
      "assigned_to": "6655faaa9f8a7f0c12345678",
      "event_id": "6655fab09f8a7f0cabcdef01",
      "attachments": [],
      "comments": [],
      "created_by": "admin123456"
    }
  }
}
```

## 🔹 update_task_service

### Описание

Обновление задачи

### Пример запроса

```json
{
  "topic": "event_requests",
  "message": {
    "action": "update_task",
    "data": {
      "_id": "6655fab09f8a7f0cabcdef01",
      "title": "Обновлённая задача",
      "status": "in_progress",
      "deadline": "2025-06-10T15:00:00Z"
    }
  }
}
```

## 🔹 delete_task

### Описание

Удаление задачи

### Пример запроса

```json
{
  "topic": "event_requests",
  "message": {
    "action": "delete_task",
    "data": {
      "_id": "6655fab09f8a7f0cabcdef01"
    }
  }
}
```


## 🔹 get_tasks_by_user

### Описание

Все задачи, назначенные определённому волонтёру

### Пример запроса

```json
{
  "topic": "event_requests",
  "message": {
    "action": "get_tasks_by_user",
    "data": {
      "user_id": "6655faaa9f8a7f0c12345678"
    }
  }
}
```

## 🔹 get_tasks_by_event

### Описание

Все задачи, связанные с определённым мероприятием

### Пример запроса

```json
{
  "topic": "event_requests",
  "message": {
    "action": "get_tasks_by_event",
    "data": {
      "event_id": "665602a19f8a7f0c99999999"
    }
  }
}
```

## 🔹 get_task_by_id

### Описание

Полная информация об одной задаче по её task_id

### Пример запроса

```json
{
  "topic": "event_requests",
  "message": {
    "action": "get_task_by_id",
    "data": {
      "task_id": "665703c78fa0190a12345678"
    }
  }
}
```

## 🔹 add_task_comment

### Описание

Добавить комментарий к задаче

### Пример запроса

```json
{
  "topic": "event_requests",
  "message": {
    "action": "add_task_comment",
    "data": {
      "task_id": "665703c78fa0190a12345678",
      "user_id": "66570aa38fa0190a11223344",
      "text": "Работаем над задачей",
      "attachments": [
        "file1.jpg",
        "file2.pdf"
      ]
    }
  }
}
```

## 🔹 add_task_attachment

### Описание

Добавить вложение напрямую в задачу

### Пример запроса

```json
{
  "topic": "event_requests",
  "message": {
    "action": "add_task_attachment",
    "data": {
      "task_id": "665703c78fa0190a12345678",
      "attachments": ["report.docx", "photo.jpg"]
    }
  }
}
```

## 🔹 change_task_status

### Описание

Изменяет статус задачи на заданный

### Пример запроса

```json
{
  "topic": "event_requests",
  "message": {
    "action": "change_task_status",
    "data": {
      "task_id": "6657d2b37c8a0f9e94b12345",
      "status": "in_progress"
    }
  }
}
```

## 🔹 remove_task_attachment

### Описание

Удаляет указанные вложения из задачи

### Пример запроса

```json
{
  "topic": "event_requests",
  "message": {
    "action": "remove_task_attachment",
    "data": {
      "task_id": "6657d2b37c8a0f9e94b12345",
      "attachments": [
        "photo1.jpg",
        "doc2.pdf"
      ]
    }
  }

}
```

## 🔹 get_task_comments

### Описание

Возвращает список комментариев по task_id

### Пример запроса

```json
{
  "topic": "event_requests",
  "message": {
    "action": "get_task_comments",
    "data": {
      "task_id": "6657d2b37c8a0f9e94b12345"
    }
  }
}
```

## 🔹 get_tasks_assigned_by_user

### Описание

Возвращает задачи назначенные пользователем 

### Пример запроса

```json
{
  "topic": "event_requests",
  "message": {
    "action": "get_tasks_assigned_by_user",
    "data": {
      "user_id": "662fa21fc8f7391cf2536ab9"
    }
  }
}
```

