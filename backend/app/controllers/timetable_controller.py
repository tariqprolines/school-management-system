from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.schemas.timetable import TimetableSlotCreate, TimetableSlotUpdate
from app.services.timetable_service import TimetableService
from app.utils.auth_utils import AdminUser, PortalUser, validate_api_key
from app.utils.responses import success_response
from app.utils.scope_utils import ScopeService

router = APIRouter(prefix="/timetable", tags=["Timetable"], dependencies=[Depends(validate_api_key)])


@router.get("/slots")
async def list_slots(
    current_user: PortalUser,
    class_section_id: UUID | None = None,
    teacher_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    allowed_sections = await ScopeService.get_accessible_section_ids(db, current_user)

    if class_section_id and allowed_sections is not None and class_section_id not in allowed_sections:
        raise HTTPException(status_code=403, detail="Insufficient permissions for this class section")

    section_filter = None
    if allowed_sections is not None and not class_section_id and not teacher_id:
        section_filter = allowed_sections

    slots = await TimetableService.list_slots(db, class_section_id, teacher_id, section_filter)
    return success_response(slots, "Timetable slots fetched")


@router.post("/slots")
async def create_slot(data: TimetableSlotCreate, _current_user: AdminUser, db: AsyncSession = Depends(get_db)):
    try:
        slot = await TimetableService.create_slot(db, data)
        return success_response(slot, "Timetable slot created", 201)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.patch("/slots/{slot_id}")
async def update_slot(
    slot_id: UUID, data: TimetableSlotUpdate, _current_user: AdminUser, db: AsyncSession = Depends(get_db)
):
    try:
        slot = await TimetableService.update_slot(db, slot_id, data)
        return success_response(slot, "Timetable slot updated")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/slots/{slot_id}")
async def delete_slot(slot_id: UUID, _current_user: AdminUser, db: AsyncSession = Depends(get_db)):
    try:
        await TimetableService.delete_slot(db, slot_id)
        return success_response(None, "Timetable slot deleted")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/check-conflicts")
async def check_conflicts(data: TimetableSlotCreate, _current_user: AdminUser, db: AsyncSession = Depends(get_db)):
    result = await TimetableService.check_conflicts(db, data)
    return success_response(result, "Conflict check completed")


@router.get("/class/{section_id}")
async def get_class_timetable(section_id: UUID, current_user: PortalUser, db: AsyncSession = Depends(get_db)):
    allowed_sections = await ScopeService.get_accessible_section_ids(db, current_user)
    if allowed_sections is not None and section_id not in allowed_sections:
        raise HTTPException(status_code=403, detail="Insufficient permissions for this class section")
    slots = await TimetableService.list_slots(db, class_section_id=section_id)
    return success_response(slots, "Class timetable fetched")
