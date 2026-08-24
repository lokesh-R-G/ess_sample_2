from __future__ import annotations

from fastapi import APIRouter, Depends

from app.db.mongo import get_database
from app.dependencies import require_permission
from app.rbac.context_providers import self_context
from app.models import SyncRequest
from app.services.sync_service import sync_essl_logs
from app.dependencies import get_current_user
from app.scheduler.scheduler import schedule_user_sync_now
from datetime import datetime


router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("/essl/")
async def sync_essl(payload: SyncRequest | None = None, _admin=Depends(require_permission("essl.sync")), db=Depends(get_database)):
    request = payload or SyncRequest()
    return await sync_essl_logs(db, request.fromDate, request.toDate)


@router.post("/my-data/", dependencies=[Depends(require_permission("attendance.sync", resource_context_provider=self_context))])
async def sync_my_data(
    current_user=Depends(get_current_user), db=Depends(get_database)):
    emp_id = current_user["empId"]

    from app.services.sync_service import DictAttrWrapper
    raw_user = await db.users.find_one({"empId": emp_id})
    user = DictAttrWrapper(raw_user)

    print("Sync triggered for:", user.empId)

    from datetime import datetime, timedelta
    if not user.lastSyncAt:
        from_date = datetime.utcnow() - timedelta(days=90)
    else:
        from_date = user.lastSyncAt - timedelta(minutes=5)

    # schedule background task
    schedule_user_sync_now(emp_id, from_date=from_date, to_date=None)
    await db.users.update_one({"empId": emp_id}, {"$set": {"dataSyncStatus": "processing"}})
    return {"status": "scheduled", "empId": emp_id}

