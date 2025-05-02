from pydantic import BaseModel, Field, HttpUrl
from datetime import date as dt_date, time as dt_time, datetime
from typing import Optional, List


class Event(BaseModel):
    title: str
    description: Optional[str] = None
    start_datetime: datetime  # заменяет date + time
    location: str
    required_volunteers: int
    photo_url: Optional[HttpUrl] = None
    category: str
    status: Optional[str] = Field(default="Новое")

    created_by: Optional[str]
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    volunteers: List[str] = Field(default_factory=list)


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_datetime: Optional[datetime] = None
    location: Optional[str] = None
    required_volunteers: Optional[int] = None
    photo_url: Optional[HttpUrl] = None
    category: Optional[str] = None
    status: Optional[str] = None

    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None
