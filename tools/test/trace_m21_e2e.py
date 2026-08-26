import asyncio
import sys
from datetime import datetime
from pprint import pprint
from app.db.mongo import get_database
from app.approval.schemas.approval import ApprovalSubmit, ApprovalAction
from app.approval.services.approval_service import ApprovalService
from app.attendance_v2.services.dirty_queue_service import DirtyQueueService
from app.attendance_v2.services.attendance_processor import AttendanceProcessor

async def trace_m21():
    db = get_database()
    
    # 1. Find a test employee
    employee = await db.employees.find_one({"employeeCode": "5188"})
    if not employee:
        print("Employee 5188 not found")
        return
    emp_uuid = employee["employeeId"]
    emp_code = employee["employeeCode"]
    
    print(f"\n--- M2.1 Trace for Employee {emp_code} ({emp_uuid}) ---")
    
    approval_svc = ApprovalService(db)
    dirty_queue_svc = DirtyQueueService(db)
    attendance_processor = AttendanceProcessor(db)

    # Clean up previous traces for 5188 today
    today_str = "2026-08-10"
    await db.approvals.delete_many({"employeeId": emp_uuid})
    await db.permission_ledgers.delete_many({"employeeId": emp_uuid, "month": "2026-08"})
    await db.attendance_snapshots.delete_many({"employeeCode": emp_code, "date": today_str})
    await db.attendance_dirty_queue.delete_many({"employeeCode": {"$exists": False}})

    # ==========================================
    # SCENARIO 1: Permission Request & Approval
    # ==========================================
    print(f"\n[1] Submitting Permission Request for {today_str} (10:00 - 11:30)")
    
    perm_submit = ApprovalSubmit(
        employeeId=emp_uuid,
        approvalType="Permission",
        requestData={
            "date": today_str,
            "fromTime": "10:00",
            "toTime": "11:30"
        },
        remarks="Trace Test Permission"
    )
    perm_req = await approval_svc.submit_request(perm_submit)
    perm_id = str(perm_req.id)
    print(f"    -> Created Approval ID: {perm_id}")
    
    print("\n[2] Approving Permission Request")
    action = ApprovalAction(action="APPROVE", actedBy="MANAGER", remarks="Approved")
    await approval_svc.execute_action(perm_id, action)
    print("    -> Approval execution successful. Dirty Queue should have been populated.")
    
    # Process Dirty Queue
    print("\n[3] Triggering Attendance Processor")
    processed_count = await attendance_processor.process_batch()
    print(f"    -> Processed {processed_count} dirty entries.")
    
    # Check Snapshot
    print("\n[4] Inspecting Attendance Snapshot")
    snapshot = await db.attendance_snapshots.find_one({"employeeCode": emp_code, "date": today_str})
    if snapshot:
        appr_snap = snapshot.get("approvalSnapshot", {})
        print("    -> approvalSnapshot details:")
        print(f"       requestedPermissionMinutes: {appr_snap.get('requestedPermissionMinutes')}")
        print(f"       allowedPermissionMinutes: {appr_snap.get('allowedPermissionMinutes')}")
        print(f"       excessPermissionMinutes: {appr_snap.get('excessPermissionMinutes')}")
        print(f"       permissionLopGenerated: {appr_snap.get('permissionLopGenerated')}")
    else:
        print("    -> Snapshot not found!")
        
    # Check Ledger
    print("\n[5] Inspecting Permission Ledger")
    ledger = await db.permission_ledgers.find_one({"employeeId": emp_uuid, "month": "2026-08"})
    if ledger:
        print(f"    -> freeAllowanceMinutes: {ledger.get('freeAllowanceMinutes')}")
        print(f"    -> consumedMinutes: {ledger.get('consumedMinutes')}")
        print(f"    -> currentExcessMinutes: {ledger.get('currentExcessMinutes')}")
        print(f"    -> previousCarriedMinutes: {ledger.get('previousCarriedMinutes')}")
        print(f"    -> accumulatedExcessMinutes: {ledger.get('accumulatedExcessMinutes')}")
        print(f"    -> lopGenerated: {ledger.get('lopGenerated')}")
    else:
        print("    -> Ledger not found!")

    # ==========================================
    # SCENARIO 2: OD Request & Approval
    # ==========================================
    print(f"\n[6] Submitting OD Request for {today_str} (13:00 - 15:00)")
    od_submit = ApprovalSubmit(
        employeeId=emp_uuid,
        approvalType="On Duty",
        requestData={
            "fromDate": today_str,
            "toDate": today_str,
            "fromTime": "13:00",
            "toTime": "15:00",
            "location": "Client Site"
        },
        remarks="Trace Test OD"
    )
    od_req = await approval_svc.submit_request(od_submit)
    od_id = str(od_req.id)
    print(f"    -> Created Approval ID: {od_id}")
    
    print("\n[7] Approving OD Request")
    await approval_svc.execute_action(od_id, action)
    print("    -> Approval execution successful.")
    
    print("\n[8] Triggering Attendance Processor")
    processed_count = await attendance_processor.process_batch()
    print(f"    -> Processed {processed_count} dirty entries.")
    
    print("\n[9] Inspecting Attendance Snapshot for OD")
    snapshot = await db.attendance_snapshots.find_one({"employeeCode": emp_code, "date": today_str})
    if snapshot:
        appr_snap = snapshot.get("approvalSnapshot", {})
        print("    -> approvalSnapshot details:")
        print(f"       requestedOdMinutes: {appr_snap.get('requestedOdMinutes')}")
    else:
        print("    -> Snapshot not found!")
        
    print("\n--- M2.1 Trace Complete ---")

if __name__ == "__main__":
    asyncio.run(trace_m21())
