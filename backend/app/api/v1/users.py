from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.dependencies import require_role
from app.models.user import User, UserRole
from app.schemas.user import (
    UserResponse, UserListResponse, UpdateRoleRequest, UpdateStatusRequest,
    CreateUserRequest,
)
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Admin creates a new club member with a specific role. Admin only.",
)
async def create_user(
    data: CreateUserRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.admin))],
):
    return await user_service.create_user(
        db, data.name, data.email, data.password,
        data.role, data.assigned_event_id, current_user,
    )


@router.get(
    "",
    response_model=UserListResponse,
    summary="List all users",
    description="List all registered users. Accessible by Admin and Analyst.",
)
async def list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    _current_user: Annotated[
        User, Depends(require_role(UserRole.admin, UserRole.analyst))
    ],
):
    users, total = await user_service.list_users(db)
    return UserListResponse(users=users, total=total)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Get a specific user's details. Accessible by Admin and Analyst.",
)
async def get_user(
    user_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current_user: Annotated[
        User, Depends(require_role(UserRole.admin, UserRole.analyst))
    ],
):
    return await user_service.get_user(db, user_id)


@router.patch(
    "/{user_id}/role",
    response_model=UserResponse,
    summary="Update user role",
    description="Change a user's role. Admin only.",
)
async def update_role(
    user_id: UUID,
    data: UpdateRoleRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.admin))],
):
    return await user_service.update_role(db, user_id, data.role, current_user)


@router.patch(
    "/{user_id}/status",
    response_model=UserResponse,
    summary="Activate/deactivate user",
    description="Activate or deactivate a user account. Admin only.",
)
async def update_status(
    user_id: UUID,
    data: UpdateStatusRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(UserRole.admin))],
):
    return await user_service.update_status(db, user_id, data.is_active, current_user)
