from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.schemas.auth import UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService
from app.utils.auth_utils import CurrentUser, validate_api_key
from app.utils.responses import success_response

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", dependencies=[Depends(validate_api_key)])
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        user = await AuthService.register(db, data)
        return success_response(UserResponse.from_orm_user(user).model_dump(), "User registered successfully", 201)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/login", dependencies=[Depends(validate_api_key)])
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    try:
        result = await AuthService.login(db, data)
        return success_response(result, "Login successful")
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e


@router.get("/me", dependencies=[Depends(validate_api_key)])
async def get_me(current_user: CurrentUser):
    return success_response(UserResponse.from_orm_user(current_user).model_dump(), "User profile fetched")
