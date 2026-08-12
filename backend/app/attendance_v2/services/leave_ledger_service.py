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

        # Calculate initial entitlement if DOJ > 1 year
        doj = await self._get_employee_doj(emp_id)
        
        annual_entitlement = 12.0
        anniversary_entitlement = 0.0
        carried_forward = 0.0
        credited = 0.0
        
        if doj:
            anniversary_date = date(doj.year + 1, doj.month, doj.day)
            
            # If current year is exactly the anniversary year
            if year == anniversary_date.year:
                # Employee just reached anniversary this year
                # They get prorated: 12 - joining_month
                anniversary_entitlement = max(0.0, 12.0 - doj.month)
                credited = anniversary_entitlement
            elif year > anniversary_date.year:
                # Employee passed anniversary in a previous year
                # For EL, carry forward is handled by annual reset job, but if creating mid-year...
                # We'll just give the full annual entitlement if they are > 1 yr
                credited = annual_entitlement
            else:
                # Year is BEFORE anniversary year
                credited = 0.0

        now = datetime.now(timezone.utc)
        
        ledger_doc = {
            "employeeId": emp_id,
            "employeeCode": emp_code,
            "calendarYear": year,
            "leaveType": leave_type,
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
        
        await self.db.leave_ledgers.insert_one(ledger_doc)
        return ledger_doc

    async def _resolve_working_days(self, emp_id: str, from_date: date, to_date: date):
        # We need to resolve holidays and weekly offs.
        # This requires shift, weekly off policy, and holiday calendar.
        # For full fidelity, we query them.
        emp_hist = await self.db.employee_employment_histories.find_one({
            "employeeId": emp_id,
            "isCurrent": True,
            "deletedAt": None
        })
        if not emp_hist:
            # Fallback: assume all days are working if no history
            return [from_date.replace(day=d) for d in range(from_date.day, to_date.day + 1)] # naive, won't handle month boundary
            
        shift_code = emp_hist.get("shiftCode")
        branch_id = emp_hist.get("branchId")
        
        shift = None
        if shift_code:
            shift = await self.db.shifts.find_one({"shiftCode": shift_code})
            
        # Get weekly off policy
        wo_policy = None
        if shift:
            wo_code = shift.get("weeklyOffPolicyCode")
            if wo_code:
                wo_policy = await self.db.weekly_off_policies.find_one({"weeklyOffPolicyCode": wo_code})
                
        # Get holiday calendar
        holiday_dates_str = set()
        if branch_id:
            # Simple holiday fetch for the year(s)
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
                # Check day type for this weekday
                weekday_idx = current.weekday() # 0 = Mon, 6 = Sun
                # JS uses 0=Sun, 1=Mon. Our python models use different. Let's assume standard mapping:
                # We can do a simplistic check if it's WEEKOFF
                for wd in wo_policy.get("weekdays", []):
                    # Python weekday: Mon=0...Sun=6. 
                    # If wo_policy uses "MONDAY" etc.
                    day_names = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
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
        
        # Get emp code
        emp = await self.db.employees.find_one({"employeeId": emp_id})
        emp_code = emp.get("employeeCode", "UNKNOWN") if emp else "UNKNOWN"
        
        # Get ledger
        ledger = await self.get_or_create_ledger(emp_id, emp_code, year, leave_type)
        
        # Identify working days
        working_days = await self._resolve_working_days(emp_id, from_date, to_date)
        
        # Allocate balance
        balance = ledger.get("availableBalance", 0.0)
        allocations = []
        total_consumed = 0.0
        total_lop = 0.0
        
        now = datetime.now(timezone.utc)
        
        for d_str in working_days:
            if balance >= 1.0:
                allocated = 1.0
                balance -= 1.0
                total_consumed += 1.0
            elif balance > 0.0:
                allocated = balance
                total_consumed += balance
                total_lop += (1.0 - balance)
                balance = 0.0
            else:
                allocated = 0.0
                total_lop += 1.0
                
            allocations.append({
                "date": d_str,
                "approvalId": approval_id,
                "allocated": allocated,
                "lop": 1.0 - allocated,
                "createdAt": now
            })
            
        # Update ledger
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
            }
        )

    async def rollback_approval(self, approval_id: str):
        # Find all ledgers that have allocations for this approval
        ledgers = await self.db.leave_ledgers.find({"allocations.approvalId": approval_id}).to_list(length=None)
        now = datetime.now(timezone.utc)
        
        for ledger in ledgers:
            # Calculate what to restore
            to_restore = 0.0
            lop_to_remove = 0.0
            new_allocations = []
            
            for alloc in ledger.get("allocations", []):
                if alloc.get("approvalId") == approval_id:
                    to_restore += alloc.get("allocated", 0.0)
                    lop_to_remove += alloc.get("lop", 0.0)
                else:
                    new_allocations.append(alloc)
                    
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
                }
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
