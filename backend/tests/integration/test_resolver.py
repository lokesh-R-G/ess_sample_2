import asyncio
from datetime import date
from app.db.mongo import get_database
from app.services.attendance_context_resolver import AttendanceContextResolver

async def f():
    db = get_database()
    resolver = AttendanceContextResolver(db)
    emp_code = "202201" # Employee UUID is 9dcf3954...
    target_date = date(2026, 8, 12)
    ctx = await resolver.resolve_context(emp_code, target_date)
    
    print("\n--- RESOLVED CONTEXT ---")
    if ctx:
        print("Approved Requests:", len(ctx.get("approvedRequests", [])))
        for req in ctx.get("approvedRequests", []):
            print(" -", req.get("approvalType"), req.get("requestData"))
    else:
        print("Context is None")

if __name__ == "__main__":
    asyncio.run(f())
