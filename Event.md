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
      "_id": "EVENT_OBJECT_ID",
      "title": "Новое название",
      "updated_by": "user1"
    }
  }
}
```













