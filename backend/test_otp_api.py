import asyncio
import httpx
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

async def run():
    load_dotenv()
    db_client = AsyncIOMotorClient(os.getenv('MONGODB_URI'))
    db = db_client[os.getenv('MONGODB_DB_NAME')]
    
    # Find a user that has a contact record with personalEmail
    contact = await db.employee_contacts.find_one({"isCurrent": True, "personalEmail": {"$ne": None}})
    if not contact:
        print("No valid contact found.")
        return
        
    emp_id = contact["employeeId"]
    email = contact["personalEmail"]
    
    # Find employee code
    user = await db.users.find_one({"employeeId": emp_id})
    if not user:
        print("No user found for emp_id", emp_id)
        return
        
    employeeCode = user["empId"]
    print(f"Using employeeCode: {employeeCode}, email: {email}")
    
    client = httpx.AsyncClient(base_url="http://127.0.0.1:8000/api/v1", timeout=60.0)
    
    # 1. Trigger OTP
    print("Triggering OTP...")
    r1 = await client.post("/auth/forgot-password/", json={
        "employeeCode": employeeCode,
        "email": email
    })
    print(r1.status_code, r1.text)
    
    # Normally we need to fetch the OTP from the DB to get the actual code since we didn't get the email
    # Let's peek into DB
    import time
    time.sleep(1) # wait for async insert
    otp_doc = await db.password_reset_otps.find_one({"employeeId": emp_id}, sort=[("createdAt", -1)])
    if not otp_doc:
        print("OTP doc not found in DB!")
        return
        
    print(f"DB OTP Doc: expiresAt={otp_doc.get('expiresAt')}, used={otp_doc.get('used')}")
    
    # Wait, the DB only stores the hash, we don't know the plain text OTP!
    # Let's just use a dummy OTP so we can trigger verify and hit the logs.
    print("Verifying OTP...")
    r2 = await client.post("/auth/verify-reset-otp/", json={
        "employeeCode": employeeCode,
        "email": email,
        "otp": "123456" # Dummy
    })
    print(r2.status_code, r2.text)
    
    await client.aclose()
    db_client.close()

if __name__ == "__main__":
    asyncio.run(run())
