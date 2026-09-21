from app.payroll.services.payroll_calculation_service import PayrollCalculationEngine

monthly_gross = 12000.0
# In the current implementation, workingDays is just calendar days (len of attendance)
working_days_current = 31.0
lop = 1.0

# Current behavior:
per_day_current = monthly_gross / working_days_current
gross_current = PayrollCalculationEngine.calculateMonthlyGross(monthly_gross, working_days_current, lop)

print(f"CURRENT BEHAVIOR:")
print(f"Working Days passed to engine: {working_days_current}")
print(f"Per day salary calculated: {per_day_current}")
print(f"LOP Deduction: {per_day_current * lop}")
print(f"Gross after LOP: {gross_current}")

# Expected behavior based on 26-day setting:
working_days_expected = 26.0
per_day_expected = monthly_gross / working_days_expected
gross_expected = monthly_gross - (per_day_expected * lop)

print(f"\nEXPECTED BEHAVIOR (26-day Divisor):")
print(f"Working Days: {working_days_expected}")
print(f"Per day salary calculated: {per_day_expected}")
print(f"LOP Deduction: {per_day_expected * lop}")
print(f"Gross after LOP: {gross_expected}")
