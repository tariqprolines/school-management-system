import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.database import Base


class Gender(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"


class StudentStatus(str, enum.Enum):
    active = "active"
    transferred = "transferred"
    graduated = "graduated"
    inactive = "inactive"


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    employee_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    qualification: Mapped[str | None] = mapped_column(String(200), nullable=True)
    joining_date: Mapped[date] = mapped_column(Date, nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user = relationship("User")
    subject_assignments = relationship("SubjectAssignment", back_populates="teacher")
    timetable_slots = relationship("TimetableSlot", back_populates="teacher")


class Student(Base):
    __tablename__ = "students"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=True
    )
    admission_no: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[Gender] = mapped_column(Enum(Gender, name="gender"), nullable=False)
    blood_group: Mapped[str | None] = mapped_column(String(10), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[StudentStatus] = mapped_column(
        Enum(StudentStatus, name="student_status"), default=StudentStatus.active, nullable=False
    )
    admission_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user = relationship("User")
    guardians = relationship("Guardian", back_populates="student", cascade="all, delete-orphan")
    enrollments = relationship("StudentEnrollment", back_populates="student")
    fee_invoices = relationship("FeeInvoice", back_populates="student")


class Guardian(Base):
    __tablename__ = "guardians"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(50), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    occupation: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_primary: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="guardians")


class StudentEnrollment(Base):
    __tablename__ = "student_enrollments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False)
    class_section_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("class_sections.id"), nullable=False
    )
    enrollment_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="enrollments")
    class_section = relationship("ClassSection", back_populates="enrollments")


class SubjectAssignment(Base):
    __tablename__ = "subject_assignments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    teacher_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("teachers.id"), nullable=False)
    subject_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    class_section_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("class_sections.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    teacher = relationship("Teacher", back_populates="subject_assignments")
    subject = relationship("Subject", back_populates="assignments")
    class_section = relationship("ClassSection", back_populates="subject_assignments")
