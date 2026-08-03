from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.mongo import get_database
from app.dependencies import get_current_user
from app.payroll.services.salary_assignment_service import SalaryAssignmentService

router = APIRouter(prefix="/assign", tags=["Payroll Salary Assignment"])

class SalaryAssignmentRequest(BaseModel):
    employeeId: str
    salaryStructureId: str
    basicSalary: float
    pfOption: str = "Default"
    esiOption: str = "Default"
    ptState: str = "None"

@router.post("/")
async def assign_salary(
    req: SalaryAssignmentRequest, 
    db: AsyncIOMotorDatabase = Depends(get_database),
    user: dict = Depends(get_current_user)
):
    service = SalaryAssignmentService(db)
    return await service.assign_salary(req.model_dump(), user.get("empId"))
