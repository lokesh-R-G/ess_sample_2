import sys
import os
import asyncio
from datetime import datetime, date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.mongo import get_database
from app.services.attendance_context_resolver import AttendanceContextResolver
from app.services.policy_engine import PolicyEngine

async def run_audit():
    db = get_database()
    resolver = AttendanceContextResolver(db)
    
    emp_code = "5188"
    target_date = date(2026, 8, 1) # Saturday CUTOFF
    
    print("="*50)
    print("FORENSIC ATTENDANCE AUDIT TRACE")
    print("="*50)
    
    # 1. MongoDB Actual Data
    print("\n--- 1. REAL MONGODB DATA ---")
    emp = await db.employees.find_one({"employeeCode": emp_code})
    if not emp:
        print(f"Employee {emp_code} not found. Using generic mock for trace.")
        return
        
    print(f"Employee Code: {emp_code}")
    print(f"Employee ID: {emp.get('_id')}")
    
    # Logs
    target_date_iso = target_date.isoformat()
    # Check for attendance logs in that day
    start_dt = datetime.strptime(f"{target_date_iso}T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
    end_dt = datetime.strptime(f"{target_date_iso}T23:59:59+00:00", "%Y-%m-%dT%H:%M:%S%z")
    
    logs_cursor = db.attendance_logs.find({"empId": emp_code, "timestamp": {"$gte": start_dt, "$lte": end_dt}})
    logs = await logs_cursor.to_list(length=100)
    print(f"\nFound {len(logs)} attendance_logs:")
    for log in logs:
        print(f"  - {log.get('_id')}: {log.get('timestamp')}")
        
    # Check attendance document
    att_doc = await db.attendance.find_one({"empId": emp_code, "date": target_date_iso})
    if att_doc:
        print(f"\nExisting Attendance Document:")
        print(f"  status: {att_doc.get('status')}")
        print(f"  lopHours: {att_doc.get('lopHours')}")
        print(f"  lateMinutes: {att_doc.get('lateMinutes')}")
        print(f"  earlyOutMinutes: {att_doc.get('earlyOutMinutes')}")
        print(f"  scheduleType: {att_doc.get('scheduleType')}")
        print(f"  actualStart: {att_doc.get('actualStartTime')}")
        print(f"  actualEnd: {att_doc.get('actualEndTime')}")
    else:
        print("\nNo attendance document found in DB.")
        
    print("\n--- 2. CONTEXT RESOLUTION TRACE ---")
    
    ctx = await resolver.resolve_context(emp_code, target_date)
    if not ctx:
        print("Failed to resolve context!")
        return
        
    shift = ctx.get("shift")
    wo_policy = ctx.get("weeklyOffPolicy")
    policy = ctx.get("policy")
    ts = ctx.get("todaySchedule")
    
    print(f"\nShift:")
    print(f"    Name = {getattr(shift, 'name', 'None')}")
    print(f"    start = {getattr(shift, 'startTime', 'None')}")
    print(f"    end = {getattr(shift, 'endTime', 'None')}")
    print(f"    W.O. ID = {getattr(shift, 'weeklyOffPolicyId', 'None')}")
    
    print(f"\nWeeklyOffPolicy:")
    print(f"    Name = {getattr(wo_policy, 'name', getattr(wo_policy, 'policyName', 'None'))}")
    
    print(f"\nTodaySchedule:")
    print(f"    dayType = {ts.get('dayType')}")
    print(f"    start = {ts.get('startTime')}")
    print(f"    end = {ts.get('endTime')}")
    
    print(f"\nAttendance Policy:")
    print(f"    Grace In: {getattr(policy, 'graceInMinutes', 0)}")
    print(f"    Grace Out: {getattr(policy, 'graceOutMinutes', 0)}")
    print(f"    Late Threshold: {getattr(policy, 'lateInThresholdMinutes', 15)}")
    print(f"    Early Out Threshold: {getattr(policy, 'earlyOutThresholdMinutes', 15)}")
    
    print("\n--- 3. ENGINE EXECUTION ---")
    
    if not logs:
        # Mock punches for trace
        ctx["rawPunches"] = [
            {"timestamp": datetime(2026, 8, 1, 9, 58, 15)},
            {"timestamp": datetime(2026, 8, 1, 17, 40, 33)}
        ]
    else:
        ctx["rawPunches"] = logs
        
    engine = PolicyEngine(ctx)
    metrics = engine.evaluate_attendance()
    
    print("\nEffective Schedule:")
    print(f"    Type = {engine.schedule.get('scheduleType')}")
    print(f"    Source = {engine.schedule.get('scheduleSource')}")
    print(f"    start = {engine.schedule.get('actualStartTime')}")
    print(f"    end = {engine.schedule.get('actualEndTime')}")
    
    print("\nCalculation:")
    print(f"    Late: {metrics.get('lateMinutes')}")
    print(f"    Early Out: {metrics.get('earlyOutMinutes')}")
    print(f"    Effective Hours: {metrics.get('effectiveHours')}")
    print(f"    LOP: {metrics.get('lopHours')}")
    print(f"    Final Status: {metrics.get('status')}")

if __name__ == "__main__":
    asyncio.run(run_audit())
