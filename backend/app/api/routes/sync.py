from __future__ import annotations

from fastapi import APIRouter, Depends

from ...db.mongo import get_database
from ...dependencies import require_roles
from ...models import SyncRequest
from ...services.sync_service import sync_essl_logs
from ...dependencies import get_current_user
from ...scheduler.scheduler import schedule_user_sync_now
from datetime import datetime


router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("/essl")
async def sync_essl(payload: SyncRequest | None = None, _admin=Depends(require_roles("Admin"))):
    db = get_database()
    request = payload or SyncRequest()
    return await sync_essl_logs(db, request.fromDate, request.toDate)


@router.post("/my-data")
async def sync_my_data(current_user=Depends(get_current_user)):
    db = get_database()
    emp_id = current_user["empId"]

    from ...services.sync_service import DictAttrWrapper
    raw_user = await db.users.find_one({"empId": emp_id})
    user = DictAttrWrapper(raw_user)

    print("🔄 Sync triggered for:", user.empId)

    from datetime import datetime, timedelta
    if not user.lastSyncAt:
        from_date = datetime.utcnow() - timedelta(days=90)
    else:
        from_date = user.lastSyncAt - timedelta(minutes=5)

    # schedule background task
    schedule_user_sync_now(emp_id, from_date=from_date, to_date=None)
    await db.users.update_one({"empId": emp_id}, {"$set": {"dataSyncStatus": "processing"}})
    return {"status": "scheduled", "empId": emp_id}

