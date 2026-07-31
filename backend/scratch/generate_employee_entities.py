import os

ENTITIES = [
    {
        "name": "EmployeeGovernmentId",
        "file_prefix": "employee_government_id"
    },
    {
        "name": "EmployeePayrollConfig",
        "file_prefix": "employee_payroll_config"
    }
]

BASE_DIR = r"c:\ess\ess_sample_2\backend\app\employee"

for entity in ENTITIES:
    name = entity["name"]
    prefix = entity["file_prefix"]
    
    # 1. Validator
    validator_code = f"""from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.schemas.{prefix} import {name}Create, {name}Update

class {name}Validator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        
    async def validate_create(self, data: {name}Create):
        pass
        
    async def validate_update(self, id: str, data: {name}Update):
        pass
"""
    with open(os.path.join(BASE_DIR, "validators", f"{prefix}_validator.py"), "w") as f:
        f.write(validator_code)
        
    # 2. Service
    service_code = f"""from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.repositories.{prefix}_repository import {name}Repository
from app.employee.validators.{prefix}_validator import {name}Validator
from app.employee.schemas.{prefix} import {name}Create, {name}Update
from app.employee.models.{prefix} import {name}Model

class {name}Service:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = {name}Repository(db)
        self.validator = {name}Validator(db)
        
    async def create(self, data: {name}Create, user_id: str = None) -> {name}Model:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["employeeId"])
        
    async def get_by_id(self, id: str) -> Optional[{name}Model]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: {name}Update, user_id: str = None) -> Optional[{name}Model]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
"""
    with open(os.path.join(BASE_DIR, "services", f"{prefix}_service.py"), "w") as f:
        f.write(service_code)
        
    # 3. Controller
    controller_code = f"""from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.services.{prefix}_service import {name}Service
from app.employee.schemas.{prefix} import {name}Create, {name}Update, {name}Response
from app.employee.models.{prefix} import {name}Model

class {name}Controller:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = {name}Service(db)
        
    async def create(self, data: {name}Create, user_id: str) -> {name}Model:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> {name}Model:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="{name} not found")
        return doc
        
    async def update(self, id: str, data: {name}Update, user_id: str) -> {name}Model:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="{name} not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="{name} not found")
        return {{"message": "{name} archived successfully"}}
"""
    with open(os.path.join(BASE_DIR, "controllers", f"{prefix}_controller.py"), "w") as f:
        f.write(controller_code)
        
    # 4. Router
    router_code = f"""from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.db.mongo import get_database
from app.dependencies import get_current_user
from app.employee.controllers.{prefix}_controller import {name}Controller
from app.employee.schemas.{prefix} import {name}Create, {name}Update, {name}Response

router = APIRouter(prefix="/{prefix}s", tags=["{name}"])

def get_controller(db = Depends(get_database)) -> {name}Controller:
    return {name}Controller(db)

@router.post("/", response_model={name}Response)
async def create(data: {name}Create, controller: {name}Controller = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.create(data, user.get("empId"))

@router.get("/")
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    employeeId: Optional[str] = None,
    status: Optional[str] = None,
    controller: {name}Controller = Depends(get_controller),
    user: dict = Depends(get_current_user)
):
    query = {{}}
    if employeeId: query["employeeId"] = employeeId
    if status: query["status"] = status
    return await controller.get_all(query, skip, limit, search)

@router.get("/{{id}}", response_model={name}Response)
async def get_by_id(id: str, controller: {name}Controller = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.get_by_id(id)

@router.put("/{{id}}", response_model={name}Response)
async def update(id: str, data: {name}Update, controller: {name}Controller = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.update(id, data, user.get("empId"))

@router.delete("/{{id}}")
async def delete(id: str, controller: {name}Controller = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.delete(id, user.get("empId"))
"""
    with open(os.path.join(BASE_DIR, "routes", f"{prefix}_routes.py"), "w") as f:
        f.write(router_code)

print("Entities generated successfully!")
