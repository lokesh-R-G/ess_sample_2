import asyncio
from datetime import date
from app.db.mongo import get_database
from app.services.attendance_context_resolver import AttendanceContextResolver
from app.services.policy_engine import PolicyEngine

async def f():
    db = get_database()
    resolver = AttendanceContextResolver(db)
    emp_code = "202201" # Employee UUID is 9dcf3954...
    target_date = date(2026, 8, 12)
    ctx = await resolver.resolve_context(emp_code, target_date)
    
    if ctx:
        engine = PolicyEngine(ctx)
        metrics = engine.evaluate_attendance()
        print("\n--- METRICS ---")
        for k, v in metrics.items():
            print(f"{k}: {v}")
    else:
        print("Context is None")

if __name__ == "__main__":
    asyncio.run(f())
