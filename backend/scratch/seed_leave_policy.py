import asyncio
from datetime import datetime, timezone
import os

os.environ["MONGODB_URI"] = "mongodb+srv://lokeshca2004_db_user:E25tA03K1Y8Hn776@cluster0.dbw3o.mongodb.net/?retryWrites=true&w=majority"
os.environ["MONGODB_DB_NAME"] = "essl_production"

from app.db.mongo import connect_to_mongo, get_database, close_mongo_connection

async def seed_policy():
    try:
        await connect_to_mongo()
    except Exception:
        pass
        
    db = get_database()
    now = datetime.now(timezone.utc)
    doc = {
        'policyCode': 'DEFAULT_LEAVE_POLICY',
        'name': 'Default Leave Policy',
        'description': 'Standard 12 SL, 12 CL, 12 EL configuration',
        'effectiveFrom': now,
        'effectiveTo': None,
        'status': 'Active',
        'version': 1,
        'isCurrent': True,
        'createdAt': now,
        'updatedAt': now,
        'createdBy': 'SYSTEM',
        'leaveTypes': [
            {
                'code': 'SL',
                'name': 'Sick Leave',
                'enabled': True,
                'annualEntitlement': 12.0,
                'carryForwardEnabled': False,
                'carryForwardLimit': 0.0,
                'carryForwardType': 'FLAT',
                'expiryEnabled': True,
                'expiryRule': 'YEAR_END',
                'joiningYearProrationEnabled': True,
                'prorationRule': 'MONTHLY_REDUCTION',
                'anniversaryEligibilityEnabled': True,
                'zeroBalanceApprovalAllowed': True,
                'lopEnabled': True
            },
            {
                'code': 'CL',
                'name': 'Casual Leave',
                'enabled': True,
                'annualEntitlement': 12.0,
                'carryForwardEnabled': False,
                'carryForwardLimit': 0.0,
                'carryForwardType': 'FLAT',
                'expiryEnabled': True,
                'expiryRule': 'YEAR_END',
                'joiningYearProrationEnabled': True,
                'prorationRule': 'MONTHLY_REDUCTION',
                'anniversaryEligibilityEnabled': True,
                'zeroBalanceApprovalAllowed': True,
                'lopEnabled': True
            },
            {
                'code': 'EL',
                'name': 'Earned Leave',
                'enabled': True,
                'annualEntitlement': 12.0,
                'carryForwardEnabled': True,
                'carryForwardLimit': 0.0, # 0 = unlimited
                'carryForwardType': 'FLAT',
                'expiryEnabled': False,
                'expiryRule': 'NONE',
                'joiningYearProrationEnabled': True,
                'prorationRule': 'MONTHLY_REDUCTION',
                'anniversaryEligibilityEnabled': True,
                'zeroBalanceApprovalAllowed': True,
                'lopEnabled': True
            }
        ]
    }
    
    await db.leave_policies.delete_many({'policyCode': 'DEFAULT_LEAVE_POLICY'})
    await db.leave_policies.insert_one(doc)
    print('Seeded Leave Policy')
    
if __name__ == "__main__":
    asyncio.run(seed_policy())
