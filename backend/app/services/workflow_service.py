from datetime import datetime, timezone
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Any, List
from ..models import Workflow, WorkflowAction

async def create_workflow(
    db: AsyncIOMotorDatabase,
    workflow_type: str,
    entity_id: str,
    employee_id: str,
    current_approver_id: str
) -> Workflow:
    workflow = {
        "workflowType": workflow_type,
        "entityId": entity_id,
        "employeeId": employee_id,
        "currentApproverId": current_approver_id,
        "status": "PENDING",
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc)
    }
    result = await db.workflows.insert_one(workflow)
    workflow["_id"] = str(result.inserted_id)
    return Workflow(**workflow)


async def get_pending_workflows(db: AsyncIOMotorDatabase, manager_id: str) -> List[dict]:
    # Aggregate to join with miss_punch_requests (and others in the future) and users
    pipeline = [
        {"$match": {"currentApproverId": manager_id, "status": "PENDING"}},
        # Lookup Miss Punch Requests
        {
            "$lookup": {
                "from": "miss_punch_requests",
                "let": {"entityId": {"$toObjectId": "$entityId"}, "wfType": "$workflowType"},
                "pipeline": [
                    {"$match": {"$expr": {"$and": [
                        {"$eq": ["$_id", "$$entityId"]},
                        {"$eq": ["$$wfType", "MISS_PUNCH"]}
                    ]}}}
                ],
                "as": "missPunchDetails"
            }
        },
        # Lookup User to get name
        {
            "$lookup": {
                "from": "users",
                "localField": "employeeId",
                "foreignField": "empId",
                "as": "user"
            }
        },
        {"$unwind": {"path": "$user", "preserveNullAndEmptyArrays": True}}
    ]
    
    docs = await db.workflows.aggregate(pipeline).to_list(length=None)
    
    results = []
    for doc in docs:
        doc["_id"] = str(doc["_id"])
        
        # Format for frontend
        formatted = {
            "id": doc["_id"],
            "workflowType": doc["workflowType"],
            "employeeId": doc["employeeId"],
            "employeeName": doc.get("user", {}).get("name", doc["employeeId"]),
            "status": doc["status"],
            "createdAt": doc["createdAt"].isoformat() if doc.get("createdAt") else None
        }
        
        if doc["workflowType"] == "MISS_PUNCH" and doc.get("missPunchDetails"):
            mp = doc["missPunchDetails"][0]
            formatted["details"] = {
                "date": mp.get("attendanceDate"),
                "type": mp.get("requestType"),
                "time": mp.get("requestedTime"),
                "reason": mp.get("reason")
            }
            
        results.append(formatted)
        
    return results


async def process_workflow_action(
    db: AsyncIOMotorDatabase,
    workflow_id: str,
    action: str, # "APPROVED", "REJECTED", "RETURNED"
    acted_by: str,
    remarks: str | None = None
) -> Workflow:
    action_doc = {
        "workflowId": workflow_id,
        "action": action,
        "actedBy": acted_by,
        "remarks": remarks,
        "actedAt": datetime.now(timezone.utc)
    }
    await db.workflow_actions.insert_one(action_doc)
    
    update_doc = {
        "status": action,
        "updatedAt": datetime.now(timezone.utc)
    }
    await db.workflows.update_one({"_id": ObjectId(workflow_id)}, {"$set": update_doc})
    
    workflow_doc = await db.workflows.find_one({"_id": ObjectId(workflow_id)})
    workflow_doc["_id"] = str(workflow_doc["_id"])
    
    workflow = Workflow(**workflow_doc)
    
    # Hook system dispatch
    if workflow.status == "APPROVED":
        await _dispatch_approval(db, workflow)
        
    return workflow


async def _dispatch_approval(db: AsyncIOMotorDatabase, workflow: Workflow):
    if workflow.workflowType == "MISS_PUNCH":
        from .miss_punch_service import handle_miss_punch_approval
        await handle_miss_punch_approval(db, workflow)
    # Future modules can hook here (Leave, Permission, etc.)
