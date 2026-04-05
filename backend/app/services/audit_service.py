from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog, AuditAction, ResourceType


async def create_audit_log(
    db: AsyncSession,
    actor_id: UUID,
    action: AuditAction,
    resource_type: ResourceType,
    resource_id: UUID,
    old_data: dict | None = None,
    new_data: dict | None = None,
) -> AuditLog:
    """Create an append-only audit log entry."""
    audit_log = AuditLog(
        actor_id=actor_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        old_data=old_data,
        new_data=new_data,
    )
    db.add(audit_log)
    await db.flush()
    return audit_log
