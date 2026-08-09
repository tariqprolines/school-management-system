from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.people import Student, StudentEnrollment, SubjectAssignment, Teacher
from app.models.user import User, UserRole
from app.schemas.people import (
    EnrollmentCreate,
    GuardianCreate,
    StudentCreate,
    StudentUpdate,
    SubjectAssignmentCreate,
    TeacherCreate,
    TeacherUpdate,
)
from app.utils.auth_utils import hash_password


class TeacherService:
    @staticmethod
    async def _next_employee_id(db: AsyncSession) -> str:
        result = await db.execute(select(func.count(Teacher.id)))
        count = result.scalar() or 0
        return f"EMP{count + 1:05d}"

    @staticmethod
    async def list_teachers(db: AsyncSession, page: int = 1, per_page: int = 20, search: str | None = None):
        query = select(Teacher).join(User, Teacher.user_id == User.id)
        if search:
            query = query.where(
                User.first_name.ilike(f"%{search}%")
                | User.last_name.ilike(f"%{search}%")
                | Teacher.employee_id.ilike(f"%{search}%")
            )
        count_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar() or 0
        result = await db.execute(
            query.options(selectinload(Teacher.user))
            .order_by(Teacher.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        teachers = []
        for teacher in result.scalars().all():
            teachers.append(TeacherService._to_response(teacher))
        return total, teachers

    @staticmethod
    def _to_response(teacher: Teacher) -> dict:
        return {
            "id": teacher.id,
            "employee_id": teacher.employee_id,
            "department": teacher.department,
            "qualification": teacher.qualification,
            "joining_date": teacher.joining_date,
            "address": teacher.address,
            "first_name": teacher.user.first_name if teacher.user else None,
            "last_name": teacher.user.last_name if teacher.user else None,
            "email": teacher.user.email if teacher.user else None,
            "phone": teacher.user.phone if teacher.user else None,
        }

    @staticmethod
    async def get_teacher_by_user_id(db: AsyncSession, user_id: UUID) -> dict | None:
        result = await db.execute(
            select(Teacher).options(selectinload(Teacher.user)).where(Teacher.user_id == user_id)
        )
        teacher = result.scalar_one_or_none()
        return TeacherService._to_response(teacher) if teacher else None

    @staticmethod
    async def get_teacher(db: AsyncSession, teacher_id: UUID) -> dict | None:
        result = await db.execute(
            select(Teacher).options(selectinload(Teacher.user)).where(Teacher.id == teacher_id)
        )
        teacher = result.scalar_one_or_none()
        return TeacherService._to_response(teacher) if teacher else None

    @staticmethod
    async def create_teacher(db: AsyncSession, data: TeacherCreate) -> dict:
        existing = await db.execute(select(User).where(User.email == data.email))
        if existing.scalar_one_or_none():
            raise ValueError("Email already exists")

        user = User(
            email=data.email,
            password_hash=hash_password(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
            phone=data.phone,
            role=UserRole.teacher,
        )
        db.add(user)
        await db.flush()

        teacher = Teacher(
            user_id=user.id,
            employee_id=await TeacherService._next_employee_id(db),
            department=data.department,
            qualification=data.qualification,
            joining_date=data.joining_date,
            address=data.address,
        )
        db.add(teacher)
        await db.commit()
        await db.refresh(teacher)
        result = await db.execute(
            select(Teacher).options(selectinload(Teacher.user)).where(Teacher.id == teacher.id)
        )
        return TeacherService._to_response(result.scalar_one())

    @staticmethod
    async def update_teacher(db: AsyncSession, teacher_id: UUID, data: TeacherUpdate) -> dict:
        result = await db.execute(
            select(Teacher).options(selectinload(Teacher.user)).where(Teacher.id == teacher_id)
        )
        teacher = result.scalar_one_or_none()
        if not teacher:
            raise ValueError("Teacher not found")

        for field, value in data.model_dump(exclude_unset=True).items():
            if field in ("first_name", "last_name", "phone") and teacher.user:
                setattr(teacher.user, field, value)
            elif hasattr(teacher, field):
                setattr(teacher, field, value)

        await db.commit()
        await db.refresh(teacher)
        return TeacherService._to_response(teacher)

    @staticmethod
    async def delete_teacher(db: AsyncSession, teacher_id: UUID) -> None:
        from app.models.academic import ClassSection
        from app.models.timetable import TimetableSlot

        result = await db.execute(
            select(Teacher).options(selectinload(Teacher.user)).where(Teacher.id == teacher_id)
        )
        teacher = result.scalar_one_or_none()
        if not teacher:
            raise ValueError("Teacher not found")

        sections = await db.execute(select(ClassSection).where(ClassSection.class_teacher_id == teacher_id))
        for section in sections.scalars().all():
            section.class_teacher_id = None

        assignments = await db.execute(select(SubjectAssignment).where(SubjectAssignment.teacher_id == teacher_id))
        for assignment in assignments.scalars().all():
            await db.delete(assignment)

        slots = await db.execute(select(TimetableSlot).where(TimetableSlot.teacher_id == teacher_id))
        for slot in slots.scalars().all():
            await db.delete(slot)

        user = teacher.user
        await db.delete(teacher)
        if user:
            await db.delete(user)
        await db.commit()

    @staticmethod
    async def assign_subject(db: AsyncSession, teacher_id: UUID, data: SubjectAssignmentCreate) -> SubjectAssignment:
        assignment = SubjectAssignment(
            teacher_id=teacher_id,
            subject_id=data.subject_id,
            class_section_id=data.class_section_id,
        )
        db.add(assignment)
        await db.commit()
        await db.refresh(assignment)
        return assignment

    @staticmethod
    async def list_assignments(db: AsyncSession, teacher_id: UUID) -> list[dict]:
        from app.models.academic import ClassSection, Subject

        result = await db.execute(
            select(SubjectAssignment, Subject.name, ClassSection.name)
            .join(Subject, SubjectAssignment.subject_id == Subject.id)
            .join(ClassSection, SubjectAssignment.class_section_id == ClassSection.id)
            .where(SubjectAssignment.teacher_id == teacher_id)
        )
        return [
            {
                "id": a.id,
                "teacher_id": a.teacher_id,
                "subject_id": a.subject_id,
                "class_section_id": a.class_section_id,
                "subject_name": subject_name,
                "class_section_name": section_name,
            }
            for a, subject_name, section_name in result.all()
        ]

    @staticmethod
    async def delete_assignment(db: AsyncSession, teacher_id: UUID, assignment_id: UUID) -> None:
        result = await db.execute(
            select(SubjectAssignment).where(
                SubjectAssignment.id == assignment_id,
                SubjectAssignment.teacher_id == teacher_id,
            )
        )
        assignment = result.scalar_one_or_none()
        if not assignment:
            raise ValueError("Subject assignment not found")
        await db.delete(assignment)
        await db.commit()


class StudentService:
    @staticmethod
    async def _next_admission_no(db: AsyncSession) -> str:
        result = await db.execute(select(func.count(Student.id)))
        count = result.scalar() or 0
        return f"ADM{count + 1:05d}"

    @staticmethod
    async def list_students(
        db: AsyncSession,
        page: int = 1,
        per_page: int = 20,
        search: str | None = None,
        student_ids: list[UUID] | None = None,
    ):
        from app.models.academic import ClassSection

        query = select(Student).options(selectinload(Student.guardians), selectinload(Student.user))
        if student_ids is not None:
            if not student_ids:
                return 0, []
            query = query.where(Student.id.in_(student_ids))
        if search:
            query = query.where(Student.admission_no.ilike(f"%{search}%"))

        count_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar() or 0
        result = await db.execute(
            query.order_by(Student.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        )

        students = []
        for student in result.scalars().all():
            enrollment = await db.execute(
                select(ClassSection.name)
                .join(StudentEnrollment, StudentEnrollment.class_section_id == ClassSection.id)
                .where(StudentEnrollment.student_id == student.id, StudentEnrollment.is_active.is_(True))
                .limit(1)
            )
            section_name = enrollment.scalar_one_or_none()
            students.append(StudentService._to_response(student, section_name))

        return total, students

    @staticmethod
    def _to_response(student: Student, class_section_name: str | None = None) -> dict:
        return {
            "id": student.id,
            "admission_no": student.admission_no,
            "first_name": student.user.first_name if student.user else None,
            "last_name": student.user.last_name if student.user else None,
            "email": student.user.email if student.user else None,
            "date_of_birth": student.date_of_birth,
            "gender": student.gender,
            "blood_group": student.blood_group,
            "address": student.address,
            "status": student.status,
            "admission_date": student.admission_date,
            "guardians": [
                {
                    "id": g.id,
                    "name": g.name,
                    "relationship_type": g.relationship_type,
                    "phone": g.phone,
                    "email": g.email,
                    "occupation": g.occupation,
                    "is_primary": g.is_primary,
                }
                for g in student.guardians
            ],
            "class_section_name": class_section_name,
        }

    @staticmethod
    async def get_student(db: AsyncSession, student_id: UUID) -> dict | None:
        result = await db.execute(
            select(Student)
            .options(selectinload(Student.guardians), selectinload(Student.user))
            .where(Student.id == student_id)
        )
        student = result.scalar_one_or_none()
        if not student:
            return None
        from app.models.academic import ClassSection

        enrollment = await db.execute(
            select(ClassSection.name)
            .join(StudentEnrollment, StudentEnrollment.class_section_id == ClassSection.id)
            .where(StudentEnrollment.student_id == student.id, StudentEnrollment.is_active.is_(True))
            .limit(1)
        )
        return StudentService._to_response(student, enrollment.scalar_one_or_none())

    @staticmethod
    async def get_student_by_user_id(db: AsyncSession, user_id: UUID) -> dict | None:
        result = await db.execute(select(Student.id).where(Student.user_id == user_id))
        student_id = result.scalar_one_or_none()
        if not student_id:
            return None
        return await StudentService.get_student(db, student_id)

    @staticmethod
    async def create_student(db: AsyncSession, data: StudentCreate) -> dict:
        from app.models.people import Guardian

        user = None
        admission_no = await StudentService._next_admission_no(db)
        email = data.email or f"{admission_no.lower()}@school.local"

        existing = await db.execute(select(User).where(User.email == email))
        if existing.scalar_one_or_none():
            raise ValueError("Email already exists")

        user = User(
            email=email,
            password_hash=hash_password("student123"),
            first_name=data.first_name,
            last_name=data.last_name,
            role=UserRole.student,
        )
        db.add(user)
        await db.flush()

        student = Student(
            user_id=user.id,
            admission_no=admission_no,
            date_of_birth=data.date_of_birth,
            gender=data.gender,
            blood_group=data.blood_group,
            address=data.address,
            admission_date=data.admission_date,
        )
        db.add(student)
        await db.flush()

        for guardian_data in data.guardians:
            guardian = Guardian(student_id=student.id, **guardian_data.model_dump())
            db.add(guardian)

        await db.commit()
        return await StudentService.get_student(db, student.id)

    @staticmethod
    async def update_student(db: AsyncSession, student_id: UUID, data: StudentUpdate) -> dict:
        result = await db.execute(
            select(Student).options(selectinload(Student.user)).where(Student.id == student_id)
        )
        student = result.scalar_one_or_none()
        if not student:
            raise ValueError("Student not found")

        for field, value in data.model_dump(exclude_unset=True).items():
            if field in ("first_name", "last_name") and student.user:
                setattr(student.user, field, value)
            elif hasattr(student, field):
                setattr(student, field, value)

        await db.commit()
        return await StudentService.get_student(db, student_id)

    @staticmethod
    async def delete_student(db: AsyncSession, student_id: UUID) -> None:
        from app.models.fee import FeeInvoice
        from app.models.people import Guardian

        result = await db.execute(
            select(Student).options(selectinload(Student.user)).where(Student.id == student_id)
        )
        student = result.scalar_one_or_none()
        if not student:
            raise ValueError("Student not found")

        invoices = await db.execute(select(FeeInvoice).where(FeeInvoice.student_id == student_id))
        if invoices.scalars().first():
            raise ValueError("Cannot delete student with fee invoices. Set status to inactive instead.")

        enrollments = await db.execute(select(StudentEnrollment).where(StudentEnrollment.student_id == student_id))
        for enrollment in enrollments.scalars().all():
            await db.delete(enrollment)

        guardians = await db.execute(select(Guardian).where(Guardian.student_id == student_id))
        for guardian in guardians.scalars().all():
            await db.delete(guardian)

        user = student.user
        await db.delete(student)
        if user:
            await db.delete(user)
        await db.commit()

    @staticmethod
    async def add_guardian(db: AsyncSession, student_id: UUID, data: GuardianCreate) -> dict:
        from app.models.people import Guardian

        guardian = Guardian(student_id=student_id, **data.model_dump())
        db.add(guardian)
        await db.commit()
        return await StudentService.get_student(db, student_id)

    @staticmethod
    async def enroll_student(db: AsyncSession, student_id: UUID, data: EnrollmentCreate) -> dict:
        existing = await db.execute(
            select(StudentEnrollment).where(
                StudentEnrollment.student_id == student_id,
                StudentEnrollment.is_active.is_(True),
            )
        )
        for enrollment in existing.scalars().all():
            enrollment.is_active = False

        enrollment = StudentEnrollment(
            student_id=student_id,
            class_section_id=data.class_section_id,
            enrollment_date=data.enrollment_date,
        )
        db.add(enrollment)
        await db.commit()
        return await StudentService.get_student(db, student_id)
