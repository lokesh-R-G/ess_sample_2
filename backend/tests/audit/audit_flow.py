import asyncio
from datetime import datetime, timezone
from app.db.mongo import get_database
from app.approval.schemas.approval import ApprovalSubmit, ApprovalAction
from app.approval.services.approval_service import ApprovalService

async def run_audit():
    db = get_database()
    service = ApprovalService(db)
    
    emp_id = "9dcf3954-27e1-439d-9832-47af55e6c7b1"  # Employee 202201
    mgr_id = "ccb45a55-14e4-4544-96c6-75a4d131e812"  # Manager 5188

    submit_data = ApprovalSubmit(
        employeeId=emp_id,
        approvalType="Permission",
        requestData={"date": "2026-08-11", "fromTime": "09:00", "toTime": "10:00"},
        remarks="Test permission flow for audit"
    )
    
    appr = await service.submit_request(submit_data)
    appr_id = appr.id
    
    record_before = await db.approvals.find_one({"_id": appr_id} if type(appr_id) != str else {"_id": appr_id})
    if not record_before:
        from bson import ObjectId
        record_before = await db.approvals.find_one({"_id": ObjectId(appr_id)})
        
    print("\n=== MongoDB Approval Record (BEFORE APPROVAL) ===")
    print(record_before)
    
    print("\n=== Manager assigned ===")
    print(f"Assigned Manager UUID: {record_before.get('reportingManagerEmployeeId')}")
    print(f"Expected Manager UUID: {mgr_id}")

    print("\n=== Manager Inbox ===")
    inbox = await service.get_manager_inbox(mgr_id)
    found = any(a.id == appr.id for a in inbox)
    print(f"Request '{appr.id}' found in inbox: {found}")

    action_data = ApprovalAction(action="APPROVE", remarks="Approved via audit", actedBy=mgr_id)
    res = await service.execute_action(appr.id, action_data)
    
    print("\n=== MongoDB Approval Record (AFTER APPROVAL) ===")
    record_after = await db.approvals.find_one({"_id": ObjectId(appr_id)})
    print(record_after)
    
    print("\n=== Verifying Dirty Queue & Attendance ===")
    dirty_queue_docs = await db.attendance_dirty_queue.find({"employeeId": emp_id}).sort("createdAt", -1).limit(2).to_list(None)
    for d in dirty_queue_docs:
        print(f"Dirty Queue Item: ID={d.get('dirtyId')}")
        print(f"- Status: {d.get('status')}")
        print(f"- From Date: {d.get('fromDate')}, To Date: {d.get('toDate')}")
        print(f"- Trigger: {d.get('trigger')}")
        print(f"- Processed At: {d.get('processedAt')}")

if __name__ == "__main__":
    asyncio.run(run_audit())
