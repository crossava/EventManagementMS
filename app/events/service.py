from app.events.repository import EventRepository


class EventService:
    @staticmethod
    def handle_command(command):
        request_id = command.get("request_id")
        message = command.get("message")
        action = message.get("action")
        data = message.get("data", {})

        if not request_id:
            return {"status": "error", "message": "Missing request_id"}

        response = {"request_id": request_id}

        if action == "create":
            event = EventRepository.create_event(data["title"], data["category"], data["date"])
            response.update({"status": "success", "event_id": str(event.id)})

        elif action == "update":
            EventRepository.update_event(data["event_id"], **data)
            response.update({"status": "updated"})

        elif action == "delete":
            EventRepository.delete_event(data["event_id"])
            response.update({"status": "deleted"})

        else:
            response.update({"status": "error", "message": "Invalid action"})

        return response
