from typing import List
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.dependencies import get_database, get_current_user, require_permission
from app.payroll.schemas.company_salary_bank import (
    CompanySalaryBankAccountCreate,
    CompanySalaryBankAccountUpdate,
    CompanySalaryBankAccountResponse
)
from app.payroll.services.company_salary_bank_service import CompanySalaryBankService

router = APIRouter()

@router.get("/", response_model=List[CompanySalaryBankAccountResponse])
async def list_all_banks(
    companyCode: str = None,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user),
    _admin = Depends(require_permission("organization.manage"))
):
    service = CompanySalaryBankService(db)
    return await service.get_all(companyCode)

@router.post("/", response_model=CompanySalaryBankAccountResponse)
async def create_bank(
    req: CompanySalaryBankAccountCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user),
    _admin = Depends(require_permission("organization.manage"))
):
    service = CompanySalaryBankService(db)
    try:
        return await service.create(req, created_by=current_user.get("employeeId", "System"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/company/{company_code}", response_model=List[CompanySalaryBankAccountResponse])
async def list_banks(
    company_code: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user),
    _admin = Depends(require_permission("organization.manage"))
):
    service = CompanySalaryBankService(db)
    return await service.get_by_company(company_code)

@router.put("/{bank_id}", response_model=CompanySalaryBankAccountResponse)
async def update_bank(
    bank_id: str,
    req: CompanySalaryBankAccountUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user),
    _admin = Depends(require_permission("organization.manage"))
):
    service = CompanySalaryBankService(db)
    try:
        updated = await service.update(bank_id, req, updated_by=current_user.get("employeeId", "System"))
        if not updated:
            raise HTTPException(status_code=404, detail="Bank account not found")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{bank_id}/primary", response_model=CompanySalaryBankAccountResponse)
async def set_primary_bank(
    bank_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user),
    _admin = Depends(require_permission("organization.manage"))
):
    service = CompanySalaryBankService(db)
    try:
        updated = await service.set_primary(bank_id, updated_by=current_user.get("employeeId", "System"))
        if not updated:
            raise HTTPException(status_code=404, detail="Bank account not found")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
