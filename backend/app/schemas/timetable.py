from datetime import time
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TimetableSlotCreate(BaseModel):
    class_section_id: UUID
    subject_id: UUID
    teacher_id: UUID
    day_of_week: int = Field(ge=0, le=6)
    start_time: time
    end_time: time
    room: str | None = None


class TimetableSlotUpdate(BaseModel):
    class_section_id: UUID | None = None
    subject_id: UUID | None = None
    teacher_id: UUID | None = None
    day_of_week: int | None = Field(default=None, ge=0, le=6)
    start_time: time | None = None
    end_time: time | None = None
    room: str | None = None


class TimetableSlotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    class_section_id: UUID
    subject_id: UUID
    teacher_id: UUID
    day_of_week: int
    start_time: time
    end_time: time
    room: str | None
    subject_name: str | None = None
    teacher_name: str | None = None
    class_section_name: str | None = None


class ConflictCheckResponse(BaseModel):
    has_conflict: bool
    conflicts: list[str] = []
