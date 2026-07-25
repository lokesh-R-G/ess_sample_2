from fastapi import APIRouter
router = APIRouter(prefix="/manualDeduction", tags=["ManualDeduction"])

@router.post("/")
async def execute_business_action():
    return {"message": "ManualDeduction processed successfully"}
