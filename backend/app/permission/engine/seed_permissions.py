import logging
from datetime import datetime
from typing import List, Dict, Any

from motor.motor_asyncio import AsyncIOMotorDatabase

# Define canonical permission catalog
CANONICAL_PERMISSIONS: List[Dict[str, Any]] = [
    # EMPLOYEE
    {"permissionId": "employee.read", "name": "Read Employee", "description": "Read employee data", "module": "employee", "action": "read"},
    {"permissionId": "employee.manage", "name": "Manage Employee", "description": "Create / update employee data", "module": "employee", "action": "manage"},
    # ATTENDANCE
    {"permissionId": "attendance.read", "name": "Read Attendance", "description": "Read attendance records", "module": "attendance", "action": "read"},
    {"permissionId": "attendance.manage", "name": "Manage Attendance", "description": "Create / update attendance records", "module": "attendance", "action": "manage"},
    {"permissionId": "attendance.sync", "name": "Sync Attendance", "description": "Synchronize attendance data", "module": "attendance", "action": "sync"},
    # LEAVE
    {"permissionId": "leave.read", "name": "Read Leave", "description": "Read leave information", "module": "leave", "action": "read"},
    {"permissionId": "leave.apply", "name": "Apply Leave", "description": "Apply for leave", "module": "leave", "action": "apply"},
    {"permissionId": "leave.manage", "name": "Manage Leave", "description": "Create / update leave policies", "module": "leave", "action": "manage"},
    {"permissionId": "leave.approve", "name": "Approve Leave", "description": "Approve leave requests", "module": "leave", "action": "approve"},
    # REIMBURSEMENT
    {"permissionId": "reimbursement.read", "name": "Read Reimbursement", "description": "Read reimbursement records", "module": "reimbursement", "action": "read"},
    {"permissionId": "reimbursement.create", "name": "Create Reimbursement", "description": "Create reimbursement claim", "module": "reimbursement", "action": "create"},
    {"permissionId": "reimbursement.manage", "name": "Manage Reimbursement", "description": "Manage reimbursement policies", "module": "reimbursement", "action": "manage"},
    {"permissionId": "reimbursement.approve", "name": "Approve Reimbursement", "description": "Approve reimbursement claims", "module": "reimbursement", "action": "approve"},
    # PAYROLL
    {"permissionId": "payroll.read", "name": "Read Payroll", "description": "Read payroll data", "module": "payroll", "action": "read"},
    {"permissionId": "payroll.salary.read", "name": "Read Salary", "description": "Read salary details", "module": "payroll", "action": "salary.read"},
    {"permissionId": "payroll.salary.manage", "name": "Manage Salary Configuration", "description": "Configure and finalize employee salary structure", "module": "payroll", "action": "salary.manage"},
    {"permissionId": "payroll.pf.read", "name": "Read PF", "description": "Read provident fund details", "module": "payroll", "action": "pf.read"},
    {"permissionId": "payroll.esi.read", "name": "Read ESI", "description": "Read employee state insurance details", "module": "payroll", "action": "esi.read"},
    {"permissionId": "payroll.branch_summary.read", "name": "Read Branch Summary", "description": "Read payroll summary per branch", "module": "payroll", "action": "branch_summary.read"},
    {"permissionId": "payroll.calculate", "name": "Calculate Payroll", "description": "Run payroll calculations", "module": "payroll", "action": "calculate"},
    {"permissionId": "payroll.publish", "name": "Publish Payroll", "description": "Publish payroll runs", "module": "payroll", "action": "publish"},
    {"permissionId": "payroll.cycle.read", "name": "Read Payroll Cycle", "description": "Read payroll cycle information", "module": "payroll", "action": "cycle.read"},
    {"permissionId": "payroll.cycle.manage", "name": "Manage Payroll Cycle", "description": "Create / update payroll cycles", "module": "payroll", "action": "cycle.manage"},
    # ORGANIZATION
    {"permissionId": "organization.read", "name": "Read Organization", "description": "Read organization details", "module": "organization", "action": "read"},
    {"permissionId": "organization.manage", "name": "Manage Organization", "description": "Create / update organization", "module": "organization", "action": "manage"},
    # POLICY
    {"permissionId": "policy.attendance.manage", "name": "Manage Attendance Policy", "description": "Manage attendance policies", "module": "policy", "action": "attendance.manage"},
    {"permissionId": "policy.leave.manage", "name": "Manage Leave Policy", "description": "Manage leave policies", "module": "policy", "action": "leave.manage"},
    {"permissionId": "policy.reimbursement.manage", "name": "Manage Reimbursement Policy", "description": "Manage reimbursement policies", "module": "policy", "action": "reimbursement.manage"},
    {"permissionId": "policy.weekly_off.manage", "name": "Manage Weekly Off Policy", "description": "Manage weekly off policies", "module": "policy", "action": "weekly_off.manage"},
    {"permissionId": "policy.shift.manage", "name": "Manage Shift Policy", "description": "Manage shift policies", "module": "policy", "action": "shift.manage"},
    # WORKFLOW
    {"permissionId": "workflow.read", "name": "Read Workflow", "description": "Read workflow definitions", "module": "workflow", "action": "read"},
    {"permissionId": "workflow.manage", "name": "Manage Workflow", "description": "Create / update workflows", "module": "workflow", "action": "manage"},
    {"permissionId": "workflow.approve", "name": "Approve Workflow", "description": "Approve workflow actions", "module": "workflow", "action": "approve"},
    # SCHEDULER
    {"permissionId": "scheduler.configure", "name": "Configure Scheduler", "description": "Configure automated jobs and schedules", "module": "scheduler", "action": "configure"},
    # ESSL
    {"permissionId": "essl.sync", "name": "Sync ESSL", "description": "Synchronize ESSL data", "module": "essl", "action": "sync"},
    {"permissionId": "essl.recovery_sync", "name": "Recovery Sync ESSL", "description": "Recover and sync ESSL data", "module": "essl", "action": "recovery_sync"},
    {"permissionId": "essl_machine.view", "name": "View ESSL Machine", "description": "View ESSL machine configuration", "module": "essl_machine", "action": "view"},
    {"permissionId": "essl_machine.manage", "name": "Manage ESSL Machine", "description": "Create and update ESSL machines", "module": "essl_machine", "action": "manage"}
]


async def seed_permissions(db: AsyncIOMotorDatabase | None = None) -> Dict[str, Any]:
    """Idempotently seed the canonical permission catalog.

    Returns a dict with counts of created, updated and any conflicts detected.
    """
    from app.db.mongo import get_database

    if db is None:
        db = get_database()

    created = 0
    updated = 0
    conflicts: List[Dict[str, Any]] = []

    for perm in CANONICAL_PERMISSIONS:
        now = datetime.utcnow()
        doc = {
            "permissionId": perm["permissionId"],
            "name": perm["name"],
            "description": perm.get("description"),
            "module": perm["module"],
            "action": perm["action"],
            "isActive": True,
            "version": 1,
            "createdAt": now,
            "updatedAt": now,
        }
        existing = await db.permissions.find_one({"permissionId": perm["permissionId"]})
        if existing:
            diff = {k: (existing.get(k), doc[k]) for k in ["name", "description", "module", "action", "isActive", "version"] if existing.get(k) != doc[k]}
            if diff:
                conflicts.append({"permissionId": perm["permissionId"], "diff": diff})
                continue
        else:
            await db.permissions.insert_one(doc)
            created += 1

    return {"created": created, "updated": updated, "conflicts": conflicts}

if __name__ == "__main__":
    import asyncio
    import sys
    from app.db.mongo import get_database

    async def main():
        db = get_database()
        result = await seed_permissions(db)
        print("Seed result:", result)
        if result["conflicts"]:
            sys.exit(1)

    asyncio.run(main())
