import os
from pathlib import Path

BASE_DIR = Path("backend/app/employee")

folders = [
    "models", "schemas", "repositories", "services", 
    "controllers", "routes", "validators", "constants", "engine"
]

entities = [
    "employee", "employee_personal", "employee_contact", 
    "employee_address", "employee_bank", "employee_emergency_contact", 
    "employee_family", "employee_education", "employee_experience", 
    "employee_document", "employment_history", "employee_shift_assignment", 
    "employee_role_assignment", "employee_reporting", "employee_probation", 
    "employee_confirmation", "employee_exit"
]

def create_structure():
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "__init__.py").touch()
    
    for folder in folders:
        folder_path = BASE_DIR / folder
        folder_path.mkdir(exist_ok=True)
        (folder_path / "__init__.py").touch()
        
def write_base_repository():
    content = """from typing import TypeVar, Generic, Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime, timezone
import math

T = TypeVar("T")

class BaseRepository(Generic[T]):
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str, model_class: type[T]):
        self.db = db
        self.collection = self.db[collection_name]
        self.model_class = model_class

    def _prepare_doc(self, doc: dict) -> dict:
        if not doc:
            return doc
        doc["_id"] = str(doc["_id"])
        return doc

    async def create(self, data: dict, created_by: str = None) -> T:
        now = datetime.now(timezone.utc)
        data["createdAt"] = now
        data["updatedAt"] = now
        data["createdBy"] = created_by
        data["updatedBy"] = created_by
        data["status"] = data.get("status", "Active")
        
        result = await self.collection.insert_one(data)
        data["_id"] = str(result.inserted_id)
        return self.model_class(**data)

    async def get_by_id(self, id: str) -> Optional[T]:
        try:
            obj_id = ObjectId(id)
        except:
            return None
        doc = await self.collection.find_one({"_id": obj_id, "deletedAt": None})
        if doc:
            return self.model_class(**self._prepare_doc(doc))
        return None

    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, sort_by: str = "createdAt", sort_order: int = -1, search: str = None, search_fields: List[str] = None) -> dict:
        if query is None:
            query = {}
            
        if "deletedAt" not in query:
            query["deletedAt"] = None
            
        if search and search_fields:
            search_query = [{"$regex": search, "$options": "i"}]
            query["$or"] = [{field: search_query[0]} for field in search_fields]
            
        cursor = self.collection.find(query)
        if sort_by:
            cursor = cursor.sort(sort_by, sort_order)
            
        total = await self.collection.count_documents(query)
        
        cursor = cursor.skip(skip).limit(limit)
        docs = await cursor.to_list(length=None)
        
        items = [self.model_class(**self._prepare_doc(doc)) for doc in docs]
        return {
            "data": items,
            "total": total,
            "page": (skip // limit) + 1 if limit > 0 else 1,
            "pageSize": limit,
            "totalPages": math.ceil(total / limit) if limit > 0 else 1
        }

    async def update(self, id: str, data: dict, updated_by: str = None) -> Optional[T]:
        data["updatedAt"] = datetime.now(timezone.utc)
        data["updatedBy"] = updated_by
        data.pop("createdAt", None)
        data.pop("createdBy", None)
        
        try:
            obj_id = ObjectId(id)
        except:
            return None
            
        result = await self.collection.find_one_and_update(
            {"_id": obj_id, "deletedAt": None},
            {"$set": data},
            return_document=True
        )
        if result:
            return self.model_class(**self._prepare_doc(result))
        return None

    async def soft_delete(self, id: str, deleted_by: str = None) -> bool:
        try:
            obj_id = ObjectId(id)
        except:
            return False
            
        result = await self.collection.update_one(
            {"_id": obj_id, "deletedAt": None},
            {"$set": {
                "deletedAt": datetime.now(timezone.utc),
                "deletedBy": deleted_by,
                "status": "Deleted"
            }}
        )
        return result.modified_count > 0

    async def exists(self, query: dict) -> bool:
        if "deletedAt" not in query:
            query["deletedAt"] = None
        doc = await self.collection.find_one(query, {"_id": 1})
        return doc is not None
"""
    with open(BASE_DIR / "repositories" / "base_repository.py", "w") as f:
        f.write(content)

def to_camel_case(snake_str):
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def write_entity_code(entity: str):
    class_name = "".join(x.capitalize() for x in entity.split('_'))
    camel_name = to_camel_case(entity)
    collection_name = entity + "s" if not entity.endswith("s") else entity
    
    if entity == "employment_history":
        collection_name = "employment_history"
    
    # Models
    with open(BASE_DIR / "models" / f"{entity}.py", "w") as f:
        f.write(f'''from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class {class_name}Model(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    employeeId: str
    status: str = "Active"
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    deletedAt: Optional[datetime] = None
    deletedBy: Optional[str] = None
''')

    # Schemas
    with open(BASE_DIR / "schemas" / f"{entity}.py", "w") as f:
        f.write(f'''from pydantic import BaseModel
from typing import Optional

class {class_name}Create(BaseModel):
    employeeId: str

class {class_name}Update(BaseModel):
    status: Optional[str] = None

class {class_name}Response({class_name}Create):
    id: str
''')

    # Repositories
    with open(BASE_DIR / "repositories" / f"{entity}_repository.py", "w") as f:
        f.write(f'''from motor.motor_asyncio import AsyncIOMotorDatabase
from app.scripts.base_repository import BaseRepository
from ..models.{entity} import {class_name}Model

class {class_name}Repository(BaseRepository[{class_name}Model]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "{collection_name}", {class_name}Model)
''')

    # Validators
    with open(BASE_DIR / "validators" / f"{entity}_validator.py", "w") as f:
        f.write(f'''from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.{entity} import {class_name}Create, {class_name}Update
from bson import ObjectId

class {class_name}Validator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["{collection_name}"]
        
    async def validate_create(self, data: {class_name}Create):
        pass # add cross collection validation if needed
            
    async def validate_update(self, id: str, data: {class_name}Update):
        pass 
''')

    # Services
    with open(BASE_DIR / "services" / f"{entity}_service.py", "w") as f:
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
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["employeeId"])
        
    async def get_by_id(self, id: str) -> Optional[{class_name}Model]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: {class_name}Update, user_id: str = None) -> Optional[{class_name}Model]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
''')

    # Controllers
    with open(BASE_DIR / "controllers" / f"{entity}_controller.py", "w") as f:
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

    # Routes
    with open(BASE_DIR / "routes" / f"{entity}_routes.py", "w") as f:
        f.write(f'''from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.db.mongo import get_database
from app.dependencies import get_current_user
from ..controllers.{entity}_controller import {class_name}Controller
from ..schemas.{entity} import {class_name}Create, {class_name}Update, {class_name}Response

router = APIRouter(prefix="/{camel_name}s", tags=["{class_name}"])

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
    employeeId: Optional[str] = None,
    status: Optional[str] = None,
    controller: {class_name}Controller = Depends(get_controller),
    user: dict = Depends(get_current_user)
):
    query = {{}}
    if employeeId: query["employeeId"] = employeeId
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

def write_master_router():
    with open(BASE_DIR / "routes" / "router.py", "w") as f:
        f.write('from fastapi import APIRouter\n')
        for entity in entities:
            f.write(f'from .{entity}_routes import router as {entity}_router\n')
        f.write('\nemployee_router = APIRouter()\n')
        for entity in entities:
            f.write(f'employee_router.include_router({entity}_router)\n')

if __name__ == "__main__":
    create_structure()
    write_base_repository()
    for e in entities:
        write_entity_code(e)
    write_master_router()
    print("Employee Engine generated successfully.")
