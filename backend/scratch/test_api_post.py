import httpx
import asyncio

async def test_api():
    async with httpx.AsyncClient() as client:
        # Simulate creating a policy
        payload = {
            "policyCode": "Leave_test_001",
            "name": "Test",
            "effectiveFrom": "2026-01-01T00:00:00Z",
            "leaveTypes": [
                {
                    "code": "SL",
                    "name": "Sick Leave",
                    "enabled": True,
                    "annualEntitlement": 12.0,
                    "carryForwardEnabled": False,
                    "carryForwardLimit": 0.0,
                    "carryForwardType": "FLAT",
                    "expiryEnabled": True,
                    "expiryRule": "YEAR_END",
                    "joiningYearProrationEnabled": True,
                    "prorationRule": "MONTHLY_REDUCTION",
                    "anniversaryEligibilityEnabled": True,
                    "zeroBalanceApprovalAllowed": True,
                    "lopEnabled": True
                }
            ]
        }
        
        # We need a token or we can just bypass auth for the test if it's protected?
        # Actually it's protected by get_current_user.
        # But wait, we can just login first.
        login_res = await client.post("http://localhost:8000/api/v1/auth/login", json={
            "employeeId": "EMP-001",
            "password": "password123"
        })
        token = login_res.json().get("access_token")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        res = await client.post("http://localhost:8000/api/v2/leave-policies", json=payload, headers=headers)
        print("POST Response Status:", res.status_code)
        print("POST Response Body:", res.text)

if __name__ == "__main__":
    asyncio.run(test_api())
