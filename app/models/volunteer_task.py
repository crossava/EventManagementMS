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

    status: str = "in_progress"

    attachments: List[HttpUrl] = []
    comments: List[Comment] = []

    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True


class VolunteerTaskUpdate(BaseModel):
    title: str = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None

    assigned_to: str = None
    event_id: Optional[str] = None

    status: str = None

    attachments: List[HttpUrl] = None
    comments: List[Comment] = None

    created_by: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True
