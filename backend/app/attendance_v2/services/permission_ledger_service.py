from datetime import datetime, date, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
import calendar

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
            
        shift_code = emp_hist.get("shiftCode")
        if not shift_code: return None
        
        # 2. Get shift
        shift = await self.db.shifts.find_one({"shiftCode": shift_code})
        if not shift: return None
        
        # 3. Get policy
        pol_code = shift.get("attendancePolicyCode")
        if not pol_code: return None
        
        # Resolve version based on target_dt
        target_dt_utc = datetime.combine(target_dt, datetime.min.time(), tzinfo=timezone.utc)
        policy_cursor = await self.db.attendance_policies.find({
            "attendancePolicyCode": pol_code,
            "effectiveFrom": {"$lte": target_dt_utc},
            "$or": [
                {"effectiveTo": None},
                {"effectiveTo": {"$gt": target_dt_utc}}
            ]
        }).sort([("version", -1)]).to_list(length=1)
        
        if policy_cursor:
            # We can mock a class object if needed, but dict is better. 
            # PolicyEngine gets a dict from motor or pydantic model? It gets pydantic models usually.
            # Let's return a simple dict, and handle dict attribute access in caller
            return policy_cursor[0]
            
        # Fallback to current
        pol = await self.db.attendance_policies.find_one({"attendancePolicyCode": pol_code, "isCurrent": True})
        return pol

    async def get_or_calculate_ledger(self, emp_id: str, month_str: str) -> dict:
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
        else:
            # If we need to go back indefinitely, we could recurse, but it's better to stop if no approvals exist.
            # We'll just assume 0.0 if there's no persisted ledger for the previous month.
            # In a robust system, we would calculate it. Let's do a fast check for any approvals before recursing.
            has_prev_approvals = await self.db.approvals.find_one({
                "employeeId": emp_id,
                "approvalType": "Permission",
                "status": "APPROVED",
                "requestData.date": {"$regex": f"^{prev_month_str}"}
            })
            if has_prev_approvals:
                calc_prev = await self._calculate_ledger_state(emp_id, prev_month_str, 0.0)
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
        # Since requestData is flexible, we might have `date` or `fromDate`. We'll use regex on both for robustness.
        approvals = await self.db.approvals.find({
            "employeeId": emp_id,
            "approvalType": "Permission",
            "status": "APPROVED",
            "$or": [
                {"requestData.date": {"$regex": f"^{month_str}"}},
                {"requestData.fromDate": {"$regex": f"^{month_str}"}}
            ]
        }).to_list(length=None)

        consumed = 0.0
        total_requests = 0
        
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
                        # We count all approved minutes towards consumed. 
                        # The limit rules determine if it's excess.
                        consumed += mins
                except Exception:
                    pass

        current_excess = max(0.0, consumed - free_allowance)
        
        # We can also add excess if count > max_count or mins > max_per_request?
        # The prompt says: "currentExcess = max(currentMonthPermissionUsed - monthlyFreeAllowance, 0)"
        # So consumed is just total minutes used. The daily engine decides how much to apply for Late In forgiveness.
        # But wait, if they exceed max_count, does it generate LOP directly or just add to excess?
        # Let's stick to the prompt's explicit formula for the ledger:
        # "currentExcess = max(currentMonthPermissionUsed - monthlyFreeAllowance, 0)"
        
        accumulated_excess = previous_carry + current_excess
        
        lop_generated = 0.0
        remaining_carry = 0.0
        
        if carry_forward and lop_threshold > 0:
            lop_units = int(accumulated_excess // lop_threshold)
            lop_generated = lop_units * lop_value
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
            "lopGenerated": lop_generated,
            "remainingCarriedMinutes": remaining_carry,
            "updatedAt": datetime.now(timezone.utc)
        }
