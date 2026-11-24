from fastapi import APIRouter
from app.holiday_calendar.routes.holiday_calendar import router as my_holiday_router
from app.holiday_calendar.routes.special_day_routes import router as special_day_router

router = APIRouter()
router.include_router(my_holiday_router)
router.include_router(special_day_router)
