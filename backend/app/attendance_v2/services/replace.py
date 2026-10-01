import sys

path = r"c:\ess\ess_sample_2\backend\app\attendance_v2\services\leave_ledger_service.py"
with open(path, "rb") as f:
    content = f.read().decode("utf-8")

target1 = """        else:
            credited = annual_entitlement

        ledger_doc = {"""

repl1 = """        else:
            credited = annual_entitlement

        renewal_deduction = 0.0
        total_absence = 0.0
        payroll_divisor = 0.0
        
        if doj:
            current_start, _ = await self._get_cycle_boundaries(cycle_year, doj, policy)
            doj_dt = datetime(doj.year, doj.month, doj.day, tzinfo=timezone.utc)
            if current_start > doj_dt:
                prev_year = cycle_year - 1
                prev_start, prev_end = await self._get_cycle_boundaries(prev_year, doj, policy)
                
                total_consumed = 0.0
                cursor = self.db.leave_ledgers.find({"employeeId": emp_id, "calendarYear": prev_year})
                async for l in cursor:
                    total_consumed += l.get("consumed", 0.0)
                    
                from app.payroll.services.lop_aggregator import LopAggregator
                att_cursor = self.db.attendance.find({
                    "employeeId": emp_id,
                    "date": {"$gte": prev_start.strftime("%Y-%m-%d"), "$lte": prev_end.strftime("%Y-%m-%d")}
                })
                att_records = [d async for d in att_cursor]
                lop_result = LopAggregator.aggregate_lop(att_records)
                total_lop = lop_result.totalLopDays
                
                total_absence = total_consumed + total_lop
                
                from app.payroll.repositories.payroll_settings_repository import PayrollSettingsRepository
                setting_repo = PayrollSettingsRepository(self.db)
                payroll_settings = await setting_repo.get_active_setting(prev_end.date())
                
                if payroll_settings:
                    calc_method = payroll_settings.defaultSalaryCalculationMethod
                    if calc_method == "Fixed 26 Days":
                        payroll_divisor = 26.0
                    elif calc_method == "Fixed 30 Days":
                        payroll_divisor = 30.0
                    elif calc_method in ["Calendar Days", "Working Days", "Attendance Based"]:
                        raise ValueError(f"Unresolved payroll divisor rule for annual renewal: {calc_method}")
                    else:
                        raise ValueError(f"Unknown salary calculation method: {calc_method}")
                        
                    if payroll_divisor > 0:
                        renewal_deduction = total_absence / payroll_divisor
                        credited = max(0.0, annual_entitlement - renewal_deduction)

        ledger_doc = {"""

target2 = """            "expired": 0.0,
            "lopDays": 0.0,
            "version": 1,"""

repl2 = """            "expired": 0.0,
            "lopDays": 0.0,
            "renewalDeduction": renewal_deduction,
            "totalAbsence": total_absence,
            "payrollDivisor": payroll_divisor,
            "version": 1,"""

target1_rn = target1.replace("\\n", "\\r\\n")
repl1_rn = repl1.replace("\\n", "\\r\\n")
target2_rn = target2.replace("\\n", "\\r\\n")
repl2_rn = repl2.replace("\\n", "\\r\\n")

if target1_rn in content:
    content = content.replace(target1_rn, repl1_rn)
elif target1 in content:
    content = content.replace(target1, repl1)
else:
    print("TARGET 1 NOT FOUND")
    sys.exit(1)

if target2_rn in content:
    content = content.replace(target2_rn, repl2_rn)
elif target2 in content:
    content = content.replace(target2, repl2)
else:
    print("TARGET 2 NOT FOUND")
    sys.exit(1)

with open(path, "wb") as f:
    f.write(content.encode("utf-8"))

print("SUCCESS")
