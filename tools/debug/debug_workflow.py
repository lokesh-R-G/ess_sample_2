import asyncio
from app.db.mongo import get_database
from app.services.workflow_service import get_pending_workflows

async def run():
    db = get_database()
    try:
        res = await get_pending_workflows(db, "0001")
        print("Success:", res[:2])
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run())
