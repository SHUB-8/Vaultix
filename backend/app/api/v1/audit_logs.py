import math
from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.dependencies import require_role
from app.models.user import User, UserRole
from app.models.audit_log import AuditLog, AuditAction, ResourceType
from app.schemas.audit_log import AuditLogResponse, AuditLogListResponse

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get(
    "",
    response_model=AuditLogListResponse,
    summary="List audit logs",
    description="List all audit log entries with optional filters. Admin and Analyst only.",
)
async def list_audit_logs(
    db: Annotated[AsyncSession, Depends(get_db)],
    _current_user: Annotated[
        User, Depends(require_role(UserRole.admin, UserRole.analyst))
    ],
    action: AuditAction | None = Query(None, description="Filter by action type"),
    resource_type: ResourceType | None = Query(None, description="Filter by resource type"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Records per page"),
):
    conditions = []
    if action:
        conditions.append(AuditLog.action == action)
    if resource_type:
        conditions.append(AuditLog.resource_type == resource_type)

    # Total count
    count_query = select(func.count(AuditLog.id))
    if conditions:
        count_query = count_query.where(*conditions)
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    pages = math.ceil(total / limit) if total > 0 else 1

    # Paginated results
    offset = (page - 1) * limit
    query = (
        select(AuditLog)
        .order_by(AuditLog.timestamp.desc())
        .offset(offset)
        .limit(limit)
    )
    if conditions:
        query = query.where(*conditions)

    result = await db.execute(query)
    logs = list(result.scalars().all())

    return AuditLogListResponse(
        audit_logs=logs, total=total, page=page, limit=limit, pages=pages
    )
