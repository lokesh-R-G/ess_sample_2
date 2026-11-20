# Investigation Methodology

## 1. Principles and Scope
This investigation is a complete historical reconstruction, architectural forensic audit, and white-box evaluation of ess_sample_2.
- Zero code modification of application business logic.
- Evidence-based analysis citing commit SHAs, file paths, line numbers, and empirical code references.
- Triangulation across Git revision history, backend FastAPI architecture, frontend React/Vite client structures, and MongoDB data models.

## 2. ReDerive Methodological Application
Using first-principles decomposition:
1. Reconstruct root intent: Employee Self Service (ESS), HRMS, Biometric (eSSL) attendance synchronization, dynamic payroll calculations, CTC revisions, and statutory compliance.
2. Trace divergence: Multiple competing backend folders, divergent route registrations, partial migrations, and duplicate calculation logic.
3. Classify defects across severity tiers: CRITICAL, HIGH, MEDIUM, LOW, and INFORMATIONAL.
