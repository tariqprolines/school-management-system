import enum
import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.database import Base


class InvoiceStatus(str, enum.Enum):
    pending = "pending"
    partial = "partial"
    paid = "paid"
    overdue = "overdue"


class PaymentMode(str, enum.Enum):
    cash = "cash"
    card = "card"
    bank_transfer = "bank_transfer"
    online = "online"


class FeeCategory(Base):
    __tablename__ = "fee_categories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    structures = relationship("FeeStructure", back_populates="category")


class FeeStructure(Base):
    __tablename__ = "fee_structures"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fee_categories.id"), nullable=False
    )
    class_section_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("class_sections.id"), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    academic_year_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("academic_years.id"), nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    category = relationship("FeeCategory", back_populates="structures")
    class_section = relationship("ClassSection", back_populates="fee_structures")
    invoices = relationship("FeeInvoice", back_populates="fee_structure")


class FeeInvoice(Base):
    __tablename__ = "fee_invoices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False)
    fee_structure_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fee_structures.id"), nullable=False
    )
    invoice_no: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    status: Mapped[InvoiceStatus] = mapped_column(
        Enum(InvoiceStatus, name="invoice_status"), default=InvoiceStatus.pending, nullable=False
    )
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    student = relationship("Student", back_populates="fee_invoices")
    fee_structure = relationship("FeeStructure", back_populates="invoices")
    payments = relationship("FeePayment", back_populates="invoice")


class FeePayment(Base):
    __tablename__ = "fee_payments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("fee_invoices.id"), nullable=False)
    receipt_no: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    payment_mode: Mapped[PaymentMode] = mapped_column(Enum(PaymentMode, name="payment_mode"), nullable=False)
    transaction_ref: Mapped[str | None] = mapped_column(String(100), nullable=True)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    invoice = relationship("FeeInvoice", back_populates="payments")
