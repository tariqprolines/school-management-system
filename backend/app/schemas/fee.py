from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.fee import InvoiceStatus, PaymentMode


class FeeCategoryCreate(BaseModel):
    name: str
    description: str | None = None


class FeeCategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class FeeCategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None


class FeeStructureCreate(BaseModel):
    category_id: UUID
    class_section_id: UUID
    amount: Decimal = Field(gt=0)
    due_date: date
    academic_year_id: UUID
    description: str | None = None


class FeeStructureUpdate(BaseModel):
    category_id: UUID | None = None
    class_section_id: UUID | None = None
    amount: Decimal | None = Field(default=None, gt=0)
    due_date: date | None = None
    academic_year_id: UUID | None = None
    description: str | None = None


class FeeStructureResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    category_id: UUID
    class_section_id: UUID
    amount: Decimal
    due_date: date
    academic_year_id: UUID
    description: str | None
    category_name: str | None = None
    class_section_name: str | None = None


class FeeCollectionCreate(BaseModel):
    invoice_id: UUID
    amount: Decimal = Field(gt=0)
    payment_mode: PaymentMode
    transaction_ref: str | None = None
    payment_date: date
    notes: str | None = None


class FeeInvoiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    student_id: UUID
    fee_structure_id: UUID
    invoice_no: str
    amount: Decimal
    paid_amount: Decimal
    status: InvoiceStatus
    due_date: date
    student_name: str | None = None
    category_name: str | None = None


class FeePaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    invoice_id: UUID
    receipt_no: str
    amount: Decimal
    payment_mode: PaymentMode
    transaction_ref: str | None
    payment_date: date
    notes: str | None


class GenerateInvoicesRequest(BaseModel):
    fee_structure_id: UUID
