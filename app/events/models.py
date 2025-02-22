from mongoengine import Document, StringField, DateTimeField, ListField, ReferenceField
import datetime


class Event(Document):
    title = StringField(required=True)
    category = StringField(choices=["conference", "concert", "workshop"], required=True)
    date = DateTimeField(default=datetime.datetime.utcnow)
    status = StringField(choices=["draft", "scheduled", "completed"], default="draft")
    guests = ListField(StringField())  # Храним ID гостей

    meta = {"collection": "events"}
