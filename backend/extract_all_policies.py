import asyncio
from app.db.mongo import get_database

async def f():
    db = get_database()
    policies = await db.attendance_policies.find().to_list(None)
    for p in policies:
        print(f"Code: {p.get('attendancePolicyCode')} Version: {p.get('version')} Status: {p.get('status')} Effective: {p.get('effectiveFrom')} to {p.get('effectiveTo')}")
        print("graceInMinutes:", p.get("graceInMinutes"))
        print("graceOutMinutes:", p.get("graceOutMinutes"))
        print("lateInThresholdMinutes:", p.get("lateInThresholdMinutes"))
        print("lateIncrementThreshold:", p.get("lateIncrementThreshold"))
        print("lateHalfDayThreshold:", p.get("lateHalfDayThreshold"))
        print("lateFullDayThreshold:", p.get("lateFullDayThreshold"))
        print("permissionMinutes:", p.get("permissionMinutes"))
        print("permissionPerMonth:", p.get("permissionPerMonth"))
        print("monthlyPermissionHours:", p.get("monthlyPermissionHours"))
        print("permissionExcessCarryForward:", p.get("permissionExcessCarryForward"))
        print("permissionLopThresholdMinutes:", p.get("permissionLopThresholdMinutes"))
        print("permissionLopValue:", p.get("permissionLopValue"))
        print("minHoursForFullDay:", p.get("minHoursForFullDay"))
        print("minHoursForHalfDay:", p.get("minHoursForHalfDay"))
        print("lopHalfDayHours:", p.get("lopHalfDayHours"))
        print("lopFullDayHours:", p.get("lopFullDayHours"))
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(f())
