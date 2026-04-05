from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.user import User, UserRole
from app.models.audit_log import AuditAction, ResourceType
from app.services.audit_service import create_audit_log


async def list_users(db: AsyncSession) -> tuple[list[User], int]:
    """List all users with total count."""
    count_result = await db.execute(select(func.count(User.id)))
    total = count_result.scalar() or 0

    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = list(result.scalars().all())
    return users, total


async def create_user(
    db: AsyncSession, name: str, email: str, password: str,
    role: UserRole, assigned_event_id, actor: User
) -> User:
    """Admin creates a new user with a specific role."""
    from app.core.security import hash_password

    existing = await db.execute(select(User).where(User.email == email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "CONFLICT",
                    "message": f"A user with email '{email}' already exists.",
                    "details": None,
                }
            },
        )

    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role=role,
        assigned_event_id=assigned_event_id,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    await create_audit_log(
        db=db,
        actor_id=actor.id,
        action=AuditAction.created,
        resource_type=ResourceType.user,
        resource_id=user.id,
        new_data={"name": name, "email": email, "role": role.value},
    )

    return user



async def get_user(db: AsyncSession, user_id: UUID) -> User:
    """Get a single user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": "User not found.",
                    "details": None,
                }
            },
        )
    return user


async def update_role(
    db: AsyncSession, user_id: UUID, new_role: UserRole, actor: User
) -> User:
    """Update a user's role. Only Admin can do this."""
    user = await get_user(db, user_id)

    if user.id == actor.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "BAD_REQUEST",
                    "message": "You cannot change your own role.",
                    "details": None,
                }
            },
        )

    old_role = user.role.value
    user.role = new_role
    await db.flush()
    await db.refresh(user)

    await create_audit_log(
        db=db,
        actor_id=actor.id,
        action=AuditAction.role_changed,
        resource_type=ResourceType.user,
        resource_id=user.id,
        old_data={"role": old_role},
        new_data={"role": new_role.value},
    )

    return user


async def update_status(
    db: AsyncSession, user_id: UUID, is_active: bool, actor: User
) -> User:
    """Activate or deactivate a user. Only Admin can do this."""
    user = await get_user(db, user_id)

    if user.id == actor.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "BAD_REQUEST",
                    "message": "You cannot change your own status.",
                    "details": None,
                }
            },
        )

    old_status = user.is_active
    user.is_active = is_active
    await db.flush()
    await db.refresh(user)

    action = AuditAction.user_activated if is_active else AuditAction.user_deactivated
    await create_audit_log(
        db=db,
        actor_id=actor.id,
        action=action,
        resource_type=ResourceType.user,
        resource_id=user.id,
        old_data={"is_active": old_status},
        new_data={"is_active": is_active},
    )

    return user
