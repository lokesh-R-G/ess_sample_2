import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.db.mongo import get_database
from app.core.security import create_access_token

def run_test():
    client = TestClient(app)
    
    emp_id = "9dcf3954-27e1-439d-9832-47af55e6c7b1"  # Employee 202201
    mgr_id = "ccb45a55-14e4-4544-96c6-75a4d131e812"  # Manager 5188
    
    # 1. Create a JWT for the employee to submit a request
    emp_token = create_access_token({
        "empId": "202201",
        "employeeId": emp_id,
        "role": "Employee"
    })
    
    print("=== Submitting Request as Employee ===")
    res = client.post(
        "/api/v2/approval/",
        json={
            "employeeId": emp_id,
            "approvalType": "Permission",
            "requestData": {"date": "2026-08-12", "fromTime": "09:00", "toTime": "10:00"},
            "remarks": "Test permission flow for HTTP test"
        },
        headers={"Authorization": f"Bearer {emp_token}"}
    )
    print(f"Submit Response: {res.status_code}")
    if res.status_code != 200:
        print(res.text)
        return
        
    appr_id = res.json()["id"]
    print(f"Created Approval ID: {appr_id}")
    
    # 2. Create a JWT for the manager
    mgr_token = create_access_token({
        "empId": "5188",
        "employeeId": mgr_id,
        "role": "Admin"
    })
    
    print("\n=== Fetching Inbox as Manager ===")
    inbox_res = client.get(
        "/api/v2/approval/inbox/manager/me",
        headers={"Authorization": f"Bearer {mgr_token}"}
    )
    print(f"Inbox Response: {inbox_res.status_code}")
    if inbox_res.status_code != 200:
        print(inbox_res.text)
        return
        
    inbox = inbox_res.json()
    print(f"Inbox count: {len(inbox)}")
    found = any(a["id"] == appr_id for a in inbox)
    print(f"Request present in inbox: {found}")
    
    print("\n=== Approving Request as Manager ===")
    action_res = client.post(
        f"/api/v2/approval/{appr_id}/action",
        json={
            "action": "APPROVE",
            "remarks": "Approved via HTTP test",
            "actedBy": mgr_id
        },
        headers={"Authorization": f"Bearer {mgr_token}"}
    )
    print(f"Action Response: {action_res.status_code}")
    if action_res.status_code != 200:
        print(action_res.text)
        return
        
    print("Status after action:", action_res.json()["status"])
    
    print("\n=== Checking Dirty Queue ===")
    # Just run an async function to check DB for dirty queue
    async def check_db():
        db = get_database()
        dirty_queue_docs = await db.attendance_dirty_queue.find({"employeeId": emp_id}).sort("createdAt", -1).limit(1).to_list(None)
        for d in dirty_queue_docs:
            print(f"Dirty Queue Item: ID={d.get('dirtyId')}")
            print(f"- Status: {d.get('status')}")
            print(f"- From Date: {d.get('fromDate')}, To Date: {d.get('toDate')}")
            print(f"- Trigger: {d.get('trigger')}")
            print(f"- Processed At: {d.get('processedAt')}")

    asyncio.run(check_db())
    print("\n=== Done ===")

if __name__ == "__main__":
    run_test()
