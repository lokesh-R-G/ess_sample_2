from fastapi import APIRouter, Depends, HTTPException
from app.db.mongo import get_database
from app.dependencies import get_current_user
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.payroll.services.payslip_service import PayslipService

router = APIRouter()

@router.get("/me/{year}/{month}")
async def get_my_payslip(year: int, month: int, db: AsyncIOMotorDatabase = Depends(get_database), current_user: dict = Depends(get_current_user)):
    service = PayslipService(db)
    payslip = await service.get_employee_payslip(current_user["employeeId"], year, month)
    
    if not payslip:
        # According to constraints, do NOT calculate. Return empty/not processed.
        return {"status": "NOT_PROCESSED", "message": "Payroll has not yet been processed for this month."}
        
    if payslip.status != "PUBLISHED":
        return {"status": "UNPUBLISHED", "message": "Payslip is not yet published."}
        
    return payslip.model_dump(by_alias=True)

@router.post("/publish/{cycle_id}")
async def publish_payslips_for_cycle(cycle_id: str, db: AsyncIOMotorDatabase = Depends(get_database), current_user: dict = Depends(get_current_user)):
    service = PayslipService(db)
    try:
        count = await service.publish_payslips(cycle_id)
        return {"publishedCount": count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
