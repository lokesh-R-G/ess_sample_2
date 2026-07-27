from datetime import datetime, timezone
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict, Any
from app.models import MissPunchRequest, Workflow, AttendanceAuditLog
from app.services.workflow_service import create_workflow

async def create_miss_punch_request(
    db: AsyncIOMotorDatabase,
    employee_id: str,
    req: MissPunchRequest
) -> MissPunchRequest:
    # Validate no duplicate pending request for this date/type
    existing = await db.miss_punch_requests.find_one({
        "employeeId": employee_id,
        "attendanceDate": req.attendanceDate,
        "requestType": req.requestType,
        "workflowId": {"$exists": True}
    })
    
    if existing:
        wf = await db.workflows.find_one({"_id": ObjectId(existing["workflowId"])})
        if wf and wf.get("status") == "PENDING":
            raise ValueError("A pending miss punch request already exists for this date and type.")

    # Find the employee's manager
    user = await db.users.find_one({"empId": employee_id})
    manager_id = user.get("managerId")
    if not manager_id:
        raise ValueError("No reporting manager assigned to this employee.")

    # Insert request
    doc = {
        "employeeId": employee_id,
        "attendanceDate": req.attendanceDate,
        "requestType": req.requestType,
        "requestedTime": req.requestedTime,
        "reason": req.reason,
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc)
    }
    result = await db.miss_punch_requests.insert_one(doc)
    request_id = str(result.inserted_id)

    # Create Workflow
    wf = await create_workflow(
        db=db,
        workflow_type="MISS_PUNCH",
        entity_id=request_id,
        employee_id=employee_id,
        current_approver_id=manager_id
    )

    # Update request with workflowId
    await db.miss_punch_requests.update_one(
        {"_id": ObjectId(request_id)},
        {"$set": {"workflowId": wf.id}}
    )

    doc["_id"] = request_id
    doc["workflowId"] = wf.id
    return MissPunchRequest(**doc)


async def get_employee_requests(db: AsyncIOMotorDatabase, employee_id: str) -> List[Dict[str, Any]]:
    cursor = db.miss_punch_requests.aggregate([
        {"$match": {"employeeId": employee_id}},
        {
            "$lookup": {
                "from": "workflows",
                "let": {"wfId": {"$toObjectId": "$workflowId"}},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$_id", "$$wfId"]}}}
                ],
                "as": "workflow"
            }
        },
        {"$unwind": "$workflow"},
        {"$sort": {"createdAt": -1}}
    ])
    
    results = await cursor.to_list(length=None)
    for res in results:
        res["_id"] = str(res["_id"])
        res["workflow"]["_id"] = str(res["workflow"]["_id"])
    return results


async def handle_miss_punch_approval(db: AsyncIOMotorDatabase, workflow: Workflow):
    """
    Hook called by Workflow engine when a Miss Punch request is approved.
    Inserts a synthetic log and recalculates attendance.
    """
    # 1. Fetch the request
    mp_req = await db.miss_punch_requests.find_one({"_id": ObjectId(workflow.entityId)})
    if not mp_req:
        return
        
    # 2. Fetch old attendance record for audit log
    old_attendance = await db.attendance.find_one({
        "empId": mp_req["employeeId"],
        "date": mp_req["attendanceDate"]
    })
    
    if old_attendance:
        old_attendance["_id"] = str(old_attendance["_id"])
        
    # 3. Create synthetic punch in attendance_logs
    import hashlib
    ts = datetime.fromisoformat(mp_req["requestedTime"].replace("Z", "+00:00"))
    synthetic_fp = hashlib.sha256(f"synthetic_{mp_req['employeeId']}_{ts.isoformat()}_{mp_req['_id']}".encode('utf-8')).hexdigest()

    synthetic_log = {
        "empId": mp_req["employeeId"],
        "timestamp": ts,
        "source": "miss_punch_approval",
        "workflowId": workflow.id,
        "createdAt": datetime.now(timezone.utc),
        "fingerprint": synthetic_fp
    }
    await db.attendance_logs.insert_one(synthetic_log)
    
    # 4. Trigger recalculation
    from .attendance_service import build_daily_summaries, upsert_daily_attendance
    
    # Fetch all logs for that day for the employee
    start_of_day = datetime.fromisoformat(mp_req["attendanceDate"]).replace(hour=0, minute=0, second=0)
    end_of_day = start_of_day.replace(hour=23, minute=59, second=59)
    
    cursor = db.attendance_logs.find({
        "empId": mp_req["employeeId"],
        "timestamp": {"$gte": start_of_day, "$lte": end_of_day}
    })
    day_logs = await cursor.to_list(length=None)
    
    if day_logs:
        # Re-run the processor
        summaries = await build_daily_summaries(db, day_logs)
        if summaries:
            await upsert_daily_attendance(db, summaries)
            
            # 5. Fetch new attendance for audit log
            new_attendance = await db.attendance.find_one({
                "empId": mp_req["employeeId"],
                "date": mp_req["attendanceDate"]
            })
            if new_attendance:
                new_attendance["_id"] = str(new_attendance["_id"])
                
            # 6. Write Audit Log
            audit = {
                "empId": mp_req["employeeId"],
                "date": mp_req["attendanceDate"],
                "oldAttendance": old_attendance,
                "newAttendance": new_attendance,
                "approverId": workflow.actedBy if hasattr(workflow, 'actedBy') else workflow.currentApproverId,
                "reason": mp_req.get("reason", "Miss Punch Approval"),
                "timestamp": datetime.now(timezone.utc)
            }
            await db.attendance_audit_logs.insert_one(audit)
