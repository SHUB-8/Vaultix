import math
from uuid import UUID
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.financial_record import (
    FinancialRecord, RecordType, RecordCategory,
    INCOME_CATEGORIES, EXPENSE_CATEGORIES,
)
from app.models.event import Event
from app.models.user import User
from app.models.audit_log import AuditAction, ResourceType
from app.services.audit_service import create_audit_log
from app.schemas.record import RecordCreate, RecordUpdate, RecordFilterParams


def _record_to_dict(record: FinancialRecord) -> dict:
    """Serialize a financial record to a dict for audit logging."""
    return {
        "id": str(record.id),
        "amount": str(record.amount),
        "type": record.type.value,
        "category": record.category.value,
        "event_id": str(record.event_id) if record.event_id else None,
        "date": record.date.isoformat(),
        "notes": record.notes,
    }


from app.models.user import UserRole
async def create_record(
    db: AsyncSession, data: RecordCreate, actor: User
) -> FinancialRecord:
    """Create a new financial record."""
    # Validate event_id if provided
    if data.event_id:
        result = await db.execute(
            select(Event).where(Event.id == data.event_id, Event.is_active == True)
        )
        event = result.scalar_one_or_none()
        if not event:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "BAD_REQUEST",
                        "message": "Event not found or inactive.",
                        "details": None,
                    }
                },
            )

    record = FinancialRecord(
        amount=data.amount,
        type=data.type,
        category=data.category,
        event_id=data.event_id,
        date=data.date,
        notes=data.notes,
        created_by_id=actor.id,
    )
    db.add(record)
    await db.flush()
    await db.refresh(record)

    await create_audit_log(
        db=db,
        actor_id=actor.id,
        action=AuditAction.created,
        resource_type=ResourceType.financial_record,
        resource_id=record.id,
        new_data=_record_to_dict(record),
    )

    return record


async def list_records(
    db: AsyncSession, filters: RecordFilterParams, user: User
) -> tuple[list[FinancialRecord], int, int]:
    """List financial records with filters and pagination. Returns (records, total, pages)."""
    conditions = [FinancialRecord.is_deleted == False]

    if user.role == UserRole.analyst and user.assigned_event_id:
        conditions.append(FinancialRecord.event_id == user.assigned_event_id)

    if filters.type:
        conditions.append(FinancialRecord.type == filters.type)
    if filters.category:
        conditions.append(FinancialRecord.category == filters.category)
    if filters.event_id:
        conditions.append(FinancialRecord.event_id == filters.event_id)
    if filters.date_from:
        conditions.append(FinancialRecord.date >= filters.date_from)
    if filters.date_to:
        conditions.append(FinancialRecord.date <= filters.date_to)
    if filters.search:
        conditions.append(FinancialRecord.notes.ilike(f"%{filters.search}%"))

    where_clause = and_(*conditions)

    # Total count
    count_result = await db.execute(
        select(func.count(FinancialRecord.id)).where(where_clause)
    )
    total = count_result.scalar() or 0
    pages = math.ceil(total / filters.limit) if total > 0 else 1

    # Paginated results
    offset = (filters.page - 1) * filters.limit
    result = await db.execute(
        select(FinancialRecord)
        .where(where_clause)
        .order_by(FinancialRecord.date.desc(), FinancialRecord.created_at.desc())
        .offset(offset)
        .limit(filters.limit)
    )
    records = list(result.scalars().all())

    return records, total, pages


async def get_record(db: AsyncSession, record_id: UUID, user: User) -> FinancialRecord:
    """Get a single non-deleted financial record by ID."""
    conditions = [
        FinancialRecord.id == record_id,
        FinancialRecord.is_deleted == False,
    ]
    if user.role == UserRole.analyst and user.assigned_event_id:
        conditions.append(FinancialRecord.event_id == user.assigned_event_id)

    result = await db.execute(
        select(FinancialRecord).where(and_(*conditions))
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Financial record not found.",
                    "details": None,
                }
            },
        )
    return record


async def update_record(
    db: AsyncSession, record_id: UUID, data: RecordUpdate, actor: User
) -> FinancialRecord:
    """Update a financial record. Captures old state for audit."""
    record = await get_record(db, record_id, actor)
    old_data = _record_to_dict(record)

    update_data = data.model_dump(exclude_unset=True)

    # Validate event_id if being updated
    if "event_id" in update_data and update_data["event_id"]:
        result = await db.execute(
            select(Event).where(
                Event.id == update_data["event_id"], Event.is_active == True
            )
        )
        event = result.scalar_one_or_none()
        if not event:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "BAD_REQUEST",
                        "message": "Event not found or inactive.",
                        "details": None,
                    }
                },
            )

    # Cross-validate type and category after update
    new_type = update_data.get("type", record.type)
    new_category = update_data.get("category", record.category)
    if isinstance(new_type, str):
        new_type = RecordType(new_type)
    if isinstance(new_category, str):
        new_category = RecordCategory(new_category)

    if new_type == RecordType.income and new_category not in INCOME_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "BAD_REQUEST",
                    "message": f"Category '{new_category.value}' is not a valid income category.",
                    "details": None,
                }
            },
        )
    if new_type == RecordType.expense and new_category not in EXPENSE_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "BAD_REQUEST",
                    "message": f"Category '{new_category.value}' is not a valid expense category.",
                    "details": None,
                }
            },
        )

    for field, value in update_data.items():
        setattr(record, field, value)

    record.updated_by_id = actor.id
    await db.flush()
    await db.refresh(record)

    await create_audit_log(
        db=db,
        actor_id=actor.id,
        action=AuditAction.updated,
        resource_type=ResourceType.financial_record,
        resource_id=record.id,
        old_data=old_data,
        new_data=_record_to_dict(record),
    )

    return record


async def soft_delete_record(
    db: AsyncSession, record_id: UUID, actor: User
) -> FinancialRecord:
    """Soft delete a financial record."""
    record = await get_record(db, record_id, actor)
    old_data = _record_to_dict(record)

    record.is_deleted = True
    record.deleted_at = datetime.now(timezone.utc)
    record.deleted_by_id = actor.id

    await db.flush()
    await db.refresh(record)

    await create_audit_log(
        db=db,
        actor_id=actor.id,
        action=AuditAction.deleted,
        resource_type=ResourceType.financial_record,
        resource_id=record.id,
        old_data=old_data,
    )

    return record
