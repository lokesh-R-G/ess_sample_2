from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from ....db.mongo import get_database
from ....dependencies import get_current_user
from ..controllers.employee_reporting_controller import EmployeeReportingController
from ..schemas.employee_reporting import EmployeeReportingCreate, EmployeeReportingUpdate, EmployeeReportingResponse

router = APIRouter(prefix="/employeeReportings", tags=["EmployeeReporting"])

def get_controller(db = Depends(get_database)) -> EmployeeReportingController:
    return EmployeeReportingController(db)

@router.post("/", response_model=EmployeeReportingResponse)
async def create(data: EmployeeReportingCreate, controller: EmployeeReportingController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.create(data, user.get("empId"))

@router.get("/")
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    employeeId: Optional[str] = None,
    status: Optional[str] = None,
    controller: EmployeeReportingController = Depends(get_controller),
    user: dict = Depends(get_current_user)
):
    query = {}
    if employeeId: query["employeeId"] = employeeId
    if status: query["status"] = status
    return await controller.get_all(query, skip, limit, search)

@router.get("/{id}", response_model=EmployeeReportingResponse)
async def get_by_id(id: str, controller: EmployeeReportingController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.get_by_id(id)

@router.put("/{id}", response_model=EmployeeReportingResponse)
async def update(id: str, data: EmployeeReportingUpdate, controller: EmployeeReportingController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.update(id, data, user.get("empId"))

@router.delete("/{id}")
async def delete(id: str, controller: EmployeeReportingController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.delete(id, user.get("empId"))
