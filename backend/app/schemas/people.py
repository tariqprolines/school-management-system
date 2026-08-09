from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.people import Gender, StudentStatus


class TeacherCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    first_name: str
    last_name: str
    phone: str | None = None
    department: str
    qualification: str | None = None
    joining_date: date
    address: str | None = None


class TeacherUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    department: str | None = None
    qualification: str | None = None
    address: str | None = None
    phone: str | None = None


class TeacherResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    employee_id: str
    department: str
    qualification: str | None
    joining_date: date
    address: str | None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None


class GuardianCreate(BaseModel):
    name: str
    relationship_type: str
    phone: str
    email: EmailStr | None = None
    occupation: str | None = None
    is_primary: bool = False


class GuardianResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    relationship_type: str
    phone: str
    email: str | None
    occupation: str | None
    is_primary: bool


class StudentCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr | None = None
    date_of_birth: date
    gender: Gender
    blood_group: str | None = None
    address: str | None = None
    admission_date: date
    guardians: list[GuardianCreate] = []


class StudentUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    blood_group: str | None = None
    address: str | None = None
    status: StudentStatus | None = None


class StudentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    admission_no: str
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    date_of_birth: date
    gender: Gender
    blood_group: str | None
    address: str | None
    status: StudentStatus
    admission_date: date
    guardians: list[GuardianResponse] = []
    class_section_name: str | None = None


class EnrollmentCreate(BaseModel):
    class_section_id: UUID
    enrollment_date: date


class SubjectAssignmentCreate(BaseModel):
    subject_id: UUID
    class_section_id: UUID


class SubjectAssignmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    teacher_id: UUID
    subject_id: UUID
    class_section_id: UUID
    subject_name: str | None = None
    class_section_name: str | None = None
