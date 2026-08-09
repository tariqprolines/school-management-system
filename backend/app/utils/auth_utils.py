from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.config.settings import settings
from app.models.user import User, UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer()
api_key_scheme = APIKeyHeader(name="X-Access-Token")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def validate_api_key(api_key: str = Security(api_key_scheme)) -> bool:
    if api_key != settings.API_ACCESS_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user


def require_roles(*roles: UserRole):
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles and current_user.role != UserRole.super_admin:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user

    return role_checker


CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(require_roles(UserRole.admin, UserRole.super_admin))]
FinanceUser = Annotated[
    User,
    Depends(require_roles(UserRole.admin, UserRole.super_admin, UserRole.accountant)),
]
StaffUser = Annotated[
    User,
    Depends(require_roles(UserRole.admin, UserRole.super_admin, UserRole.teacher, UserRole.accountant)),
]
PortalUser = Annotated[
    User,
    Depends(
        require_roles(
            UserRole.admin,
            UserRole.super_admin,
            UserRole.teacher,
            UserRole.accountant,
            UserRole.parent,
            UserRole.student,
        )
    ),
]
