from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, examples=["Rahul Sharma"])
    email: EmailStr = Field(..., examples=["rahul@vaultix.dev"])
    password: str = Field(..., min_length=8, max_length=128, examples=["securepass123"])


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., examples=["admin@vaultix.dev"])
    password: str = Field(..., examples=["admin123"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
