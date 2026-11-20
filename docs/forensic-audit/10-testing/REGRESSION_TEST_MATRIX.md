# Regression Test Matrix

| ID | Test Scenario | Module | Expected Result | Regression Risk |
|---|---|---|---|---|
| REG-01 | CTC revision with PF wage ceiling cap | Payroll / CTC | PF capped at 1,800/mo | High |
| REG-02 | Leave cancellation after payroll run lock | Leave / Ledger | Reversal rejected or flagged | High |
| REG-03 | Biometric punch outside shift window | Attendance | Flagged as irregular punch | Medium |
| REG-04 | Dual backend route conflict | Gateway / Routing | Route collision or 404 | Critical |
