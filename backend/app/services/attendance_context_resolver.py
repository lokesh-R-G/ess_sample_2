from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, date, timedelta
from app.holiday_calendar.repositories.holiday_calendar_repository import HolidayCalendarRepository, HolidayDateRepository
from app.employee.repositories.employee_repository import EmployeeRepository
from app.attendance_policy.repositories.attendance_policy_repository import AttendancePolicyRepository
from app.attendance_policy.repositories.weekly_off_policy_repository import WeeklyOffPolicyRepository
from app.organization.repositories.shift_repository import ShiftRepository
from app.attendance_policy.models.weekly_off_policy import DayType
from datetime import timezone

class AttendanceContextResolver:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.holiday_calendar_repo = HolidayCalendarRepository(db)
        self.holiday_date_repo = HolidayDateRepository(db)
        self.employee_repo = EmployeeRepository(db)
        self.policy_repo = AttendancePolicyRepository(db)
        self.weekly_off_repo = WeeklyOffPolicyRepository(db)
        self.shift_repo = ShiftRepository(db)

    def resolve_today_schedule(self, weekly_off_policy, target_date: date) -> dict:
        """
        Resolves the specific DaySchedule for the target_date from the WeeklyOffPolicy.
        Returns a dict: {"dayType": ..., "startTime": ..., "endTime": ...}
        """
        if not weekly_off_policy:
            # Fallback to WORKING only if NO policy is configured on the shift
            return {"dayType": "WORKING", "startTime": None, "endTime": None}
            
        day_mapping = {
            0: weekly_off_policy.monday,
            1: weekly_off_policy.tuesday,
            2: weekly_off_policy.wednesday,
            3: weekly_off_policy.thursday,
            4: weekly_off_policy.friday,
            5: weekly_off_policy.saturday,
            6: weekly_off_policy.sunday,
        }
        
        weekday = target_date.weekday()
        day_schedule = day_mapping.get(weekday)
        
        if not day_schedule or not day_schedule.enabled:
            return {"dayType": "WORKING", "startTime": None, "endTime": None}
            
        return {
            "dayType": day_schedule.dayType.value,
            "startTime": day_schedule.startTime,
            "endTime": day_schedule.endTime
        }

    async def resolve_context(self, emp_id: str, target_date: date):
        """
        Resolves all necessary master data required for the PolicyEngine.
        1. Resolve Employee -> Employment -> Branch
        2. Resolve Employment -> Shift -> Attendance Policy
        3. Resolve Holiday Calendar and Dates for Branch
        4. Resolve Weekly Off (Temporary Sunday Resolver)
        """
        print(f"\nEmployee Code : {emp_id}")

        # 1. Resolve Employment using Employee Code
        employee = await self.employee_repo.get_by_employee_code(emp_id)
        if not employee:
            print("Employee Missing")
            print("Attendance Skipped")
            return None

        # Resolve ledger
        from app.attendance_v2.services.permission_ledger_service import PermissionLedgerService
        ledger_service = PermissionLedgerService(self.db)
        month_str = target_date.strftime("%Y-%m")
        # Ensure we pass employee.employeeId for ledger calculation if it uses UUID
        permission_ledger = await ledger_service.get_or_calculate_ledger(employee.employeeId, month_str)
            
        print(f"Employee UUID : {employee.employeeId}")

        employment_doc = await self.db.employee_employment_histories.find_one({
            "employeeId": employee.employeeId,
            "isCurrent": True,
            "deletedAt": None
        })
        
        if not employment_doc:
            print("Employment Missing")
            print("Attendance Skipped")
            return None
            
        print("Employment : FOUND")
        
        branch_id = employment_doc.get("branchId")
        shift_id = employment_doc.get("shiftId")
        shift_code = employment_doc.get("shiftCode")

        # 2. Resolve Shift
        shift = None
        policy = None
        weekly_off_policy = None
        target_dt_utc = datetime.combine(target_date, datetime.min.time(), tzinfo=timezone.utc)
        
        if shift_code:
            shift = await self.shift_repo.get_by_code_and_date("shiftCode", shift_code, target_dt_utc)
        if not shift and shift_id:
            shift = await self.shift_repo.get_by_id(shift_id)
            
        if shift:
            print(f"Shift : {shift.name}")
            
            # Resolve Attendance Policy
            att_pol_code = getattr(shift, "attendancePolicyCode", None)
            att_pol_id = getattr(shift, "attendancePolicyId", None)
            
            if att_pol_code:
                policy = await self.policy_repo.get_by_code_and_date("attendancePolicyCode", att_pol_code, target_dt_utc)
            if not policy and att_pol_id:
                policy = await self.policy_repo.get_by_id(att_pol_id)
                
            # Resolve Weekly Off Policy
            wo_pol_code = getattr(shift, "weeklyOffPolicyCode", None)
            wo_pol_id = getattr(shift, "weeklyOffPolicyId", None)
            
            if wo_pol_code:
                weekly_off_policy = await self.weekly_off_repo.get_by_code_and_date("weeklyOffPolicyCode", wo_pol_code, target_dt_utc)
            if not weekly_off_policy and wo_pol_id:
                weekly_off_policy = await self.weekly_off_repo.get_by_id(wo_pol_id)
                
            if not weekly_off_policy and wo_pol_id:
                raise ValueError(f"Shift configured with weeklyOffPolicyId {wo_pol_id} but policy not found")
            
        if not shift:
            print("Shift Missing")
            print("Attendance Skipped")
            return None

        # Do NOT fallback to global policy. Shift is the source of truth.
        if not policy:
            print("Attendance Policy Missing")
            print("Attendance Skipped")
            return None
            
        print(f"Attendance Policy : {policy.name}")

        # 3. Resolve Holiday Calendar
        holiday_dates = []
        calendar_id = None
        calendar_name = "None"
        if branch_id:
            # Get active calendar for branch matching the target year and effective date
            calendar_cursor = await self.db.holiday_calendars.find({
                "branchId": branch_id,
                "deletedAt": None,
                "year": target_date.year,
                "effectiveFrom": {"$lte": target_dt_utc},
                "$or": [
                    {"effectiveTo": None},
                    {"effectiveTo": {"$gt": target_dt_utc}}
                ]
            }).sort([("version", -1)]).to_list(length=1)
            
            if not calendar_cursor:
                # Fallback to the old logic just in case migration hasn't stamped effectiveFrom
                calendar_cursor = await self.db.holiday_calendars.find({
                    "branchId": branch_id,
                    "status": "Active",
                    "deletedAt": None,
                    "year": target_date.year
                }).to_list(length=1)
            
            if calendar_cursor:
                calendar = calendar_cursor[0]
                calendar_id = str(calendar["_id"])
                calendar_name = calendar.get("name", calendar_id)
                
                # Resolve Holiday Dates
                dates_cursor = await self.db.holiday_dates.find({
                    "calendarId": calendar_id,
                    "deletedAt": None,
                    "effectiveFrom": {"$lte": target_dt_utc},
                    "$or": [
                        {"effectiveTo": None},
                        {"effectiveTo": {"$gt": target_dt_utc}}
                    ]
                }).sort([("version", -1)]).to_list(length=None)
                
                if not dates_cursor:
                    dates_cursor = await self.db.holiday_dates.find({
                        "calendarId": calendar_id,
                        "status": "Active",
                        "deletedAt": None
                    }).to_list(length=None)
                    
                holiday_dates = dates_cursor
                
        print(f"Holiday Calendar : {calendar_name}")

        # 4. Resolve Weekly Off
        today_schedule = self.resolve_today_schedule(weekly_off_policy, target_date)
        print(f"Today Schedule : {today_schedule['dayType']}")
        
        # 5. Resolve Approvals for Phase 7
        target_iso = target_date.isoformat()
        # In a real implementation we might check range overlap. Here we check exact match on date string or isoformat
        # for simplicity since requestData structure can vary by approvalType.
        approvals_cursor = self.db.approvals.find({
            "employeeId": employee.employeeId,
            "status": "APPROVED"
        })
        approvals = await approvals_cursor.to_list(length=None)
        
        # Filter for today
        today_approvals = []
        for app in approvals:
            rd = app.get("requestData", {})
            d1 = rd.get("date", "")
            d2 = rd.get("punchTime", "")
            d3_from = rd.get("fromDate", "")
            d3_to = rd.get("toDate", "")
            
            # Helper to parse any date string to a date object
            def parse_date(d_str):
                if not d_str: return None
                try:
                    # Handles YYYY-MM-DD and ISO formats up to the 'T'
                    return datetime.fromisoformat(d_str.replace("Z", "+00:00")).date()
                except:
                    # Fallback for simple date strings
                    if len(d_str) >= 10:
                        try:
                            return datetime.strptime(d_str[:10], "%Y-%m-%d").date()
                        except:
                            pass
                return None

            match = False
            p_d1 = parse_date(d1)
            p_d2 = parse_date(d2)
            if (p_d1 and p_d1 == target_date) or (p_d2 and p_d2 == target_date):
                match = True
            else:
                p_from = parse_date(d3_from)
                p_to = parse_date(d3_to)
                if p_from and p_to and p_from <= target_date <= p_to:
                    match = True
            
            if match:
                # If Leave, fetch allocation
                if app.get("approvalType") == "Leave":
                    from app.attendance_v2.services.leave_ledger_service import LeaveLedgerService
                    ledger_service = LeaveLedgerService(self.db)
                    alloc = await ledger_service.get_daily_allocation(
                        emp_id=employee.employeeId, 
                        target_date_str=target_date.isoformat(), 
                        approval_id=str(app.get("_id"))
                    )
                    if alloc:
                        app["leaveAllocation"] = alloc
                        
                today_approvals.append(app)

        print(f"Approvals resolved : {len(today_approvals)}")
        # 6. Resolve Monthly Records for Late/Early Out Aggregation
        month_str = target_date.strftime("%Y-%m")
        monthly_cursor = self.db.attendance.find({
            "empId": emp_id,
            "date": {"$regex": f"^{month_str}"}
        })
        monthly_records = await monthly_cursor.to_list(length=None)
        
        # Calculate monthlyLateCount
        monthly_late_count = sum(
            1 for r in monthly_records 
            if r.get("lateMinutes", 0) > 0 and r.get("status") not in ["Holiday", "Week Off", "Leave", "On Duty", "Permission"]
        )

        # 7. Resolve Raw Punches for Target Date
        next_date = target_date + timedelta(days=1)
        start_dt = datetime.combine(target_date, datetime.min.time())
        end_dt = datetime.combine(next_date, datetime.min.time())
        
        logs_cursor = self.db.attendance_logs.find({
            "empId": emp_id,
            "timestamp": {"$gte": start_dt, "$lt": end_dt}
        }).sort([("timestamp", 1)])
        raw_punches = await logs_cursor.to_list(length=None)

        print("Policy Engine Executed")

        return {
            "employee": employee,
            "employment": employment_doc,
            "shift": shift,
            "policy": policy,
            "weeklyOffPolicy": weekly_off_policy,
            "branch": branch_id,
            "holidayCalendar": calendar_id,
            "holidayDates": holiday_dates,
            "todaySchedule": today_schedule,
            "approvedRequests": today_approvals,
            "monthlyRecords": monthly_records,
            "monthlyLateCount": monthly_late_count,
            "rawPunches": raw_punches,
            "permissionLedger": permission_ledger,
            "targetDate": target_date
        }
