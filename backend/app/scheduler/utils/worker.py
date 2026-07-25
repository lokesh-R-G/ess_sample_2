import asyncio

class MongoSchedulerWorker:
    """
    Polls the 'scheduled_jobs' collection every N seconds to find jobs
    where nextRun <= now and status == 'Active'.
    """
    async def run_loop(self):
        while True:
            # db.scheduled_jobs.find({"nextRun": {"$lte": now}})
            await asyncio.sleep(60)
