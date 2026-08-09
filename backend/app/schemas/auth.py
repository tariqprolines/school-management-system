from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


class PaginatedResult(BaseModel, Generic[T]):
    page: int
    per_page: int
    total_records: int
    data: list[T]


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    first_name: str
    last_name: str
    phone: str | None = None
    role: UserRole


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    first_name: str
    last_name: str
    phone: str | None
    role: UserRole
    is_active: bool

    @classmethod
    def from_orm_user(cls, user) -> "UserResponse":
        return cls(
            id=str(user.id),
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            role=user.role,
            is_active=user.is_active,
        )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
