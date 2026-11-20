# Frontend Forensic Audit

## Findings Summary

### Finding: FRONTEND-001 (HIGH)
- **Affected Module:** Payroll UI & CTC Revision
- **File:** src/pages/admin/payroll/CTCRevisionCalculator.tsx
- **Expected Behavior:** Strict synchrony between frontend preview calculations and backend persistence endpoints.
- **Actual Behavior:** Frontend independently computes EPF, ESI, and Gratuity using ctcCalculatorEngine.ts, which occasionally diverges from backend salary assignment schemas if configuration flags differ.
- **Confidence:** High

### Finding: FRONTEND-002 (MEDIUM)
- **Affected Module:** Navigation & Sidebar
- **File:** src/components/layout/Sidebar.tsx
- **Expected Behavior:** Dynamic menu items driven by user role and permissions.
- **Actual Behavior:** Several routes are hardcoded or commented out (e.g. commit 566c370: refactor: comment out unused navigation items in Sidebar component), leading to dead UI paths.
- **Confidence:** High
