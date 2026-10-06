from datetime import datetime, date, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
import calendar
from fastapi import HTTPException
from bson import ObjectId

class PermissionLedgerService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def _get_policy_for_month(self, emp_id: str, month_str: str):
        # Query the DB directly to prevent circular dependency with ContextResolver
        # 1. Get employment
        emp_hist = await self.db.employee_employment_histories.find_one({
            "employeeId": emp_id,
            "isCurrent": True,
            "deletedAt": None
        })
        if not emp_hist: return None
        
        y, m = map(int, month_str.split('-'))
        import calendar
        last_day = calendar.monthrange(y, m)[1]
        target_dt = date(y, m, last_day)
        now = datetime.now(timezone.utc).date()
        if now.year == y and now.month == m:
            target_dt = now
            
        shift_id = emp_hist.get("shiftId")
        shift_code = emp_hist.get("shiftCode")
        
        # 2. Get shift
        shift = None
        if shift_id and ObjectId.is_valid(shift_id):
            shift = await self.db.shifts.find_one({"_id": ObjectId(shift_id)})
            
        if not shift and shift_code:
            shift = await self.db.shifts.find_one({"shiftCode": shift_code})
            
        if not shift: return None
        
        # 3. Get policy
        pol_id = shift.get("attendancePolicyId")
        pol_code = shift.get("attendancePolicyCode")
        
        pol_query_base = None
        if pol_id and ObjectId.is_valid(pol_id):
            pol_query_base = {"_id": ObjectId(pol_id)}
        elif pol_code:
            pol_query_base = {"attendancePolicyCode": pol_code}
            
        if not pol_query_base: return None
        
        # Resolve version based on target_dt
        target_dt_utc = datetime.combine(target_dt, datetime.min.time(), tzinfo=timezone.utc)
        
        policy_query = pol_query_base.copy()
        policy_query["effectiveFrom"] = {"$lte": target_dt_utc}
        policy_query["$or"] = [
            {"effectiveTo": None},
            {"effectiveTo": {"$gt": target_dt_utc}}
        ]
        
        policy_cursor = await self.db.attendance_policies.find(policy_query).sort([("version", -1)]).to_list(length=1)
        
        if policy_cursor:
            # We can mock a class object if needed, but dict is better. 
            # PolicyEngine gets a dict from motor or pydantic model? It gets pydantic models usually.
            # Let's return a simple dict, and handle dict attribute access in caller
            return policy_cursor[0]
            
        # Fallback to current
        fallback_query = pol_query_base.copy()
        fallback_query["isCurrent"] = True
        pol = await self.db.attendance_policies.find_one(fallback_query)
        return pol

    async def get_or_calculate_ledger(self, emp_id: str, month_str: str, depth: int = 0) -> dict:
        """
        Dynamically calculates the ledger for the given month from the source of truth.
        """
        y, m = map(int, month_str.split('-'))
        
        # 1. Calculate previous month's ledger to get carry forward
        prev_m = m - 1
        prev_y = y
        if prev_m == 0:
            prev_m = 12
            prev_y -= 1
        prev_month_str = f"{prev_y:04d}-{prev_m:02d}"
        
        # Avoid deep recursion by only going back to a certain limit or if ledger exists in DB
        # For performance, we'll try to read previous month from DB first. If it doesn't exist, we calculate it.
        prev_ledger = await self.db.permission_ledgers.find_one({
            "employeeId": emp_id,
            "month": prev_month_str
        })
        
        previous_carry = 0.0
        if prev_ledger:
            previous_carry = prev_ledger.get("remainingCarriedMinutes", 0.0)
        elif depth < 12:
            # If we need to go back indefinitely, we could recurse, but it's better to stop if no approvals exist.
            # We'll just assume 0.0 if there's no persisted ledger for the previous month.
            # In a robust system, we would calculate it. Let's do a fast check for any approvals before recursing.
            has_prev_approvals = await self.db.approvals.find_one({
                "employeeId": emp_id,
                "approvalType": "Permission",
                "status": "APPROVED",
                "$or": [
                    {"requestData.date": {"$regex": f"^{prev_month_str}"}},
                    {"requestData.fromDate": {"$regex": f"^{prev_month_str}"}}
                ]
            })
            if has_prev_approvals:
                calc_prev = await self.get_or_calculate_ledger(emp_id, prev_month_str, depth + 1)
                previous_carry = calc_prev.get("remainingCarriedMinutes", 0.0)

        # 2. Calculate current month
        ledger_state = await self._calculate_ledger_state(emp_id, month_str, previous_carry)
        
        # 3. Persist the updated ledger state
        await self.db.permission_ledgers.update_one(
            {"employeeId": emp_id, "month": month_str},
            {"$set": ledger_state},
            upsert=True
        )
        return ledger_state

    async def _calculate_ledger_state(self, emp_id: str, month_str: str, previous_carry: float) -> dict:
        # Get all approved permissions for this month
        # Since requestData is flexible, we might have date or romDate. We'll use regex on both for robustness.
        approvals = await self.db.approvals.find({
            "employeeId": emp_id,
            "approvalType": "Permission",
            "status": "APPROVED",
            "$or": [
                {"requestData.date": {"$regex": f"^{month_str}"}},
                {"requestData.fromDate": {"$regex": f"^{month_str}"}}
            ]
        }).to_list(length=None)

        # Sort chronologically by date/fromDate, then createdAt
        def get_date(app):
            rd = app.get("requestData", {})
            return rd.get("date") or rd.get("fromDate") or ""
        
        approvals.sort(key=lambda a: (get_date(a), a.get("createdAt", datetime.min)))

        consumed = 0.0
        total_requests = 0
        
        # We need to map minutes to permissions for allocation
        permission_minutes_map = []
        
        # Get policy limits
        policy = await self._get_policy_for_month(emp_id, month_str)
        free_allowance = 0.0
        carry_forward = False
        lop_threshold = 240
        lop_value = 0.5
        max_per_request = 60
        max_count = 2
        
        if policy:
            free_allowance = policy.get("monthlyPermissionHours", 1.0) * 60.0
            carry_forward = policy.get("permissionExcessCarryForward", True)
            lop_threshold = policy.get("permissionLopThresholdMinutes", 240)
            lop_value = policy.get("permissionLopValue", 0.5)
            max_per_request = policy.get("permissionMinutes", 60)
            max_count = policy.get("permissionPerMonth", 2)

        for app in approvals:
            rd = app.get("requestData", {})
            ft = rd.get("fromTime")
            tt = rd.get("toTime")
            if ft and tt:
                try:
                    f_dt = datetime.strptime(ft, "%H:%M")
                    t_dt = datetime.strptime(tt, "%H:%M")
                    mins = (t_dt - f_dt).total_seconds() / 60.0
                    if mins > 0:
                        total_requests += 1
                        consumed += mins
                        permission_minutes_map.append({
                            "permissionId": str(app["_id"]),
                            "leaveType": rd.get("conversionLeaveType"),
                            "mins": mins
                        })
                except Exception:
                    pass

        current_excess = max(0.0, consumed - free_allowance)
        
        accumulated_excess = previous_carry + current_excess
        
        lop_generated = 0.0
        remaining_carry = 0.0
        leave_converted_days = 0.0
        
        if carry_forward and lop_threshold > 0:
            lop_units = int(accumulated_excess // lop_threshold)
            initial_lop_generated = lop_units * lop_value
            
            if initial_lop_generated > 0:
                conversion_enabled = policy.get("permissionConversionEnabled", False) if policy else False
                
                if conversion_enabled:
                    # ALLOCATION ANALYSIS
                    allocations_dict = {}
                    
                    for unit in range(1, lop_units + 1):
                        crossing_minute = unit * lop_threshold
                        
                        if crossing_minute <= previous_carry:
                            alloc_key = "CARRY_FORWARD"
                            leave_type = None
                            perm_id = None
                        else:
                            target_perm_minute = (crossing_minute - previous_carry) + free_allowance
                            
                            current_perm_minute = 0
                            alloc_key = "UNKNOWN"
                            leave_type = None
                            perm_id = None
                            
                            for p in permission_minutes_map:
                                current_perm_minute += p["mins"]
                                if current_perm_minute >= target_perm_minute:
                                    perm_id = p["permissionId"]
                                    leave_type = p["leaveType"]
                                    alloc_key = perm_id
                                    break
                        
                        if alloc_key not in allocations_dict:
                            allocations_dict[alloc_key] = {
                                "permissionId": perm_id,
                                "leaveType": leave_type,
                                "amount": 0.0
                            }
                        allocations_dict[alloc_key]["amount"] += lop_value
                        
                    allocations = list(allocations_dict.values())
                    
                    from app.attendance_v2.services.leave_ledger_service import LeaveLedgerService
                    ledger_svc = LeaveLedgerService(self.db)
                    leave_converted_days = await ledger_svc.consume_for_permission(emp_id, month_str, allocations=allocations)
                    
                lop_generated = max(0.0, initial_lop_generated - leave_converted_days)
            
            remaining_carry = accumulated_excess % lop_threshold
        else:
            remaining_carry = 0.0 # If carry forward is disabled, we drop the excess

        return {
            "employeeId": emp_id,
            "month": month_str,
            "freeAllowanceMinutes": free_allowance,
            "consumedMinutes": consumed,
            "currentExcessMinutes": current_excess,
            "previousCarriedMinutes": previous_carry,
            "accumulatedExcessMinutes": accumulated_excess,
            "leaveConvertedDays": leave_converted_days,
            "lopGenerated": lop_generated,
            "remainingCarriedMinutes": remaining_carry,
            "updatedAt": datetime.now(timezone.utc)
        }

    async def validate_permission_limit(self, emp_id: str, month_str: str, requested_minutes: float, exclude_approval_id: str = None):
        """
        Validates whether the requested permission duration exceeds the configured maxPermissionHoursPerMonth limit.
        Counts both APPROVED and PENDING permissions, except for exclude_approval_id.
        Raises HTTPException 400 if exceeded.
        """
        policy = await self._get_policy_for_month(emp_id, month_str)
        if not policy:
            return
            
        max_hours = policy.get("maxPermissionHoursPerMonth")
        if max_hours is None:
            return
            
        max_minutes = max_hours * 60.0
        
        query = {
            "employeeId": emp_id,
            "approvalType": "Permission",
            "status": {"$in": ["APPROVED", "PENDING"]},
            "$or": [
                {"requestData.date": {"$regex": f"^{month_str}"}},
                {"requestData.fromDate": {"$regex": f"^{month_str}"}}
            ]
        }
        if exclude_approval_id:
            from bson import ObjectId
            if isinstance(exclude_approval_id, str) and len(exclude_approval_id) == 24:
                query["_id"] = {"$ne": ObjectId(exclude_approval_id)}
            else:
                query["_id"] = {"$ne": exclude_approval_id}
            
        approvals = await self.db.approvals.find(query).to_list(length=None)
        
        consumed = 0.0
        for app in approvals:
            rd = app.get("requestData", {})
            ft = rd.get("fromTime")
            tt = rd.get("toTime")
            if ft and tt:
                try:
                    f_dt = datetime.strptime(ft, "%H:%M")
                    t_dt = datetime.strptime(tt, "%H:%M")
                    mins = (t_dt - f_dt).total_seconds() / 60.0
                    if mins > 0:
                        consumed += mins
                except Exception:
                    pass
                    
        total_after_request = consumed + requested_minutes
        
        if total_after_request > max_minutes:
            remaining_mins = max(0.0, max_minutes - consumed)
            remaining_hours = remaining_mins / 60.0
            if remaining_hours <= 0:
                raise HTTPException(status_code=400, detail=f"You have reached your monthly permission limit of {max_hours:g} hours.")
            else:
                # Format remaining hours nicely, e.g. 1.5
                formatted_remaining = f"{remaining_hours:g}"
                raise HTTPException(status_code=400, detail=f"You can only avail {formatted_remaining} more permission hours this month.")
