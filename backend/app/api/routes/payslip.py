from __future__ import annotations

from fastapi import APIRouter, Depends

from app.db.mongo import get_database
from app.dependencies import get_current_user


router = APIRouter(prefix="/payslip", tags=["payslip"])


@router.get("/me/")
async def my_payslips(current_user=Depends(get_current_user)):
    db = get_database()
    payslips = await db.payslips.find({"empId": current_user["empId"]}, {"_id": 0}).sort("periodEnd", -1).to_list(length=None)
    return {"payslips": payslips}
