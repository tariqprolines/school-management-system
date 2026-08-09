from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AcademicYearCreate(BaseModel):
    name: str
    start_date: date
    end_date: date
    is_current: bool = False


class AcademicYearUpdate(BaseModel):
    name: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool | None = None


class AcademicYearResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    start_date: date
    end_date: date
    is_current: bool


class GradeCreate(BaseModel):
    name: str
    level: int
    description: str | None = None


class GradeUpdate(BaseModel):
    name: str | None = None
    level: int | None = None
    description: str | None = None


class GradeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    level: int
    description: str | None = None


class SubjectCreate(BaseModel):
    name: str
    code: str
    subject_type: str = "core"
    description: str | None = None


class SubjectUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    subject_type: str | None = None
    description: str | None = None


class SubjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    code: str
    subject_type: str
    description: str | None = None


class ClassSectionCreate(BaseModel):
    name: str
    capacity: int = Field(default=40, ge=1)
    academic_year_id: UUID
    grade_id: UUID
    class_teacher_id: UUID | None = None


class ClassSectionUpdate(BaseModel):
    name: str | None = None
    capacity: int | None = Field(default=None, ge=1)
    academic_year_id: UUID | None = None
    grade_id: UUID | None = None
    class_teacher_id: UUID | None = None


class ClassSectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    capacity: int
    academic_year_id: UUID
    grade_id: UUID
    class_teacher_id: UUID | None = None
    grade_name: str | None = None
    academic_year_name: str | None = None
