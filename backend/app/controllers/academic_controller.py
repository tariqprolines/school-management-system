from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.schemas.academic import (
    AcademicYearCreate,
    AcademicYearUpdate,
    ClassSectionCreate,
    ClassSectionUpdate,
    GradeCreate,
    GradeUpdate,
    SubjectCreate,
    SubjectUpdate,
)
from app.services.academic_service import AcademicService
from app.utils.auth_utils import AdminUser, StaffUser, validate_api_key
from app.utils.responses import success_response

router = APIRouter(prefix="/academic", tags=["Academic"], dependencies=[Depends(validate_api_key)])


@router.get("/years")
async def list_academic_years(_current_user: StaffUser, db: AsyncSession = Depends(get_db)):
    years = await AcademicService.list_academic_years(db)
    return success_response(years, "Academic years fetched")


@router.post("/years")
async def create_academic_year(data: AcademicYearCreate, _current_user: AdminUser, db: AsyncSession = Depends(get_db)):
    try:
        year = await AcademicService.create_academic_year(db, data)
        return success_response(year, "Academic year created", 201)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.patch("/years/{year_id}")
async def update_academic_year(
    year_id: UUID, data: AcademicYearUpdate, _current_user: AdminUser, db: AsyncSession = Depends(get_db)
):
    try:
        year = await AcademicService.update_academic_year(db, year_id, data)
        return success_response(year, "Academic year updated")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/years/{year_id}")
async def delete_academic_year(year_id: UUID, _current_user: AdminUser, db: AsyncSession = Depends(get_db)):
    try:
        await AcademicService.delete_academic_year(db, year_id)
        return success_response(None, "Academic year deleted")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/grades")
async def list_grades(_current_user: StaffUser, db: AsyncSession = Depends(get_db)):
    grades = await AcademicService.list_grades(db)
    return success_response(grades, "Grades fetched")


@router.post("/grades")
async def create_grade(data: GradeCreate, _current_user: AdminUser, db: AsyncSession = Depends(get_db)):
    try:
        grade = await AcademicService.create_grade(db, data)
        return success_response(grade, "Grade created", 201)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.patch("/grades/{grade_id}")
async def update_grade(grade_id: UUID, data: GradeUpdate, _current_user: AdminUser, db: AsyncSession = Depends(get_db)):
    try:
        grade = await AcademicService.update_grade(db, grade_id, data)
        return success_response(grade, "Grade updated")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/grades/{grade_id}")
async def delete_grade(grade_id: UUID, _current_user: AdminUser, db: AsyncSession = Depends(get_db)):
    try:
        await AcademicService.delete_grade(db, grade_id)
        return success_response(None, "Grade deleted")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/subjects")
async def list_subjects(_current_user: StaffUser, db: AsyncSession = Depends(get_db)):
    subjects = await AcademicService.list_subjects(db)
    return success_response(subjects, "Subjects fetched")


@router.post("/subjects")
async def create_subject(data: SubjectCreate, _current_user: AdminUser, db: AsyncSession = Depends(get_db)):
    try:
        subject = await AcademicService.create_subject(db, data)
        return success_response(subject, "Subject created", 201)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.patch("/subjects/{subject_id}")
async def update_subject(
    subject_id: UUID, data: SubjectUpdate, _current_user: AdminUser, db: AsyncSession = Depends(get_db)
):
    try:
        subject = await AcademicService.update_subject(db, subject_id, data)
        return success_response(subject, "Subject updated")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/subjects/{subject_id}")
async def delete_subject(subject_id: UUID, _current_user: AdminUser, db: AsyncSession = Depends(get_db)):
    try:
        await AcademicService.delete_subject(db, subject_id)
        return success_response(None, "Subject deleted")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/class-sections")
async def list_class_sections(
    _current_user: StaffUser,
    academic_year_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    sections = await AcademicService.list_class_sections(db, academic_year_id)
    return success_response(sections, "Class sections fetched")


@router.post("/class-sections")
async def create_class_section(data: ClassSectionCreate, _current_user: AdminUser, db: AsyncSession = Depends(get_db)):
    section = await AcademicService.create_class_section(db, data)
    return success_response(section, "Class section created", 201)


@router.patch("/class-sections/{section_id}")
async def update_class_section(
    section_id: UUID, data: ClassSectionUpdate, _current_user: AdminUser, db: AsyncSession = Depends(get_db)
):
    try:
        section = await AcademicService.update_class_section(db, section_id, data)
        return success_response(section, "Class section updated")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/class-sections/{section_id}")
async def delete_class_section(section_id: UUID, _current_user: AdminUser, db: AsyncSession = Depends(get_db)):
    try:
        await AcademicService.delete_class_section(db, section_id)
        return success_response(None, "Class section deleted")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/class-sections/{section_id}/students")
async def get_class_students(section_id: UUID, _current_user: StaffUser, db: AsyncSession = Depends(get_db)):
    students = await AcademicService.get_class_section_students(db, section_id)
    return success_response(students, "Class students fetched")
