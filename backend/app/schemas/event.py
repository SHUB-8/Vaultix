from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.event import EventType

_EventType = EventType


class EventCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, examples=["TechSurge 2025"])
    type: _EventType = Field(..., examples=["major_fest"])
    parent_event_id: UUID | None = Field(None, examples=[None])
    description: str | None = Field(None, examples=["Annual technical fest"])


class EventUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    is_active: bool | None = None


class EventResponse(BaseModel):
    id: UUID
    name: str
    type: _EventType
    parent_event_id: UUID | None
    description: str | None
    is_active: bool
    created_by_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EventListResponse(BaseModel):
    events: list[EventResponse]
    total: int
