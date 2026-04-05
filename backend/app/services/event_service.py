from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.event import Event, EventType
from app.models.user import User
from app.models.audit_log import AuditAction, ResourceType
from app.services.audit_service import create_audit_log
from app.schemas.event import EventCreate, EventUpdate


async def create_event(
    db: AsyncSession, data: EventCreate, actor: User
) -> Event:
    """Create a new event."""
    # Validate parent_event_id if provided
    if data.parent_event_id:
        parent = await db.execute(
            select(Event).where(Event.id == data.parent_event_id)
        )
        parent_event = parent.scalar_one_or_none()
        if not parent_event:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "BAD_REQUEST",
                        "message": "Parent event not found.",
                        "details": None,
                    }
                },
            )
        if parent_event.type != EventType.major_fest:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "BAD_REQUEST",
                        "message": "Parent event must be a major fest.",
                        "details": None,
                    }
                },
            )

    # Sub-events must have a parent
    if data.type == EventType.sub_event and not data.parent_event_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "BAD_REQUEST",
                    "message": "Sub-events must specify a parent event.",
                    "details": None,
                }
            },
        )

    event = Event(
        name=data.name,
        type=data.type,
        parent_event_id=data.parent_event_id,
        description=data.description,
        created_by_id=actor.id,
    )
    db.add(event)
    await db.flush()
    await db.refresh(event)

    await create_audit_log(
        db=db,
        actor_id=actor.id,
        action=AuditAction.created,
        resource_type=ResourceType.event,
        resource_id=event.id,
        new_data={"name": event.name, "type": event.type.value},
    )

    return event


async def list_events(db: AsyncSession) -> tuple[list[Event], int]:
    """List all events with total count."""
    count_result = await db.execute(select(func.count(Event.id)))
    total = count_result.scalar() or 0

    result = await db.execute(select(Event).order_by(Event.created_at.desc()))
    events = list(result.scalars().all())
    return events, total


async def get_event(db: AsyncSession, event_id: UUID) -> Event:
    """Get a single event by ID."""
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Event not found.",
                    "details": None,
                }
            },
        )
    return event


async def update_event(
    db: AsyncSession, event_id: UUID, data: EventUpdate, actor: User
) -> Event:
    """Update an event's fields."""
    event = await get_event(db, event_id)

    old_data = {"name": event.name, "description": event.description, "is_active": event.is_active}
    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(event, field, value)

    await db.flush()
    await db.refresh(event)

    await create_audit_log(
        db=db,
        actor_id=actor.id,
        action=AuditAction.updated,
        resource_type=ResourceType.event,
        resource_id=event.id,
        old_data=old_data,
        new_data=update_data,
    )

    return event
