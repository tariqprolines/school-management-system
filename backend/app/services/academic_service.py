from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.academic import AcademicYear, ClassSection, Grade, Subject
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
from app.utils.db_errors import integrity_error_message


class AcademicService:
    @staticmethod
    async def list_academic_years(db: AsyncSession) -> list[AcademicYear]:
        result = await db.execute(select(AcademicYear).order_by(AcademicYear.start_date.desc()))
        return list(result.scalars().all())

    @staticmethod
    async def create_academic_year(db: AsyncSession, data: AcademicYearCreate) -> AcademicYear:
        if data.end_date <= data.start_date:
            raise ValueError("End date must be after start date")

        existing = await db.execute(select(AcademicYear).where(AcademicYear.name == data.name))
        if existing.scalar_one_or_none():
            raise ValueError("An academic year with this name already exists")

        if data.is_current:
            current = await db.execute(select(AcademicYear).where(AcademicYear.is_current.is_(True)))
            for year in current.scalars().all():
                year.is_current = False

        year = AcademicYear(**data.model_dump())
        db.add(year)
        try:
            await db.commit()
            await db.refresh(year)
        except IntegrityError as exc:
            await db.rollback()
            raise ValueError(integrity_error_message(exc)) from exc
        return year

    @staticmethod
    async def update_academic_year(db: AsyncSession, year_id: UUID, data: AcademicYearUpdate) -> AcademicYear:
        year = await db.get(AcademicYear, year_id)
        if not year:
            raise ValueError("Academic year not found")

        updates = data.model_dump(exclude_unset=True)
        if "name" in updates:
            existing = await db.execute(
                select(AcademicYear).where(AcademicYear.name == updates["name"], AcademicYear.id != year_id)
            )
            if existing.scalar_one_or_none():
                raise ValueError("An academic year with this name already exists")

        start = updates.get("start_date", year.start_date)
        end = updates.get("end_date", year.end_date)
        if end <= start:
            raise ValueError("End date must be after start date")

        if updates.get("is_current"):
            current = await db.execute(select(AcademicYear).where(AcademicYear.is_current.is_(True)))
            for current_year in current.scalars().all():
                if current_year.id != year_id:
                    current_year.is_current = False

        for field, value in updates.items():
            setattr(year, field, value)

        try:
            await db.commit()
            await db.refresh(year)
        except IntegrityError as exc:
            await db.rollback()
            raise ValueError(integrity_error_message(exc)) from exc
        return year

    @staticmethod
    async def delete_academic_year(db: AsyncSession, year_id: UUID) -> None:
        year = await db.get(AcademicYear, year_id)
        if not year:
            raise ValueError("Academic year not found")

        sections = await db.execute(select(ClassSection).where(ClassSection.academic_year_id == year_id))
        if sections.scalars().first():
            raise ValueError("Cannot delete academic year with linked class sections")

        await db.delete(year)
        await db.commit()

    @staticmethod
    async def list_grades(db: AsyncSession) -> list[Grade]:
        result = await db.execute(select(Grade).order_by(Grade.level))
        return list(result.scalars().all())

    @staticmethod
    async def create_grade(db: AsyncSession, data: GradeCreate) -> Grade:
        grade = Grade(**data.model_dump())
        db.add(grade)
        try:
            await db.commit()
            await db.refresh(grade)
        except IntegrityError as exc:
            await db.rollback()
            raise ValueError(integrity_error_message(exc)) from exc
        return grade

    @staticmethod
    async def update_grade(db: AsyncSession, grade_id: UUID, data: GradeUpdate) -> Grade:
        grade = await db.get(Grade, grade_id)
        if not grade:
            raise ValueError("Grade not found")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(grade, field, value)

        try:
            await db.commit()
            await db.refresh(grade)
        except IntegrityError as exc:
            await db.rollback()
            raise ValueError(integrity_error_message(exc)) from exc
        return grade

    @staticmethod
    async def delete_grade(db: AsyncSession, grade_id: UUID) -> None:
        grade = await db.get(Grade, grade_id)
        if not grade:
            raise ValueError("Grade not found")

        sections = await db.execute(select(ClassSection).where(ClassSection.grade_id == grade_id))
        if sections.scalars().first():
            raise ValueError("Cannot delete grade with linked class sections")

        await db.delete(grade)
        await db.commit()

    @staticmethod
    async def list_subjects(db: AsyncSession) -> list[Subject]:
        result = await db.execute(select(Subject).order_by(Subject.name))
        return list(result.scalars().all())

    @staticmethod
    async def create_subject(db: AsyncSession, data: SubjectCreate) -> Subject:
        subject = Subject(**data.model_dump())
        db.add(subject)
        try:
            await db.commit()
            await db.refresh(subject)
        except IntegrityError as exc:
            await db.rollback()
            raise ValueError(integrity_error_message(exc)) from exc
        return subject

    @staticmethod
    async def update_subject(db: AsyncSession, subject_id: UUID, data: SubjectUpdate) -> Subject:
        subject = await db.get(Subject, subject_id)
        if not subject:
            raise ValueError("Subject not found")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(subject, field, value)

        try:
            await db.commit()
            await db.refresh(subject)
        except IntegrityError as exc:
            await db.rollback()
            raise ValueError(integrity_error_message(exc)) from exc
        return subject

    @staticmethod
    async def delete_subject(db: AsyncSession, subject_id: UUID) -> None:
        from app.models.people import SubjectAssignment
        from app.models.timetable import TimetableSlot

        subject = await db.get(Subject, subject_id)
        if not subject:
            raise ValueError("Subject not found")

        assignments = await db.execute(select(SubjectAssignment).where(SubjectAssignment.subject_id == subject_id))
        if assignments.scalars().first():
            raise ValueError("Cannot delete subject assigned to teachers")

        slots = await db.execute(select(TimetableSlot).where(TimetableSlot.subject_id == subject_id))
        if slots.scalars().first():
            raise ValueError("Cannot delete subject used in timetable")

        await db.delete(subject)
        await db.commit()

    @staticmethod
    async def list_class_sections(db: AsyncSession, academic_year_id: UUID | None = None) -> list[dict]:
        query = (
            select(ClassSection, Grade.name, AcademicYear.name)
            .join(Grade, ClassSection.grade_id == Grade.id)
            .join(AcademicYear, ClassSection.academic_year_id == AcademicYear.id)
        )
        if academic_year_id:
            query = query.where(ClassSection.academic_year_id == academic_year_id)
        result = await db.execute(query.order_by(ClassSection.name))
        sections = []
        for section, grade_name, year_name in result.all():
            sections.append(
                {
                    "id": section.id,
                    "name": section.name,
                    "capacity": section.capacity,
                    "academic_year_id": section.academic_year_id,
                    "grade_id": section.grade_id,
                    "class_teacher_id": section.class_teacher_id,
                    "grade_name": grade_name,
                    "academic_year_name": year_name,
                }
            )
        return sections

    @staticmethod
    async def create_class_section(db: AsyncSession, data: ClassSectionCreate) -> ClassSection:
        section = ClassSection(**data.model_dump())
        db.add(section)
        await db.commit()
        await db.refresh(section)
        return section

    @staticmethod
    async def update_class_section(db: AsyncSession, section_id: UUID, data: ClassSectionUpdate) -> ClassSection:
        section = await db.get(ClassSection, section_id)
        if not section:
            raise ValueError("Class section not found")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(section, field, value)

        try:
            await db.commit()
            await db.refresh(section)
        except IntegrityError as exc:
            await db.rollback()
            raise ValueError(integrity_error_message(exc)) from exc
        return section

    @staticmethod
    async def delete_class_section(db: AsyncSession, section_id: UUID) -> None:
        from app.models.fee import FeeStructure
        from app.models.people import StudentEnrollment, SubjectAssignment
        from app.models.timetable import TimetableSlot

        section = await db.get(ClassSection, section_id)
        if not section:
            raise ValueError("Class section not found")

        if (await db.execute(select(StudentEnrollment).where(StudentEnrollment.class_section_id == section_id))).scalars().first():
            raise ValueError("Cannot delete class section with enrolled students")
        if (await db.execute(select(TimetableSlot).where(TimetableSlot.class_section_id == section_id))).scalars().first():
            raise ValueError("Cannot delete class section with timetable slots")
        if (await db.execute(select(FeeStructure).where(FeeStructure.class_section_id == section_id))).scalars().first():
            raise ValueError("Cannot delete class section with fee structures")
        if (await db.execute(select(SubjectAssignment).where(SubjectAssignment.class_section_id == section_id))).scalars().first():
            raise ValueError("Cannot delete class section with subject assignments")

        await db.delete(section)
        await db.commit()

    @staticmethod
    async def get_class_section_students(db: AsyncSession, section_id: UUID) -> list[dict]:
        from app.models.people import Student, StudentEnrollment

        result = await db.execute(
            select(Student, StudentEnrollment)
            .join(StudentEnrollment, StudentEnrollment.student_id == Student.id)
            .where(
                StudentEnrollment.class_section_id == section_id,
                StudentEnrollment.is_active.is_(True),
            )
        )
        students = []
        for student, _ in result.all():
            students.append(
                {
                    "id": student.id,
                    "admission_no": student.admission_no,
                    "date_of_birth": student.date_of_birth,
                    "gender": student.gender,
                    "status": student.status,
                }
            )
        return students
