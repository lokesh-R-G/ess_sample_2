from fastapi import APIRouter
from pydantic import BaseModel
router = APIRouter(prefix="/holiday", tags=["Holiday Calendar Engine"])

class HolidayRequest(BaseModel):
    name: str
    date: str
    type: str

@router.post("/create")
async def create_holiday(req: HolidayRequest):
    return {"status": "Success", "message": "Holiday created and ready for assignment."}

@router.post("/assign")
async def assign_holiday():
    return {"status": "Success", "message": "Holiday assigned to branches."}

@router.post("/publish")
async def publish_holiday():
    return {"status": "Success", "message": "Holiday published, triggering CalendarEngine update."}
