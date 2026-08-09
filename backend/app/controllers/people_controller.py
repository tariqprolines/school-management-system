from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.models.user import UserRole
from app.schemas.people import (
    EnrollmentCreate,
    GuardianCreate,
    StudentCreate,
    StudentUpdate,
    SubjectAssignmentCreate,
    TeacherCreate,
    TeacherUpdate,
)
from app.services.people_service import StudentService, TeacherService
from app.utils.auth_utils import AdminUser, CurrentUser, PortalUser, StaffUser, validate_api_key
from app.utils.responses import success_response
from app.utils.scope_utils import ScopeService

router = APIRouter(tags=["People"], dependencies=[Depends(validate_api_key)])


@router.get("/teachers")
async def list_teachers(
    _current_user: AdminUser,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    total, teachers = await TeacherService.list_teachers(db, page, per_page, search)
    return success_response(
        {"page": page, "per_page": per_page, "total_records": total, "data": teachers},
        "Teachers fetched",
    )


@router.get("/teachers/me")
async def get_my_teacher_profile(current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    if current_user.role != UserRole.teacher:
        raise HTTPException(status_code=403, detail="Only teachers can access this endpoint")
    teacher = await TeacherService.get_teacher_by_user_id(db, current_user.id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found")
    return success_response(teacher, "Teacher profile fetched")


@router.post("/teachers")
async def create_teacher(data: TeacherCreate, _current_user: AdminUser, db: AsyncSession = Depends(get_db)):
    try:
        teacher = await TeacherService.create_teacher(db, data)
        return success_response(teacher, "Teacher created", 201)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/teachers/{teacher_id}")
async def get_teacher(teacher_id: UUID, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    if current_user.role == UserRole.teacher:
        own = await TeacherService.get_teacher_by_user_id(db, current_user.id)
        if not own or str(own["id"]) != str(teacher_id):
            raise HTTPException(status_code=403, detail="Teachers can only view their own profile")
    elif current_user.role not in (UserRole.admin, UserRole.super_admin, UserRole.accountant):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    teacher = await TeacherService.get_teacher(db, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return success_response(teacher, "Teacher fetched")


@router.patch("/teachers/{teacher_id}")
async def update_teacher(
    teacher_id: UUID, data: TeacherUpdate, _current_user: AdminUser, db: AsyncSession = Depends(get_db)
):
    try:
        teacher = await TeacherService.update_teacher(db, teacher_id, data)
        return success_response(teacher, "Teacher updated")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.delete("/teachers/{teacher_id}")
async def delete_teacher(teacher_id: UUID, _current_user: AdminUser, db: AsyncSession = Depends(get_db)):
    try:
        await TeacherService.delete_teacher(db, teacher_id)
        return success_response(None, "Teacher deleted")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/teachers/{teacher_id}/subjects")
async def assign_subject(
    teacher_id: UUID, data: SubjectAssignmentCreate, _current_user: AdminUser, db: AsyncSession = Depends(get_db)
):
    assignment = await TeacherService.assign_subject(db, teacher_id, data)
    return success_response(assignment, "Subject assigned", 201)


@router.get("/teachers/{teacher_id}/subjects")
async def list_teacher_subjects(teacher_id: UUID, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    if current_user.role == UserRole.teacher:
        own = await TeacherService.get_teacher_by_user_id(db, current_user.id)
        if not own or str(own["id"]) != str(teacher_id):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
    elif current_user.role not in (UserRole.admin, UserRole.super_admin):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    assignments = await TeacherService.list_assignments(db, teacher_id)
    return success_response(assignments, "Teacher subjects fetched")


@router.delete("/teachers/{teacher_id}/subjects/{assignment_id}")
async def delete_teacher_subject(
    teacher_id: UUID, assignment_id: UUID, _current_user: AdminUser, db: AsyncSession = Depends(get_db)
):
    try:
        await TeacherService.delete_assignment(db, teacher_id, assignment_id)
        return success_response(None, "Subject assignment removed")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("/students/me")
async def get_my_student_profile(current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    if current_user.role != UserRole.student:
        raise HTTPException(status_code=403, detail="Only students can access this endpoint")
    student = await StudentService.get_student_by_user_id(db, current_user.id)
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return success_response(student, "Student profile fetched")


@router.get("/students")
async def list_students(
    current_user: PortalUser,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    student_ids = await ScopeService.get_accessible_student_ids(db, current_user)
    total, students = await StudentService.list_students(db, page, per_page, search, student_ids)
    return success_response(
        {"page": page, "per_page": per_page, "total_records": total, "data": students},
        "Students fetched",
    )


@router.post("/students")
async def create_student(data: StudentCreate, _current_user: AdminUser, db: AsyncSession = Depends(get_db)):
    try:
        student = await StudentService.create_student(db, data)
        return success_response(student, "Student created", 201)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/students/{student_id}")
async def get_student(student_id: UUID, current_user: PortalUser, db: AsyncSession = Depends(get_db)):
    if not await ScopeService.can_access_student(db, current_user, student_id):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    student = await StudentService.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return success_response(student, "Student fetched")


@router.patch("/students/{student_id}")
async def update_student(
    student_id: UUID, data: StudentUpdate, _current_user: AdminUser, db: AsyncSession = Depends(get_db)
):
    try:
        student = await StudentService.update_student(db, student_id, data)
        return success_response(student, "Student updated")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.delete("/students/{student_id}")
async def delete_student(student_id: UUID, _current_user: AdminUser, db: AsyncSession = Depends(get_db)):
    try:
        await StudentService.delete_student(db, student_id)
        return success_response(None, "Student deleted")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/students/{student_id}/guardians")
async def add_guardian(
    student_id: UUID, data: GuardianCreate, _current_user: AdminUser, db: AsyncSession = Depends(get_db)
):
    student = await StudentService.add_guardian(db, student_id, data)
    return success_response(student, "Guardian added", 201)


@router.post("/students/{student_id}/enroll")
async def enroll_student(
    student_id: UUID, data: EnrollmentCreate, _current_user: AdminUser, db: AsyncSession = Depends(get_db)
):
    student = await StudentService.enroll_student(db, student_id, data)
    return success_response(student, "Student enrolled", 201)
