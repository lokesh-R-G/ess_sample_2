monthly_gross = 12000.0
lop_days = 1.0

# Current Implementation:
attendance_records_count = 31 # (Aug 2026)
current_divisor = attendance_records_count
current_daily = monthly_gross / current_divisor
current_lop_amount = current_daily * lop_days

print("CURRENT (Attendance derived):")
print(f"Divisor: {current_divisor}")
print(f"Daily Salary: {current_daily:.2f}")
print(f"LOP Amount: {current_lop_amount:.2f}")

# Expected Implementation based on Fixed 30 Days:
expected_divisor = 30.0
expected_daily = monthly_gross / expected_divisor
expected_lop_amount = expected_daily * lop_days

print("\nEXPECTED (Fixed 30 Days config):")
print(f"Divisor: {expected_divisor}")
print(f"Daily Salary: {expected_daily:.2f}")
print(f"LOP Amount: {expected_lop_amount:.2f}")
