from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional

from app.db.mongo import get_database
from app.dependencies import get_current_user
from app.domain_models import SalaryComponent
from app.organization.schemas.salary_component import SalaryComponentCreate, SalaryComponentUpdate, SalaryComponentResponse
from app.organization.routes.generic_routes import GenericService

router = APIRouter(prefix="/salary-components", tags=["Salary Component"])

def get_service(db = Depends(get_database)) -> GenericService:
    return GenericService(db, "salary_components", SalaryComponent)

async def validate_salary_component(data_dict: dict, db: AsyncIOMotorDatabase, exclude_id: str = None):
    # 1. Basic Component Uniqueness
    if data_dict.get("isBasicComponent"):
        query = {"isBasicComponent": True, "deletedAt": None}
        if exclude_id:
            query["_id"] = {"$ne": ObjectId(exclude_id)}
        existing_basic = await db.salary_components.find_one(query)
        if existing_basic:
            raise HTTPException(status_code=400, detail="Another Basic component already exists. Only one is allowed.")

    # 2. Percentage Validation
    if data_dict.get("calculationMethod") == "Percentage":
        perc = data_dict.get("percentageValue")
        if perc is None or perc < 0 or perc > 1000:
            raise HTTPException(status_code=400, detail="Invalid percentage range")

        ref_id = data_dict.get("percentageDerivedFromComponentId")
        if not ref_id:
            raise HTTPException(status_code=400, detail="Percentage calculation requires a derived component ID")
        if exclude_id and ref_id == exclude_id:
            raise HTTPException(status_code=400, detail="Component cannot reference itself")
            
        if not ObjectId.is_valid(ref_id):
            raise HTTPException(status_code=400, detail="Invalid referenced component ID format")

        # 3. Referenced Component Exists & Active
        ref_comp = await db.salary_components.find_one({"_id": ObjectId(ref_id), "deletedAt": None})
        if not ref_comp:
            raise HTTPException(status_code=400, detail="Referenced component does not exist")
        if not ref_comp.get("isActive", True):
            raise HTTPException(status_code=400, detail="Referenced component must be active")

        # 4. Circular Dependency Check
        # Traverse up the dependencies
        visited = set()
        current_ref = ref_id
        while current_ref:
            if exclude_id and current_ref == exclude_id:
                raise HTTPException(status_code=400, detail="Circular dependency detected")
            if current_ref in visited:
                break # A loop exists somewhere above, which should have been prevented, but break to avoid infinite loop
            visited.add(current_ref)
            parent = await db.salary_components.find_one({"_id": ObjectId(current_ref)})
            if not parent:
                break
            if parent.get("calculationMethod") == "Percentage":
                current_ref = parent.get("percentageDerivedFromComponentId")
            else:
                current_ref = None

@router.post("/", response_model=SalaryComponentResponse)
async def create_component(data: SalaryComponentCreate, service: GenericService = Depends(get_service), user: dict = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    data_dict = data.model_dump(exclude_unset=True)
    await validate_salary_component(data_dict, db)
    return await service.create(data, user.get("empId"))

@router.get("/")
async def get_components(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    companyId: Optional[str] = None,
    status: Optional[str] = None,
    service: GenericService = Depends(get_service),
    user: dict = Depends(get_current_user)
):
    query = {}
    if companyId: query["companyId"] = companyId
    if status: query["status"] = status
    return await service.get_all(query, skip, limit, search, ["name"])

@router.get("/{id}", response_model=SalaryComponentResponse)
async def get_component(id: str, service: GenericService = Depends(get_service), user: dict = Depends(get_current_user)):
    doc = await service.get_by_id(id)
    if not doc: raise HTTPException(status_code=404, detail="Salary Component not found")
    return doc

@router.put("/{id}", response_model=SalaryComponentResponse)
async def update_component(id: str, data: SalaryComponentUpdate, service: GenericService = Depends(get_service), user: dict = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid component ID")
        
    data_dict = data.model_dump(exclude_unset=True)
    
    # Merge with existing for validation
    existing = await service.get_by_id(id)
    if not existing:
        raise HTTPException(status_code=404, detail="Salary Component not found")
    
    merged = existing.model_dump()
    merged.update(data_dict)
    
    await validate_salary_component(merged, db, exclude_id=id)
    
    doc = await service.update(id, data, user.get("empId"))
    return doc

@router.delete("/{id}")
async def delete_component(id: str, service: GenericService = Depends(get_service), user: dict = Depends(get_current_user)):
    success = await service.delete(id, user.get("empId"))
    if not success: raise HTTPException(status_code=404, detail="Salary Component not found")
    return {"message": "Salary Component archived successfully"}
