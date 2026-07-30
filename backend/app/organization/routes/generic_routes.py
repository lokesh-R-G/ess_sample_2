from typing import TypeVar, Type, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from app.db.mongo import get_database
from app.dependencies import get_current_user
from app.organization.repositories.base_repository import BaseRepository
from datetime import datetime, timezone

TModel = TypeVar("TModel", bound=BaseModel)
TCreate = TypeVar("TCreate", bound=BaseModel)
TUpdate = TypeVar("TUpdate", bound=BaseModel)

class GenericService:
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str, model_class: Type[TModel]):
        self.repo = BaseRepository(db, collection_name, model_class)
        self.db = db

    async def create(self, data: TCreate, user_id: str = None) -> TModel:
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None, search_fields: list = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=search_fields or ["name"])
        
    async def get_by_id(self, id: str) -> Optional[TModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: TUpdate, user_id: str = None) -> Optional[TModel]:
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)

def create_generic_router(
    prefix: str,
    tag: str,
    collection_name: str,
    model_class: Type[TModel],
    create_schema: Type[TCreate],
    update_schema: Type[TUpdate],
    response_schema: Type[BaseModel],
    search_fields: list = ["name"]
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=[tag])

    def get_service(db = Depends(get_database)) -> GenericService:
        return GenericService(db, collection_name, model_class)

    @router.post("/", response_model=response_schema)
    async def create(data: create_schema, service: GenericService = Depends(get_service), user: dict = Depends(get_current_user)):
        return await service.create(data, user.get("empId"))

    @router.get("/")
    async def get_all(
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
        return await service.get_all(query, skip, limit, search, search_fields)

    @router.get("/{id}", response_model=response_schema)
    async def get_by_id(id: str, service: GenericService = Depends(get_service), user: dict = Depends(get_current_user)):
        doc = await service.get_by_id(id)
        if not doc: raise HTTPException(status_code=404, detail=f"{tag} not found")
        return doc

    @router.put("/{id}", response_model=response_schema)
    async def update(id: str, data: update_schema, service: GenericService = Depends(get_service), user: dict = Depends(get_current_user)):
        doc = await service.update(id, data, user.get("empId"))
        if not doc: raise HTTPException(status_code=404, detail=f"{tag} not found")
        return doc

    @router.delete("/{id}")
    async def delete(id: str, service: GenericService = Depends(get_service), user: dict = Depends(get_current_user)):
        success = await service.delete(id, user.get("empId"))
        if not success: raise HTTPException(status_code=404, detail=f"{tag} not found")
        return {"message": f"{tag} archived successfully"}

    return router
