from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List
from datetime import datetime, timezone
from app.db.mongo import get_database
from app.dependencies import require_permission, get_current_user
from app.models import SchedulerJobConfig
from app.scheduler.scheduler import update_job_schedule

router = APIRouter(tags=["Scheduler Engine"])

class SchedulerConfigUpdate(BaseModel):
    enabled: bool
    frequencyMinutes: int
    lookbackDays: int

@router.get("/config", response_model=List[SchedulerJobConfig])
async def get_scheduler_config(db=Depends(get_database), _admin=Depends(require_permission("scheduler.configure"))):
    cursor = db.scheduler_configs.find({})
    configs = await cursor.to_list(length=None)
    
    # Map _id -> id
    for c in configs:
        c["_id"] = str(c["_id"])
        
    return configs

@router.put("/config/{job_key}", response_model=SchedulerJobConfig)
async def update_scheduler_config(
    job_key: str, 
    payload: SchedulerConfigUpdate, 
    db=Depends(get_database), 
    current_user=Depends(get_current_user),
    _admin=Depends(require_permission("scheduler.configure"))
):

    if payload.frequencyMinutes < 1:
        raise HTTPException(status_code=400, detail="Frequency must be at least 1 minute")
        
    if payload.lookbackDays < 0:
        raise HTTPException(status_code=400, detail="Lookback days cannot be negative")

    update_data = {
        "enabled": payload.enabled,
        "frequencyMinutes": payload.frequencyMinutes,
        "lookbackDays": payload.lookbackDays,
        "updatedAt": datetime.now(timezone.utc),
        "updatedBy": current_user.get("empId")
    }

    result = await db.scheduler_configs.find_one_and_update(
        {"jobKey": job_key},
        {"$set": update_data},
        return_document=True
    )

    if not result:
        raise HTTPException(status_code=404, detail="Job configuration not found")

    result["_id"] = str(result["_id"])
    
    # Dynamically update the running scheduler instance
    update_job_schedule(job_key, update_data["enabled"], update_data["frequencyMinutes"])

    return result
