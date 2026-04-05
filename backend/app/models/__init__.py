# Import all models so Alembic can discover them via Base.metadata
from app.models.user import User, UserRole
from app.models.event import Event, EventType
from app.models.financial_record import (
    FinancialRecord,
    RecordType,
    RecordCategory,
    INCOME_CATEGORIES,
    EXPENSE_CATEGORIES,
    SPONSORSHIP_CATEGORIES,
)
from app.models.audit_log import AuditLog, AuditAction, ResourceType

__all__ = [
    "User", "UserRole",
    "Event", "EventType",
    "FinancialRecord", "RecordType", "RecordCategory",
    "INCOME_CATEGORIES", "EXPENSE_CATEGORIES", "SPONSORSHIP_CATEGORIES",
    "AuditLog", "AuditAction", "ResourceType",
]
