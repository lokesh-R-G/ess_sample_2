from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.mongo import get_database
from app.dependencies import get_current_user
from app.organization.repositories.base_repository import BaseRepository
from app.domain_models import SalaryStructure
from app.organization.schemas.salary_structure import (
    SalaryStructureCreate, SalaryStructureUpdate, SalaryStructureResponse
)

router = APIRouter(prefix="/salary-structures", tags=["Salary Structure"])


def get_repo(db: AsyncIOMotorDatabase = Depends(get_database)) -> BaseRepository:
    return BaseRepository(db, "salary_structures", SalaryStructure)


async def _enrich_components(structures: list, db: AsyncIOMotorDatabase) -> list:
    """Batch-load Salary Component summaries to avoid N+1 queries."""
    if not structures:
        return structures

    # Collect all unique component IDs across every structure
    all_ids: set = set()
    for s in structures:
        ids = getattr(s, "componentIds", None) or []
        for cid in ids:
            all_ids.add(cid)

    if not all_ids:
        return structures

    obj_ids = []
    for cid in all_ids:
        try:
            obj_ids.append(ObjectId(cid))
        except Exception:
            pass

    cursor = db["salary_components"].find(
        {"_id": {"$in": obj_ids}, "deletedAt": None},
        {"_id": 1, "name": 1, "componentType": 1, "calculationMethod": 1}
    )
    docs = await cursor.to_list(length=None)

    # Build lookup map keyed by string id
    component_map = {str(doc["_id"]): {"id": str(doc["_id"]), "name": doc.get("name"), "componentType": doc.get("componentType"), "calculationMethod": doc.get("calculationMethod")} for doc in docs}

    # Attach to each structure
    for s in structures:
        ids = getattr(s, "componentIds", None) or []
        setattr(s, "components", [component_map[cid] for cid in ids if cid in component_map])

    return structures


@router.post("/", response_model=SalaryStructureResponse)
async def create(
    data: SalaryStructureCreate,
    repo: BaseRepository = Depends(get_repo),
    db: AsyncIOMotorDatabase = Depends(get_database),
    user: dict = Depends(get_current_user)
):
    structure = await repo.create(data.model_dump(exclude_unset=True), user.get("empId"))
    enriched = await _enrich_components([structure], db)
    return enriched[0]


@router.get("/")
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    status: Optional[str] = None,
    repo: BaseRepository = Depends(get_repo),
    db: AsyncIOMotorDatabase = Depends(get_database),
    user: dict = Depends(get_current_user)
):
    query = {}
    if status:
        query["status"] = status
    result = await repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
    result["data"] = await _enrich_components(result["data"], db)
    return result


@router.get("/{id}", response_model=SalaryStructureResponse)
async def get_by_id(
    id: str,
    repo: BaseRepository = Depends(get_repo),
    db: AsyncIOMotorDatabase = Depends(get_database),
    user: dict = Depends(get_current_user)
):
    doc = await repo.get_by_id(id)
    if not doc:
        raise HTTPException(status_code=404, detail="Salary Structure not found")
    enriched = await _enrich_components([doc], db)
    return enriched[0]


@router.put("/{id}", response_model=SalaryStructureResponse)
async def update(
    id: str,
    data: SalaryStructureUpdate,
    repo: BaseRepository = Depends(get_repo),
    db: AsyncIOMotorDatabase = Depends(get_database),
    user: dict = Depends(get_current_user)
):
    doc = await repo.update(id, data.model_dump(exclude_unset=True), user.get("empId"))
    if not doc:
        raise HTTPException(status_code=404, detail="Salary Structure not found")
    enriched = await _enrich_components([doc], db)
    return enriched[0]


@router.delete("/{id}")
async def delete(
    id: str,
    repo: BaseRepository = Depends(get_repo),
    user: dict = Depends(get_current_user)
):
    success = await repo.soft_delete(id, user.get("empId"))
    if not success:
        raise HTTPException(status_code=404, detail="Salary Structure not found")
    return {"message": "Salary Structure archived successfully"}
