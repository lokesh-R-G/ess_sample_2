with open('c:/ess/ess_sample_2/backend/app/attendance_v2/services/permission_ledger_service.py', 'r') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'def _calculate_ledger_state' in l:
        start_idx = i
    if 'return {' in l and 'employeeId' in lines[i+1]:
        end_idx = i
        break

new_method = '''    async def _calculate_ledger_state(self, emp_id: str, month_str: str, previous_carry: float) -> dict:
        # Get all approved permissions for this month
        # Since requestData is flexible, we might have date or romDate. We'll use regex on both for robustness.
        approvals = await self.db.approvals.find({
            "employeeId": emp_id,
            "approvalType": "Permission",
            "status": "APPROVED",
            "": [
                {"requestData.date": {"": f"^{month_str}"}},
                {"requestData.fromDate": {"": f"^{month_str}"}}
            ]
        }).to_list(length=None)

        # Sort chronologically by date/fromDate, then createdAt
        def get_date(app):
            rd = app.get("requestData", {})
            return rd.get("date") or rd.get("fromDate") or ""
        
        approvals.sort(key=lambda a: (get_date(a), a.get("createdAt", datetime.min)))

        consumed = 0.0
        total_requests = 0
        
        # We need to map minutes to permissions for allocation
        permission_minutes_map = []
        
        # Get policy limits
        policy = await self._get_policy_for_month(emp_id, month_str)
        free_allowance = 0.0
        carry_forward = False
        lop_threshold = 240
        lop_value = 0.5
        max_per_request = 60
        max_count = 2
        
        if policy:
            free_allowance = policy.get("monthlyPermissionHours", 1.0) * 60.0
            carry_forward = policy.get("permissionExcessCarryForward", True)
            lop_threshold = policy.get("permissionLopThresholdMinutes", 240)
            lop_value = policy.get("permissionLopValue", 0.5)
            max_per_request = policy.get("permissionMinutes", 60)
            max_count = policy.get("permissionPerMonth", 2)

        for app in approvals:
            rd = app.get("requestData", {})
            ft = rd.get("fromTime")
            tt = rd.get("toTime")
            if ft and tt:
                try:
                    f_dt = datetime.strptime(ft, "%H:%M")
                    t_dt = datetime.strptime(tt, "%H:%M")
                    mins = (t_dt - f_dt).total_seconds() / 60.0
                    if mins > 0:
                        total_requests += 1
                        consumed += mins
                        permission_minutes_map.append({
                            "permissionId": str(app["_id"]),
                            "leaveType": rd.get("conversionLeaveType"),
                            "mins": mins
                        })
                except Exception:
                    pass

        current_excess = max(0.0, consumed - free_allowance)
        
        accumulated_excess = previous_carry + current_excess
        
        lop_generated = 0.0
        remaining_carry = 0.0
        leave_converted_days = 0.0
        
        if carry_forward and lop_threshold > 0:
            lop_units = int(accumulated_excess // lop_threshold)
            initial_lop_generated = lop_units * lop_value
            
            if initial_lop_generated > 0:
                conversion_enabled = policy.get("permissionConversionEnabled", False) if policy else False
                
                if conversion_enabled:
                    # ALLOCATION ANALYSIS
                    allocations_dict = {}
                    
                    for unit in range(1, lop_units + 1):
                        crossing_minute = unit * lop_threshold
                        
                        if crossing_minute <= previous_carry:
                            alloc_key = "CARRY_FORWARD"
                            leave_type = None
                            perm_id = None
                        else:
                            target_perm_minute = (crossing_minute - previous_carry) + free_allowance
                            
                            current_perm_minute = 0
                            alloc_key = "UNKNOWN"
                            leave_type = None
                            perm_id = None
                            
                            for p in permission_minutes_map:
                                current_perm_minute += p["mins"]
                                if current_perm_minute >= target_perm_minute:
                                    perm_id = p["permissionId"]
                                    leave_type = p["leaveType"]
                                    alloc_key = perm_id
                                    break
                        
                        if alloc_key not in allocations_dict:
                            allocations_dict[alloc_key] = {
                                "permissionId": perm_id,
                                "leaveType": leave_type,
                                "amount": 0.0
                            }
                        allocations_dict[alloc_key]["amount"] += lop_value
                        
                    allocations = list(allocations_dict.values())
                    
                    from app.attendance_v2.services.leave_ledger_service import LeaveLedgerService
                    ledger_svc = LeaveLedgerService(self.db)
                    leave_converted_days = await ledger_svc.consume_for_permission(emp_id, month_str, allocations=allocations)
                    
                lop_generated = max(0.0, initial_lop_generated - leave_converted_days)
            
            remaining_carry = accumulated_excess % lop_threshold
        else:
            remaining_carry = 0.0 # If carry forward is disabled, we drop the excess

'''

lines = lines[:start_idx] + [new_method] + lines[end_idx:]

with open('c:/ess/ess_sample_2/backend/app/attendance_v2/services/permission_ledger_service.py', 'w') as f:
    f.writelines(lines)
print('Done!')
