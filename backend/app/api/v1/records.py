from typing import Annotated
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.dependencies import require_role
from app.models.user import User, UserRole
from app.models.financial_record import RecordType, RecordCategory
from app.schemas.record import (
    RecordCreate, RecordUpdate, RecordResponse,
    RecordListResponse, RecordFilterParams,
)
from app.services import record_service

router = APIRouter(prefix="/records", tags=["Financial Records"])


@router.post(
    "",
    response_model=RecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create financial record",
    description="Create a new financial record (income or expense). Admin only.",
)
async def create_record(
    data: RecordCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.admin))],
):
    return await record_service.create_record(db, data, current_user)


@router.get(
    "",
    response_model=RecordListResponse,
    summary="List financial records",
    description="List financial records with optional filters. Accessible by Admin and Analyst.",
)
async def list_records(
    db: Annotated[AsyncSession, Depends(get_db)],
    _current_user: Annotated[
        User, Depends(require_role(UserRole.admin, UserRole.analyst))
    ],
    type: RecordType | None = Query(None, description="Filter by income or expense"),
    category: RecordCategory | None = Query(None, description="Filter by category"),
    event_id: UUID | None = Query(None, description="Filter by event"),
    date_from: date | None = Query(None, description="Start date filter"),
    date_to: date | None = Query(None, description="End date filter"),
    search: str | None = Query(None, description="Search in notes"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Records per page"),
):
    filters = RecordFilterParams(
        type=type,
        category=category,
        event_id=event_id,
        date_from=date_from,
        date_to=date_to,
        search=search,
        page=page,
        limit=limit,
    )
    records, total, pages = await record_service.list_records(db, filters, _current_user)
    return RecordListResponse(
        records=records, total=total, page=page, limit=limit, pages=pages
    )


@router.get(
    "/{record_id}",
    response_model=RecordResponse,
    summary="Get financial record",
    description="Get a specific financial record. Accessible by Admin and Analyst.",
)
async def get_record(
    record_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current_user: Annotated[
        User, Depends(require_role(UserRole.admin, UserRole.analyst))
    ],
):
    return await record_service.get_record(db, record_id, _current_user)


@router.patch(
    "/{record_id}",
    response_model=RecordResponse,
    summary="Update financial record",
    description="Update a financial record. Admin only.",
)
async def update_record(
    record_id: UUID,
    data: RecordUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.admin))],
):
    return await record_service.update_record(db, record_id, data, current_user)


@router.delete(
    "/{record_id}",
    response_model=RecordResponse,
    summary="Soft delete financial record",
    description="Soft delete a financial record. The record is not removed from the database. Admin only.",
)
async def delete_record(
    record_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.admin))],
):
    return await record_service.soft_delete_record(db, record_id, current_user)
