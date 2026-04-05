from uuid import UUID
from datetime import date as Date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field, model_validator
from app.models.financial_record import (
    RecordType, RecordCategory,
    INCOME_CATEGORIES, EXPENSE_CATEGORIES,
)

# Type aliases to avoid Pydantic field name clashes with builtins
_RecordType = RecordType
_RecordCategory = RecordCategory
_Date = Date


class RecordCreate(BaseModel):
    amount: Decimal = Field(..., gt=0, decimal_places=2, examples=[25000.00])
    type: _RecordType = Field(..., examples=["income"])
    category: _RecordCategory = Field(..., examples=["sponsorship_title"])
    event_id: UUID | None = Field(None)
    date: _Date = Field(..., examples=["2025-02-15"])
    notes: str | None = Field(None, max_length=1000, examples=["Title sponsorship from TechCorp"])

    @model_validator(mode="after")
    def validate_category_matches_type(self):
        if self.type == RecordType.income and self.category not in INCOME_CATEGORIES:
            raise ValueError(
                f"Category '{self.category.value}' is not a valid income category."
            )
        if self.type == RecordType.expense and self.category not in EXPENSE_CATEGORIES:
            raise ValueError(
                f"Category '{self.category.value}' is not a valid expense category."
            )
        return self

    @model_validator(mode="after")
    def validate_date_not_future(self):
        if self.date > Date.today():
            raise ValueError("Transaction date cannot be in the future.")
        return self


class RecordUpdate(BaseModel):
    amount: Decimal | None = Field(None, gt=0, decimal_places=2)
    type: _RecordType | None = None
    category: _RecordCategory | None = None
    event_id: UUID | None = None
    date: _Date | None = None
    notes: str | None = Field(None, max_length=1000)

    @model_validator(mode="after")
    def validate_category_matches_type(self):
        if self.type and self.category:
            if self.type == RecordType.income and self.category not in INCOME_CATEGORIES:
                raise ValueError(
                    f"Category '{self.category.value}' is not a valid income category."
                )
            if self.type == RecordType.expense and self.category not in EXPENSE_CATEGORIES:
                raise ValueError(
                    f"Category '{self.category.value}' is not a valid expense category."
                )
        return self

    @model_validator(mode="after")
    def validate_date_not_future(self):
        if self.date and self.date > Date.today():
            raise ValueError("Transaction date cannot be in the future.")
        return self


class RecordResponse(BaseModel):
    id: UUID
    amount: Decimal
    type: _RecordType
    category: _RecordCategory
    event_id: UUID | None
    date: _Date
    notes: str | None
    is_deleted: bool
    created_by_id: UUID
    updated_by_id: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RecordListResponse(BaseModel):
    records: list[RecordResponse]
    total: int
    page: int
    limit: int
    pages: int


class RecordFilterParams(BaseModel):
    type: _RecordType | None = None
    category: _RecordCategory | None = None
    event_id: UUID | None = None
    date_from: _Date | None = None
    date_to: _Date | None = None
    search: str | None = None
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)
