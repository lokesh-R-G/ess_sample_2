from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, date
from app.holiday_calendar.repositories.holiday_calendar_repository import HolidayCalendarRepository, HolidayDateRepository
from app.employee.repositories.employee_repository import EmployeeRepository
from app.attendance_policy.repositories.attendance_policy_repository import AttendancePolicyRepository
from app.attendance_policy.repositories.weekly_off_policy_repository import WeeklyOffPolicyRepository
from app.organization.repositories.shift_repository import ShiftRepository
from app.attendance_policy.models.weekly_off_policy import DayType

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
            return {"dayType": DayType.WORKING, "startTime": None, "endTime": None}
            
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
            return {"dayType": DayType.WORKING, "startTime": None, "endTime": None}
            
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

        # 2. Resolve Shift
        shift = None
        policy = None
        weekly_off_policy = None
        if shift_id:
            shift = await self.shift_repo.get_by_id(shift_id)
            if shift:
                print(f"Shift : {shift.name}")
                if getattr(shift, "attendancePolicyId", None):
                    policy = await self.policy_repo.get_by_id(shift.attendancePolicyId)
                if getattr(shift, "weeklyOffPolicyId", None):
                    weekly_off_policy = await self.weekly_off_repo.get_by_id(shift.weeklyOffPolicyId)
            
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
            # Get active calendar for branch matching the target year
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
            "employeeId": emp_id,
            "status": "APPROVED"
        })
        approvals = await approvals_cursor.to_list(length=None)
        
        # Filter for today
        today_approvals = []
        for app in approvals:
            rd = app.get("requestData", {})
            # If Leave, check fromDate/toDate overlap, else check date or punchTime
            # Simplistic check for demo:
            d1 = rd.get("date", "")
            d2 = rd.get("punchTime", "")
            d3_from = rd.get("fromDate", "")
            d3_to = rd.get("toDate", "")
            
            if target_iso in d1 or target_iso in d2:
                today_approvals.append(app)
            elif d3_from and d3_to and d3_from <= target_iso <= d3_to:
                today_approvals.append(app)

        print(f"Approvals resolved : {len(today_approvals)}")
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
            "approvedRequests": today_approvals
        }
