import enum
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy import (
    String, Boolean, Date, DateTime, Text, ForeignKey, Numeric,
    Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class RecordType(str, enum.Enum):
    income = "income"
    expense = "expense"


class RecordCategory(str, enum.Enum):
    # Income categories
    college_grant = "college_grant"
    sponsorship_title = "sponsorship_title"
    sponsorship_associate = "sponsorship_associate"
    registration_fees = "registration_fees"
    workshop_fees = "workshop_fees"
    merchandise_sales = "merchandise_sales"
    alumni_donation = "alumni_donation"
    other_income = "other_income"

    # Expense categories
    venue_logistics = "venue_logistics"
    guest_honorarium = "guest_honorarium"
    marketing_printing = "marketing_printing"
    food_hospitality = "food_hospitality"
    equipment_av = "equipment_av"
    prizes_certificates = "prizes_certificates"
    digital_tools = "digital_tools"
    travel = "travel"
    miscellaneous = "miscellaneous"


# Category validation sets
INCOME_CATEGORIES = {
    RecordCategory.college_grant,
    RecordCategory.sponsorship_title,
    RecordCategory.sponsorship_associate,
    RecordCategory.registration_fees,
    RecordCategory.workshop_fees,
    RecordCategory.merchandise_sales,
    RecordCategory.alumni_donation,
    RecordCategory.other_income,
}

EXPENSE_CATEGORIES = {
    RecordCategory.venue_logistics,
    RecordCategory.guest_honorarium,
    RecordCategory.marketing_printing,
    RecordCategory.food_hospitality,
    RecordCategory.equipment_av,
    RecordCategory.prizes_certificates,
    RecordCategory.digital_tools,
    RecordCategory.travel,
    RecordCategory.miscellaneous,
}

SPONSORSHIP_CATEGORIES = {
    RecordCategory.sponsorship_title,
    RecordCategory.sponsorship_associate,
}


class FinancialRecord(Base):
    __tablename__ = "financial_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    type: Mapped[RecordType] = mapped_column(
        SAEnum(RecordType, name="record_type", create_constraint=True),
        nullable=False,
    )
    category: Mapped[RecordCategory] = mapped_column(
        SAEnum(RecordCategory, name="record_category", create_constraint=True),
        nullable=False,
    )
    event_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("events.id"), nullable=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Soft delete fields
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # Tracking fields
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    updated_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    event = relationship("Event", lazy="selectin")
    created_by = relationship("User", foreign_keys=[created_by_id], lazy="selectin")
    updated_by = relationship("User", foreign_keys=[updated_by_id], lazy="selectin")
    deleted_by = relationship("User", foreign_keys=[deleted_by_id], lazy="selectin")

    def __repr__(self) -> str:
        return f"<FinancialRecord {self.type.value} {self.amount} ({self.category.value})>"
