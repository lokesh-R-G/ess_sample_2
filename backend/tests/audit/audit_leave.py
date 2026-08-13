import asyncio
from app.db.mongo import get_database

async def audit_leave():
    db = get_database()
    collections = await db.list_collection_names()
    leave_colls = [c for c in collections if 'leave' in c.lower()]
    print("Leave Collections:", leave_colls)
    
    for coll in leave_colls:
        count = await db[coll].count_documents({})
        print(f"{coll} count: {count}")
        if count > 0:
            doc = await db[coll].find_one()
            print(f"Sample {coll}:", doc)

    # Check for approvals of type Leave
    leave_approvals = await db.approvals.count_documents({"approvalType": "Leave"})
    print("Approvals with type 'Leave':", leave_approvals)
    if leave_approvals > 0:
        app = await db.approvals.find_one({"approvalType": "Leave"})
        print("Sample Leave Approval:", app)

if __name__ == "__main__":
    asyncio.run(audit_leave())
