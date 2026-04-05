from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from app.models.audit_log import AuditAction, ResourceType


class AuditLogResponse(BaseModel):
    id: UUID
    actor_id: UUID
    action: AuditAction
    resource_type: ResourceType
    resource_id: UUID
    old_data: dict | None
    new_data: dict | None
    timestamp: datetime

    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    audit_logs: list[AuditLogResponse]
    total: int
    page: int
    limit: int
    pages: int
