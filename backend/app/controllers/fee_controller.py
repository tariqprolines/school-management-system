from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.models.fee import InvoiceStatus
from app.schemas.fee import FeeCategoryCreate, FeeCategoryUpdate, FeeCollectionCreate, FeeStructureCreate, FeeStructureUpdate, GenerateInvoicesRequest
from app.services.fee_service import FeeService
from app.utils.auth_utils import CurrentUser, FinanceUser, PortalUser, StaffUser, validate_api_key
from app.utils.responses import success_response
from app.utils.scope_utils import ScopeService

router = APIRouter(prefix="/fees", tags=["Fees"], dependencies=[Depends(validate_api_key)])


@router.get("/categories")
async def list_categories(_current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    categories = await FeeService.list_categories(db)
    return success_response(categories, "Fee categories fetched")


@router.post("/categories")
async def create_category(data: FeeCategoryCreate, _current_user: FinanceUser, db: AsyncSession = Depends(get_db)):
    category = await FeeService.create_category(db, data)
    return success_response(category, "Fee category created", 201)


@router.patch("/categories/{category_id}")
async def update_category(
    category_id: UUID, data: FeeCategoryUpdate, _current_user: FinanceUser, db: AsyncSession = Depends(get_db)
):
    try:
        category = await FeeService.update_category(db, category_id, data)
        return success_response(category, "Fee category updated")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/categories/{category_id}")
async def delete_category(category_id: UUID, _current_user: FinanceUser, db: AsyncSession = Depends(get_db)):
    try:
        await FeeService.delete_category(db, category_id)
        return success_response(None, "Fee category deleted")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/structures")
async def list_structures(_current_user: StaffUser, db: AsyncSession = Depends(get_db)):
    structures = await FeeService.list_structures(db)
    return success_response(structures, "Fee structures fetched")


@router.post("/structures")
async def create_structure(data: FeeStructureCreate, _current_user: FinanceUser, db: AsyncSession = Depends(get_db)):
    structure = await FeeService.create_structure(db, data)
    return success_response(structure, "Fee structure created", 201)


@router.patch("/structures/{structure_id}")
async def update_structure(
    structure_id: UUID, data: FeeStructureUpdate, _current_user: FinanceUser, db: AsyncSession = Depends(get_db)
):
    try:
        structure = await FeeService.update_structure(db, structure_id, data)
        return success_response(structure, "Fee structure updated")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/structures/{structure_id}")
async def delete_structure(structure_id: UUID, _current_user: FinanceUser, db: AsyncSession = Depends(get_db)):
    try:
        await FeeService.delete_structure(db, structure_id)
        return success_response(None, "Fee structure deleted")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/generate-invoices")
async def generate_invoices(data: GenerateInvoicesRequest, _current_user: FinanceUser, db: AsyncSession = Depends(get_db)):
    try:
        count = await FeeService.generate_invoices(db, data)
        return success_response({"created": count}, f"{count} invoices generated")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/invoices")
async def list_invoices(
    current_user: PortalUser,
    status: InvoiceStatus | None = None,
    db: AsyncSession = Depends(get_db),
):
    student_ids = await ScopeService.get_accessible_student_ids(db, current_user)
    invoices = await FeeService.list_invoices(db, status, student_ids)
    return success_response(invoices, "Invoices fetched")


@router.post("/collect")
async def collect_fee(data: FeeCollectionCreate, _current_user: FinanceUser, db: AsyncSession = Depends(get_db)):
    try:
        payment = await FeeService.collect_fee(db, data)
        return success_response(payment, "Fee collected", 201)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/defaulters")
async def list_defaulters(_current_user: FinanceUser, db: AsyncSession = Depends(get_db)):
    defaulters = await FeeService.list_defaulters(db)
    return success_response(defaulters, "Fee defaulters fetched")
