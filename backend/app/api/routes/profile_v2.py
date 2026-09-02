from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime

from app.db.mongo import get_database
from app.dependencies import get_current_user
from app.core.serialize import serialize_mongo_doc

router = APIRouter(prefix="/me/profile", tags=["profile_v2"])


class EmployeeSelfProfileUpdate(BaseModel):
    mobilePhone: Optional[str] = None
    personalEmail: Optional[str] = None
    currentAddressLine1: Optional[str] = None
    currentCity: Optional[str] = None
    currentState: Optional[str] = None
    currentCountry: Optional[str] = None
    currentPincode: Optional[str] = None
    
    model_config = {"extra": "forbid"}  # Enforce rejection of unauthorized fields


@router.get("/")
async def get_my_profile(current_user=Depends(get_current_user)):
    db = get_database()
    emp_uuid = current_user.get("employeeId")
    if not emp_uuid:
        # Fallback to resolving via user table if employeeId isn't natively on JWT (which it should be in V2)
        emp_code = current_user.get("empId")
        if emp_code:
            emp = await db.employees.find_one({"employeeCode": emp_code})
            if emp:
                emp_uuid = emp.get("employeeId")
                
    if not emp_uuid:
        raise HTTPException(status_code=400, detail="Could not resolve employee UUID")

    # Fetch all domain models
    employee = await db.employees.find_one({"employeeId": emp_uuid})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
        
    personal = await db.employee_personals.find_one({"employeeId": emp_uuid}) or {}
    contact = await db.employee_contacts.find_one({"employeeId": emp_uuid}) or {}
    address = await db.employee_addresses.find_one({"employeeId": emp_uuid}) or {}
    bank = await db.employee_banks.find_one({"employeeId": emp_uuid}) or {}
    
    # Fetch active employment history
    emp_history = await db.employee_employment_histories.find_one(
        {"employeeId": emp_uuid, "status": "Active"},
        sort=[("effectiveFrom", -1)]
    ) or {}
    
    # Resolve human-readable names for employment history
    org_name = ""
    branch_name = ""
    dept_name = ""
    desig_name = ""
    manager_name = ""

    from bson import ObjectId
    
    # Helper to parse object ID or string
    def parse_id(id_val):
        if not id_val: return None
        try:
            return ObjectId(id_val)
        except:
            return id_val

    if emp_history.get("companyId"):
        org = await db.organizations.find_one({"_id": parse_id(emp_history["companyId"])})
        if org: org_name = org.get("name", "")
        
    if emp_history.get("branchId"):
        branch = await db.branches.find_one({"_id": parse_id(emp_history["branchId"])})
        if branch: branch_name = branch.get("name", "")
        
    if emp_history.get("departmentId"):
        dept = await db.departments.find_one({"_id": parse_id(emp_history["departmentId"])})
        if dept: dept_name = dept.get("name", "")
        
    if emp_history.get("designationId"):
        desig = await db.designations.find_one({"_id": parse_id(emp_history["designationId"])})
        if desig: desig_name = desig.get("name", "")
        
    if emp_history.get("reportingManagerEmployeeId"):
        manager_code = emp_history["reportingManagerEmployeeId"]
        manager = await db.employees.find_one({"employeeId": manager_code})
        if not manager:
             manager = await db.employees.find_one({"employeeCode": manager_code})
        if manager:
            manager_personal = await db.employee_personals.find_one({"employeeId": manager.get("employeeId")})
            if manager_personal:
                first = manager_personal.get("firstName", "")
                last = manager_personal.get("lastName", "")
                manager_name = f"{first} {last}".strip()
            else:
                manager_name = manager.get("employeeCode", manager_code)

    response = {
        "personal": {
            "employeeId": employee.get("employeeId"),
            "employeeCode": employee.get("employeeCode"),
            "firstName": personal.get("firstName"),
            "lastName": personal.get("lastName"),
            "dob": personal.get("dob"),
            "gender": personal.get("gender"),
            "bloodGroup": personal.get("bloodGroup"),
            "maritalStatus": personal.get("maritalStatus")
        },
        "contact": {
            "mobilePhone": contact.get("mobilePhone"),
            "personalEmail": contact.get("personalEmail"),
            "workEmail": contact.get("workEmail")
        },
        "address": {
            "currentAddressLine1": address.get("currentAddressLine1"),
            "currentCity": address.get("currentCity"),
            "currentState": address.get("currentState"),
            "currentCountry": address.get("currentCountry"),
            "currentPincode": address.get("currentPincode")
        },
        "emergencyContact": {
            "name": contact.get("emergencyContactName"),
            "relationship": contact.get("emergencyContactRelation"),
            "phone": contact.get("emergencyContactNumber")
        },
        "bank": {
            "bankName": bank.get("bankName"),
            "accountNumber": bank.get("accountNumber"),
            "ifscCode": bank.get("ifscCode"),
            "accountType": bank.get("accountType")
        },
        "employment": {
            "dateOfJoining": emp_history.get("dateOfJoining"),
            "organization": org_name,
            "branch": branch_name,
            "department": dept_name,
            "designation": desig_name,
            "reportingManager": manager_name,
            "employmentType": emp_history.get("employmentType"),
            "status": employee.get("status")
        },
        "permissions": {
            "canEditMobile": True,
            "canEditAddress": True,
            "canEditBank": False,
            "canEditEmergencyContact": False,
            "canEditEmployment": False
        }
    }
    
    return serialize_mongo_doc(response)


@router.patch("/")
async def update_my_profile(payload: EmployeeSelfProfileUpdate, current_user=Depends(get_current_user)):
    db = get_database()
    emp_uuid = current_user.get("employeeId")
    if not emp_uuid:
        emp_code = current_user.get("empId")
        if emp_code:
            emp = await db.employees.find_one({"employeeCode": emp_code})
            if emp: emp_uuid = emp.get("employeeId")
            
    if not emp_uuid:
        raise HTTPException(status_code=400, detail="Could not resolve employee UUID")

    data = payload.model_dump(exclude_unset=True)
    if not data:
        return await get_my_profile(current_user)
        
    contact_updates = {}
    address_updates = {}
    
    if "mobilePhone" in data:
        contact_updates["mobilePhone"] = data["mobilePhone"]
    if "personalEmail" in data:
        contact_updates["personalEmail"] = data["personalEmail"]
        
    for field in ["currentAddressLine1", "currentCity", "currentState", "currentCountry", "currentPincode"]:
        if field in data:
            address_updates[field] = data[field]
            
    if contact_updates:
        # Check if exists
        existing_contact = await db.employee_contacts.find_one({"employeeId": emp_uuid})
        if existing_contact:
            await db.employee_contacts.update_one(
                {"employeeId": emp_uuid},
                {"$set": contact_updates}
            )
        else:
            contact_updates["employeeId"] = emp_uuid
            await db.employee_contacts.insert_one(contact_updates)
            
    if address_updates:
        existing_addr = await db.employee_addresses.find_one({"employeeId": emp_uuid})
        if existing_addr:
            await db.employee_addresses.update_one(
                {"employeeId": emp_uuid},
                {"$set": address_updates}
            )
        else:
            address_updates["employeeId"] = emp_uuid
            await db.employee_addresses.insert_one(address_updates)

    return await get_my_profile(current_user)
