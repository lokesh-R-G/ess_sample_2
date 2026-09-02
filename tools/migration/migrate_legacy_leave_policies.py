import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

async def run():
    load_dotenv('../../backend/.env')
    db_client = AsyncIOMotorClient(os.getenv('MONGODB_URI'))
    db = db_client[os.getenv('MONGODB_DB_NAME')]
    
    docs = await db.leave_policies.find({}).to_list(None)
    migrated_count = 0
    
    for doc in docs:
        needs_update = False
        
        # 1. Check top-level name
        if not doc.get("name"):
            policy_code = doc.get("policyCode", "UNKNOWN")
            doc["name"] = policy_code.replace("-", " ").replace("_", " ").title()
            needs_update = True
            
        # 2. Check leaveTypes
        leave_types = doc.get("leaveTypes", [])
        for lt in leave_types:
            code = lt.get("code", "")
            
            if "name" not in lt:
                # Infer name from code
                lt["name"] = f"{code.upper()} Leave" if code else "Leave"
                if code.upper() == "SL": lt["name"] = "Sick Leave"
                if code.upper() == "CL": lt["name"] = "Casual Leave"
                if code.upper() == "EL": lt["name"] = "Earned Leave"
                if code.upper() == "PL": lt["name"] = "Privilege Leave"
                needs_update = True
                
            if "annualEntitlement" not in lt:
                lt["annualEntitlement"] = 12.0
                needs_update = True
                
            if "carryForwardEnabled" not in lt:
                lt["carryForwardEnabled"] = False
                lt["carryForwardLimit"] = 0.0
                lt["carryForwardType"] = "FLAT"
                needs_update = True
                
            if "expiryEnabled" not in lt:
                lt["expiryEnabled"] = True
                lt["expiryRule"] = "YEAR_END"
                needs_update = True
                
            if "joiningYearProrationEnabled" not in lt:
                lt["joiningYearProrationEnabled"] = True
                lt["prorationRule"] = "MONTHLY_REDUCTION"
                needs_update = True
                
            if "anniversaryEligibilityEnabled" not in lt:
                lt["anniversaryEligibilityEnabled"] = True
                needs_update = True
                
            if "zeroBalanceApprovalAllowed" not in lt:
                lt["zeroBalanceApprovalAllowed"] = True
                needs_update = True
                
            if "lopEnabled" not in lt:
                lt["lopEnabled"] = True
                needs_update = True
                
        if needs_update:
            print(f"Migrating policy {doc.get('policyCode')} (v{doc.get('version')})")
            await db.leave_policies.replace_one({"_id": doc["_id"]}, doc)
            migrated_count += 1
            
    print(f"Migration complete. Repaired {migrated_count} legacy documents.")
    db_client.close()

if __name__ == "__main__":
    asyncio.run(run())
