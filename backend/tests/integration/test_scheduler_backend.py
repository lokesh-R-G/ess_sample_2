import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.mongo import get_database
from app.scheduler.routes.router import get_scheduler_config, update_scheduler_config, SchedulerConfigUpdate
from app.scheduler.scheduler import initialize_jobs, init_scheduler

async def test_scheduler_backend():
    db = get_database()
    
    print("0. Initializing jobs (seeding config)")
    init_scheduler()
    await asyncio.sleep(1) # wait for job to run
    
    print("1. Testing GET /api/v2/scheduler/config equivalent")
    configs = await get_scheduler_config(db=db)
    print("Configs fetched:", len(configs))
    for c in configs:
        print(f" - {c['jobKey']}: enabled={c['enabled']}, freq={c['frequencyMinutes']}")
        
    print("\n2. Testing PUT /api/v2/scheduler/config/ESSL_SHORT_SYNC equivalent")
    update_payload = SchedulerConfigUpdate(enabled=True, frequencyMinutes=30, lookbackDays=2)
    # mock current_user
    current_user = {"role": "Admin", "empId": "SYSTEM"}
    
    updated = await update_scheduler_config(
        job_key="ESSL_SHORT_SYNC",
        payload=update_payload,
        db=db,
        current_user=current_user
    )
    print("Updated config:")
    print(updated)

if __name__ == "__main__":
    asyncio.run(test_scheduler_backend())
