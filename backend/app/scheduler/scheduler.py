from __future__ import annotations

import asyncio
from datetime import datetime, timezone, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.db.mongo import get_database
from app.services.sync_service import sync_essl_logs, sync_user
from app.attendance_v2.services.attendance_processor import AttendanceProcessor

scheduler: AsyncIOScheduler | None = None

DEFAULT_JOBS = [
    {
        "jobKey": "ESSL_SHORT_SYNC",
        "enabled": True,
        "frequencyMinutes": 90,
        "lookbackDays": 1,
        "timezone": "Asia/Kolkata"
    },
    {
        "jobKey": "ESSL_RECOVERY_SYNC",
        "enabled": True,
        "frequencyMinutes": 4320,  # 3 days
        "lookbackDays": 7,
        "timezone": "Asia/Kolkata"
    },
    {
        "jobKey": "ATTENDANCE_CALCULATION",
        "enabled": True,
        "frequencyMinutes": 1440,  # 1 day
        "lookbackDays": 2,
        "timezone": "Asia/Kolkata"
    }
]

async def seed_scheduler_configs(db):
    for job in DEFAULT_JOBS:
        existing = await db.scheduler_configs.find_one({"jobKey": job["jobKey"]})
        if not existing:
            job["createdAt"] = datetime.now(timezone.utc)
            job["updatedAt"] = datetime.now(timezone.utc)
            await db.scheduler_configs.insert_one(job)

async def run_essl_short_sync():
    import logging
    logger = logging.getLogger("scheduler")
    logger.info("Running ESSL_SHORT_SYNC")
    db = get_database()
    config = await db.scheduler_configs.find_one({"jobKey": "ESSL_SHORT_SYNC"})
    if not config or not config.get("enabled"):
        return
        
    lookback = config.get("lookbackDays", 1)
    # Using UTC here because sync_essl_logs expects UTC or aware
    to_date = datetime.now(timezone.utc)
    from_date = to_date - timedelta(days=lookback)
    
    try:
        await sync_essl_logs(db, from_date, to_date)
    except Exception as e:
        logger.error(f"ESSL_SHORT_SYNC failed: {e}")

async def run_essl_recovery_sync():
    import logging
    logger = logging.getLogger("scheduler")
    logger.info("Running ESSL_RECOVERY_SYNC")
    db = get_database()
    config = await db.scheduler_configs.find_one({"jobKey": "ESSL_RECOVERY_SYNC"})
    if not config or not config.get("enabled"):
        return
        
    lookback = config.get("lookbackDays", 7)
    to_date = datetime.now(timezone.utc)
    from_date = to_date - timedelta(days=lookback)
    
    try:
        await sync_essl_logs(db, from_date, to_date)
    except Exception as e:
        logger.error(f"ESSL_RECOVERY_SYNC failed: {e}")

async def run_attendance_calculation():
    import logging
    logger = logging.getLogger("scheduler")
    logger.info("Running ATTENDANCE_CALCULATION")
    db = get_database()
    config = await db.scheduler_configs.find_one({"jobKey": "ATTENDANCE_CALCULATION"})
    if not config or not config.get("enabled"):
        return
        
    lookback = config.get("lookbackDays", 2)
    to_date = datetime.now(timezone.utc).date()
    from_date = to_date - timedelta(days=lookback)
    
    processor = AttendanceProcessor(db)
    try:
        await processor.process_range(from_date=from_date, to_date=to_date, force=True)
    except Exception as e:
        logger.error(f"ATTENDANCE_CALCULATION failed: {e}")

JOB_MAPPING = {
    "ESSL_SHORT_SYNC": run_essl_short_sync,
    "ESSL_RECOVERY_SYNC": run_essl_recovery_sync,
    "ATTENDANCE_CALCULATION": run_attendance_calculation
}

async def initialize_jobs():
    db = get_database()
    await seed_scheduler_configs(db)
    
    cursor = db.scheduler_configs.find({})
    configs = await cursor.to_list(length=None)
    
    for config in configs:
        job_key = config["jobKey"]
        enabled = config.get("enabled", False)
        freq = config.get("frequencyMinutes", 60)
        
        if job_key in JOB_MAPPING:
            func = JOB_MAPPING[job_key]
            if enabled:
                # max_instances=1 prevents overlapping executions
                scheduler.add_job(func, IntervalTrigger(minutes=freq), id=job_key, max_instances=1, replace_existing=True)

def init_scheduler():
    global scheduler
    import logging
    logger = logging.getLogger("scheduler")
    logger.setLevel(logging.INFO)

    if scheduler is not None and scheduler.running:
        logger.info("Scheduler already running.")
        return scheduler

    scheduler = AsyncIOScheduler()
    
    # We must run initialize_jobs asynchronously.
    # We can schedule it to run immediately.
    scheduler.add_job(initialize_jobs, 'date', run_date=datetime.now())

    scheduler.start()
    logger.info("Scheduler started successfully.")
    return scheduler

def update_job_schedule(job_key: str, enabled: bool, frequency_minutes: int):
    global scheduler
    import logging
    logger = logging.getLogger("scheduler")
    
    if not scheduler:
        return
        
    if not enabled:
        try:
            scheduler.remove_job(job_key)
            logger.info(f"Removed job {job_key} because it was disabled")
        except Exception:
            pass
        return
        
    if job_key in JOB_MAPPING:
        func = JOB_MAPPING[job_key]
        scheduler.add_job(func, IntervalTrigger(minutes=frequency_minutes), id=job_key, max_instances=1, replace_existing=True)
        logger.info(f"Updated job {job_key} with frequency {frequency_minutes} mins")

def schedule_user_sync_now(emp_id: str, from_date=None, to_date=None):
    # schedule a fire-and-forget background sync for a single user
    loop = asyncio.get_event_loop()
    db = get_database()
    import logging
    logger = logging.getLogger("scheduler")
    logger.info("Scheduling immediate sync for empId %s", emp_id)
    loop.create_task(sync_user(db, emp_id, from_date=from_date, to_date=to_date))
