import asyncio
import httpx
from datetime import timedelta
from app.db.mongo import get_database
from app.core.security import create_access_token

async def test_endpoint():
    db = get_database()
    # Find an admin
    admin = await db.users.find_one({"role": "Admin"})
    if not admin:
        print("No admin found")
        return

    # Create token
    access_token_expires = timedelta(minutes=15)
    token = create_access_token(
        payload={"sub": admin["empId"]},
        expires_delta=access_token_expires
    )
    
    print(f"Testing with Admin empId: {admin['empId']}")
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        resp = await client.get("http://localhost:8000/api/v1/workflows/pending/", headers=headers)
        
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            print(f"Response (first 2): {resp.json()[:2]}")
        else:
            print(f"Error: {resp.text}")

if __name__ == "__main__":
    asyncio.run(test_endpoint())
