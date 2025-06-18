from datetime import datetime
from typing import List

from pydantic import BaseModel


class ChatMessage(BaseModel):
    author: str
    message: str
    timestamp: datetime


class Chat(BaseModel):
    event_id: str
    messages: List[ChatMessage] = []