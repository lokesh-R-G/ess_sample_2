# Backend Forensic Audit

## Findings Summary

### Finding: BACKEND-001 (CRITICAL)
- **Affected Module:** Backend Architecture (/app vs /backend/app)
- **File:** pp/main.py vs ackend/app/main.py
- **Expected Behavior:** Single authoritative application entry point and modular structure.
- **Actual Behavior:** Duplicate application structures with diverging router registrations.
- **Technical Explanation:** /backend/app contains legacy and partially migrated modules while /app contains updated payroll v2 and leave ledger code. Running or deploying the incorrect root leads to 404s or stale business logic execution.
- **Confidence:** High (Verified via codebase directory audit)

### Finding: BACKEND-002 (HIGH)
- **Affected Module:** Attendance & eSSL Sync
- **File:** pp/attendance/services/essl_sync_service.py
- **Expected Behavior:** Resilient biometric sync with transactional rollback and network timeout handling.
- **Actual Behavior:** Fragile TCP/SOAP socket handling without proper retry backoff; unhandled connection dropouts freeze sync tasks.
- **Confidence:** High

### Finding: BACKEND-003 (HIGH)
- **Affected Module:** Payroll Calculation Engine
- **File:** pp/payroll/services/payroll_calculation_service.py
- **Expected Behavior:** Atomic calculation of salary slips with strict rounding and rounding-difference adjustment.
- **Actual Behavior:** Float-based arithmetic in legacy calculation paths produces 1-paise discrepancy when compared to integer/decimal implementations.
- **Confidence:** High
