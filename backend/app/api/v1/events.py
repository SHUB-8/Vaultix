from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.dependencies import require_role
from app.models.user import User, UserRole
from app.schemas.event import EventCreate, EventUpdate, EventResponse, EventListResponse
from app.services import event_service

router = APIRouter(prefix="/events", tags=["Events"])


@router.post(
    "",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create event",
    description="Create a new event (major fest or sub-event). Admin only.",
)
async def create_event(
    data: EventCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.admin))],
):
    return await event_service.create_event(db, data, current_user)


@router.get(
    "",
    response_model=EventListResponse,
    summary="List all events",
    description="List all events. Accessible by Admin and Analyst.",
)
async def list_events(
    db: Annotated[AsyncSession, Depends(get_db)],
    _current_user: Annotated[
        User, Depends(require_role(UserRole.admin, UserRole.analyst))
    ],
):
    events, total = await event_service.list_events(db)
    return EventListResponse(events=events, total=total)


@router.get(
    "/{event_id}",
    response_model=EventResponse,
    summary="Get event",
    description="Get a specific event's details. Accessible by Admin and Analyst.",
)
async def get_event(
    event_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current_user: Annotated[
        User, Depends(require_role(UserRole.admin, UserRole.analyst))
    ],
):
    return await event_service.get_event(db, event_id)


@router.patch(
    "/{event_id}",
    response_model=EventResponse,
    summary="Update event",
    description="Update an event's name, description, or status. Admin only.",
)
async def update_event(
    event_id: UUID,
    data: EventUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.admin))],
):
    return await event_service.update_event(db, event_id, data, current_user)
