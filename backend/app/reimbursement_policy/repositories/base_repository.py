from typing import TypeVar, Generic, Optional, List
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
        if not doc: return doc
        doc["_id"] = str(doc["_id"])
        return doc

    async def create(self, data: dict, created_by: str = None, session=None) -> T:
        now = datetime.now(timezone.utc)
        data["createdAt"] = now
        data["updatedAt"] = now
        data["createdBy"] = created_by
        data["updatedBy"] = created_by
        data["status"] = data.get("status", "Active")
        result = await self.collection.insert_one(data, session=session)
        data["_id"] = str(result.inserted_id)
        return self.model_class(**data)

    async def get_by_id(self, id: str, session=None) -> Optional[T]:
        try: obj_id = ObjectId(id)
        except: return None
        doc = await self.collection.find_one({"_id": obj_id, "deletedAt": None}, session=session)
        return self.model_class(**self._prepare_doc(doc)) if doc else None
