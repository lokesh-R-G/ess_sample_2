from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.db.mongo import get_database
from app.authz import authorize, AuthorizedScope
from app.employee.controllers.employee_document_controller import EmployeeDocumentController
from app.employee.schemas.employee_document import EmployeeDocumentCreate, EmployeeDocumentUpdate, EmployeeDocumentResponse

router = APIRouter(prefix="/employeeDocuments", tags=["EmployeeDocument"])

def get_controller(db = Depends(get_database)) -> EmployeeDocumentController:
    return EmployeeDocumentController(db)

@router.post("/", response_model=EmployeeDocumentResponse)
async def create(data: EmployeeDocumentCreate, controller: EmployeeDocumentController = Depends(get_controller), authz: AuthorizedScope = Depends(authorize("employee.manage"))):
    await authz.validate_resource_employee(data.employeeId)
    return await controller.create(data, authz.employee_id)

@router.get("/")
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    employeeId: Optional[str] = None,
    status: Optional[str] = None,
    controller: EmployeeDocumentController = Depends(get_controller),
    authz: AuthorizedScope = Depends(authorize("employee.read"))
):
    query = await authz.get_mongo_filter("employeeId")
    if employeeId:
        await authz.validate_resource_employee(employeeId)
        query["employeeId"] = employeeId
    if status: query["status"] = status
    return await controller.get_all(query, skip, limit, search)

@router.get("/{id}", response_model=EmployeeDocumentResponse)
async def get_by_id(id: str, controller: EmployeeDocumentController = Depends(get_controller), authz: AuthorizedScope = Depends(authorize("employee.read"))):
    doc = await controller.get_by_id(id)
    await authz.validate_resource_employee(doc.employeeId)
    return doc

@router.put("/{id}", response_model=EmployeeDocumentResponse)
async def update(id: str, data: EmployeeDocumentUpdate, controller: EmployeeDocumentController = Depends(get_controller), authz: AuthorizedScope = Depends(authorize("employee.manage"))):
    doc = await controller.get_by_id(id)
    await authz.validate_resource_employee(doc.employeeId)
    if getattr(data, "employeeId", None) and data.employeeId != doc.employeeId:
        await authz.validate_resource_employee(data.employeeId)
    return await controller.update(id, data, authz.employee_id)

@router.delete("/{id}")
async def delete(id: str, controller: EmployeeDocumentController = Depends(get_controller), authz: AuthorizedScope = Depends(authorize("employee.manage"))):
    doc = await controller.get_by_id(id)
    await authz.validate_resource_employee(doc.employeeId)
    return await controller.delete(id, authz.employee_id)
