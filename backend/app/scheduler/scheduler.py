from __future__ import annotations

import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from ..db.mongo import get_database
from ..services.sync_service import sync_all_users_incremental, sync_user

scheduler: AsyncIOScheduler | None = None


def init_scheduler():
    global scheduler
    if scheduler is not None:
        return scheduler
    scheduler = AsyncIOScheduler()
    import logging
    logger = logging.getLogger("scheduler")

    async def job_all_users():
        db = get_database()
        logger.info("Background full sync started")
        # run the incremental sync for all users
        await sync_all_users_incremental(db)
        logger.info("Background full sync finished")

    # schedule every 6 hours
    scheduler.add_job(job_all_users, IntervalTrigger(hours=0.1), next_run_time=datetime.now())
    scheduler.start()
    return scheduler


def schedule_user_sync_now(emp_id: str, from_date=None, to_date=None):
    # schedule a fire-and-forget background sync for a single user
    loop = asyncio.get_event_loop()
    db = get_database()
    import logging
    logger = logging.getLogger("scheduler")
    logger.info("Scheduling immediate sync for empId %s", emp_id)
    loop.create_task(sync_user(db, emp_id, from_date=from_date, to_date=to_date))
