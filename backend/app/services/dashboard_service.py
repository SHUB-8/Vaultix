from datetime import date
from decimal import Decimal
from sqlalchemy import select, func, case, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.financial_record import (
    FinancialRecord, RecordType, RecordCategory,
    SPONSORSHIP_CATEGORIES,
)
from app.models.event import Event
from app.schemas.dashboard import (
    SummaryResponse, AnalyticsResponse, TrendItem,
    EventPnL, CategoryBreakdownItem,
)
from app.models.user import User, UserRole

def get_base_conditions(user: User) -> list:
    conditions = [FinancialRecord.is_deleted == False]
    if user.role == UserRole.analyst and user.assigned_event_id:
        conditions.append(FinancialRecord.event_id == user.assigned_event_id)
    return conditions

# Base condition: exclude soft-deleted records
_active = FinancialRecord.is_deleted == False


async def get_summary(db: AsyncSession, user: User) -> SummaryResponse:
    """Get total income, expenses, net balance, and record count."""
    result = await db.execute(
        select(
            func.coalesce(
                func.sum(case((FinancialRecord.type == RecordType.income, FinancialRecord.amount))),
                Decimal("0"),
            ).label("total_income"),
            func.coalesce(
                func.sum(case((FinancialRecord.type == RecordType.expense, FinancialRecord.amount))),
                Decimal("0"),
            ).label("total_expenses"),
            func.count(FinancialRecord.id).label("total_records"),
        ).where(*get_base_conditions(user))
    )
    row = result.one()
    total_income = row.total_income
    total_expenses = row.total_expenses

    return SummaryResponse(
        total_income=total_income,
        total_expenses=total_expenses,
        net_balance=total_income - total_expenses,
        total_records=row.total_records,
        as_of=date.today(),
    )


async def get_trends(db: AsyncSession, user: User) -> list[TrendItem]:
    """Get monthly income vs expense trend."""
    month_col = func.to_char(FinancialRecord.date, "YYYY-MM").label("month")
    result = await db.execute(
        select(
            month_col,
            func.coalesce(
                func.sum(case((FinancialRecord.type == RecordType.income, FinancialRecord.amount))),
                Decimal("0"),
            ).label("income"),
            func.coalesce(
                func.sum(case((FinancialRecord.type == RecordType.expense, FinancialRecord.amount))),
                Decimal("0"),
            ).label("expenses"),
        )
        .where(*get_base_conditions(user))
        .group_by(month_col)
        .order_by(month_col)
    )
    rows = result.all()
    return [
        TrendItem(month=row.month, income=row.income, expenses=row.expenses)
        for row in rows
    ]


async def get_event_pnl(db: AsyncSession, user: User) -> list[EventPnL]:
    """Get profit/loss breakdown per event."""
    result = await db.execute(
        select(
            FinancialRecord.event_id,
            Event.name.label("event_name"),
            func.coalesce(
                func.sum(case((FinancialRecord.type == RecordType.income, FinancialRecord.amount))),
                Decimal("0"),
            ).label("income"),
            func.coalesce(
                func.sum(case((FinancialRecord.type == RecordType.expense, FinancialRecord.amount))),
                Decimal("0"),
            ).label("expenses"),
        )
        .join(Event, FinancialRecord.event_id == Event.id)
        .where(*get_base_conditions(user), FinancialRecord.event_id.isnot(None))
        .group_by(FinancialRecord.event_id, Event.name)
        .order_by(Event.name)
    )
    rows = result.all()
    return [
        EventPnL(
            event_id=row.event_id,
            event_name=row.event_name,
            income=row.income,
            expenses=row.expenses,
            profit_loss=row.income - row.expenses,
        )
        for row in rows
    ]


async def get_category_breakdown(db: AsyncSession, user: User) -> list[CategoryBreakdownItem]:
    """Get each expense category as a percentage of total expenses."""
    # Total expenses
    total_result = await db.execute(
        select(
            func.coalesce(func.sum(FinancialRecord.amount), Decimal("0"))
        ).where(*get_base_conditions(user), FinancialRecord.type == RecordType.expense)
    )
    total_expenses = total_result.scalar() or Decimal("0")

    if total_expenses == 0:
        return []

    result = await db.execute(
        select(
            FinancialRecord.category,
            func.sum(FinancialRecord.amount).label("amount"),
        )
        .where(*get_base_conditions(user), FinancialRecord.type == RecordType.expense)
        .group_by(FinancialRecord.category)
        .order_by(func.sum(FinancialRecord.amount).desc())
    )
    rows = result.all()
    return [
        CategoryBreakdownItem(
            category=row.category.value,
            amount=row.amount,
            percentage=round(row.amount / total_expenses * 100, 2),
        )
        for row in rows
    ]


async def get_analytics(db: AsyncSession, user: User) -> AnalyticsResponse:
    """Get full analytics payload including all dashboard metrics."""
    summary = await get_summary(db, user)
    trends = await get_trends(db, user)
    event_pnl = await get_event_pnl(db, user)
    category_breakdown = await get_category_breakdown(db, user)

    # Sponsorship dependency ratio
    sponsorship_cats = [c.value for c in SPONSORSHIP_CATEGORIES]
    sponsorship_result = await db.execute(
        select(
            func.coalesce(func.sum(FinancialRecord.amount), Decimal("0"))
        ).where(
            *get_base_conditions(user),
            FinancialRecord.type == RecordType.income,
            FinancialRecord.category.in_(sponsorship_cats),
        )
    )
    sponsorship_income = sponsorship_result.scalar() or Decimal("0")
    dependency_ratio = (
        round(sponsorship_income / summary.total_income * 100, 2)
        if summary.total_income > 0
        else Decimal("0")
    )

    # Top expense category
    top_expense = category_breakdown[0].category if category_breakdown else None

    # Top income source
    income_result = await db.execute(
        select(
            FinancialRecord.category,
            func.sum(FinancialRecord.amount).label("total"),
        )
        .where(*get_base_conditions(user), FinancialRecord.type == RecordType.income)
        .group_by(FinancialRecord.category)
        .order_by(func.sum(FinancialRecord.amount).desc())
        .limit(1)
    )
    top_income_row = income_result.first()
    top_income = top_income_row.category.value if top_income_row else None

    return AnalyticsResponse(
        summary=summary,
        sponsorship_dependency_ratio=dependency_ratio,
        top_expense_category=top_expense,
        top_income_source=top_income,
        month_over_month_trend=trends,
        event_pnl=event_pnl,
        category_breakdown=category_breakdown,
    )
