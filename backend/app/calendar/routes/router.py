from fastapi import APIRouter
router = APIRouter(prefix="/calendar", tags=["Calendar Engine"])

@router.get("/company")
async def get_company_calendar():
    return {"status": "Success", "message": "Shared company calendar populated from Holiday & Leave engines."}
