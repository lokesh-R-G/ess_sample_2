from typing import List, Dict, Any
from pydantic import BaseModel

class LopAggregationResult(BaseModel):
    totalLopDays: float = 0.0
    leaveLopDays: float = 0.0
    permissionLopDays: float = 0.0
    lateLopDays: float = 0.0
    earlyOutLopDays: float = 0.0
    absenceLopDays: float = 0.0
    otherLopDays: float = 0.0
    payableDays: float = 0.0
    workingDays: float = 0.0
    breakdown: List[Dict[str, Any]] = []

class LopAggregator:
    @staticmethod
    def aggregate_lop(attendance_records: List[Dict[str, Any]], hours_per_day: float = 8.0) -> LopAggregationResult:
        result = LopAggregationResult()
        
        for record in attendance_records:
            date_str = record.get("date")
            lop_reason = record.get("lopReason")
            
            # Explicit Leave LOP
            leave_lop = record.get("leaveLopDays", 0.0)
            if leave_lop > 0:
                result.leaveLopDays += leave_lop
                result.breakdown.append({"date": date_str, "type": "Leave", "days": leave_lop, "reason": lop_reason})
                
                # IMPORTANT: If leaveLopDays > 0, we completely ignore `lopHours` to prevent double counting
                continue

            # Permission LOP
            perm_lop_mins = record.get("permissionLopGenerated", 0.0)
            if perm_lop_mins > 0:
                perm_lop_days = perm_lop_mins / (hours_per_day * 60)
                result.permissionLopDays += perm_lop_days
                result.breakdown.append({"date": date_str, "type": "Permission", "days": perm_lop_days, "reason": "Excess Permission"})

            # Remaining LOP Hours
            lop_hours = record.get("lopHours", 0.0)
            if lop_hours > 0:
                lop_days = lop_hours / hours_per_day
                
                if not lop_reason:
                    result.otherLopDays += lop_days
                    result.breakdown.append({"date": date_str, "type": "Other", "days": lop_days, "reason": "Unknown"})
                elif "Late" in lop_reason:
                    result.lateLopDays += lop_days
                    result.breakdown.append({"date": date_str, "type": "Late", "days": lop_days, "reason": lop_reason})
                elif "Early Out" in lop_reason:
                    result.earlyOutLopDays += lop_days
                    result.breakdown.append({"date": date_str, "type": "EarlyOut", "days": lop_days, "reason": lop_reason})
                elif "Missing" in lop_reason or "Low Effective Hours" in lop_reason:
                    result.absenceLopDays += lop_days
                    result.breakdown.append({"date": date_str, "type": "Absence", "days": lop_days, "reason": lop_reason})
                else:
                    result.otherLopDays += lop_days
                    result.breakdown.append({"date": date_str, "type": "Other", "days": lop_days, "reason": lop_reason})
                    
        # Total LOP sum
        result.totalLopDays = (
            result.leaveLopDays + 
            result.permissionLopDays + 
            result.lateLopDays + 
            result.earlyOutLopDays + 
            result.absenceLopDays + 
            result.otherLopDays
        )
        
        # Determine working and payable days
        result.workingDays = len(attendance_records)
        result.payableDays = max(0.0, result.workingDays - result.totalLopDays)
        
        return result
