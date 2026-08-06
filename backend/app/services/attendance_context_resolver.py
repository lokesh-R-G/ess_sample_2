from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, date
from app.holiday_calendar.repositories.holiday_calendar_repository import HolidayCalendarRepository, HolidayDateRepository
from app.employee.repositories.employee_repository import EmployeeRepository
from app.attendance_policy.repositories.attendance_policy_repository import AttendancePolicyRepository
from app.organization.repositories.shift_repository import ShiftRepository

class AttendanceContextResolver:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.holiday_calendar_repo = HolidayCalendarRepository(db)
        self.holiday_date_repo = HolidayDateRepository(db)
        self.employee_repo = EmployeeRepository(db)
        self.policy_repo = AttendancePolicyRepository(db)
        self.shift_repo = ShiftRepository(db)

    def resolve_weekoff(self, target_date: date) -> bool:
        """
        Temporary implementation.
        TODO:
        Replace with:
        Employee -> Employment -> Branch -> WeeklyOffPolicy
        """
        return target_date.weekday() == 6

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
        if shift_id:
            shift = await self.shift_repo.get_by_id(shift_id)
            if shift:
                print(f"Shift : {shift.name}")
                if getattr(shift, "attendancePolicyId", None):
                    policy = await self.policy_repo.get_by_id(shift.attendancePolicyId)
            
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
        weekly_off = self.resolve_weekoff(target_date)
        print(f"Weekly Off : {weekly_off}")
        print("Policy Engine Executed")

        return {
            "employee": employee,
            "employment": employment_doc,
            "shift": shift,
            "policy": policy,
            "branch": branch_id,
            "holidayCalendar": calendar_id,
            "holidayDates": holiday_dates,
            "weeklyOff": weekly_off
        }
