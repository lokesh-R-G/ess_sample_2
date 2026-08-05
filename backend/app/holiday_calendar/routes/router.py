from fastapi import APIRouter
from app.holiday_calendar.routes.holiday_calendar import router as my_holiday_router

router = APIRouter()
router.include_router(my_holiday_router)
