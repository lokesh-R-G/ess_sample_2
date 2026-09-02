import asyncio
import uuid
from datetime import datetime, timezone
from app.db.mongo import get_database
from app.approval.schemas.approval import ApprovalSubmit, ApprovalAction
from app.approval.services.approval_service import ApprovalService

async def run_test():
    db = get_database()
    service = ApprovalService(db)
    
    emp_id = "9dcf3954-27e1-439d-9832-47af55e6c7b1"  # Employee 202201
    mgr_id = "ccb45a55-14e4-4544-96c6-75a4d131e812"  # Manager 5188

    print("1. Submitting Permission Request for employee:", emp_id)
    submit_data = ApprovalSubmit(
        employeeId=emp_id,
        approvalType="Permission",
        requestData={
            "date": "2026-08-11",
            "fromTime": "09:00",
            "toTime": "10:00"
        },
        remarks="Test permission flow"
    )
    
    try:
        appr = await service.submit_request(submit_data)
        print(f"Created Approval ID: {appr.id}")
        print(f"Assigned Manager ID: {appr.reportingManagerEmployeeId}")
        if appr.reportingManagerEmployeeId != mgr_id:
            print("X MANAGER ID MISMATCH!")
        else:
            print("OK Manager successfully resolved!")
            
        print("\n2. Fetching Manager Inbox for:", mgr_id)
        inbox = await service.get_manager_inbox(mgr_id)
        print(f"Inbox count: {len(inbox)}")
        
        found = False
        for a in inbox:
            if a.id == appr.id:
                found = True
                break
        if found:
            print("OK Request found in Manager Inbox!")
        else:
            print("X Request NOT found in manager inbox!")
            
        print("\n3. Approving the request")
        action_data = ApprovalAction(action="APPROVE", remarks="Approved via test", actedBy=mgr_id)
        res = await service.execute_action(appr.id, action_data)
        print("Status after action:", res.status)
        if res.status == "APPROVED":
            print("OK Action successfully executed!")
            
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_test())
