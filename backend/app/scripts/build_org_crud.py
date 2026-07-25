import os
from pathlib import Path

BASE_DIR = Path("backend/app/organization")
entities = [
    "organization", "company", "branch", "department", 
    "designation", "role", "shift", "holiday"
]

def write_base_repository():
    content = """from typing import TypeVar, Generic, Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime, timezone

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
        doc = await self.collection.find_one({"_id": ObjectId(id), "deletedAt": None})
        if doc:
            return self.model_class(**self._prepare_doc(doc))
        return None

    async def get_all(self, query: dict = None) -> List[T]:
        if query is None:
            query = {}
        query["deletedAt"] = None
        cursor = self.collection.find(query)
        docs = await cursor.to_list(length=None)
        return [self.model_class(**self._prepare_doc(doc)) for doc in docs]

    async def update(self, id: str, data: dict, updated_by: str = None) -> Optional[T]:
        data["updatedAt"] = datetime.now(timezone.utc)
        data["updatedBy"] = updated_by
        
        # Prevent immutable field updates
        data.pop("createdAt", None)
        data.pop("createdBy", None)
        
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(id), "deletedAt": None},
            {"$set": data},
            return_document=True
        )
        if result:
            return self.model_class(**self._prepare_doc(result))
        return None

    async def soft_delete(self, id: str, deleted_by: str = None) -> bool:
        result = await self.collection.update_one(
            {"_id": ObjectId(id), "deletedAt": None},
            {"$set": {
                "deletedAt": datetime.now(timezone.utc),
                "deletedBy": deleted_by,
                "status": "Deleted"
            }}
        )
        return result.modified_count > 0
"""
    with open(BASE_DIR / "repositories" / "base_repository.py", "w") as f:
        f.write(content)

def write_entity_code(entity: str):
    cap = entity.capitalize()
    
    # Update Repo
    repo_content = f"""from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.{entity} import {cap}Model

class {cap}Repository(BaseRepository[{cap}Model]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "{entity if entity.endswith('s') else entity + 's'}", {cap}Model)
"""
    with open(BASE_DIR / "repositories" / f"{entity}_repository.py", "w") as f:
        f.write(repo_content)

    # Update Service
    svc_content = f"""from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..repositories.{entity}_repository import {cap}Repository
from ..validators.{entity}_validator import {cap}Validator
from ..schemas.{entity} import {cap}Create, {cap}Update
from ..models.{entity} import {cap}Model

class {cap}Service:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.repo = {cap}Repository(db)
        self.validator = {cap}Validator(db)
        
    async def create(self, data: {cap}Create, user_id: str = None) -> {cap}Model:
        # await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None) -> List[{cap}Model]:
        return await self.repo.get_all(query)
        
    async def get_by_id(self, id: str) -> Optional[{cap}Model]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: {cap}Update, user_id: str = None) -> Optional[{cap}Model]:
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
"""
    with open(BASE_DIR / "services" / f"{entity}_service.py", "w") as f:
        f.write(svc_content)

    # Update Controller
    ctrl_content = f"""from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.{entity}_service import {cap}Service
from ..schemas.{entity} import {cap}Create, {cap}Update, {cap}Response
from ..models.{entity} import {cap}Model

class {cap}Controller:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = {cap}Service(db)
        
    async def create(self, data: {cap}Create, user_id: str = None) -> {cap}Model:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict = None) -> List[{cap}Model]:
        return await self.service.get_all(query)
        
    async def get_by_id(self, id: str) -> {cap}Model:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="{cap} not found")
        return doc
        
    async def update(self, id: str, data: {cap}Update, user_id: str = None) -> {cap}Model:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="{cap} not found")
        return doc
        
    async def delete(self, id: str, user_id: str = None) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="{cap} not found")
        return {{"message": "{cap} deleted successfully"}}
"""
    with open(BASE_DIR / "controllers" / f"{entity}_controller.py", "w") as f:
        f.write(ctrl_content)

    # Update Routes
    route_content = f"""from typing import List
from fastapi import APIRouter, Depends
from ....db.mongo import get_database
from ..controllers.{entity}_controller import {cap}Controller
from ..schemas.{entity} import {cap}Create, {cap}Update, {cap}Response

router = APIRouter(prefix="/{entity if entity.endswith('s') else entity + 's'}", tags=["{cap}"])

def get_controller(db = Depends(get_database)) -> {cap}Controller:
    return {cap}Controller(db)

@router.post("/", response_model={cap}Response)
async def create(data: {cap}Create, controller: {cap}Controller = Depends(get_controller)):
    return await controller.create(data)

@router.get("/", response_model=List[{cap}Response])
async def get_all(controller: {cap}Controller = Depends(get_controller)):
    return await controller.get_all()

@router.get("/{{id}}", response_model={cap}Response)
async def get_by_id(id: str, controller: {cap}Controller = Depends(get_controller)):
    return await controller.get_by_id(id)

@router.put("/{{id}}", response_model={cap}Response)
async def update(id: str, data: {cap}Update, controller: {cap}Controller = Depends(get_controller)):
    return await controller.update(id, data)

@router.delete("/{{id}}")
async def delete(id: str, controller: {cap}Controller = Depends(get_controller)):
    return await controller.delete(id)
"""
    with open(BASE_DIR / "routes" / f"{entity}_routes.py", "w") as f:
        f.write(route_content)


if __name__ == "__main__":
    write_base_repository()
    for e in entities:
        write_entity_code(e)
    print("CRUD logic applied successfully.")
