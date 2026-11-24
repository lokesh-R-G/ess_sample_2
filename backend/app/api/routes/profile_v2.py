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
    # Resolve canonical employee document
    employee = None
    # 1. Try by employeeId if present on current_user
    emp_uuid = current_user.get("employeeId")
    if emp_uuid:
        employee = await db.employees.find_one({"employeeId": emp_uuid})
    
    # 2. Try by employeeCode / empId if not found yet
    emp_code = current_user.get("employeeCode") or current_user.get("empId")
    if not employee and emp_code:
        employee = await db.employees.find_one({
            "$or": [{"employeeCode": emp_code}, {"empId": emp_code}, {"employeeId": emp_code}]
        })
    
    # 3. If employee found, ensure emp_uuid and emp_code are canonical
    if employee:
        emp_uuid = employee.get("employeeId") or str(employee.get("_id"))
        emp_code = employee.get("employeeCode") or emp_code
    else:
        # Fallback if employee table entry does not exist
        if not emp_uuid and emp_code:
            emp_uuid = emp_code
        if not emp_uuid:
            raise HTTPException(status_code=400, detail="Could not resolve employee UUID")
        employee = {"employeeId": emp_uuid, "employeeCode": emp_code}
        
    personal = await db.employee_personals.find_one({
        "$or": [{"employeeId": emp_uuid}, {"employeeCode": emp_code}] if emp_code else {"employeeId": emp_uuid}
    }) or {}
    contact = await db.employee_contacts.find_one({
        "$or": [{"employeeId": emp_uuid}, {"employeeCode": emp_code}] if emp_code else {"employeeId": emp_uuid}
    }) or {}
    address = await db.employee_addresses.find_one({
        "$or": [{"employeeId": emp_uuid}, {"employeeCode": emp_code}] if emp_code else {"employeeId": emp_uuid}
    }) or {}
    bank = await db.employee_bank_accounts.find_one({
        "$or": [{"employeeId": emp_uuid}, {"employeeCode": emp_code}] if emp_code else {"employeeId": emp_uuid}
    }) or {}
    
    # Fetch authoritative employment history:
    # First check current record (isCurrent: True, deletedAt: None), fallback to latest Active, then latest by effectiveFrom
    emp_history_query = {
        "$or": [{"employeeId": emp_uuid}, {"employeeCode": emp_code}] if emp_code else {"employeeId": emp_uuid},
        "deletedAt": None
    }
    
    emp_history = await db.employee_employment_histories.find_one(
        {**emp_history_query, "isCurrent": True},
        sort=[("effectiveFrom", -1), ("createdAt", -1)]
    )
    if not emp_history:
        emp_history = await db.employee_employment_histories.find_one(
            {**emp_history_query, "status": "Active"},
            sort=[("effectiveFrom", -1), ("createdAt", -1)]
        )
    if not emp_history:
        emp_history = await db.employee_employment_histories.find_one(
            emp_history_query,
            sort=[("effectiveFrom", -1), ("createdAt", -1)]
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
        if isinstance(id_val, ObjectId):
            return id_val
        try:
            return ObjectId(str(id_val))
        except Exception:
            return id_val

    # Company / Organization lookup:
    # Primary collection is 'companies'; fallback to 'organizations'
    if emp_history.get("companyId"):
        c_id = parse_id(emp_history["companyId"])
        company = await db.companies.find_one({"_id": c_id})
        if not company and isinstance(c_id, ObjectId):
            company = await db.companies.find_one({"_id": str(c_id)})
        if not company:
            company = await db.organizations.find_one({"_id": c_id})
        if not company and isinstance(c_id, ObjectId):
            company = await db.organizations.find_one({"_id": str(c_id)})
        if company:
            org_name = company.get("name") or company.get("companyName") or ""
        
    # Branch lookup:
    # Primary collection is 'branchs'; fallback to 'branches'
    if emp_history.get("branchId"):
        b_id = parse_id(emp_history["branchId"])
        branch = await db.branchs.find_one({"_id": b_id})
        if not branch and isinstance(b_id, ObjectId):
            branch = await db.branchs.find_one({"_id": str(b_id)})
        if not branch:
            branch = await db.branches.find_one({"_id": b_id})
        if not branch and isinstance(b_id, ObjectId):
            branch = await db.branches.find_one({"_id": str(b_id)})
        if branch:
            branch_name = branch.get("name") or branch.get("branchName") or ""
        
    # Department lookup
    if emp_history.get("departmentId"):
        d_id = parse_id(emp_history["departmentId"])
        dept = await db.departments.find_one({"_id": d_id})
        if not dept and isinstance(d_id, ObjectId):
            dept = await db.departments.find_one({"_id": str(d_id)})
        if dept:
            dept_name = dept.get("name") or dept.get("departmentName") or ""
        
    # Designation lookup
    if emp_history.get("designationId"):
        des_id = parse_id(emp_history["designationId"])
        desig = await db.designations.find_one({"_id": des_id})
        if not desig and isinstance(des_id, ObjectId):
            desig = await db.designations.find_one({"_id": str(des_id)})
        if desig:
            desig_name = desig.get("name") or desig.get("designationName") or ""
        
    # Reporting Manager lookup:
    # Can be ObjectId (string or ObjectId), employeeId, or employeeCode
    if emp_history.get("reportingManagerEmployeeId"):
        manager_ref = str(emp_history["reportingManagerEmployeeId"]).strip()
        manager_or = [{"employeeId": manager_ref}, {"employeeCode": manager_ref}]
        if len(manager_ref) == 24:
            try:
                manager_or.append({"_id": ObjectId(manager_ref)})
            except Exception:
                pass
        
        manager = await db.employees.find_one({"$or": manager_or})
        if manager:
            mgr_emp_id = manager.get("employeeId")
            mgr_emp_code = manager.get("employeeCode")
            mgr_pers_or = []
            if mgr_emp_id:
                mgr_pers_or.append({"employeeId": mgr_emp_id})
            if mgr_emp_code:
                mgr_pers_or.append({"employeeCode": mgr_emp_code})
            
            manager_personal = await db.employee_personals.find_one({"$or": mgr_pers_or}) if mgr_pers_or else None
            if manager_personal:
                first = manager_personal.get("firstName", "")
                last = manager_personal.get("lastName", "")
                manager_name = f"{first} {last}".strip()
            if not manager_name:
                first = manager.get("firstName", "")
                last = manager.get("lastName", "")
                manager_name = f"{first} {last}".strip()
            if not manager_name:
                manager_name = manager.get("employeeCode", manager_ref)

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
