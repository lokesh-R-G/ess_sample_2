from typing import TypeVar, Generic, Optional, List, Dict, Any
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
        data["isDeleted"] = False
        
        result = await self.collection.insert_one(data)
        data["_id"] = str(result.inserted_id)
        return self.model_class(**data)

    async def get_by_id(self, id: str) -> Optional[T]:
        try:
            obj_id = ObjectId(id)
        except:
            return None
        doc = await self.collection.find_one({"_id": obj_id, "isDeleted": False})
        if doc:
            return self.model_class(**self._prepare_doc(doc))
        return None

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
            {"_id": obj_id, "isDeleted": False},
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
            {"_id": obj_id, "isDeleted": False},
            {"$set": {
                "isDeleted": True,
                "deletedAt": datetime.now(timezone.utc),
                "deletedBy": deleted_by,
                "status": "Deleted"
            }}
        )
        return result.modified_count > 0
