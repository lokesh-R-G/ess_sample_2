from fastapi import APIRouter, Depends, HTTPException, Query, Body
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.db.mongo import get_database
from app.dependencies import require_roles, get_current_user
from app.domain_models import AuthUser, PayrollCycle
from app.deduction.models.manual_deduction import ManualPayrollAdjustment
from app.payroll.services.payroll_processor import PayrollProcessor
from app.payroll.services.payslip_service import PayslipService
from bson import ObjectId

router = APIRouter()

# 1. LEAVE BALANCES
@router.get("/leave-balances")
async def get_leave_balances(
    companyId: str,
    cycleId: str = Query(..., description="Payroll Cycle ID"),
    branchId: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: AuthUser = Depends(require_roles(["Admin", "Super Admin", "HR"]))
):
    # Enforce company scope
    if current_user.role != "Super Admin" and current_user.companyId != companyId:
        raise HTTPException(status_code=403, detail="Unauthorized company access")
        
    emp_query = {"companyId": companyId, "status": "Active"}
    if branchId:
        emp_query["branchId"] = branchId
        
    employees = await db.employees.find(emp_query).to_list(length=1000)
    employee_ids = [e["employeeId"] for e in employees]
    
    # Fetch leave ledgers
    ledgers = await db.leave_ledgers.find({
        "employeeId": {"$in": employee_ids}
    }).to_list(length=5000)
    
    # Group by employeeId
    result = []
    for emp in employees:
        emp_ledgers = [l for l in ledgers if l["employeeId"] == emp["employeeId"]]
        
        # Build dynamic breakdown
        breakdown = {}
        total_credited = 0
        total_availed = 0
        total_balance = 0
        lop_days = 0 # Normally fetched from attendance aggregator
        
        for ledger in emp_ledgers:
            lt = ledger.get("leaveType", "UNKNOWN")
            cr = ledger.get("credited", 0.0)
            av = ledger.get("availed", 0.0)
            bal = ledger.get("balance", 0.0)
            
            breakdown[lt] = {
                "credited": cr,
                "availed": av,
                "balance": bal
            }
            
            total_credited += cr
            total_availed += av
            total_balance += bal
            
        result.append({
            "employeeId": emp["employeeId"],
            "employeeCode": emp.get("employeeCode"),
            "employeeName": f"{emp.get('firstName', '')} {emp.get('lastName', '')}".strip(),
            "branchId": emp.get("branchId"),
            "breakdown": breakdown,
            "totalCredited": total_credited,
            "totalAvailed": total_availed,
            "totalBalance": total_balance,
            "lopDays": lop_days
        })
        
    return result

# 2. REIMBURSEMENTS
@router.get("/reimbursements")
async def get_reimbursements(
    companyId: str,
    branchId: Optional[str] = None,
    payrollCycleId: Optional[str] = None,
    month: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: AuthUser = Depends(require_roles(["Admin", "Super Admin", "HR"]))
):
    if current_user.role != "Super Admin" and current_user.companyId != companyId:
        raise HTTPException(status_code=403, detail="Unauthorized company access")

    emp_query = {"companyId": companyId, "status": "Active"}
    if branchId:
        emp_query["branchId"] = branchId
        
    employees = await db.employees.find(emp_query).to_list(length=1000)
    employee_ids = [e["employeeId"] for e in employees]
    
    query = {
        "employeeId": {"$in": employee_ids},
        "deletedAt": None,
        "status": {"$in": ["PAYROLL_ELIGIBLE", "PAYROLL_INCLUDED"]}
    }
    if payrollCycleId:
        query["payrollCycleId"] = payrollCycleId
        
    claims = await db.reimbursement_claims.find(query).to_list(length=5000)
    
    # Map with employee details
    emp_map = {e["employeeId"]: e for e in employees}
    
    result = []
    for c in claims:
        emp = emp_map.get(c["employeeId"], {})
        c["_id"] = str(c["_id"])
        c["employeeName"] = f"{emp.get('firstName', '')} {emp.get('lastName', '')}".strip()
        c["employeeCode"] = emp.get("employeeCode")
        c["branchId"] = emp.get("branchId")
        result.append(c)
        
    return result

# 3. DEDUCTIONS (GET)
@router.get("/deductions")
async def get_deductions(
    companyId: str,
    branchId: Optional[str] = None,
    payrollCycleId: Optional[str] = None,
    month: Optional[str] = Query(None, description="YYYY-MM"),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: AuthUser = Depends(require_roles(["Admin", "Super Admin", "HR"]))
):
    if current_user.role != "Super Admin" and current_user.companyId != companyId:
        raise HTTPException(status_code=403, detail="Unauthorized company access")

    query = {"companyId": companyId, "status": "Active", "deletedAt": None, "isCurrent": True}
    if branchId:
        query["branchId"] = branchId
    if payrollCycleId:
        query["payrollCycleId"] = payrollCycleId
    elif month:
        query["payrollPeriod"] = month
        
    deductions = await db.manual_payroll_adjustments.find(query).to_list(length=5000)
    
    # Fetch employees for mapping
    employee_ids = list(set([d["employeeId"] for d in deductions]))
    if not employee_ids:
        return []
        
    employees = await db.employees.find({"employeeId": {"$in": employee_ids}}).to_list(length=1000)
    emp_map = {e["employeeId"]: e for e in employees}
    
    result = []
    for d in deductions:
        emp = emp_map.get(d["employeeId"], {})
        d["_id"] = str(d["_id"])
        d["employeeName"] = f"{emp.get('firstName', '')} {emp.get('lastName', '')}".strip()
        d["employeeCode"] = emp.get("employeeCode")
        result.append(d)
        
    return result

# 4. DEDUCTIONS (POST)
@router.post("/deductions")
async def create_deduction(
    payload: ManualPayrollAdjustment,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: AuthUser = Depends(require_roles(["Admin", "Super Admin", "HR"]))
):
    if current_user.role != "Super Admin" and current_user.companyId != payload.companyId:
        raise HTTPException(status_code=403, detail="Unauthorized company access")
        
    # Check cycle status
    if payload.payrollCycleId:
        cycle = await db.payroll_cycles.find_one({"_id": ObjectId(payload.payrollCycleId)})
        if cycle and cycle.get("processingStatus") in ["CALCULATED", "PUBLISHED"]:
            raise HTTPException(status_code=400, detail="Cannot modify deductions for a calculated or published cycle.")

    payload.createdBy = current_user.employeeId
    
    doc = payload.model_dump(by_alias=True, exclude_none=True)
    res = await db.manual_payroll_adjustments.insert_one(doc)
    doc["_id"] = str(res.inserted_id)
    return doc

# 4.5 DEDUCTIONS (PUT)
@router.put("/deductions/{deduction_id}")
async def update_deduction(
    deduction_id: str,
    payload: ManualPayrollAdjustment,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: AuthUser = Depends(require_roles(["Admin", "Super Admin", "HR"]))
):
    doc = await db.manual_payroll_adjustments.find_one({"_id": ObjectId(deduction_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    if current_user.role != "Super Admin" and current_user.companyId != doc["companyId"]:
        raise HTTPException(status_code=403, detail="Unauthorized company access")

    cycle_id = doc.get("payrollCycleId")
    if cycle_id:
        cycle = await db.payroll_cycles.find_one({"_id": ObjectId(cycle_id)})
        if cycle and cycle.get("processingStatus") in ["CALCULATED", "PUBLISHED"]:
            raise HTTPException(status_code=400, detail="Cannot modify deductions for a calculated or published cycle.")

    # Archive old
    await db.manual_payroll_adjustments.update_one(
        {"_id": ObjectId(deduction_id)},
        {"$set": {
            "status": "Archived", 
            "isCurrent": False,
            "updatedAt": datetime.utcnow(),
            "updatedBy": current_user.employeeId
        }}
    )

    # Insert new version
    payload.version = doc.get("version", 1) + 1
    payload.isCurrent = True
    payload.originalAdjustmentId = doc.get("originalAdjustmentId") or str(doc["_id"])
    payload.createdBy = doc.get("createdBy")
    payload.createdAt = doc.get("createdAt")
    payload.updatedBy = current_user.employeeId
    payload.updatedAt = datetime.utcnow()

    new_doc = payload.model_dump(by_alias=True, exclude_none=True)
    new_doc.pop("_id", None)
    res = await db.manual_payroll_adjustments.insert_one(new_doc)
    new_doc["_id"] = str(res.inserted_id)
    return new_doc

# 5. DEDUCTIONS (DELETE)
@router.delete("/deductions/{deduction_id}")
async def delete_deduction(
    deduction_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: AuthUser = Depends(require_roles(["Admin", "Super Admin", "HR"]))
):
    doc = await db.manual_payroll_adjustments.find_one({"_id": ObjectId(deduction_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    if current_user.role != "Super Admin" and current_user.companyId != doc["companyId"]:
        raise HTTPException(status_code=403, detail="Unauthorized company access")
        
    cycle_id = doc.get("payrollCycleId")
    if cycle_id:
        cycle = await db.payroll_cycles.find_one({"_id": ObjectId(cycle_id)})
        if cycle and cycle.get("processingStatus") in ["CALCULATED", "PUBLISHED"]:
            raise HTTPException(status_code=400, detail="Cannot modify deductions for a calculated or published cycle.")
            
    await db.manual_payroll_adjustments.update_one(
        {"_id": ObjectId(deduction_id)},
        {"$set": {"status": "Deleted", "isCurrent": False, "deletedAt": datetime.utcnow(), "updatedBy": current_user.employeeId}}
    )
    return {"success": True}

# 6. CALCULATE PAYROLL
@router.post("/calculate/{cycle_id}")
async def calculate_payroll_for_company(
    cycle_id: str,
    company_id: str = Body(..., embed=True),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: AuthUser = Depends(require_roles(["Admin", "Super Admin", "HR"]))
):
    if current_user.role != "Super Admin" and current_user.companyId != company_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    processor = PayrollProcessor(db)
    
    emp_query = {"companyId": company_id, "status": "Active"}
        
    employees = await db.employees.find(emp_query).to_list(length=10000)
    
    results = []
    errors = []
    
    for emp in employees:
        try:
            # We recalculate everything. If existing, it overwrites (creates new version).
            res = await processor.process_employee(
                cycle_id=cycle_id,
                employee_id=emp["employeeId"],
                recalculated_by=current_user.employeeId,
                reason="Admin Batch Calculation"
            )
            results.append(emp["employeeId"])
        except Exception as e:
            errors.append({"employeeId": emp["employeeId"], "error": str(e)})
            
    # Update cycle status if needed
    await db.payroll_cycles.update_one(
        {"_id": ObjectId(cycle_id)},
        {"$set": {"processingStatus": "CALCULATED"}}
    )
            
    return {"success": len(results), "errors": errors}

# 7. REPORTS: SALARY BREAKDOWN
@router.get("/reports/salary/{cycle_id}")
async def get_salary_report(
    cycle_id: str,
    companyId: str,
    branchId: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: AuthUser = Depends(require_roles(["Admin", "Super Admin", "HR"]))
):
    if current_user.role != "Super Admin" and current_user.companyId != companyId:
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    # Aggregate payrolls
    pipeline = [
        {"$match": {"cycleId": cycle_id, "isActive": True}},
        {
            "$lookup": {
                "from": "employees",
                "localField": "employeeId",
                "foreignField": "employeeId",
                "as": "employee"
            }
        },
        {"$unwind": "$employee"},
        {"$match": {"employee.companyId": companyId}}
    ]
    if branchId:
        pipeline.append({"$match": {"employee.branchId": branchId}})
        
    payrolls = await db.payrolls.aggregate(pipeline).to_list(length=1000)
    
    for p in payrolls:
        p["_id"] = str(p["_id"])
        # Fetch line items
        line_items = await db.payroll_line_items.find({"payrollId": p["_id"]}).to_list(length=1000)
        p["lineItems"] = [{"componentId": li["componentId"], "amount": li["amount"], "type": li["itemType"], "desc": li["description"]} for li in line_items]
        p["employeeName"] = f"{p['employee'].get('firstName', '')} {p['employee'].get('lastName', '')}".strip()
        p["employeeCode"] = p['employee'].get('employeeCode')
        p["branchId"] = p['employee'].get('branchId')
        del p["employee"]
        
    return payrolls

# 8. REPORTS: PF BREAKDOWN
@router.get("/reports/pf/{cycle_id}")
async def get_pf_report(
    cycle_id: str,
    companyId: str,
    branchId: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: AuthUser = Depends(require_roles(["Admin", "Super Admin", "HR"]))
):
    # Enforces same rules, returning the PF math specifically
    pipeline = [
        {"$match": {"cycleId": cycle_id, "isActive": True}},
        {
            "$lookup": {
                "from": "employees",
                "localField": "employeeId",
                "foreignField": "employeeId",
                "as": "employee"
            }
        },
        {"$unwind": "$employee"},
        {"$match": {"employee.companyId": companyId}}
    ]
    if branchId:
        pipeline.append({"$match": {"employee.branchId": branchId}})
        
    payrolls = await db.payrolls.aggregate(pipeline).to_list(length=1000)
    
    result = []
    for p in payrolls:
        snap = p.get("payloadSnapshot", {})
        pf = snap.get("pfCalculation", {})
        result.append({
            "employeeId": p["employeeId"],
            "employeeName": f"{p['employee'].get('firstName', '')} {p['employee'].get('lastName', '')}".strip(),
            "employeeCode": p['employee'].get('employeeCode'),
            "branchId": p['employee'].get('branchId'),
            "pfGross": snap.get("pfGross", 0.0),
            "epfEmployee": pf.get("employeePf", 0.0),
            "epfEmployer": pf.get("employerPf", 0.0),
            "epsEmployer": pf.get("employerPension", 0.0),
            "edli": pf.get("edli", 0.0),
            "adminCharges": pf.get("adminCharges", 0.0),
            "totalEpf": pf.get("employeePf", 0.0) + pf.get("employerPf", 0.0) + pf.get("employerPension", 0.0)
        })
    return result

# 9. REPORTS: ESI BREAKDOWN
@router.get("/reports/esi/{cycle_id}")
async def get_esi_report(
    cycle_id: str,
    companyId: str,
    branchId: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: AuthUser = Depends(require_roles(["Admin", "Super Admin", "HR"]))
):
    pipeline = [
        {"$match": {"cycleId": cycle_id, "isActive": True}},
        {
            "$lookup": {
                "from": "employees",
                "localField": "employeeId",
                "foreignField": "employeeId",
                "as": "employee"
            }
        },
        {"$unwind": "$employee"},
        {"$match": {"employee.companyId": companyId}}
    ]
    if branchId:
        pipeline.append({"$match": {"employee.branchId": branchId}})
        
    payrolls = await db.payrolls.aggregate(pipeline).to_list(length=1000)
    
    result = []
    for p in payrolls:
        snap = p.get("payloadSnapshot", {})
        esi = snap.get("esiCalculation", {})
        result.append({
            "employeeId": p["employeeId"],
            "employeeName": f"{p['employee'].get('firstName', '')} {p['employee'].get('lastName', '')}".strip(),
            "employeeCode": p['employee'].get('employeeCode'),
            "branchId": p['employee'].get('branchId'),
            "esiGross": snap.get("esiGross", 0.0),
            "employeeEsi": esi.get("employeeEsi", 0.0),
            "employerEsi": esi.get("employerEsi", 0.0),
            "totalEsi": esi.get("employeeEsi", 0.0) + esi.get("employerEsi", 0.0)
        })
    return result

# 10. PUBLISH
@router.post("/publish/{cycle_id}")
async def publish_payroll(
    cycle_id: str,
    company_id: str = Body(..., embed=True),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: AuthUser = Depends(require_roles(["Admin", "Super Admin", "HR"]))
):
    if current_user.role != "Super Admin" and current_user.companyId != company_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    payslip_service = PayslipService(db)
    
    payrolls = await db.payrolls.find({"cycleId": cycle_id, "isActive": True}).to_list(length=1000)
    success = 0
    errors = []
    
    for p in payrolls:
        try:
            # Reuses existing payslip publisher
            await payslip_service.generate_and_publish_payslip(str(p["_id"]))
            success += 1
        except Exception as e:
            errors.append({"employeeId": p["employeeId"], "error": str(e)})
            
    await db.payroll_cycles.update_one(
        {"_id": ObjectId(cycle_id)},
        {"$set": {"processingStatus": "PUBLISHED"}}
    )
    
    return {"success": success, "errors": errors}
