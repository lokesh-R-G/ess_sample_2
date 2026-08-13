import asyncio
from httpx import AsyncClient

async def run_tests():
    async with AsyncClient(base_url="http://localhost:8000", timeout=30.0) as client:
        # We need an admin login, maybe 'admin' / 'admin'?
        login_res = await client.post("/api/v1/auth/login/", json={"empId": "5188", "password": "password123"})
        if login_res.status_code != 200:
            print(f"Login failed: {login_res.status_code} - {login_res.text}")
            
            # Let's try 202201
            login_res = await client.post("/api/v1/auth/login/", json={"empId": "202201", "password": "password123"})
            if login_res.status_code != 200:
                print(f"Login failed: {login_res.status_code} - {login_res.text}")
                return
            
        token = login_res.json()["accessToken"]
        headers = {"Authorization": f"Bearer {token}"}
        
        print("1. Testing GET /api/v2/scheduler/config")
        get_res = await client.get("/api/v2/scheduler/config", headers=headers)
        print(f"Status: {get_res.status_code}")
        print(f"Response: {get_res.json()}")
        
        print("\n2. Testing PUT /api/v2/scheduler/config/ESSL_SHORT_SYNC")
        put_res = await client.put(
            "/api/v2/scheduler/config/ESSL_SHORT_SYNC", 
            json={"enabled": True, "frequencyMinutes": 45, "lookbackDays": 2},
            headers=headers
        )
        print(f"Status: {put_res.status_code}")
        print(f"Response: {put_res.json()}")

if __name__ == "__main__":
    asyncio.run(run_tests())
