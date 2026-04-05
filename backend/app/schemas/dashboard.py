from datetime import date
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel


class SummaryResponse(BaseModel):
    total_income: Decimal
    total_expenses: Decimal
    net_balance: Decimal
    total_records: int
    as_of: date


class TrendItem(BaseModel):
    month: str  # e.g. "2025-01"
    income: Decimal
    expenses: Decimal


class EventPnL(BaseModel):
    event_id: UUID
    event_name: str
    income: Decimal
    expenses: Decimal
    profit_loss: Decimal


class CategoryBreakdownItem(BaseModel):
    category: str
    amount: Decimal
    percentage: Decimal


class AnalyticsResponse(BaseModel):
    summary: SummaryResponse
    sponsorship_dependency_ratio: Decimal
    top_expense_category: str | None
    top_income_source: str | None
    month_over_month_trend: list[TrendItem]
    event_pnl: list[EventPnL]
    category_breakdown: list[CategoryBreakdownItem]
