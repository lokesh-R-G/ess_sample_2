import asyncio
from app.db.mongo import get_database

async def f():
    db = get_database()
    emp = await db.employees.find_one({'employeeCode': '202201'})
    emp_id = emp['employeeId']
    h = await db.employee_employment_histories.find_one({'employeeId': emp_id, 'isCurrent': True})
    shift_code = h.get('shiftCode')
    shift = await db.shifts.find_one({'shiftCode': shift_code})
    print("Shift:", shift.get('name'))
    print("StartTime:", shift.get('startTime'))
    print("EndTime:", shift.get('endTime'))

if __name__ == "__main__":
    asyncio.run(f())
