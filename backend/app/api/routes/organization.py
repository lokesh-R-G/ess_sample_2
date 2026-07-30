from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.db.mongo import get_database
from app.dependencies import require_roles
from app.models import Company, Branch, Department, Designation
from app.services import organization_service

router = APIRouter(prefix="/organization", tags=["organization"])

@router.get("/companies/", response_model=List[Company])
async def get_companies():
    db = get_database()
    return await organization_service.get_companies(db)

@router.post("/companies/", response_model=Company)
async def create_company(company: Company, _admin=Depends(require_roles("Admin"))):
    db = get_database()
    return await organization_service.create_company(db, company)

@router.get("/branches/", response_model=List[Branch])
async def get_branches(companyId: str = None):
    db = get_database()
    return await organization_service.get_branches(db, companyId)

@router.post("/branches/", response_model=Branch)
async def create_branch(branch: Branch, _admin=Depends(require_roles("Admin"))):
    db = get_database()
    return await organization_service.create_branch(db, branch)

@router.get("/departments/", response_model=List[Department])
async def get_departments(companyId: str = None):
    db = get_database()
    return await organization_service.get_departments(db, companyId)

@router.post("/departments/", response_model=Department)
async def create_department(dept: Department, _admin=Depends(require_roles("Admin"))):
    db = get_database()
    return await organization_service.create_department(db, dept)

@router.get("/designations/", response_model=List[Designation])
async def get_designations(companyId: str = None, departmentId: str = None):
    db = get_database()
    return await organization_service.get_designations(db, companyId, departmentId)

@router.post("/designations/", response_model=Designation)
async def create_designation(desig: Designation, _admin=Depends(require_roles("Admin"))):
    db = get_database()
    return await organization_service.create_designation(db, desig)
