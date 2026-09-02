import asyncio
import os
from datetime import datetime, timezone
from pprint import pprint

from motor.motor_asyncio import AsyncIOMotorClient
from app.services.attendance_context_resolver import AttendanceContextResolver
from app.services.policy_engine import PolicyEngine

async def main():
    client = AsyncIOMotorClient("mongodb+srv://lokeshca2004_db_user:sA6L0yL2zP0n3rA1@cluster0.o5h4w8s.mongodb.net/?retryWrites=true&w=majority")
    db = client.essl_production

    # Phase 2: Context Resolver
    print("--- Phase 2: Context Resolver Audit ---")
    resolver = AttendanceContextResolver(db)
    emp_id = "5188" # from previous context, Lokesh
    target_date = datetime(2026, 8, 1) # A Saturday
    
    ctx = await resolver.resolve_context(emp_id, target_date)
    print("Context returned:")
    for k, v in ctx.items():
        if v and hasattr(v, 'dict'):
            print(f"{k}: {v.dict()}")
        else:
            print(f"{k}: {v}")
            
    # Check if shift contains attendancePolicyId and weeklyOffPolicyId
    print("\n--- Phase 3: Shift Resolution ---")
    if ctx.get("shift"):
        shift = ctx.get("shift")
        print(f"Shift ID: {getattr(shift, 'id', getattr(shift, '_id', None))}")
        print(f"attendancePolicyId in Shift: {getattr(shift, 'attendancePolicyId', None)}")
        print(f"weeklyOffPolicyId in Shift: {getattr(shift, 'weeklyOffPolicyId', None)}")
    else:
        print("No shift resolved.")
        
    print("\n--- Phase 4: Weekly Off Policy Resolution ---")
    print(f"todaySchedule: {ctx.get('todaySchedule')}")
    
    print("\n--- Phase 5 & 6: Policy Engine Audit ---")
    # Simulate a Saturday CUTOFF
    engine = PolicyEngine(
        shift=ctx.get("shift"),
        policy=ctx.get("policy"),
        holiday_dates=ctx.get("holidayDates"),
        today_schedule=ctx.get("todaySchedule"),
        monthly_records=[],
        approved_requests=ctx.get("approvedRequests", [])
    )
    
    print(f"Engine todaySchedule initialized: {engine.today_schedule}")
    metrics = await engine.evaluate_attendance(emp_id, target_date, None, None)
    print(f"Metrics (Zero Punches): {metrics}")
    
    in_time = datetime(2026, 8, 1, 9, 15, tzinfo=timezone.utc)
    out_time = datetime(2026, 8, 1, 13, 0, tzinfo=timezone.utc)
    metrics_with_punches = await engine.evaluate_attendance(emp_id, target_date, in_time, out_time)
    print(f"Metrics (With Punches): {metrics_with_punches}")

if __name__ == "__main__":
    asyncio.run(main())
