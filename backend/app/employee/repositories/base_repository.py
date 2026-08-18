from typing import TypeVar, Generic, Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime, timezone
import math
from pymongo import ReturnDocument

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
        data["version"] = data.get("version", 1)
        data["isCurrent"] = data.get("isCurrent", True)
        data["effectiveFrom"] = data.get("effectiveFrom") or now
        if data["effectiveFrom"].tzinfo is None:
            data["effectiveFrom"] = data["effectiveFrom"].replace(tzinfo=timezone.utc)
        data["effectiveTo"] = None
        
        result = await self.collection.insert_one(data)
        data["_id"] = str(result.inserted_id)
        return self.model_class(**data)

    async def upsert_by_field(self, query_field: str, query_value: Any, data: dict, user_id: str = None) -> T:
        now = datetime.now(timezone.utc)
        data["updatedAt"] = now
        data["updatedBy"] = user_id
        data["status"] = data.get("status", "Active")
        
        # Check if current version exists
        async with await self.db.client.start_session() as session:
            async with session.start_transaction():
                current_doc = await self.collection.find_one(
                    {query_field: query_value, "isCurrent": True, "deletedAt": None},
                    session=session
                )
                
                if current_doc:
                    new_effective_from = data.get("effectiveFrom")
                    
                    current_eff = current_doc.get("effectiveFrom")
                    if current_eff and current_eff.tzinfo is None:
                        current_eff = current_eff.replace(tzinfo=timezone.utc)
                        
                    if new_effective_from:
                        if new_effective_from.tzinfo is None:
                            new_effective_from = new_effective_from.replace(tzinfo=timezone.utc)
                        if current_eff and new_effective_from <= current_eff:
                            new_effective_from = now
                    else:
                        new_effective_from = now
                        
                    # Mark current as false
                    await self.collection.update_one(
                        {"_id": current_doc["_id"]}, 
                        {"$set": {"isCurrent": False, "effectiveTo": new_effective_from}},
                        session=session
                    )
                    
                    # Prepare new document
                    new_doc = {**current_doc, **data}
                    new_doc.pop("_id", None)
                    new_doc["version"] = current_doc.get("version", 1) + 1
                    new_doc["isCurrent"] = True
                    new_doc["effectiveFrom"] = new_effective_from
                    new_doc["effectiveTo"] = None
                    
                    result = await self.collection.insert_one(new_doc, session=session)
                    new_doc["_id"] = str(result.inserted_id)
                    return self.model_class(**self._prepare_doc(new_doc))
                else:
                    # Insert first version
                    data["createdAt"] = now
                    data["createdBy"] = user_id
                    data["version"] = 1
                    data["isCurrent"] = True
                    data["effectiveFrom"] = data.get("effectiveFrom") or now
                    if data["effectiveFrom"].tzinfo is None:
                        data["effectiveFrom"] = data["effectiveFrom"].replace(tzinfo=timezone.utc)
                    data["effectiveTo"] = None
                    
                    result = await self.collection.insert_one(data, session=session)
                    data["_id"] = str(result.inserted_id)
                    return self.model_class(**self._prepare_doc(data))

    async def get_by_id(self, id: str) -> Optional[T]:
        try:
            obj_id = ObjectId(id)
        except:
            return None
        doc = await self.collection.find_one({"_id": obj_id, "deletedAt": None})
        if doc:
            return self.model_class(**self._prepare_doc(doc))
        return None

    async def get_by_code_and_date(self, code_field: str, code_value: str, target_date: datetime) -> Optional[T]:
        """
        Resolves the configuration using businessCode + attendanceDate.
        Effective rule: effectiveFrom <= attendanceDate < effectiveTo
        If effectiveTo is null: effectiveFrom <= attendanceDate
        """
        query = {
            code_field: code_value,
            "deletedAt": None,
            "effectiveFrom": {"$lte": target_date},
            "$or": [
                {"effectiveTo": None},
                {"effectiveTo": {"$gt": target_date}}
            ]
        }
        
        # We sort by version descending just in case there's an overlap bug, 
        # picking the highest version that matches the date.
        doc = await self.collection.find_one(query, sort=[("version", -1)])
        if doc:
            return self.model_class(**self._prepare_doc(doc))
        return None

    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, sort_by: str = "createdAt", sort_order: int = -1, search: str = None, search_fields: List[str] = None) -> dict:
        if query is None:
            query = {}
            
        if "deletedAt" not in query:
            query["deletedAt"] = None
            
        if "isCurrent" not in query:
            query["isCurrent"] = True
            
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
            
        now = datetime.now(timezone.utc)
            
        async with await self.db.client.start_session() as session:
            async with session.start_transaction():
                current_doc = await self.collection.find_one(
                    {"_id": obj_id, "deletedAt": None},
                    session=session
                )
                if not current_doc:
                    return None
                    
                new_effective_from = data.get("effectiveFrom")
                
                current_eff = current_doc.get("effectiveFrom")
                if current_eff and current_eff.tzinfo is None:
                    current_eff = current_eff.replace(tzinfo=timezone.utc)
                    
                if new_effective_from:
                    if new_effective_from.tzinfo is None:
                        new_effective_from = new_effective_from.replace(tzinfo=timezone.utc)
                    if current_eff and new_effective_from <= current_eff:
                        new_effective_from = now
                else:
                    new_effective_from = now
                
                await self.collection.update_one(
                    {"_id": obj_id}, 
                    {"$set": {"isCurrent": False, "effectiveTo": new_effective_from}},
                    session=session
                )
                
                new_doc = {**current_doc, **data}
                new_doc.pop("_id", None)
                new_doc["version"] = current_doc.get("version", 1) + 1
                new_doc["isCurrent"] = True
                new_doc["effectiveFrom"] = new_effective_from
                new_doc["effectiveTo"] = None
                
                result = await self.collection.insert_one(new_doc, session=session)
                new_doc["_id"] = str(result.inserted_id)
                return self.model_class(**self._prepare_doc(new_doc))

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
        if "isCurrent" not in query:
            query["isCurrent"] = True
        doc = await self.collection.find_one(query, {"_id": 1})
        return doc is not None

    async def get_history(self, query_field: str, query_value: Any) -> List[T]:
        # Returns all versions sorted by version ascending
        cursor = self.collection.find({query_field: query_value, "deletedAt": None})
        cursor = cursor.sort("version", 1)
        docs = await cursor.to_list(length=None)
        return [self.model_class(**self._prepare_doc(doc)) for doc in docs]
