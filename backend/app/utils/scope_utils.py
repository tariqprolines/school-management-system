from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.academic import ClassSection
from app.models.people import Guardian, Student, StudentEnrollment, SubjectAssignment, Teacher
from app.models.timetable import TimetableSlot
from app.models.user import User, UserRole


class ScopeService:
    @staticmethod
    async def get_parent_student_ids(db: AsyncSession, parent_email: str) -> list[UUID]:
        result = await db.execute(select(Guardian.student_id).where(Guardian.email == parent_email))
        return list({row[0] for row in result.all()})

    @staticmethod
    async def get_student_id_for_user(db: AsyncSession, user_id: UUID) -> UUID | None:
        result = await db.execute(select(Student.id).where(Student.user_id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_teacher_id_for_user(db: AsyncSession, user_id: UUID) -> UUID | None:
        result = await db.execute(select(Teacher.id).where(Teacher.user_id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_teacher_section_ids(db: AsyncSession, teacher_id: UUID) -> set[UUID]:
        section_ids: set[UUID] = set()

        class_teacher = await db.execute(
            select(ClassSection.id).where(ClassSection.class_teacher_id == teacher_id)
        )
        section_ids.update(row[0] for row in class_teacher.all())

        assignments = await db.execute(
            select(SubjectAssignment.class_section_id).where(SubjectAssignment.teacher_id == teacher_id)
        )
        section_ids.update(row[0] for row in assignments.all())

        slots = await db.execute(
            select(TimetableSlot.class_section_id).where(TimetableSlot.teacher_id == teacher_id)
        )
        section_ids.update(row[0] for row in slots.all())

        return section_ids

    @staticmethod
    async def get_accessible_student_ids(db: AsyncSession, user: User) -> list[UUID] | None:
        """Return None for unrestricted school-wide access."""
        if user.role in (UserRole.super_admin, UserRole.admin, UserRole.accountant):
            return None

        if user.role == UserRole.student:
            student_id = await ScopeService.get_student_id_for_user(db, user.id)
            return [student_id] if student_id else []

        if user.role == UserRole.parent:
            return await ScopeService.get_parent_student_ids(db, user.email)

        if user.role == UserRole.teacher:
            teacher_id = await ScopeService.get_teacher_id_for_user(db, user.id)
            if not teacher_id:
                return []

            section_ids = await ScopeService.get_teacher_section_ids(db, teacher_id)
            if not section_ids:
                return []

            result = await db.execute(
                select(StudentEnrollment.student_id).where(
                    StudentEnrollment.class_section_id.in_(section_ids),
                    StudentEnrollment.is_active.is_(True),
                )
            )
            return list({row[0] for row in result.all()})

        return []

    @staticmethod
    async def can_access_student(db: AsyncSession, user: User, student_id: UUID) -> bool:
        allowed = await ScopeService.get_accessible_student_ids(db, user)
        if allowed is None:
            return True
        return student_id in allowed

    @staticmethod
    async def get_accessible_section_ids(db: AsyncSession, user: User) -> list[UUID] | None:
        if user.role in (UserRole.super_admin, UserRole.admin, UserRole.accountant):
            return None

        if user.role == UserRole.student:
            student_id = await ScopeService.get_student_id_for_user(db, user.id)
            if not student_id:
                return []
            result = await db.execute(
                select(StudentEnrollment.class_section_id).where(
                    StudentEnrollment.student_id == student_id,
                    StudentEnrollment.is_active.is_(True),
                )
            )
            return [row[0] for row in result.all()]

        if user.role == UserRole.parent:
            student_ids = await ScopeService.get_parent_student_ids(db, user.email)
            if not student_ids:
                return []
            result = await db.execute(
                select(StudentEnrollment.class_section_id).where(
                    StudentEnrollment.student_id.in_(student_ids),
                    StudentEnrollment.is_active.is_(True),
                )
            )
            return list({row[0] for row in result.all()})

        if user.role == UserRole.teacher:
            teacher_id = await ScopeService.get_teacher_id_for_user(db, user.id)
            if not teacher_id:
                return []
            return list(await ScopeService.get_teacher_section_ids(db, teacher_id))

        return []
