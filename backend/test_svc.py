import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from app.auth.forgot_password.services.forgot_password_service import ForgotPasswordService

async def run():
    load_dotenv()
    db_client = AsyncIOMotorClient(os.getenv('MONGODB_URI'))
    db = db_client[os.getenv('MONGODB_DB_NAME')]
    
    import pprint
    docs = await db.password_reset_otps.find({"employeeId": "ccb45a55-14e4-4544-96c6-75a4d131e812"}).sort("createdAt", -1).to_list(3)
    for d in docs:
        pprint.pprint({
            "id": str(d["_id"]),
            "email": d.get("email"),
            "used": d.get("used"),
            "verified": d.get("verified"),
            "attemptCount": d.get("attemptCount"),
            "createdAt": d.get("createdAt"),
            "expiresAt": d.get("expiresAt")
        })
        
    db_client.close()

if __name__ == "__main__":
    asyncio.run(run())
