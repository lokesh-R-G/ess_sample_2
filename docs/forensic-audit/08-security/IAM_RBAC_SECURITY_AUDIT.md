# IAM and RBAC Forensic Audit

## 1. Authentication Architecture
- JWT-based bearer authentication.
- Password hashing using bcrypt.
- Roles: SUPER_ADMIN, ADMIN, EMPLOYEE, FLEET_MANAGER, STORE_MANAGER.

## 2. Forensic Findings

### Finding: SECURITY-001 (HIGH)
- **Vulnerability:** Broken Object Level Authorization (BOLA) in Document Retrieval.
- **Affected Endpoint:** /api/v1/employees/{id}/documents
- **Issue:** Endpoint does not strictly verify whether the requesting user owns the employee record or holds an administrative role for that specific company branch.
- **Impact:** Risk of unauthorized employee document access across organizational boundaries.

### Finding: SECURITY-002 (MEDIUM)
- **Vulnerability:** Unrestricted eSSL Machine Registration Endpoint.
- **Affected Route:** app/attendance/routes/essl_routes.py
- **Issue:** Machine heartbeat / sync endpoints accept incoming data payloads without requiring pre-shared machine HMAC authentication tokens.
