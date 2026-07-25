import os
from pathlib import Path

# Directories
MODULES = {
    "attendance_policy": {
        "entities": [
            "attendance_policy", "grace_policy", "late_policy", "late_penalty_rule",
            "permission_policy", "permission_overflow_rule", "leave_conversion_rule",
            "shift_attendance_policy", "attendance_policy_history", "attendance_policy_version"
        ],
        "prefix": "attendance-policy"
    },
    "permission": {
        "entities": [
            "permission_request", "permission_approval", "permission_balance",
            "permission_usage", "permission_overflow", "permission_history",
            "permission_attachment", "grace_request", "grace_approval"
        ],
        "prefix": "permission"
    },
    "attendance_v2": {
        "entities": [
            "attendance", "attendance_log", "daily_attendance", "monthly_attendance",
            "late_log", "grace_log", "attendance_adjustment", "attendance_history",
            "attendance_calculation"
        ],
        "prefix": "attendance"
    }
}

FOLDERS = ["models", "schemas", "repositories", "services", "controllers", "routes", "validators", "constants", "engine", "events"]

def to_camel_case(snake_str):
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def write_base_repository(base_path: Path):
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
        try:
            obj_id = ObjectId(id)
        except:
            return None
        doc = await self.collection.find_one({"_id": obj_id, "deletedAt": None}, session=session)
        if doc:
            return self.model_class(**self._prepare_doc(doc))
        return None

    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, sort_by: str = "createdAt", sort_order: int = -1, search: str = None, search_fields: List[str] = None, session=None) -> dict:
        if query is None:
            query = {}
        if "deletedAt" not in query:
            query["deletedAt"] = None
        if search and search_fields:
            search_query = [{"$regex": search, "$options": "i"}]
            query["$or"] = [{field: search_query[0]} for field in search_fields]
            
        cursor = self.collection.find(query, session=session)
        if sort_by:
            cursor = cursor.sort(sort_by, sort_order)
            
        total = await self.collection.count_documents(query, session=session)
        
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

    async def update(self, id: str, data: dict, updated_by: str = None, session=None) -> Optional[T]:
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
            return_document=True,
            session=session
        )
        if result:
            return self.model_class(**self._prepare_doc(result))
        return None

    async def soft_delete(self, id: str, deleted_by: str = None, session=None) -> bool:
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
            }},
            session=session
        )
        return result.modified_count > 0
"""
    with open(base_path / "repositories" / "base_repository.py", "w") as f:
        f.write(content)

def write_entity_files(base_path: Path, module_name: str, entity: str):
    class_name = "".join(x.capitalize() for x in entity.split('_'))
    camel_name = to_camel_case(entity)
    collection_name = entity + "s" if not entity.endswith("s") and not entity.endswith("history") else entity

    # Model
    with open(base_path / "models" / f"{entity}.py", "w") as f:
        f.write(f'''from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class {class_name}Model(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    name: Optional[str] = None
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
from typing import Optional

class {class_name}Create(BaseModel):
    name: Optional[str] = None

class {class_name}Update(BaseModel):
    status: Optional[str] = None

class {class_name}Response({class_name}Create):
    id: str
''')

    # Repo
    with open(base_path / "repositories" / f"{entity}_repository.py", "w") as f:
        f.write(f'''from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
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
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
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
from ....db.mongo import get_database
from ....dependencies import get_current_user
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
    name: Optional[str] = None,
    status: Optional[str] = None,
    controller: {class_name}Controller = Depends(get_controller),
    user: dict = Depends(get_current_user)
):
    query = {{}}
    if name: query["name"] = name
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

def write_simulator(base_path: Path):
    # Simulator Schema
    with open(base_path / "schemas" / "simulator.py", "w") as f:
        f.write('''from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SimulationRequest(BaseModel):
    employeeId: str
    shiftId: str
    scheduledIn: datetime
    scheduledOut: datetime
    actualIn: datetime
    actualOut: datetime
    permissionRequestedMinutes: int = 0
    currentLateCount: int = 0
    currentPermissionBalanceMinutes: int = 0
    policyVersionId: Optional[str] = None

class SimulationResponse(BaseModel):
    graceUsedMinutes: int
    graceApproved: bool
    lateMinutes: int
    lateCountAfterCalculation: int
    permissionUsedMinutes: int
    permissionRemainingMinutes: int
    permissionOverflowMinutes: int
    leaveDeduction: float
    penaltyApplied: str
    attendanceStatus: str
    calculationTrace: list[str]
''')

    # Simulator Service (using dummy logic matching actual calculations for trace generation)
    with open(base_path / "services" / "simulator_service.py", "w") as f:
        f.write('''from typing import Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..schemas.simulator import SimulationRequest, SimulationResponse

class SimulationEngine:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def simulate(self, req: SimulationRequest) -> SimulationResponse:
        trace = []
        trace.append(f"Starting simulation for Employee {req.employeeId}")
        trace.append(f"Scheduled: {req.scheduledIn} to {req.scheduledOut}")
        trace.append(f"Actual: {req.actualIn} to {req.actualOut}")
        
        # Calculate diffs
        in_diff = (req.actualIn - req.scheduledIn).total_seconds() / 60
        out_diff = (req.scheduledOut - req.actualOut).total_seconds() / 60
        
        grace_used = 0
        late_mins = 0
        grace_approved = False
        status = "Present"
        
        trace.append("Checking Grace Policy...")
        if in_diff > 0:
            if in_diff <= 15: # Dummy grace window
                grace_used = int(in_diff)
                trace.append(f"Punched inside grace window ({grace_used} mins).")
                grace_approved = False  # requires manual approval usually
                if not grace_approved:
                    late_mins = grace_used
                    trace.append("Grace not approved yet. Marking as Late.")
            else:
                late_mins = int(in_diff)
                trace.append(f"Punched outside grace. Late by {late_mins} mins.")
        
        late_count = req.currentLateCount
        if late_mins > 0:
            late_count += 1
            status = "Late"
            trace.append(f"Late count incremented to {late_count}.")
            
        # Permission logic
        trace.append("Checking Permission Policy...")
        perm_used = req.permissionRequestedMinutes
        perm_remaining = req.currentPermissionBalanceMinutes
        perm_overflow = 0
        
        if perm_used > 0:
            trace.append(f"Permission requested: {perm_used} mins.")
            if perm_used > perm_remaining:
                perm_overflow = perm_used - perm_remaining
                perm_remaining = 0
                trace.append(f"Permission overflow recorded: {perm_overflow} mins.")
            else:
                perm_remaining -= perm_used
                trace.append(f"Permission balance remaining: {perm_remaining} mins.")
                
        # Penalty calculation
        leave_deduction = 0.0
        penalty = "None"
        if late_count >= 3:
            leave_deduction = 0.5
            penalty = "Half Day Leave Deducted (Late Threshold Reached)"
            trace.append(penalty)
        if perm_overflow > 60:
            leave_deduction += 0.5
            penalty = "Half Day Leave Deducted (Permission Overflow)"
            trace.append(penalty)
            
        trace.append(f"Final Status: {status}")
            
        return SimulationResponse(
            graceUsedMinutes=grace_used,
            graceApproved=grace_approved,
            lateMinutes=late_mins,
            lateCountAfterCalculation=late_count,
            permissionUsedMinutes=perm_used,
            permissionRemainingMinutes=perm_remaining,
            permissionOverflowMinutes=perm_overflow,
            leaveDeduction=leave_deduction,
            penaltyApplied=penalty,
            attendanceStatus=status,
            calculationTrace=trace
        )
''')

    # Simulator Route
    with open(base_path / "routes" / "simulator_routes.py", "w") as f:
        f.write('''from fastapi import APIRouter, Depends
from ....db.mongo import get_database
from ....dependencies import get_current_user
from ..schemas.simulator import SimulationRequest, SimulationResponse
from ..services.simulator_service import SimulationEngine
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter(prefix="/simulate", tags=["Simulator"])

@router.post("/", response_model=SimulationResponse)
async def simulate_policy(req: SimulationRequest, db: AsyncIOMotorDatabase = Depends(get_database), user: dict = Depends(get_current_user)):
    engine = SimulationEngine(db)
    return await engine.simulate(req)
''')

def generate_module(module_name: str, config: dict):
    base_path = Path(f"backend/app/{module_name}")
    base_path.mkdir(parents=True, exist_ok=True)
    (base_path / "__init__.py").touch()
    
    for folder in FOLDERS:
        (base_path / folder).mkdir(exist_ok=True)
        (base_path / folder / "__init__.py").touch()
        
    write_base_repository(base_path)
    
    for entity in config["entities"]:
        write_entity_files(base_path, module_name, entity)
        
    if module_name == "attendance_policy":
        write_simulator(base_path)
        
    # Master Router
    with open(base_path / "routes" / "router.py", "w") as f:
        f.write('from fastapi import APIRouter\n')
        for entity in config["entities"]:
            f.write(f'from .{entity}_routes import router as {entity}_router\n')
            
        if module_name == "attendance_policy":
            f.write(f'from .simulator_routes import router as simulator_router\n')
            
        f.write(f'\\n{module_name}_router = APIRouter()\n')
        for entity in config["entities"]:
            f.write(f'{module_name}_router.include_router({entity}_router)\n')
            
        if module_name == "attendance_policy":
            f.write(f'{module_name}_router.include_router(simulator_router)\n')


if __name__ == "__main__":
    for module_name, config in MODULES.items():
        generate_module(module_name, config)
    print("Attendance Suite generated successfully.")
