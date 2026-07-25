from fastapi import APIRouter
router = APIRouter(prefix="/scheduler", tags=["Scheduler Engine"])

@router.post("/trigger")
async def trigger_job():
    return {"status": "Success", "message": "Manual trigger for testing database-driven worker loop."}
