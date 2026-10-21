valid_transitions = {
    "DRAFT": ["OPEN", "ATTENDANCE_FINALIZED"],
    "OPEN": ["APPROVAL_PENDING", "ATTENDANCE_FINALIZED"],
    "APPROVAL_PENDING": ["APPROVAL_LOCKED"],
    "APPROVAL_LOCKED": ["ATTENDANCE_FINALIZED"],
    "ATTENDANCE_FINALIZED": ["PROCESSING"],
    "PROCESSING": ["CALCULATED", "DRAFT"],
    "CALCULATED": ["ADMIN_REVIEW"],
    "ADMIN_REVIEW": ["FINALIZED", "PROCESSING"],
    "FINALIZED": ["PUBLISHED"],
    "PUBLISHED": ["EXPORTED", "CLOSED"],
    "EXPORTED": ["CLOSED"]
}

fast_path = [
    ("DRAFT","OPEN"),
    ("OPEN","ATTENDANCE_FINALIZED"),
    ("ATTENDANCE_FINALIZED","PROCESSING"),
    ("PROCESSING","CALCULATED"),
    ("CALCULATED","ADMIN_REVIEW"),
    ("ADMIN_REVIEW","FINALIZED"),
    ("FINALIZED","PUBLISHED"),
]

approval_path = [
    ("DRAFT","OPEN"),
    ("OPEN","APPROVAL_PENDING"),
    ("APPROVAL_PENDING","APPROVAL_LOCKED"),
    ("APPROVAL_LOCKED","ATTENDANCE_FINALIZED"),
    ("ATTENDANCE_FINALIZED","PROCESSING"),
    ("PROCESSING","CALCULATED"),
]

print("=== Fast-path (no approval sub-workflow) ===")
all_ok = True
for s, d in fast_path:
    ok = d in valid_transitions.get(s, [])
    status = "OK" if ok else "FAIL"
    print("  " + s + " -> " + d + ": " + status)
    if not ok:
        all_ok = False

print()
print("=== Approval sub-path ===")
for s, d in approval_path:
    ok = d in valid_transitions.get(s, [])
    status = "OK" if ok else "FAIL"
    print("  " + s + " -> " + d + ": " + status)
    if not ok:
        all_ok = False

print()
print("Previously broken: OPEN -> ATTENDANCE_FINALIZED")
was_broken = "ATTENDANCE_FINALIZED" not in ["APPROVAL_PENDING"]   # old map
now_fixed  = "ATTENDANCE_FINALIZED" in valid_transitions["OPEN"]
print("  Before fix: FAIL")
print("  After fix: " + ("OK" if now_fixed else "STILL BROKEN"))
print()
print("All transitions: " + ("ALL PASS" if all_ok else "FAILURES DETECTED"))
