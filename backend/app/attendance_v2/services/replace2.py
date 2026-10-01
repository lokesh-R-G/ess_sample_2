import sys

path = r"c:\ess\ess_sample_2\backend\app\attendance_v2\services\leave_ledger_service.py"
with open(path, "rb") as f:
    content = f.read().decode("utf-8")

target = """            "expired": 0.0,
            "lopDays": 0.0,
            "version": 1,
            "createdAt": now,
            "updatedAt": now,
            "allocations": []
        }"""

replacement = """            "expired": 0.0,
            "lopDays": 0.0,
            "renewalDeduction": renewal_deduction,
            "totalAbsence": total_absence,
            "payrollDivisor": payroll_divisor,
            "version": 1,
            "createdAt": now,
            "updatedAt": now,
            "allocations": []
        }"""

target_rn = target.replace("\n", "\r\n")
repl_rn = replacement.replace("\n", "\r\n")

if target_rn in content:
    content = content.replace(target_rn, repl_rn)
elif target in content:
    content = content.replace(target, replacement)
else:
    print("NOT FOUND")
    sys.exit(1)

with open(path, "wb") as f:
    f.write(content.encode("utf-8"))
print("SUCCESS")
