import asyncio
import requests
from app.db.mongo import get_database
from app.core.security import create_access_token

def run_test():
    emp_id = "9dcf3954-27e1-439d-9832-47af55e6c7b1"  # Employee 202201
    mgr_id = "ccb45a55-14e4-4544-96c6-75a4d131e812"  # Manager 5188
    
    emp_token = create_access_token({"empId": "202201", "employeeId": emp_id, "role": "Employee"})
    mgr_token = create_access_token({"empId": "5188", "employeeId": mgr_id, "role": "Admin"})
    
    base_url = "http://127.0.0.1:8000/api/v2/approval"
    
    # Create request 1 (For Approve)
    res = requests.post(
        f"{base_url}/",
        json={
            "employeeId": emp_id,
            "approvalType": "Permission",
            "requestData": {"date": "2026-08-15", "fromTime": "09:00", "toTime": "10:00"}
        },
        headers={"Authorization": f"Bearer {emp_token}"}
    )
    appr_1 = res.json()["id"]
    
    # Simulate OLD frontend (causes 422)
    res_422 = requests.post(
        f"{base_url}/{appr_1}/action",
        json={"action": "APPROVE", "remarks": "No actedBy provided"},
        headers={"Authorization": f"Bearer {mgr_token}"}
    )
    print("=== OLD FRONTEND PAYLOAD (422) ===")
    print("Status:", res_422.status_code)
    print("Response:", res_422.text)
    
    # Simulate NEW frontend (APPROVE)
    res_200 = requests.post(
        f"{base_url}/{appr_1}/action",
        json={"action": "APPROVE", "remarks": "Approving with actedBy", "actedBy": mgr_id},
        headers={"Authorization": f"Bearer {mgr_token}"}
    )
    print("\n=== NEW FRONTEND PAYLOAD (APPROVE) ===")
    print("Status:", res_200.status_code)
    print("Response Status in JSON:", res_200.json().get("status"))
    
    # Create request 2 (For Reject)
    res2 = requests.post(
        f"{base_url}/",
        json={
            "employeeId": emp_id,
            "approvalType": "Permission",
            "requestData": {"date": "2026-08-16", "fromTime": "09:00", "toTime": "10:00"}
        },
        headers={"Authorization": f"Bearer {emp_token}"}
    )
    appr_2 = res2.json()["id"]
    
    # Simulate NEW frontend (REJECT)
    res_reject = requests.post(
        f"{base_url}/{appr_2}/action",
        json={"action": "REJECT", "remarks": "Rejecting with actedBy", "actedBy": mgr_id},
        headers={"Authorization": f"Bearer {mgr_token}"}
    )
    print("\n=== NEW FRONTEND PAYLOAD (REJECT) ===")
    print("Status:", res_reject.status_code)
    print("Response Status in JSON:", res_reject.json().get("status"))

    print("\n=== DB VERIFICATION ===")
    async def check_db():
        db = get_database()
        
        # Check Approval 1
        a1 = await db.approvals.find_one({"_id": appr_1} if type(appr_1) != str else {"_id": appr_1})
        if not a1:
            from bson import ObjectId
            a1 = await db.approvals.find_one({"_id": ObjectId(appr_1)})
        print(f"Approval 1 Status: {a1.get('status')}")
        
        # Check Dirty Queue for Approval 1 Date (2026-08-15)
        dq = await db.attendance_dirty_queue.find_one({"employeeId": emp_id, "fromDate": "2026-08-15", "trigger": "APPROVAL"})
        print("Dirty Queue created for Approval 1 (APPROVE):", dq is not None)
        
        # Check Approval 2
        a2 = await db.approvals.find_one({"_id": appr_2} if type(appr_2) != str else {"_id": appr_2})
        if not a2:
            from bson import ObjectId
            a2 = await db.approvals.find_one({"_id": ObjectId(appr_2)})
        print(f"Approval 2 Status: {a2.get('status')}")
        
    asyncio.run(check_db())

if __name__ == "__main__":
    run_test()
