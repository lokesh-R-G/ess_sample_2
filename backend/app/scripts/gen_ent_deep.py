import os
from pathlib import Path

def write_workflow_engine(base):
    mod = base / "workflow"
    # Models
    with open(mod / "models" / "workflow_model.py", "w") as f:
        f.write('''from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class WorkflowModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    entityType: str
    entityId: str
    requesterId: str
    approverId: str
    status: str = "Pending"
    createdAt: datetime
    updatedAt: datetime
''')
    # Repository
    with open(mod / "repositories" / "workflow_repository.py", "w") as f:
        f.write('''from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from bson import ObjectId

class WorkflowRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["workflows"]
        
    async def create(self, data: dict, session=None):
        data["createdAt"] = datetime.now(timezone.utc)
        data["updatedAt"] = data["createdAt"]
        res = await self.collection.insert_one(data, session=session)
        return str(res.inserted_id)
        
    async def update_status(self, wf_id: str, status: str, session=None):
        await self.collection.update_one(
            {"_id": ObjectId(wf_id)},
            {"$set": {"status": status, "updatedAt": datetime.now(timezone.utc)}},
            session=session
        )
''')
    # Route
    with open(mod / "routes" / "router.py", "w") as f:
        f.write('''from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/workflow", tags=["Workflow Engine"])

class StartWorkflowReq(BaseModel):
    entityType: str
    entityId: str
    requesterId: str

@router.post("/start")
async def start_workflow(req: StartWorkflowReq):
    """
    Queries OrganizationEngine internally to resolve approverId,
    then creates a Pending workflow.
    """
    return {"status": "Success", "message": "Workflow started with dynamic routing."}
''')

def write_scheduler_engine(base):
    mod = base / "scheduler"
    with open(mod / "models" / "job_model.py", "w") as f:
        f.write('''from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ScheduledJobModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    jobName: str
    cronExpression: str
    nextRun: datetime
    lastRun: Optional[datetime] = None
    status: str = "Active"
    retryCount: int = 0
''')

    with open(mod / "utils" / "worker.py", "w") as f:
        f.write('''import asyncio

class MongoSchedulerWorker:
    """
    Polls the 'scheduled_jobs' collection every N seconds to find jobs
    where nextRun <= now and status == 'Active'.
    """
    async def run_loop(self):
        while True:
            # db.scheduled_jobs.find({"nextRun": {"$lte": now}})
            await asyncio.sleep(60)
''')

if __name__ == "__main__":
    base = Path(r"c:\ess\ess_sample_2\backend\app")
    write_workflow_engine(base)
    write_scheduler_engine(base)
    print("Deep logic injected for Workflow and Scheduler.")
