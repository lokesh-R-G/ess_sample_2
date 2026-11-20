# Business Logic and Calculation Engine Audit

## 1. Scope of Domain Calculations
- **CTC Breakdown:** Basic, HRA, Special Allowance, PF (Employer/Employee), ESI (Employer/Employee), Gratuity, Professional Tax (PT).
- **Attendance LOP (Loss of Pay):** Contextual shift calculation vs actual punch times, grace period, and permission hours.
- **Leave Accrual & Balance:** Earned leave, Casual leave, Sick leave, and compensatory off tracking.

## 2. Audit Findings

### Finding: BUSINESS-001 (HIGH)
- **Affected Module:** CTC Revision Engine
- **Files:** src/utils/ctcCalculatorEngine.ts and app/payroll/services/salary_calculation_service.py
- **Issue:** Gratuity formula divergence:
  - Frontend formula uses (15 / 26) * Basic / 12
  - Certain backend formulas rounded basic salary prior to multiplier application.
- **Impact:** Discrepancy between the CTC revision displayed to HR admins and final persisted salary assignment.

### Finding: BUSINESS-002 (MEDIUM)
- **Affected Module:** Leave LOP Calculation
- **Issue:** LOP calculation in payroll run period handles month-end date boundaries inconsistently when February has 28 vs 29 days.
