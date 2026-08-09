from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.schemas.auth import UserCreate, UserLogin, UserResponse
from app.utils.auth_utils import create_access_token, hash_password, verify_password


class AuthService:
    @staticmethod
    async def register(db: AsyncSession, data: UserCreate) -> User:
        existing = await db.execute(select(User).where(User.email == data.email))
        if existing.scalar_one_or_none():
            raise ValueError("Email already registered")

        user = User(
            email=data.email,
            password_hash=hash_password(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
            phone=data.phone,
            role=data.role,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def login(db: AsyncSession, data: UserLogin) -> dict:
        result = await db.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()
        if not user or not verify_password(data.password, user.password_hash):
            raise ValueError("Invalid email or password")
        if not user.is_active:
            raise ValueError("Account is inactive")

        token = create_access_token(
            {"sub": user.email, "id": str(user.id), "role": user.role.value}
        )
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": UserResponse.from_orm_user(user).model_dump(),
        }

