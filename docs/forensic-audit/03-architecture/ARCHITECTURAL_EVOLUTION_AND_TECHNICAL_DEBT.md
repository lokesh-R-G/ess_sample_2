# Architectural Evolution and Technical Debt

## 1. Evolutionary Divergence
- **Initial Phase (Commits 1-40):** Basic CRUD scaffolding and generic components.
- **Expansion Phase (Commits 41-110):** Direct copy-pasting of backend services between /backend and /app rather than cleanly refactoring.
- **Patch Phase (Commits 111-200):** Ad-hoc bug fixes, e.g. 	estsmtp, 
ectified bug admin attendance page, HOLIDAY CALENDER BBUG PATCH FOR NON TRIGGRED.

## 2. Technical Debt Register
1. **Parallel Backend Trees:** /app and /backend/app create split truth.
2. **Duplicate Calculation Logic:** Frontend CTC calculator in src/utils/ctcCalculatorEngine.ts maintains independent business logic from backend payroll engines.
3. **Mock vs Production DB Inconsistency:** Multiple tests and tools rely on conflicting mongomock configurations.
4. **Scattered Audit and Migration Scripts:** Root directory contains ad-hoc scripts (ppend_frontend.py, stub_audit.py, phase_8_migration.py) that clutter production codebases.
