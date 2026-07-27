import os
from pathlib import Path

BASE_DIR = Path("backend/app/organization")

entities = ["organization", "company", "branch", "department", "designation", "role", "shift", "holiday"]

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
            
        # Default ignore soft-deleted
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

def write_entity_code(entity: str):
    cap = entity.capitalize()
    
    # 1. Validator
    val_content = f"""from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.{entity} import {cap}Create, {cap}Update
from bson import ObjectId

class {cap}Validator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["{entity if entity.endswith('s') else entity + 's'}"]
        
    async def validate_create(self, data: {cap}Create):
        query = {{"name": data.name, "deletedAt": None}}
        if hasattr(data, 'companyId') and data.companyId:
            query["companyId"] = data.companyId
            parent = await self.db["companies"].find_one({{"_id": ObjectId(data.companyId), "deletedAt": None}})
            if not parent:
                raise HTTPException(status_code=400, detail="Parent company not found or archived")
        if await self.collection.find_one(query):
            raise HTTPException(status_code=409, detail=f"{cap} with this name already exists")
            
    async def validate_update(self, id: str, data: {cap}Update):
        pass # Optional update validation
"""
    with open(BASE_DIR / "validators" / f"{entity}_validator.py", "w") as f:
        f.write(val_content)

    # 2. Service
    svc_content = f"""from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..repositories.{entity}_repository import {cap}Repository
from ..validators.{entity}_validator import {cap}Validator
from ..schemas.{entity} import {cap}Create, {cap}Update
from ..models.{entity} import {cap}Model

class {cap}Service:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = {cap}Repository(db)
        self.validator = {cap}Validator(db)
        
    async def create(self, data: {cap}Create, user_id: str = None) -> {cap}Model:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[{cap}Model]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: {cap}Update, user_id: str = None) -> Optional[{cap}Model]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        # Relationship Integrity
        if "{entity}" == "company":
            has_branches = await self.db["branches"].find_one({{"companyId": id, "deletedAt": None}})
            if has_branches:
                raise HTTPException(status_code=409, detail="Cannot archive Company with active Branches")
        elif "{entity}" == "branch":
            has_depts = await self.db["departments"].find_one({{"branchId": id, "deletedAt": None}})
            if has_depts:
                raise HTTPException(status_code=409, detail="Cannot archive Branch with active Departments")
        return await self.repo.soft_delete(id, user_id)
"""
    with open(BASE_DIR / "services" / f"{entity}_service.py", "w") as f:
        f.write(svc_content)

    # 3. Controller
    ctrl_content = f"""from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.{entity}_service import {cap}Service
from ..schemas.{entity} import {cap}Create, {cap}Update, {cap}Response
from ..models.{entity} import {cap}Model

class {cap}Controller:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = {cap}Service(db)
        
    async def create(self, data: {cap}Create, user_id: str) -> {cap}Model:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> {cap}Model:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="{cap} not found")
        return doc
        
    async def update(self, id: str, data: {cap}Update, user_id: str) -> {cap}Model:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="{cap} not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="{cap} not found")
        return {{"message": "{cap} archived successfully"}}
"""
    with open(BASE_DIR / "controllers" / f"{entity}_controller.py", "w") as f:
        f.write(ctrl_content)

    # 4. Routes (Injects Auth JWT)
    route_content = f"""from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.db.mongo import get_database
from app.dependencies import get_current_user
from ..controllers.{entity}_controller import {cap}Controller
from ..schemas.{entity} import {cap}Create, {cap}Update, {cap}Response

router = APIRouter(prefix="/{entity if entity.endswith('s') else entity + 's'}", tags=["{cap}"])

def get_controller(db = Depends(get_database)) -> {cap}Controller:
    return {cap}Controller(db)

@router.post("/", response_model={cap}Response)
async def create(data: {cap}Create, controller: {cap}Controller = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.create(data, user.get("empId"))

@router.get("/")
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    companyId: Optional[str] = None,
    status: Optional[str] = None,
    controller: {cap}Controller = Depends(get_controller),
    user: dict = Depends(get_current_user)
):
    query = {{}}
    if companyId: query["companyId"] = companyId
    if status: query["status"] = status
    return await controller.get_all(query, skip, limit, search)

@router.get("/{{id}}", response_model={cap}Response)
async def get_by_id(id: str, controller: {cap}Controller = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.get_by_id(id)

@router.put("/{{id}}", response_model={cap}Response)
async def update(id: str, data: {cap}Update, controller: {cap}Controller = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.update(id, data, user.get("empId"))

@router.delete("/{{id}}")
async def delete(id: str, controller: {cap}Controller = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.delete(id, user.get("empId"))
"""
    with open(BASE_DIR / "routes" / f"{entity}_routes.py", "w") as f:
        f.write(route_content)

def write_index_script():
    content = """import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def init_org_indexes():
    MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.ess
    
    # Company Indexes
    await db["companies"].create_index([("organizationId", 1), ("name", 1)], unique=True, sparse=True)
    
    # Branch Indexes
    await db["branches"].create_index([("companyId", 1), ("name", 1)], unique=True, sparse=True)
    
    # Department Indexes
    await db["departments"].create_index([("companyId", 1), ("name", 1)], unique=True, sparse=True)
    
    # Designation Indexes
    await db["designations"].create_index([("departmentId", 1), ("name", 1)], unique=True, sparse=True)
    
    # Role Indexes
    await db["roles"].create_index([("companyId", 1), ("name", 1)], unique=True, sparse=True)
    
    # Shift Indexes
    await db["shifts"].create_index([("companyId", 1), ("name", 1)], unique=True, sparse=True)
    
    # Holiday Indexes
    await db["holidays"].create_index([("companyId", 1), ("branchId", 1), ("date", 1)], unique=True, sparse=True)
    
    print("Organization Engine MongoDB Indexes initialized successfully.")

if __name__ == "__main__":
    asyncio.run(init_org_indexes())
"""
    with open("backend/app/scripts/init_org_indexes.py", "w") as f:
        f.write(content)

if __name__ == "__main__":
    write_base_repository()
    for e in entities:
        write_entity_code(e)
    write_index_script()
    print("Remediation complete.")
