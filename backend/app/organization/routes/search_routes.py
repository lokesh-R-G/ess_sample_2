from typing import Optional, Dict
from fastapi import APIRouter, Depends, Query, HTTPException
from app.db.mongo import get_database
from app.dependencies import get_current_user

router = APIRouter(prefix="/search", tags=["Search"])

ENTITY_REGISTRY = {
    "Company": {"collection": "companys", "fields": ["name", "registrationNumber"]},
    "Branch": {"collection": "branchs", "fields": ["name", "code"]},
    "Department": {"collection": "departments", "fields": ["name", "code"]},
    "Designation": {"collection": "designations", "fields": ["name", "code"]},
    "Holiday": {"collection": "holidays", "fields": ["name", "date"]},
    "Role": {"collection": "roles", "fields": ["name", "code"]},
    "Shift": {"collection": "shifts", "fields": ["name", "code", "startTime", "endTime"]},
    "ESSLMachine": {"collection": "essl_machines", "fields": ["serialNumber", "ipAddress"]},
    "SalaryComponent": {"collection": "salary_components", "fields": ["name", "code"]},
    "SalaryStructure": {"collection": "salary_structures", "fields": ["name", "code"]},
}

@router.get("/")
async def global_search(
    entity: str = Query(..., description="The entity to search (e.g. Company, Branch)"),
    search: str = Query(..., description="The text to search for"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query("Active", description="Filter by status (default: Active)"),
    db = Depends(get_database),
    user: dict = Depends(get_current_user)
):
    if entity not in ENTITY_REGISTRY:
        raise HTTPException(status_code=400, detail=f"Invalid entity: {entity}. Supported entities: {list(ENTITY_REGISTRY.keys())}")
        
    config = ENTITY_REGISTRY[entity]
    collection = db[config["collection"]]
    
    # Base query: active records only by default, and not deleted
    query: Dict = {"deletedAt": None}
    if status:
        query["status"] = status
        
    # Apply text search if query is provided
    if search:
        or_conditions = []
        for field in config["fields"]:
            or_conditions.append({field: {"$regex": search, "$options": "i"}})
        if or_conditions:
            query["$or"] = or_conditions
            
    cursor = collection.find(query).skip(skip).limit(limit)
    documents = await cursor.to_list(length=limit)
    
    # Format documents to ensure _id is string
    results = []
    for doc in documents:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
        
    # Get total count
    total_count = await collection.count_documents(query)
    
    return {
        "data": results,
        "total": total_count,
        "skip": skip,
        "limit": limit
    }
