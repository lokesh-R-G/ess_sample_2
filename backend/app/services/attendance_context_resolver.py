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
        # 1. Resolve Employment
        employee = await self.employee_repo.get_by_employee_id(emp_id)
        if not employee:
            return None

        employment_doc = await self.db.employee_employment_histories.find_one({
            "employeeId": emp_id,
            "isCurrent": True,
            "deletedAt": None
        })
        
        branch_id = employment_doc.get("branchId") if employment_doc else None
        shift_id = employment_doc.get("shiftId") if employment_doc else None

        # 2. Resolve Shift
        shift = None
        policy = None
        if shift_id:
            shift = await self.shift_repo.get_by_id(shift_id)
            if shift and getattr(shift, "attendancePolicyId", None):
                policy = await self.policy_repo.get_by_id(shift.attendancePolicyId)

        # Fallback to active policy if not found from shift
        if not policy:
            policy = await self.policy_repo.get_active_policy()

        # 3. Resolve Holiday Calendar
        holiday_dates = []
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
                
                # 3. Resolve Holiday Dates
                dates_cursor = await self.db.holiday_dates.find({
                    "calendarId": calendar_id,
                    "status": "Active",
                    "deletedAt": None
                }).to_list(length=None)
                
                holiday_dates = dates_cursor

        # 4. Resolve Weekly Off
        weekly_off = self.resolve_weekoff(target_date)

        return {
            "employee": employee,
            "employment": employment_doc,
            "shift": shift,
            "policy": policy,
            "branch": branch_id,
            "holidayCalendar": calendar_id if branch_id and calendar_cursor else None,
            "holidayDates": holiday_dates,
            "weeklyOff": weekly_off
        }
