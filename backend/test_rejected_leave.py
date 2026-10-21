import asyncio
from datetime import datetime, date
from app.services.policy_engine import PolicyEngine

class DummyPolicy:
    lopFullDayHours = 8.0
    lopHalfDayHours = 4.0
    minHoursForFullDay = 8.0
    graceInMinutes = 0
    lateInThresholdMinutes = 15
    graceOutMinutes = 0
    earlyOutThresholdMinutes = 15

class DummyShift:
    startTime = "09:00:00"
    endTime = "18:00:00"

def get_base_ctx():
    return {
        "targetDate": date(2026, 10, 1),
        "policy": DummyPolicy(),
        "shift": DummyShift(),
        "holidayDates": [],
        "todaySchedule": {"dayType": "WORKING", "startTime": None, "endTime": None},
        "monthlyRecords": [],
        "approvedRequests": [],
        "rawPunches": [],
        "monthlyLateCount": 0,
        "leavePolicy": {"rejectedLeaveAbsentLopDays": 2.0}
    }

def print_result(name, metrics):
    print(f"--- {name} ---")
    print(f"status: {metrics.get('status')}")
    print(f"lopHours: {metrics.get('lopHours')}")
    print(f"rejectedLeaveLopDays: {metrics.get('rejectedLeaveLopDays', 0.0)}")
    print(f"lopReason: {metrics.get('lopReason')}")
    print(f"effectiveHours: {metrics.get('effectiveHours')}")
    print()

def run_tests():
    # A. Full-day APPROVED Leave + no punches
    ctx = get_base_ctx()
    ctx["approvedRequests"] = [{"_id": "1", "approvalType": "Leave", "status": "APPROVED", "requestData": {}}]
    engine = PolicyEngine(ctx)
    print_result("A. Full-day APPROVED Leave + no punches", engine.evaluate_attendance())

    # B. Full-day REJECTED Leave + no punches
    ctx = get_base_ctx()
    ctx["approvedRequests"] = [{"_id": "2", "approvalType": "Leave", "status": "REJECTED", "requestData": {}}]
    engine = PolicyEngine(ctx)
    print_result("B. Full-day REJECTED Leave + no punches", engine.evaluate_attendance())

    # C. Full-day REJECTED Leave + valid punches
    ctx = get_base_ctx()
    ctx["approvedRequests"] = [{"_id": "3", "approvalType": "Leave", "status": "REJECTED", "requestData": {}}]
    ctx["rawPunches"] = [{"timestamp": datetime(2026, 10, 1, 9, 0, 0)}, {"timestamp": datetime(2026, 10, 1, 18, 0, 0)}]
    engine = PolicyEngine(ctx)
    print_result("C. Full-day REJECTED Leave + valid punches", engine.evaluate_attendance())

    # D. Half-day REJECTED Leave + no punches
    ctx = get_base_ctx()
    ctx["approvedRequests"] = [{"_id": "4", "approvalType": "Leave", "status": "REJECTED", "requestData": {"fromTime": "14:00:00", "toTime": "18:00:00"}}]
    engine = PolicyEngine(ctx)
    print_result("D. Half-day REJECTED Leave + no punches", engine.evaluate_attendance())

    # E. Half-day REJECTED Leave + valid punches
    ctx = get_base_ctx()
    ctx["approvedRequests"] = [{"_id": "5", "approvalType": "Leave", "status": "REJECTED", "requestData": {"fromTime": "14:00:00", "toTime": "18:00:00"}}]
    ctx["rawPunches"] = [{"timestamp": datetime(2026, 10, 1, 9, 0, 0)}, {"timestamp": datetime(2026, 10, 1, 18, 0, 0)}]
    engine = PolicyEngine(ctx)
    print_result("E. Half-day REJECTED Leave + valid punches", engine.evaluate_attendance())

    # F. Rejected Leave + Holiday
    ctx = get_base_ctx()
    ctx["approvedRequests"] = [{"_id": "6", "approvalType": "Leave", "status": "REJECTED", "requestData": {}}]
    ctx["holidayDates"] = [{"holidayDate": date(2026, 10, 1)}]
    engine = PolicyEngine(ctx)
    print_result("F. Rejected Leave + Holiday", engine.evaluate_attendance())

    # G. Rejected Leave + Weekly Off
    ctx = get_base_ctx()
    ctx["approvedRequests"] = [{"_id": "7", "approvalType": "Leave", "status": "REJECTED", "requestData": {}}]
    ctx["todaySchedule"] = {"dayType": "WEEKOFF"}
    engine = PolicyEngine(ctx)
    print_result("G. Rejected Leave + Weekly Off", engine.evaluate_attendance())

if __name__ == "__main__":
    run_tests()
