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

    async def _get_cycle_boundaries(self, cycle_year: int, doj: date, policy: dict):
        start_type = policy.get("leaveCycleStartType", "CALENDAR_YEAR")
        from datetime import timedelta
        if start_type == "DATE_OF_JOINING" and doj:
            try:
                start_date = datetime(cycle_year, doj.month, doj.day, tzinfo=timezone.utc)
            except ValueError:
                start_date = datetime(cycle_year, doj.month, doj.day - 1, tzinfo=timezone.utc)
            try:
                end_date = datetime(cycle_year + 1, doj.month, doj.day, tzinfo=timezone.utc)
            except ValueError:
                end_date = datetime(cycle_year + 1, doj.month, doj.day - 1, tzinfo=timezone.utc)
            end_date = end_date - timedelta(microseconds=1)
            return start_date, end_date
        else:
            start_date = datetime(cycle_year, 1, 1, tzinfo=timezone.utc)
            end_date = datetime(cycle_year, 12, 31, 23, 59, 59, 999999, tzinfo=timezone.utc)
            return start_date, end_date

    async def get_or_create_ledger(self, emp_id: str, emp_code: str, target_date_or_year, leave_type: str, create_if_missing: bool = True):
        now = datetime.now(timezone.utc)
        
        if isinstance(target_date_or_year, int):
            year = target_date_or_year
            target_date = now if year == now.year else datetime(year, 1, 1, tzinfo=timezone.utc)
        else:
            target_date = target_date_or_year
            if isinstance(target_date, date) and not isinstance(target_date, datetime):
                target_date = datetime.combine(target_date, datetime.min.time(), tzinfo=timezone.utc)

        # Query active policy first to determine cycle
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
        
        doj = await self._get_employee_doj(emp_id)
        cycle_year = target_date.year
        
        if policy.get("leaveCycleStartType") == "DATE_OF_JOINING" and doj:
            try:
                cycle_start_this_year = datetime(target_date.year, doj.month, doj.day, tzinfo=timezone.utc)
            except ValueError:
                # Leap year edge case
                cycle_start_this_year = datetime(target_date.year, doj.month, doj.day - 1, tzinfo=timezone.utc)
                
            if target_date < cycle_start_this_year:
                cycle_year = target_date.year - 1

        type_config = next((t for t in policy.get("leaveTypes", []) if t.get("code") == leave_type), None)
        
        if not type_config or not type_config.get("enabled", True):
            return None

        ledger = await self.db.leave_ledgers.find_one({
            "employeeId": emp_id,
            "calendarYear": cycle_year,
            "leaveType": leave_type
        })
        if ledger:
            return ledger

        annual_entitlement = float(type_config.get("annualEntitlement", 0.0))
        anniversary_entitlement = 0.0
        carried_forward = 0.0
        credited = 0.0

        doj = await self._get_employee_doj(emp_id)
        if doj:
            anniversary_date = date(cycle_year + 1, doj.month, doj.day)
            
            anniversary_eligibility_enabled = type_config.get("anniversaryEligibilityEnabled", True)
            joining_year_proration_enabled = type_config.get("joiningYearProrationEnabled", True)
            proration_rule = type_config.get("prorationRule", "MONTHLY_REDUCTION")
            
            def calc_prorated():
                if joining_year_proration_enabled:
                    if proration_rule == "MONTHLY_REDUCTION":
                        return max(0.0, annual_entitlement - (doj.month - 1))
                return annual_entitlement

            if anniversary_eligibility_enabled:
                if cycle_year == anniversary_date.year:
                    if now.date() >= anniversary_date:
                        anniversary_entitlement = annual_entitlement
                        credited = anniversary_entitlement
                    else:
                        credited = 0.0
                elif cycle_year > anniversary_date.year:
                    credited = annual_entitlement
                else:
                    credited = 0.0
            else:
                if cycle_year == doj.year:
                    credited = calc_prorated()
                elif cycle_year > doj.year:
                    credited = annual_entitlement
                else:
                    credited = 0.0
        else:
            credited = annual_entitlement

        renewal_deduction = 0.0
        total_absence = 0.0
        payroll_divisor = 0.0
        
        if doj:
            current_start, _ = await self._get_cycle_boundaries(cycle_year, doj, policy)
            doj_dt = datetime(doj.year, doj.month, doj.day, tzinfo=timezone.utc)
            if current_start > doj_dt:
                prev_year = cycle_year - 1
                prev_start, prev_end = await self._get_cycle_boundaries(prev_year, doj, policy)
                
                total_consumed = 0.0
                cursor = self.db.leave_ledgers.find({"employeeId": emp_id, "calendarYear": prev_year})
                async for l in cursor:
                    total_consumed += l.get("consumed", 0.0)
                    
                from app.payroll.services.lop_aggregator import LopAggregator
                att_cursor = self.db.attendance.find({
                    "employeeId": emp_id,
                    "date": {"$gte": prev_start.strftime("%Y-%m-%d"), "$lte": prev_end.strftime("%Y-%m-%d")}
                })
                att_records = [d async for d in att_cursor]
                lop_result = LopAggregator.aggregate_lop(att_records)
                total_lop = lop_result.totalLopDays
                
                total_absence = total_consumed + total_lop
                
                from app.payroll.repositories.payroll_setting_repository import PayrollSettingRepository
                setting_repo = PayrollSettingRepository(self.db)
                
                # `target_date` passed to get_active_setting should be a datetime, not just date.
                # Since prev_end is datetime, we can just use prev_end
                payroll_settings = await setting_repo.get_active_setting(prev_end)
                
                if payroll_settings:
                    calc_method = payroll_settings.defaultSalaryCalculationMethod
                    if calc_method == "Fixed 26 Days":
                        payroll_divisor = 26.0
                    elif calc_method == "Fixed 30 Days":
                        payroll_divisor = 30.0
                    elif calc_method in ["Calendar Days", "Working Days", "Attendance Based"]:
                        raise ValueError(f"Unresolved payroll divisor rule for annual renewal: {calc_method}")
                    else:
                        raise ValueError(f"Unknown salary calculation method: {calc_method}")
                        
                    if payroll_divisor > 0:
                        renewal_deduction = total_absence / payroll_divisor
                        credited = max(0.0, annual_entitlement - renewal_deduction)

        ledger_doc = {
            "employeeId": emp_id,
            "employeeCode": emp_code,
            "calendarYear": cycle_year,
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
            "renewalDeduction": renewal_deduction,
            "totalAbsence": total_absence,
            "payrollDivisor": payroll_divisor,
            "version": 1,
            "createdAt": now,
            "updatedAt": now,
            "allocations": []
        }
        
        if not create_if_missing:
            ledger_doc["openingBalance"] = 0.0
            ledger_doc["credited"] = 0.0
            ledger_doc["availableBalance"] = 0.0
            return ledger_doc
            
        try:
            await self.db.leave_ledgers.insert_one(ledger_doc)
        except Exception:
            # Handle potential race condition on insert
            ledger = await self.db.leave_ledgers.find_one({
                "employeeId": emp_id,
                "calendarYear": cycle_year,
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

    async def consume_for_permission(self, emp_id: str, month_str: str, days_needed: float = 0.0, allocations: list = None) -> float:
        if days_needed <= 0 and not allocations:
            return 0.0

        # We will attempt to consume from CL, then EL
        emp = await self.db.employees.find_one({"employeeId": emp_id})
        emp_code = emp.get("employeeCode", "UNKNOWN") if emp else "UNKNOWN"
        
        # Use the end of the month as the target date for resolution
        y, m = map(int, month_str.split("-"))
        import calendar
        last_day = calendar.monthrange(y, m)[1]
        target_date = date(y, m, last_day)
        
        now = datetime.now(timezone.utc)
        if target_date > now.date():
            target_date = now.date()
            
        target_date_str = target_date.isoformat()
        
        if allocations is None:
            allocations = [{"permissionId": None, "leaveType": None, "amount": days_needed}]
            
        overall_consumed = 0.0
        
        for alloc in allocations:
            perm_id = alloc.get("permissionId")
            leave_type = alloc.get("leaveType")
            amount_needed = alloc.get("amount", 0.0)
            
            if amount_needed <= 0:
                continue
                
            if not leave_type:
                leave_types = ["CL", "EL"]
                approval_id = f"permission_conversion_{month_str}"
            else:
                leave_types = [leave_type]
                approval_id = f"perm_conv_{perm_id}" if perm_id else f"permission_conversion_{month_str}"
                
            remaining_needed = amount_needed
            alloc_consumed = 0.0
            
            for lt in leave_types:
                if remaining_needed <= 0:
                    break
                    
                ledger_base = await self.get_or_create_ledger(emp_id, emp_code, target_date, lt)
                if not ledger_base:
                    continue
                    
                async with await self.db.client.start_session() as session:
                    async with session.start_transaction():
                        ledger = await self.db.leave_ledgers.find_one({"_id": ledger_base["_id"]}, session=session)
                        if not ledger:
                            continue
                            
                        existing_allocs = [a for a in ledger.get("allocations", []) if a.get("approvalId") == approval_id]
                        already_consumed = sum(a.get("allocated", 0.0) for a in existing_allocs)
                        
                        if already_consumed >= remaining_needed:
                            alloc_consumed += remaining_needed
                            remaining_needed = 0
                            break
                            
                        to_consume = remaining_needed - already_consumed
                        
                        balance = ledger.get("availableBalance", 0.0)
                        if balance <= 0:
                            alloc_consumed += already_consumed
                            remaining_needed -= already_consumed
                            continue
                            
                        actual_consumption = min(balance, to_consume)
                        if actual_consumption > 0:
                            new_alloc = {
                                "date": target_date_str,
                                "approvalId": approval_id,
                                "allocated": actual_consumption,
                                "lop": 0.0,
                                "createdAt": now
                            }
                            
                            await self.db.leave_ledgers.update_one(
                                {"_id": ledger["_id"]},
                                {
                                    "$set": {
                                        "availableBalance": balance - actual_consumption,
                                        "consumed": ledger.get("consumed", 0.0) + actual_consumption,
                                        "updatedAt": now
                                    },
                                    "$push": {
                                        "allocations": new_alloc
                                    },
                                    "$inc": {"version": 1}
                                },
                                session=session
                            )
                        
                        alloc_consumed += (already_consumed + actual_consumption)
                        remaining_needed -= (already_consumed + actual_consumption)
                        
            overall_consumed += alloc_consumed
            
        return overall_consumed


    async def log_rejected_leave_penalty(self, employee_code: str, approval_id: str, penalty_days: float):
        from bson import ObjectId
        from datetime import timezone
        
        app = await self.db.approvals.find_one({"_id": ObjectId(approval_id)})
        if not app:
            return
            
        emp_id = app.get("employeeId")
        rd = app.get("requestData", {})
        leave_type = rd.get("leaveType", "CL")
        
        from_date_str = rd.get("fromDate")
        if not from_date_str: return
        
        from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
        year = from_date.year
        
        ledger_base = await self.get_or_create_ledger(emp_id, employee_code, year, leave_type)
        if not ledger_base: return
        
        now = datetime.now(timezone.utc)
        
        async with await self.db.client.start_session() as session:
            async with session.start_transaction():
                ledger = await self.db.leave_ledgers.find_one({"_id": ledger_base["_id"]}, session=session)
                if not ledger: return
                
                # Idempotency check: Ensure penalty is not duplicated for the same request
                existing = [a for a in ledger.get("allocations", []) if str(a.get("approvalId")) == approval_id and a.get("type") == "REJECTED_ABSENCE_PENALTY"]
                if existing:
                    return
                
                alloc = {
                    "date": from_date_str,
                    "approvalId": approval_id,
                    "type": "REJECTED_ABSENCE_PENALTY",
                    "allocated": 0.0,
                    "penaltyDays": penalty_days,
                    "createdAt": now
                }
                
                await self.db.leave_ledgers.update_one(
                    {"_id": ledger["_id"]},
                    {
                        "$push": {"allocations": alloc},
                        "$inc": {"version": 1},
                        "$set": {"updatedAt": now}
                    },
                    session=session
                )
