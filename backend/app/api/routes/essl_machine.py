from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
from bson import ObjectId

from app.db.mongo import get_database
from app.services.auth_service import serialize_user
from app.dependencies import require_permission, get_current_user

router = APIRouter(prefix="/api/v2/essl-machine", tags=["ESSL Machine"])

class EsslMachineCreate(BaseModel):
    serialNumber: str = Field(..., description="Unique hardware serial number of the ESSL device")
    machineName: str = Field(..., description="Human readable name for the machine")
    ipAddress: Optional[str] = Field(None, description="IP address of the machine")
    status: str = Field("Active", description="Status of the machine (Active | Inactive)")

class EsslMachineUpdate(BaseModel):
    machineName: Optional[str] = None
    ipAddress: Optional[str] = None
    status: Optional[str] = None

class EsslMachineResponse(EsslMachineCreate):
    id: str = Field(alias="_id")
    lastSyncAt: Optional[datetime] = None
    lastSuccessfulSyncAt: Optional[datetime] = None
    lastSyncError: Optional[str] = None
    syncStatus: str = "IDLE"
    createdAt: datetime
    updatedAt: datetime
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None

    class Config:
        populate_by_name = True

@router.post("", response_model=EsslMachineResponse, status_code=status.HTTP_201_CREATED)
async def create_machine(
    data: EsslMachineCreate,
    db = Depends(get_database),
    _admin = Depends(require_permission("essl_machine.manage"))
):
    existing = await db.essl_machines.find_one({"serialNumber": data.serialNumber})
    if existing:
        raise HTTPException(status_code=400, detail="Machine with this serial number already exists")

    now = datetime.now(timezone.utc)
    
    doc = data.dict()
    doc["syncStatus"] = "IDLE"
    doc["createdAt"] = now
    doc["updatedAt"] = now
    
    result = await db.essl_machines.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return doc

@router.get("", response_model=List[EsslMachineResponse])
async def list_machines(
    db = Depends(get_database),
    _view = Depends(require_permission("essl_machine.view"))
):
    cursor = db.essl_machines.find({}).sort("createdAt", -1)
    machines = await cursor.to_list(length=None)
    for m in machines:
        m["_id"] = str(m["_id"])
    return machines

@router.get("/{machine_id}", response_model=EsslMachineResponse)
async def get_machine(
    machine_id: str,
    db = Depends(get_database),
    _view = Depends(require_permission("essl_machine.view"))
):
    if not ObjectId.is_valid(machine_id):
        raise HTTPException(status_code=400, detail="Invalid machine ID")
        
    machine = await db.essl_machines.find_one({"_id": ObjectId(machine_id)})
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    machine["_id"] = str(machine["_id"])
    return machine

@router.patch("/{machine_id}", response_model=EsslMachineResponse)
async def update_machine(
    machine_id: str,
    data: EsslMachineUpdate,
    db = Depends(get_database),
    _admin = Depends(require_permission("essl_machine.manage"))
):
    if not ObjectId.is_valid(machine_id):
        raise HTTPException(status_code=400, detail="Invalid machine ID")
        
    machine = await db.essl_machines.find_one({"_id": ObjectId(machine_id)})
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    update_data = {k: v for k, v in data.dict().items() if v is not None}
    if not update_data:
        machine["_id"] = str(machine["_id"])
        return machine

    update_data["updatedAt"] = datetime.now(timezone.utc)
    await db.essl_machines.update_one(
        {"_id": ObjectId(machine_id)},
        {"$set": update_data}
    )
    
    updated = await db.essl_machines.find_one({"_id": ObjectId(machine_id)})
    updated["_id"] = str(updated["_id"])
    return updated

@router.delete("/{machine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_machine(
    machine_id: str,
    db = Depends(get_database),
    _admin = Depends(require_permission("essl_machine.manage"))
):
    if not ObjectId.is_valid(machine_id):
        raise HTTPException(status_code=400, detail="Invalid machine ID")
        
    machine = await db.essl_machines.find_one({"_id": ObjectId(machine_id)})
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
        
    # Soft deactivate
    await db.essl_machines.update_one(
        {"_id": ObjectId(machine_id)},
        {"$set": {"status": "Inactive", "updatedAt": datetime.now(timezone.utc)}}
    )
