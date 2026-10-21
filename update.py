with open('c:/ess/ess_sample_2/backend/app/attendance_v2/services/leave_ledger_service.py', 'r') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'def consume_for_permission' in l:
        start_idx = i
    if 'def log_rejected_leave_penalty' in l:
        end_idx = i - 1
        break

new_method = '''    async def consume_for_permission(self, emp_id: str, month_str: str, days_needed: float = 0.0, allocations: list = None) -> float:
        if days_needed <= 0 and not allocations:
            return 0.0

        # We will attempt to consume from CL, then EL
        emp = await self.db.employees.find_one({"employeeId": emp_id})
        emp_code = emp.get("employeeCode", "UNKNOWN") if emp else "UNKNOWN"
        
        # Use the end of the month as the target date for resolution
        y, m = map(int, month_str.split("-"))
        import calendar
        last_day = calendar.monthrange(y, m)[1]
        target_date = date(y, m, last_day)
        
        now = datetime.now(timezone.utc)
        if target_date > now.date():
            target_date = now.date()
            
        target_date_str = target_date.isoformat()
        
        if allocations is None:
            allocations = [{"permissionId": None, "leaveType": None, "amount": days_needed}]
            
        overall_consumed = 0.0
        
        for alloc in allocations:
            perm_id = alloc.get("permissionId")
            leave_type = alloc.get("leaveType")
            amount_needed = alloc.get("amount", 0.0)
            
            if amount_needed <= 0:
                continue
                
            if not leave_type:
                leave_types = ["CL", "EL"]
                approval_id = f"permission_conversion_{month_str}"
            else:
                leave_types = [leave_type]
                approval_id = f"perm_conv_{perm_id}" if perm_id else f"permission_conversion_{month_str}"
                
            remaining_needed = amount_needed
            alloc_consumed = 0.0
            
            for lt in leave_types:
                if remaining_needed <= 0:
                    break
                    
                ledger_base = await self.get_or_create_ledger(emp_id, emp_code, target_date, lt)
                if not ledger_base:
                    continue
                    
                async with await self.db.client.start_session() as session:
                    async with session.start_transaction():
                        ledger = await self.db.leave_ledgers.find_one({"_id": ledger_base["_id"]}, session=session)
                        if not ledger:
                            continue
                            
                        existing_allocs = [a for a in ledger.get("allocations", []) if a.get("approvalId") == approval_id]
                        already_consumed = sum(a.get("allocated", 0.0) for a in existing_allocs)
                        
                        if already_consumed >= remaining_needed:
                            alloc_consumed += remaining_needed
                            remaining_needed = 0
                            break
                            
                        to_consume = remaining_needed - already_consumed
                        
                        balance = ledger.get("availableBalance", 0.0)
                        if balance <= 0:
                            alloc_consumed += already_consumed
                            remaining_needed -= already_consumed
                            continue
                            
                        actual_consumption = min(balance, to_consume)
                        if actual_consumption > 0:
                            new_alloc = {
                                "date": target_date_str,
                                "approvalId": approval_id,
                                "allocated": actual_consumption,
                                "lop": 0.0,
                                "createdAt": now
                            }
                            
                            await self.db.leave_ledgers.update_one(
                                {"_id": ledger["_id"]},
                                {
                                    "": {
                                        "availableBalance": balance - actual_consumption,
                                        "consumed": ledger.get("consumed", 0.0) + actual_consumption,
                                        "updatedAt": now
                                    },
                                    "": {
                                        "allocations": new_alloc
                                    },
                                    "": {"version": 1}
                                },
                                session=session
                            )
                        
                        alloc_consumed += (already_consumed + actual_consumption)
                        remaining_needed -= (already_consumed + actual_consumption)
                        
            overall_consumed += alloc_consumed
            
        return overall_consumed

'''

lines = lines[:start_idx] + [new_method] + lines[end_idx:]

with open('c:/ess/ess_sample_2/backend/app/attendance_v2/services/leave_ledger_service.py', 'w') as f:
    f.writelines(lines)
print('Done!')
