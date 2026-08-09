from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.academic import ClassSection
from app.models.fee import FeeInvoice, InvoiceStatus
from app.models.people import Student, StudentEnrollment, Teacher
from app.schemas.dashboard import DashboardSummary


class DashboardService:
    @staticmethod
    async def get_summary(db: AsyncSession) -> DashboardSummary:
        students = await db.execute(select(func.count(Student.id)))
        teachers = await db.execute(select(func.count(Teacher.id)))
        classes = await db.execute(select(func.count(ClassSection.id)))
        enrollments = await db.execute(
            select(func.count(StudentEnrollment.id)).where(StudentEnrollment.is_active.is_(True))
        )

        collected = await db.execute(
            select(func.coalesce(func.sum(FeeInvoice.paid_amount), 0))
        )
        pending = await db.execute(
            select(func.coalesce(func.sum(FeeInvoice.amount - FeeInvoice.paid_amount), 0)).where(
                FeeInvoice.status != InvoiceStatus.paid
            )
        )
        total_amount = await db.execute(select(func.coalesce(func.sum(FeeInvoice.amount), 0)))

        total_students = students.scalar() or 0
        total_teachers = teachers.scalar() or 0
        total_classes = classes.scalar() or 0
        active_enrollments = enrollments.scalar() or 0
        total_fee_collected = float(collected.scalar() or 0)
        total_fee_pending = float(pending.scalar() or 0)
        total_fee = float(total_amount.scalar() or 0)

        fee_rate = (total_fee_collected / total_fee * 100) if total_fee > 0 else 0.0

        capacity_result = await db.execute(select(func.coalesce(func.sum(ClassSection.capacity), 0)))
        total_capacity = capacity_result.scalar() or 0
        occupancy = (active_enrollments / total_capacity * 100) if total_capacity > 0 else 0.0

        return DashboardSummary(
            total_students=total_students,
            total_teachers=total_teachers,
            total_classes=total_classes,
            active_enrollments=active_enrollments,
            total_fee_collected=total_fee_collected,
            total_fee_pending=total_fee_pending,
            fee_collection_rate=round(fee_rate, 2),
            class_occupancy_rate=round(occupancy, 2),
        )
