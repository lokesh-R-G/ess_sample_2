from datetime import datetime, date, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson.objectid import ObjectId

class LeaveLedgerService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def _get_employee_doj(self, emp_id: str):
        emp = await self.db.employees.find_one({"employeeId": emp_id})
        if not emp: return None
        doj_str = emp.get("dateOfJoining")
        if not doj_str: return None
        return datetime.strptime(doj_str, "%Y-%m-%d").date()

    async def get_or_create_ledger(self, emp_id: str, emp_code: str, year: int, leave_type: str):
        ledger = await self.db.leave_ledgers.find_one({
            "employeeId": emp_id,
            "calendarYear": year,
            "leaveType": leave_type
        })
        if ledger:
            return ledger

        now = datetime.now(timezone.utc)
        target_date = now if year == now.year else datetime(year, 1, 1, tzinfo=timezone.utc)

        # Query active policy
        query = {
            "deletedAt": None,
            "effectiveFrom": {"$lte": target_date},
            "$or": [
                {"effectiveTo": None},
                {"effectiveTo": {"$gt": target_date}}
            ]
        }
        docs = await self.db.leave_policies.find(query).sort([("version", -1)]).to_list(length=1)
        if not docs:
            docs = await self.db.leave_policies.find({"deletedAt": None, "isCurrent": True}).sort([("version", -1)]).to_list(length=1)
            
        if not docs:
            return None

        policy = docs[0]
        type_config = next((t for t in policy.get("leaveTypes", []) if t.get("code") == leave_type), None)
        
        if not type_config or not type_config.get("enabled", True):
            return None

        annual_entitlement = float(type_config.get("annualEntitlement", 0.0))
        anniversary_entitlement = 0.0
        carried_forward = 0.0
        credited = 0.0

        doj = await self._get_employee_doj(emp_id)
        if doj:
            anniversary_date = date(doj.year + 1, doj.month, doj.day)
            
            anniversary_eligibility_enabled = type_config.get("anniversaryEligibilityEnabled", True)
            joining_year_proration_enabled = type_config.get("joiningYearProrationEnabled", True)
            proration_rule = type_config.get("prorationRule", "MONTHLY_REDUCTION")
            
            def calc_prorated():
                if joining_year_proration_enabled:
                    if proration_rule == "MONTHLY_REDUCTION":
                        return max(0.0, annual_entitlement - (doj.month - 1))
                return annual_entitlement

            if anniversary_eligibility_enabled:
                if year == anniversary_date.year:
                    if now.date() >= anniversary_date:
                        anniversary_entitlement = annual_entitlement
                        credited = anniversary_entitlement
                    else:
                        credited = 0.0
                elif year > anniversary_date.year:
                    credited = annual_entitlement
                else:
                    credited = 0.0
            else:
                if year == doj.year:
                    credited = calc_prorated()
                elif year > doj.year:
                    credited = annual_entitlement
                else:
                    credited = 0.0
        else:
            credited = annual_entitlement

        ledger_doc = {
            "employeeId": emp_id,
            "employeeCode": emp_code,
            "calendarYear": year,
            "leaveType": leave_type,
            "policyCode": policy.get("policyCode"),
            "policyVersion": policy.get("version"),
            "openingBalance": credited,
            "annualEntitlement": annual_entitlement,
            "anniversaryEntitlement": anniversary_entitlement,
            "carriedForward": carried_forward,
            "credited": credited,
            "consumed": 0.0,
            "availableBalance": credited,
            "expired": 0.0,
            "lopDays": 0.0,
            "version": 1,
            "createdAt": now,
            "updatedAt": now,
            "allocations": []
        }
        
        try:
            await self.db.leave_ledgers.insert_one(ledger_doc)
        except Exception:
            # Handle potential race condition on insert
            ledger = await self.db.leave_ledgers.find_one({
                "employeeId": emp_id,
                "calendarYear": year,
                "leaveType": leave_type
            })
            if ledger:
                return ledger
                
        return ledger_doc

    async def _resolve_working_days(self, emp_id: str, from_date: date, to_date: date):
        emp_hist = await self.db.employee_employment_histories.find_one({
            "employeeId": emp_id,
            "isCurrent": True,
            "deletedAt": None
        })
        if not emp_hist:
            return [from_date.replace(day=d) for d in range(from_date.day, to_date.day + 1)]
            
        shift_code = emp_hist.get("shiftCode")
        branch_id = emp_hist.get("branchId")
        
        shift = None
        if shift_code:
            shift = await self.db.shifts.find_one({"shiftCode": shift_code})
            
        wo_policy = None
        if shift:
            wo_code = shift.get("weeklyOffPolicyCode")
            if wo_code:
                wo_policy = await self.db.weekly_off_policies.find_one({"weeklyOffPolicyCode": wo_code})
                
        holiday_dates_str = set()
        if branch_id:
            cursor = self.db.holiday_calendars.find({
                "branchId": branch_id,
                "status": "Active",
                "year": {"$in": [from_date.year, to_date.year]}
            })
            async for hc in cursor:
                for h in hc.get("holidays", []):
                    if h.get("date"):
                        holiday_dates_str.add(h["date"])
                        
        working_days = []
        current = from_date
        from datetime import timedelta
        
        while current <= to_date:
            d_str = current.isoformat()
            is_holiday = d_str in holiday_dates_str
            
            is_wo = False
            if wo_policy:
                weekday_idx = current.weekday()
                day_names = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
                for wd in wo_policy.get("weekdays", []):
                    if wd.get("day") == day_names[weekday_idx] and wd.get("dayType") == "WEEKOFF":
                        is_wo = True
                        break
                        
            if not is_holiday and not is_wo:
                working_days.append(d_str)
                
            current += timedelta(days=1)
            
        return working_days

    async def commit_approval(self, approval_id: str):
        app = await self.db.approvals.find_one({"_id": ObjectId(approval_id)})
        if not app or app.get("approvalType") != "Leave" or app.get("status") != "APPROVED":
            return
            
        emp_id = app["employeeId"]
        rd = app.get("requestData", {})
        leave_type = rd.get("leaveType", "CL")
        
        from_date_str = rd.get("fromDate")
        to_date_str = rd.get("toDate")
        if not from_date_str or not to_date_str: return
        
        from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
        to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
        
        year = from_date.year
        
        emp = await self.db.employees.find_one({"employeeId": emp_id})
        emp_code = emp.get("employeeCode", "UNKNOWN") if emp else "UNKNOWN"
        
        ledger_base = await self.get_or_create_ledger(emp_id, emp_code, year, leave_type)
        if not ledger_base: return
        
        working_days = await self._resolve_working_days(emp_id, from_date, to_date)
        if not working_days: return
        
        now = datetime.now(timezone.utc)
        
        async with await self.db.client.start_session() as session:
            async with session.start_transaction():
                # Re-fetch ledger inside transaction
                ledger = await self.db.leave_ledgers.find_one({"_id": ledger_base["_id"]}, session=session)
                if not ledger: return
                
                # Idempotency check
                existing = [a for a in ledger.get("allocations", []) if a.get("approvalId") == approval_id]
                if existing:
                    return
                
                # Check zero balance policy
                policy_code = ledger.get("policyCode")
                policy_version = ledger.get("policyVersion")
                zero_allowed = True
                
                if policy_code:
                    policy = await self.db.leave_policies.find_one({"policyCode": policy_code, "version": policy_version}, session=session)
                    if policy:
                        type_config = next((t for t in policy.get("leaveTypes", []) if t.get("code") == leave_type), None)
                        if type_config:
                            zero_allowed = type_config.get("zeroBalanceApprovalAllowed", True)
                
                balance = ledger.get("availableBalance", 0.0)
                
                if balance < len(working_days) and not zero_allowed:
                    # Cannot approve, zero balance not allowed
                    return
                
                allocations = []
                total_consumed = 0.0
                total_lop = 0.0
                
                is_half_day = rd.get("isHalfDay", False)
                daily_deduction = 0.5 if is_half_day else 1.0
                
                for d_str in working_days:
                    if balance >= daily_deduction:
                        allocated = daily_deduction
                        balance -= daily_deduction
                        total_consumed += daily_deduction
                        lop = 0.0
                    else:
                        allocated = balance
                        lop = daily_deduction - balance
                        total_consumed += balance
                        total_lop += lop
                        balance = 0.0
                        
                    allocations.append({
                        "date": d_str,
                        "approvalId": approval_id,
                        "allocated": allocated,
                        "lop": lop,
                        "createdAt": now
                    })
                    
                await self.db.leave_ledgers.update_one(
                    {"_id": ledger["_id"]},
                    {
                        "$set": {
                            "availableBalance": balance,
                            "consumed": ledger.get("consumed", 0.0) + total_consumed,
                            "lopDays": ledger.get("lopDays", 0.0) + total_lop,
                            "updatedAt": now
                        },
                        "$push": {
                            "allocations": {"$each": allocations}
                        },
                        "$inc": {"version": 1}
                    },
                    session=session
                )

    async def rollback_approval(self, approval_id: str):
        now = datetime.now(timezone.utc)
        async with await self.db.client.start_session() as session:
            async with session.start_transaction():
                ledgers = await self.db.leave_ledgers.find({"allocations.approvalId": approval_id}, session=session).to_list(length=None)
                
                for ledger in ledgers:
                    to_restore = 0.0
                    lop_to_remove = 0.0
                    new_allocations = []
                    found = False
                    
                    for alloc in ledger.get("allocations", []):
                        if alloc.get("approvalId") == approval_id:
                            to_restore += alloc.get("allocated", 0.0)
                            lop_to_remove += alloc.get("lop", 0.0)
                            found = True
                        else:
                            new_allocations.append(alloc)
                            
                    if found:
                        await self.db.leave_ledgers.update_one(
                            {"_id": ledger["_id"]},
                            {
                                "$set": {
                                    "availableBalance": ledger.get("availableBalance", 0.0) + to_restore,
                                    "consumed": max(0.0, ledger.get("consumed", 0.0) - to_restore),
                                    "lopDays": max(0.0, ledger.get("lopDays", 0.0) - lop_to_remove),
                                    "allocations": new_allocations,
                                    "updatedAt": now
                                },
                                "$inc": {"version": 1}
                            },
                            session=session
                        )

    async def get_daily_allocation(self, emp_id: str, target_date_str: str, approval_id: str):
        y = int(target_date_str.split("-")[0])
        cursor = self.db.leave_ledgers.find({"employeeId": emp_id, "calendarYear": y, "allocations.approvalId": approval_id})
        
        async for ledger in cursor:
            for alloc in ledger.get("allocations", []):
                if alloc.get("approvalId") == approval_id and alloc.get("date") == target_date_str:
                    return {
                        "allocated": alloc.get("allocated", 0.0),
                        "lop": alloc.get("lop", 0.0),
                        "leaveType": ledger.get("leaveType")
                    }
        return None
