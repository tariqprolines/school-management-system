from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.services.dashboard_service import DashboardService
from app.utils.auth_utils import StaffUser, validate_api_key
from app.utils.responses import success_response

router = APIRouter(prefix="/dashboard", tags=["Dashboard"], dependencies=[Depends(validate_api_key)])


@router.get("/summary")
async def get_dashboard_summary(_current_user: StaffUser, db: AsyncSession = Depends(get_db)):
    summary = await DashboardService.get_summary(db)
    return success_response(summary.model_dump(), "Dashboard summary fetched")
