from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


class Comment(BaseModel):
    user_id: str
    text: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True


class VolunteerTask(BaseModel):
    title: str
    description: Optional[str] = ""
    deadline: Optional[datetime]

    assigned_to: str
    event_id: Optional[str] = None

    status: str = "assigned"

    attachments: List[HttpUrl] = []
    comments: List[Comment] = []

    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True
