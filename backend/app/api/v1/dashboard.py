from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User, UserRole
from app.schemas.dashboard import (
    SummaryResponse, AnalyticsResponse, TrendItem,
    EventPnL, CategoryBreakdownItem,
)
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard & Analytics"])


@router.get(
    "/summary",
    response_model=SummaryResponse,
    summary="Dashboard summary",
    description="Total income, expenses, net balance. Available to all authenticated roles.",
)
async def get_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
    _current_user: Annotated[User, Depends(get_current_user)],
):
    return await dashboard_service.get_summary(db, _current_user)


@router.get(
    "/analytics",
    response_model=AnalyticsResponse,
    summary="Full analytics",
    description="Complete analytics payload including sponsorship dependency, trends, event P&L, and category breakdown. Admin and Analyst only.",
)
async def get_analytics(
    db: Annotated[AsyncSession, Depends(get_db)],
    _current_user: Annotated[
        User, Depends(require_role(UserRole.admin, UserRole.analyst))
    ],
):
    return await dashboard_service.get_analytics(db, _current_user)


@router.get(
    "/trends",
    response_model=list[TrendItem],
    summary="Monthly trends",
    description="Monthly income vs expense trend data. Admin and Analyst only.",
)
async def get_trends(
    db: Annotated[AsyncSession, Depends(get_db)],
    _current_user: Annotated[
        User, Depends(require_role(UserRole.admin, UserRole.analyst))
    ],
):
    return await dashboard_service.get_trends(db, _current_user)


@router.get(
    "/events",
    response_model=list[EventPnL],
    summary="Event P&L",
    description="Profit and loss breakdown per event. Admin and Analyst only.",
)
async def get_event_pnl(
    db: Annotated[AsyncSession, Depends(get_db)],
    _current_user: Annotated[
        User, Depends(require_role(UserRole.admin, UserRole.analyst))
    ],
):
    return await dashboard_service.get_event_pnl(db, _current_user)


@router.get(
    "/categories",
    response_model=list[CategoryBreakdownItem],
    summary="Category breakdown",
    description="Expense breakdown by category with percentages. Admin and Analyst only.",
)
async def get_category_breakdown(
    db: Annotated[AsyncSession, Depends(get_db)],
    _current_user: Annotated[
        User, Depends(require_role(UserRole.admin, UserRole.analyst))
    ],
):
    return await dashboard_service.get_category_breakdown(db, _current_user)
