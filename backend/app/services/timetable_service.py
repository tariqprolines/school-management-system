from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.academic import ClassSection, Subject
from app.models.people import Teacher
from app.models.timetable import TimetableSlot
from app.schemas.timetable import TimetableSlotCreate, TimetableSlotUpdate


class TimetableService:
    @staticmethod
    async def _check_conflicts(db: AsyncSession, data: TimetableSlotCreate, exclude_id: UUID | None = None) -> list[str]:
        conflicts = []

        teacher_query = select(TimetableSlot).where(
            TimetableSlot.teacher_id == data.teacher_id,
            TimetableSlot.day_of_week == data.day_of_week,
            TimetableSlot.start_time < data.end_time,
            TimetableSlot.end_time > data.start_time,
        )
        if exclude_id:
            teacher_query = teacher_query.where(TimetableSlot.id != exclude_id)
        teacher_conflict = await db.execute(teacher_query)
        if teacher_conflict.scalars().first():
            conflicts.append("Teacher is already scheduled at this time")

        if data.room:
            room_query = select(TimetableSlot).where(
                TimetableSlot.room == data.room,
                TimetableSlot.day_of_week == data.day_of_week,
                TimetableSlot.start_time < data.end_time,
                TimetableSlot.end_time > data.start_time,
            )
            if exclude_id:
                room_query = room_query.where(TimetableSlot.id != exclude_id)
            room_conflict = await db.execute(room_query)
            if room_conflict.scalars().first():
                conflicts.append(f"Room {data.room} is already booked at this time")

        section_query = select(TimetableSlot).where(
            TimetableSlot.class_section_id == data.class_section_id,
            TimetableSlot.day_of_week == data.day_of_week,
            TimetableSlot.start_time < data.end_time,
            TimetableSlot.end_time > data.start_time,
        )
        if exclude_id:
            section_query = section_query.where(TimetableSlot.id != exclude_id)
        section_conflict = await db.execute(section_query)
        if section_conflict.scalars().first():
            conflicts.append("Class section already has a slot at this time")

        return conflicts

    @staticmethod
    async def create_slot(db: AsyncSession, data: TimetableSlotCreate) -> TimetableSlot:
        conflicts = await TimetableService._check_conflicts(db, data)
        if conflicts:
            raise ValueError("; ".join(conflicts))

        slot = TimetableSlot(**data.model_dump())
        db.add(slot)
        await db.commit()
        await db.refresh(slot)
        return slot

    @staticmethod
    async def update_slot(db: AsyncSession, slot_id: UUID, data: TimetableSlotUpdate) -> TimetableSlot:
        slot = await db.get(TimetableSlot, slot_id)
        if not slot:
            raise ValueError("Timetable slot not found")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(slot, field, value)

        slot_data = TimetableSlotCreate(
            class_section_id=slot.class_section_id,
            subject_id=slot.subject_id,
            teacher_id=slot.teacher_id,
            day_of_week=slot.day_of_week,
            start_time=slot.start_time,
            end_time=slot.end_time,
            room=slot.room,
        )
        conflicts = await TimetableService._check_conflicts(db, slot_data, exclude_id=slot_id)
        if conflicts:
            raise ValueError("; ".join(conflicts))

        await db.commit()
        await db.refresh(slot)
        return slot

    @staticmethod
    async def delete_slot(db: AsyncSession, slot_id: UUID) -> None:
        slot = await db.get(TimetableSlot, slot_id)
        if not slot:
            raise ValueError("Timetable slot not found")
        await db.delete(slot)
        await db.commit()

    @staticmethod
    async def list_slots(
        db: AsyncSession,
        class_section_id: UUID | None = None,
        teacher_id: UUID | None = None,
        section_ids: list[UUID] | None = None,
    ) -> list[dict]:
        query = (
            select(TimetableSlot, Subject.name, Teacher, ClassSection.name)
            .join(Subject, TimetableSlot.subject_id == Subject.id)
            .join(Teacher, TimetableSlot.teacher_id == Teacher.id)
            .join(ClassSection, TimetableSlot.class_section_id == ClassSection.id)
        )
        if class_section_id:
            query = query.where(TimetableSlot.class_section_id == class_section_id)
        if teacher_id:
            query = query.where(TimetableSlot.teacher_id == teacher_id)
        if section_ids is not None:
            if not section_ids:
                return []
            query = query.where(TimetableSlot.class_section_id.in_(section_ids))

        result = await db.execute(query.order_by(TimetableSlot.day_of_week, TimetableSlot.start_time))
        slots = []
        for slot, subject_name, teacher, section_name in result.all():
            user_result = await db.execute(select(User).where(User.id == teacher.user_id))
            user = user_result.scalar_one_or_none()
            slots.append(
                {
                    "id": slot.id,
                    "class_section_id": slot.class_section_id,
                    "subject_id": slot.subject_id,
                    "teacher_id": slot.teacher_id,
                    "day_of_week": slot.day_of_week,
                    "start_time": slot.start_time,
                    "end_time": slot.end_time,
                    "room": slot.room,
                    "subject_name": subject_name,
                    "teacher_name": f"{user.first_name} {user.last_name}" if user else None,
                    "class_section_name": section_name,
                }
            )
        return slots

    @staticmethod
    async def check_conflicts(db: AsyncSession, data: TimetableSlotCreate) -> dict:
        conflicts = await TimetableService._check_conflicts(db, data)
        return {"has_conflict": len(conflicts) > 0, "conflicts": conflicts}
