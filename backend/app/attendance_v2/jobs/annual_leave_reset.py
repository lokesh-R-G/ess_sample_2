import asyncio
from datetime import datetime, date, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.mongo import get_database, connect_to_mongo
from app.attendance_policy.repositories.leave_policy_repository import LeavePolicyRepository

async def run_annual_leave_reset():
    db = get_database()
    now = datetime.now(timezone.utc)
    current_year = now.year
    
    # 1. Get the active leave policy for Jan 1 of the new year
    target_date = datetime(current_year, 1, 1, tzinfo=timezone.utc)
    query = {
        "deletedAt": None,
        "isCurrent": True,
        "effectiveFrom": {"$lte": target_date},
        "$or": [
            {"effectiveTo": None},
            {"effectiveTo": {"$gt": target_date}}
        ]
    }
    
    docs = await db.leave_policies.find(query).sort([("version", -1)]).to_list(length=1)
    if not docs:
        docs = await db.leave_policies.find({"deletedAt": None, "isCurrent": True}).sort([("version", -1)]).to_list(length=1)
        
    if not docs:
        print("No active Leave Policy found. Skipping annual reset.")
        return
        
    policy = docs[0]
    leave_types_config = {t["code"]: t for t in policy.get("leaveTypes", []) if t.get("enabled", True)}
    
    if not leave_types_config:
        print("No enabled leave types found. Skipping.")
        return
        
    # 2. Iterate over all active employees
    cursor = db.employees.find({"status": "Active"})
    
    async for emp in cursor:
        emp_id = emp["employeeId"]
        emp_code = emp.get("employeeCode", "UNKNOWN")
        doj_str = emp.get("dateOfJoining")
        if not doj_str:
            continue
            
        doj = datetime.strptime(doj_str, "%Y-%m-%d").date()
        anniversary_date = date(doj.year + 1, doj.month, doj.day)
        
        for lt_code, config in leave_types_config.items():
            # Check if ledger for current year already exists (Idempotency)
            existing = await db.leave_ledgers.find_one({
                "employeeId": emp_id,
                "calendarYear": current_year,
                "leaveType": lt_code
            })
            if existing:
                continue
                
            # Handle carry forward from previous year
            carried_forward = 0.0
            if config.get("carryForwardEnabled", False):
                prev_ledger = await db.leave_ledgers.find_one({
                    "employeeId": emp_id,
                    "calendarYear": current_year - 1,
                    "leaveType": lt_code
                })
                if prev_ledger:
                    available = prev_ledger.get("availableBalance", 0.0)
                    limit = config.get("carryForwardLimit", 0.0)
                    cf_type = config.get("carryForwardType", "FLAT")
                    
                    if limit > 0:
                        if cf_type == "PERCENTAGE":
                            carried_forward = min(available, available * (limit / 100.0))
                        else:
                            carried_forward = min(available, limit)
                    else:
                        # 0 means unlimited
                        carried_forward = available
                        
            # Determine entitlement
            annual_entitlement = float(config.get("annualEntitlement", 0.0))
            anniversary_eligibility_enabled = config.get("anniversaryEligibilityEnabled", True)
            
            credited = 0.0
            anniversary_entitlement = 0.0
            
            # Since this is Jan 1st of current_year, if anniversary is this year, we wait for it
            if anniversary_eligibility_enabled:
                if current_year < anniversary_date.year:
                    credited = 0.0
                elif current_year == anniversary_date.year:
                    # They will get it on their anniversary, which hasn't happened yet since it's Jan 1.
                    # Unless DOJ was Jan 1
                    if now.date() >= anniversary_date:
                        anniversary_entitlement = annual_entitlement
                        credited = annual_entitlement
                    else:
                        credited = 0.0
                else:
                    # Past anniversary year
                    credited = annual_entitlement
            else:
                if current_year == doj.year:
                    if config.get("joiningYearProrationEnabled", True):
                        credited = max(0.0, annual_entitlement - (doj.month - 1))
                    else:
                        credited = annual_entitlement
                elif current_year > doj.year:
                    credited = annual_entitlement
                else:
                    credited = 0.0
                    
            opening_balance = credited + carried_forward
            
            ledger_doc = {
                "employeeId": emp_id,
                "employeeCode": emp_code,
                "calendarYear": current_year,
                "leaveType": lt_code,
                "policyCode": policy.get("policyCode"),
                "policyVersion": policy.get("version"),
                "openingBalance": opening_balance,
                "annualEntitlement": annual_entitlement,
                "anniversaryEntitlement": anniversary_entitlement,
                "carriedForward": carried_forward,
                "credited": credited,
                "consumed": 0.0,
                "availableBalance": opening_balance,
                "expired": 0.0, # Will be set on the previous year's ledger
                "lopDays": 0.0,
                "version": 1,
                "createdAt": now,
                "updatedAt": now,
                "allocations": []
            }
            
            await db.leave_ledgers.insert_one(ledger_doc)
            
            # Expire previous year's balance if applicable
            if config.get("expiryEnabled", True) and current_year > 1:
                prev_ledger = await db.leave_ledgers.find_one({
                    "employeeId": emp_id,
                    "calendarYear": current_year - 1,
                    "leaveType": lt_code
                })
                if prev_ledger:
                    expired = prev_ledger.get("availableBalance", 0.0) - carried_forward
                    if expired > 0:
                        await db.leave_ledgers.update_one(
                            {"_id": prev_ledger["_id"]},
                            {"$set": {"expired": expired, "availableBalance": prev_ledger.get("availableBalance", 0.0) - expired, "updatedAt": now}}
                        )
                        
    print("Annual Leave Reset Completed.")

if __name__ == "__main__":
    async def main():
        await connect_to_mongo()
        await run_annual_leave_reset()
    asyncio.run(main())
