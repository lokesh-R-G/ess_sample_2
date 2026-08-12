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
    },
    {
        "jobKey": "DAILY_LEAVE_ELIGIBILITY",
        "enabled": True,
        "frequencyMinutes": 1440,  # 1 day
        "lookbackDays": 0,
        "timezone": "Asia/Kolkata"
    },
    {
        "jobKey": "ANNUAL_LEAVE_RESET",
        "enabled": True,
        "frequencyMinutes": 1440,  # 1 day (but logic checks if it's Jan 1)
        "lookbackDays": 0,
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

async def run_daily_leave_eligibility_check():
    import logging
    logger = logging.getLogger("scheduler")
    logger.info("Running DAILY_LEAVE_ELIGIBILITY")
    db = get_database()
    
    # Run daily to check 1 year DOJ
    today = datetime.now(timezone.utc).date()
    cursor = db.employees.find({"dateOfJoining": {"$exists": True}})
    
    async for emp in cursor:
        doj_str = emp.get("dateOfJoining")
        if not doj_str: continue
        try:
            doj = datetime.strptime(doj_str, "%Y-%m-%d").date()
        except Exception:
            continue
            
        # Check if today is exactly their 1st anniversary
        if today.year - doj.year == 1 and today.month == doj.month and today.day == doj.day:
            from app.attendance_v2.services.leave_ledger_service import LeaveLedgerService
            ledger_svc = LeaveLedgerService(db)
            emp_id = emp.get("employeeId")
            emp_code = emp.get("employeeCode", "UNKNOWN")
            
            for lt in ["SL", "CL", "EL"]:
                await ledger_svc.get_or_create_ledger(emp_id, emp_code, today.year, lt)
                
async def run_annual_leave_reset():
    import logging
    logger = logging.getLogger("scheduler")
    logger.info("Running ANNUAL_LEAVE_RESET")
    db = get_database()
    
    today = datetime.now(timezone.utc).date()
    if today.month != 1 or today.day != 1:
        return
        
    prev_year = today.year - 1
    cursor = db.leave_ledgers.find({"calendarYear": prev_year})
    
    now = datetime.now(timezone.utc)
    async for ledger in cursor:
        emp_id = ledger.get("employeeId")
        emp_code = ledger.get("employeeCode")
        lt = ledger.get("leaveType")
        prev_balance = ledger.get("availableBalance", 0.0)
        
        carried = 0.0
        expired = 0.0
        if lt == "EL":
            carried = prev_balance
        else:
            expired = prev_balance
            
        await db.leave_ledgers.update_one(
            {"_id": ledger["_id"]},
            {"$set": {"expired": expired, "updatedAt": now}}
        )
        
        doj_str = None
        emp = await db.employees.find_one({"employeeId": emp_id})
        if emp: doj_str = emp.get("dateOfJoining")
        
        credited = 12.0
        if doj_str:
            doj = datetime.strptime(doj_str, "%Y-%m-%d").date()
            if today.year == doj.year + 1:
                credited = max(0.0, 12.0 - doj.month)
            elif today.year <= doj.year:
                credited = 0.0
                
        new_ledger = {
            "employeeId": emp_id,
            "employeeCode": emp_code,
            "calendarYear": today.year,
            "leaveType": lt,
            "openingBalance": credited + carried,
            "annualEntitlement": 12.0,
            "anniversaryEntitlement": 0.0,
            "carriedForward": carried,
            "credited": credited,
            "consumed": 0.0,
            "availableBalance": credited + carried,
            "expired": 0.0,
            "lopDays": 0.0,
            "version": 1,
            "createdAt": now,
            "updatedAt": now,
            "allocations": []
        }
        await db.leave_ledgers.insert_one(new_ledger)

JOB_MAPPING = {
    "ESSL_SHORT_SYNC": run_essl_short_sync,
    "ESSL_RECOVERY_SYNC": run_essl_recovery_sync,
    "ATTENDANCE_CALCULATION": run_attendance_calculation,
    "DAILY_LEAVE_ELIGIBILITY": run_daily_leave_eligibility_check,
    "ANNUAL_LEAVE_RESET": run_annual_leave_reset
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
