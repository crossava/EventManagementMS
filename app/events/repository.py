from datetime import datetime

from app.events.models import Event


class EventRepository:
    @staticmethod
    def create_event(title: str, category: str, date: str):
        """Создает новое событие в базе"""
        try:
            # ✅ Конвертация строки в datetime
            event_date = datetime.fromisoformat(date)
        except ValueError:
            raise ValueError(f"❌ Ошибка: Неверный формат даты: {date}")

        event = Event(title=title, category=category, date=event_date)
        print("event is created", event)
        # event.save()
        return event

    @staticmethod
    def get_event(event_id):
        return Event.objects(id=event_id).first()

    @staticmethod
    def update_event(event_id, **kwargs):
        return Event.objects(id=event_id).update_one(**kwargs)

    @staticmethod
    def delete_event(event_id):
        return Event.objects(id=event_id).delete()
