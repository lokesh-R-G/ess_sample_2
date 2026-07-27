import os
from pathlib import Path

# Directories
MODULES = {
    "attendance_v2": {
        "entities": [
            "attendance_calendar", "attendance_summary", "leave_conversion_ledger",
            "attendance_exception", "attendance_replay_queue", "attendance_engine_health",
            "attendance_closing"
        ]
    },
    "permission": {
        "entities": [
            "grace_balance"
        ]
    }
}

FOLDERS = ["models", "schemas", "repositories", "services", "controllers", "routes"]

def to_camel_case(snake_str):
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def write_entity_files(base_path: Path, module_name: str, entity: str):
    class_name = "".join(x.capitalize() for x in entity.split('_'))
    camel_name = to_camel_case(entity)
    collection_name = entity + "s" if not entity.endswith("s") and not entity.endswith("health") and not entity.endswith("closing") else entity
    
    if entity == "attendance_engine_health": collection_name = "attendance_engine_health"
    if entity == "attendance_closing": collection_name = "attendance_closing"

    # Model
    with open(base_path / "models" / f"{entity}.py", "w") as f:
        f.write(f'''from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class {class_name}Model(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    status: str = "Active"
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    deletedAt: Optional[datetime] = None
    deletedBy: Optional[str] = None
''')

    # Schema
    with open(base_path / "schemas" / f"{entity}.py", "w") as f:
        f.write(f'''from pydantic import BaseModel
from typing import Optional, Dict, Any

class {class_name}Create(BaseModel):
    status: Optional[str] = None

class {class_name}Update(BaseModel):
    status: Optional[str] = None

class {class_name}Response({class_name}Create):
    id: str
''')

    # Repo
    with open(base_path / "repositories" / f"{entity}_repository.py", "w") as f:
        f.write(f'''from motor.motor_asyncio import AsyncIOMotorDatabase
from app.scripts.base_repository import BaseRepository
from ..models.{entity} import {class_name}Model

class {class_name}Repository(BaseRepository[{class_name}Model]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "{collection_name}", {class_name}Model)
''')

    # Validator
    with open(base_path / "validators" / f"{entity}_validator.py", "w") as f:
        f.write(f'''from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.{entity} import {class_name}Create, {class_name}Update

class {class_name}Validator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["{collection_name}"]
        
    async def validate_create(self, data: {class_name}Create):
        pass
            
    async def validate_update(self, id: str, data: {class_name}Update):
        pass 
''')

    # Service
    with open(base_path / "services" / f"{entity}_service.py", "w") as f:
        f.write(f'''from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..repositories.{entity}_repository import {class_name}Repository
from ..validators.{entity}_validator import {class_name}Validator
from ..schemas.{entity} import {class_name}Create, {class_name}Update
from ..models.{entity} import {class_name}Model

class {class_name}Service:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = {class_name}Repository(db)
        self.validator = {class_name}Validator(db)
        
    async def create(self, data: {class_name}Create, user_id: str = None) -> {class_name}Model:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["status"])
        
    async def get_by_id(self, id: str) -> Optional[{class_name}Model]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: {class_name}Update, user_id: str = None) -> Optional[{class_name}Model]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
''')

    # Controller
    with open(base_path / "controllers" / f"{entity}_controller.py", "w") as f:
        f.write(f'''from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.{entity}_service import {class_name}Service
from ..schemas.{entity} import {class_name}Create, {class_name}Update, {class_name}Response
from ..models.{entity} import {class_name}Model

class {class_name}Controller:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = {class_name}Service(db)
        
    async def create(self, data: {class_name}Create, user_id: str) -> {class_name}Model:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> {class_name}Model:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="{class_name} not found")
        return doc
        
    async def update(self, id: str, data: {class_name}Update, user_id: str) -> {class_name}Model:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="{class_name} not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="{class_name} not found")
        return {{"message": "{class_name} archived successfully"}}
''')

    # Route
    with open(base_path / "routes" / f"{entity}_routes.py", "w") as f:
        f.write(f'''from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.db.mongo import get_database
from app.dependencies import get_current_user
from ..controllers.{entity}_controller import {class_name}Controller
from ..schemas.{entity} import {class_name}Create, {class_name}Update, {class_name}Response

router = APIRouter(prefix="/{camel_name.replace('attendanceClosing', 'close')}", tags=["{class_name}"])

def get_controller(db = Depends(get_database)) -> {class_name}Controller:
    return {class_name}Controller(db)

@router.post("/", response_model={class_name}Response)
async def create(data: {class_name}Create, controller: {class_name}Controller = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.create(data, user.get("empId"))

@router.get("/")
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    status: Optional[str] = None,
    controller: {class_name}Controller = Depends(get_controller),
    user: dict = Depends(get_current_user)
):
    query = {{}}
    if status: query["status"] = status
    return await controller.get_all(query, skip, limit, search)

@router.get("/{{id}}", response_model={class_name}Response)
async def get_by_id(id: str, controller: {class_name}Controller = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.get_by_id(id)

@router.put("/{{id}}", response_model={class_name}Response)
async def update(id: str, data: {class_name}Update, controller: {class_name}Controller = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.update(id, data, user.get("empId"))

@router.delete("/{{id}}")
async def delete(id: str, controller: {class_name}Controller = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.delete(id, user.get("empId"))
''')

def generate_enhancements():
    for module_name, config in MODULES.items():
        base_path = Path(f"backend/app/{module_name}")
        for entity in config["entities"]:
            write_entity_files(base_path, module_name, entity)
            
        # Register new routers in master router
        router_path = base_path / "routes" / "router.py"
        if router_path.exists():
            with open(router_path, "a") as f:
                for entity in config["entities"]:
                    f.write(f'from .{entity}_routes import router as {entity}_router\n')
                    f.write(f'{module_name}_router.include_router({entity}_router)\n')

if __name__ == "__main__":
    generate_enhancements()
    print("Attendance Enhancements generated successfully.")
