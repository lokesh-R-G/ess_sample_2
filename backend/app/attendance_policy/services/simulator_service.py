from typing import Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..schemas.simulator import SimulationRequest, SimulationResponse

class SimulationEngine:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def simulate(self, req: SimulationRequest) -> SimulationResponse:
        trace = []
        trace.append(f"Starting simulation for Employee {req.employeeId}")
        trace.append(f"Scheduled: {req.scheduledIn} to {req.scheduledOut}")
        trace.append(f"Actual: {req.actualIn} to {req.actualOut}")
        
        # Calculate diffs
        in_diff = (req.actualIn - req.scheduledIn).total_seconds() / 60
        out_diff = (req.scheduledOut - req.actualOut).total_seconds() / 60
        
        grace_used = 0
        late_mins = 0
        grace_approved = False
        status = "Present"
        
        trace.append("Checking Grace Policy...")
        if in_diff > 0:
            if in_diff <= 15: # Dummy grace window
                grace_used = int(in_diff)
                trace.append(f"Punched inside grace window ({grace_used} mins).")
                grace_approved = False  # requires manual approval usually
                if not grace_approved:
                    late_mins = grace_used
                    trace.append("Grace not approved yet. Marking as Late.")
            else:
                late_mins = int(in_diff)
                trace.append(f"Punched outside grace. Late by {late_mins} mins.")
        
        late_count = req.currentLateCount
        if late_mins > 0:
            late_count += 1
            status = "Late"
            trace.append(f"Late count incremented to {late_count}.")
            
        # Permission logic
        trace.append("Checking Permission Policy...")
        perm_used = req.permissionRequestedMinutes
        perm_remaining = req.currentPermissionBalanceMinutes
        perm_overflow = 0
        
        if perm_used > 0:
            trace.append(f"Permission requested: {perm_used} mins.")
            if perm_used > perm_remaining:
                perm_overflow = perm_used - perm_remaining
                perm_remaining = 0
                trace.append(f"Permission overflow recorded: {perm_overflow} mins.")
            else:
                perm_remaining -= perm_used
                trace.append(f"Permission balance remaining: {perm_remaining} mins.")
                
        # Penalty calculation
        leave_deduction = 0.0
        penalty = "None"
        if late_count >= 3:
            leave_deduction = 0.5
            penalty = "Half Day Leave Deducted (Late Threshold Reached)"
            trace.append(penalty)
        if perm_overflow > 60:
            leave_deduction += 0.5
            penalty = "Half Day Leave Deducted (Permission Overflow)"
            trace.append(penalty)
            
        trace.append(f"Final Status: {status}")
            
        return SimulationResponse(
            graceUsedMinutes=grace_used,
            graceApproved=grace_approved,
            lateMinutes=late_mins,
            lateCountAfterCalculation=late_count,
            permissionUsedMinutes=perm_used,
            permissionRemainingMinutes=perm_remaining,
            permissionOverflowMinutes=perm_overflow,
            leaveDeduction=leave_deduction,
            penaltyApplied=penalty,
            attendanceStatus=status,
            calculationTrace=trace
        )
