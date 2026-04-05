from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.user import UserRole


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    role: UserRole
    is_active: bool
    assigned_event_id: UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int


class UpdateRoleRequest(BaseModel):
    role: UserRole = Field(..., examples=["analyst"])


class UpdateStatusRequest(BaseModel):
    is_active: bool = Field(..., examples=[False])


class CreateUserRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, examples=["Rohan Kumar"])
    email: str = Field(..., examples=["rohan@vaultix.dev"])
    password: str = Field(..., min_length=8, max_length=128, examples=["rohan123"])
    role: UserRole = Field(UserRole.viewer, examples=["analyst"])
    assigned_event_id: UUID | None = Field(None)
