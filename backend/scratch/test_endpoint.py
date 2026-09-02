import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import get_settings
import httpx
from app.core.security import create_access_token

async def main():
    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongo_uri)
    db = client[settings.mongo_db_name]
    
    # Check for a user with roleId = super_admin
    user = await db.users.find_one({"roleId": "super_admin"})
    if not user:
        print("Super admin user not found.")
        return
        
    empId = str(user.get("empId"))
    print(f"Testing with super_admin user: {empId}")
    
    token = create_access_token(
        {
            "sub": empId,
            "empId": empId,
            "employeeId": user.get("employeeId"),
            "employeeCode": user.get("employeeCode", empId),
            "role": user.get("role", "super_admin"),
            "roleId": "super_admin",
            "companyId": user.get("companyId"),
            "branchId": user.get("branchId"),
            "firstLogin": user.get("firstLogin", False),
        }
    )
    
    headers = {"Authorization": f"Bearer {token}"}
    
    url = "http://127.0.0.1:8000/api/v1/attendance/me/?fromDate=2026-08-01&toDate=2026-08-31"
    print(f"Fetching {url}")
    
    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Raw Response: {response.text}")

if __name__ == "__main__":
    asyncio.run(main())
