from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.fee import FeeCategory, FeeInvoice, FeePayment, FeeStructure, InvoiceStatus
from app.models.people import Student, StudentEnrollment
from app.models.user import User
from app.schemas.fee import FeeCategoryCreate, FeeCategoryUpdate, FeeCollectionCreate, FeeStructureCreate, FeeStructureUpdate, GenerateInvoicesRequest


class FeeService:
    @staticmethod
    async def list_categories(db: AsyncSession) -> list[FeeCategory]:
        result = await db.execute(select(FeeCategory).order_by(FeeCategory.name))
        return list(result.scalars().all())

    @staticmethod
    async def create_category(db: AsyncSession, data: FeeCategoryCreate) -> FeeCategory:
        category = FeeCategory(**data.model_dump())
        db.add(category)
        await db.commit()
        await db.refresh(category)
        return category

    @staticmethod
    async def update_category(db: AsyncSession, category_id: UUID, data: FeeCategoryUpdate) -> FeeCategory:
        category = await db.get(FeeCategory, category_id)
        if not category:
            raise ValueError("Fee category not found")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(category, field, value)

        await db.commit()
        await db.refresh(category)
        return category

    @staticmethod
    async def delete_category(db: AsyncSession, category_id: UUID) -> None:
        category = await db.get(FeeCategory, category_id)
        if not category:
            raise ValueError("Fee category not found")

        structures = await db.execute(select(FeeStructure).where(FeeStructure.category_id == category_id))
        if structures.scalars().first():
            raise ValueError("Cannot delete category with linked fee structures")

        await db.delete(category)
        await db.commit()

    @staticmethod
    async def list_structures(db: AsyncSession) -> list[dict]:
        from app.models.academic import ClassSection

        result = await db.execute(
            select(FeeStructure, FeeCategory.name, ClassSection.name)
            .join(FeeCategory, FeeStructure.category_id == FeeCategory.id)
            .join(ClassSection, FeeStructure.class_section_id == ClassSection.id)
            .order_by(FeeStructure.due_date.desc())
        )
        return [
            {
                "id": s.id,
                "category_id": s.category_id,
                "class_section_id": s.class_section_id,
                "amount": s.amount,
                "due_date": s.due_date,
                "academic_year_id": s.academic_year_id,
                "description": s.description,
                "category_name": cat_name,
                "class_section_name": section_name,
            }
            for s, cat_name, section_name in result.all()
        ]

    @staticmethod
    async def create_structure(db: AsyncSession, data: FeeStructureCreate) -> FeeStructure:
        structure = FeeStructure(**data.model_dump())
        db.add(structure)
        await db.commit()
        await db.refresh(structure)
        return structure

    @staticmethod
    async def update_structure(db: AsyncSession, structure_id: UUID, data: FeeStructureUpdate) -> FeeStructure:
        structure = await db.get(FeeStructure, structure_id)
        if not structure:
            raise ValueError("Fee structure not found")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(structure, field, value)

        await db.commit()
        await db.refresh(structure)
        return structure

    @staticmethod
    async def delete_structure(db: AsyncSession, structure_id: UUID) -> None:
        structure = await db.get(FeeStructure, structure_id)
        if not structure:
            raise ValueError("Fee structure not found")

        invoices = await db.execute(select(FeeInvoice).where(FeeInvoice.fee_structure_id == structure_id))
        if invoices.scalars().first():
            raise ValueError("Cannot delete fee structure with generated invoices")

        await db.delete(structure)
        await db.commit()

    @staticmethod
    async def _next_invoice_no(db: AsyncSession) -> str:
        result = await db.execute(select(func.count(FeeInvoice.id)))
        count = result.scalar() or 0
        return f"INV{count + 1:06d}"

    @staticmethod
    async def _next_receipt_no(db: AsyncSession) -> str:
        result = await db.execute(select(func.count(FeePayment.id)))
        count = result.scalar() or 0
        return f"RCP{count + 1:06d}"

    @staticmethod
    async def generate_invoices(db: AsyncSession, data: GenerateInvoicesRequest) -> int:
        structure = await db.get(FeeStructure, data.fee_structure_id)
        if not structure:
            raise ValueError("Fee structure not found")

        enrollments = await db.execute(
            select(StudentEnrollment).where(
                StudentEnrollment.class_section_id == structure.class_section_id,
                StudentEnrollment.is_active.is_(True),
            )
        )
        created = 0
        for enrollment in enrollments.scalars().all():
            existing = await db.execute(
                select(FeeInvoice).where(
                    FeeInvoice.student_id == enrollment.student_id,
                    FeeInvoice.fee_structure_id == structure.id,
                )
            )
            if existing.scalar_one_or_none():
                continue

            invoice = FeeInvoice(
                student_id=enrollment.student_id,
                fee_structure_id=structure.id,
                invoice_no=await FeeService._next_invoice_no(db),
                amount=structure.amount,
                paid_amount=Decimal("0"),
                status=InvoiceStatus.pending,
                due_date=structure.due_date,
            )
            db.add(invoice)
            created += 1

        await db.commit()
        return created

    @staticmethod
    async def list_invoices(
        db: AsyncSession, status: InvoiceStatus | None = None, student_ids: list[UUID] | None = None
    ) -> list[dict]:
        from app.models.academic import ClassSection

        query = (
            select(FeeInvoice, Student, User, FeeCategory.name)
            .join(Student, FeeInvoice.student_id == Student.id)
            .outerjoin(User, Student.user_id == User.id)
            .join(FeeStructure, FeeInvoice.fee_structure_id == FeeStructure.id)
            .join(FeeCategory, FeeStructure.category_id == FeeCategory.id)
        )
        if status:
            query = query.where(FeeInvoice.status == status)
        if student_ids is not None:
            if not student_ids:
                return []
            query = query.where(FeeInvoice.student_id.in_(student_ids))

        result = await db.execute(query.order_by(FeeInvoice.due_date))
        invoices = []
        for invoice, student, user, category_name in result.all():
            name = f"{user.first_name} {user.last_name}" if user else student.admission_no
            invoices.append(
                {
                    "id": invoice.id,
                    "student_id": invoice.student_id,
                    "fee_structure_id": invoice.fee_structure_id,
                    "invoice_no": invoice.invoice_no,
                    "amount": invoice.amount,
                    "paid_amount": invoice.paid_amount,
                    "status": invoice.status,
                    "due_date": invoice.due_date,
                    "student_name": name,
                    "category_name": category_name,
                }
            )
        return invoices

    @staticmethod
    async def collect_fee(db: AsyncSession, data: FeeCollectionCreate) -> FeePayment:
        invoice = await db.get(FeeInvoice, data.invoice_id)
        if not invoice:
            raise ValueError("Invoice not found")

        remaining = invoice.amount - invoice.paid_amount
        if data.amount > remaining:
            raise ValueError(f"Payment exceeds remaining balance of {remaining}")

        payment = FeePayment(
            invoice_id=invoice.id,
            receipt_no=await FeeService._next_receipt_no(db),
            amount=data.amount,
            payment_mode=data.payment_mode,
            transaction_ref=data.transaction_ref,
            payment_date=data.payment_date,
            notes=data.notes,
        )
        db.add(payment)

        invoice.paid_amount += data.amount
        if invoice.paid_amount >= invoice.amount:
            invoice.status = InvoiceStatus.paid
        else:
            invoice.status = InvoiceStatus.partial

        if invoice.due_date < date.today() and invoice.status != InvoiceStatus.paid:
            invoice.status = InvoiceStatus.overdue

        await db.commit()
        await db.refresh(payment)
        return payment

    @staticmethod
    async def list_defaulters(db: AsyncSession) -> list[dict]:
        today = date.today()
        result = await db.execute(
            select(FeeInvoice)
            .where(
                FeeInvoice.status.in_([InvoiceStatus.pending, InvoiceStatus.partial, InvoiceStatus.overdue]),
                FeeInvoice.due_date < today,
            )
            .order_by(FeeInvoice.due_date)
        )
        defaulters = []
        for invoice in result.scalars().all():
            student = await db.get(Student, invoice.student_id)
            user = await db.get(User, student.user_id) if student and student.user_id else None
            name = f"{user.first_name} {user.last_name}" if user else (student.admission_no if student else "Unknown")
            defaulters.append(
                {
                    "id": invoice.id,
                    "student_id": invoice.student_id,
                    "fee_structure_id": invoice.fee_structure_id,
                    "invoice_no": invoice.invoice_no,
                    "amount": invoice.amount,
                    "paid_amount": invoice.paid_amount,
                    "status": invoice.status,
                    "due_date": invoice.due_date,
                    "student_name": name,
                    "outstanding": invoice.amount - invoice.paid_amount,
                }
            )
        return defaulters
