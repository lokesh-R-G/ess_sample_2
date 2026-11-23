# 04. API Integration & Network Architecture

## 1. Host Resolution & Android Emulator Network
In Android development, `localhost` or `127.0.0.1` inside the Android environment refers to the device itself.
- For **Android Emulator**, the host machine's loopback is `http://10.0.2.2:8000/api`.
- For **Physical Android Devices**, the workstation's local area network IP (e.g. `http://192.168.1.x:8000/api`) is used.
- The mobile API client dynamically reads this from configuration or an in-app developer switch, defaulting to `http://10.0.2.2:8000/api`.

---

## 2. API Client Architecture (`src/api/client.ts`)
The mobile API client standardizes:
1. **Bearer Token Injection:** Automatically attaches `Authorization: Bearer <token>` from secure storage.
2. **Error Normalization:** Parses backend responses (`detail` string or validation arrays) into clean `ApiError` instances.
3. **Session Expiry (401) Interception:** Triggers automatic logout and redirects to Login screen on token expiration.
4. **Timeout Handling:** Ensures requests do not hang indefinitely on unstable mobile connections.

---

## 3. Endpoints Mapping

### 3.1 Authentication
- `POST /v1/auth/login/`: Request: `{ empId, password }`. Returns: `{ accessToken, tokenType, empId, employeeId, employeeCode, role, firstLogin, mustChangePassword }`.
- `POST /v1/auth/change-password/`: Request: `{ currentPassword, newPassword }`. Returns: `{ success: true }`.
- `GET /v1/auth/me/`: Returns authenticated user's profile, role, and permission dictionary.

### 3.2 Employee Dashboard & Profile
- `GET /v2/employees/dashboard/summary/`: Overview counts for attendance, leave, holidays.
- `GET /v2/employees/me/profile/`: Complete personal, contact, address, bank, and employment details.
- `PATCH /v2/employees/me/profile/`: Updates permitted profile fields based on `permissions.canEdit*`.

### 3.3 Attendance
- `GET /v2/attendance/my-summary/`: Present, Absent, Half Day, Weekly Off counts for the selected month.
- `GET /v2/attendance/my-records/`: Log of daily in/out times and status tags.
- `POST /v2/attendance/punch/`: Submits mobile punch with `{ latitude, longitude, punchType, remarks }`.
- `POST /v2/attendance/regularization/`: Submits punch regularization requests.

### 3.4 Leave Management
- `GET /v2/leave/my-balances/`: Balances for Casual Leave (CL), Sick Leave (SL), Earned Leave (EL).
- `GET /v2/leave/my-applications/`: History of employee leave requests.
- `POST /v2/leave/applications/`: Submits new leave with `{ leaveTypeId, startDate, endDate, reason, isHalfDay }`.

### 3.5 Payroll & Payslips
- `GET /v2/payroll/my-payslips/`: List of published monthly payslip records.
- `GET /v2/payroll/payslip/{id}/`: Detail breakdown of earnings, deductions, gross pay, net pay.
- `GET /v2/payroll/payslip/{id}/download/`: Downloadable payslip PDF blob.

### 3.6 Reimbursements
- `GET /v1/reimbursements/my-claims/`: List of claims with amounts and approval status.
- `POST /v1/reimbursements/claims/`: Submits claim with bills and metadata.

### 3.7 Admin & Approvals
- `GET /v2/admin/dashboard/summary/`: Organization-wide headcount and attendance statistics.
- `GET /v2/leave/pending-approvals/`: Pending leave applications awaiting manager action.
- `POST /v2/leave/applications/{id}/action/`: Approve or reject leave with `{ action: 'APPROVE' | 'REJECT', remarks }`.
- `GET /v1/reimbursements/pending/`: Pending reimbursement requests.
- `POST /v1/reimbursements/{id}/action/`: Approve or reject reimbursement.
- `GET /v2/employees/`: Employee directory with pagination and filters.
- `GET /v2/attendance/monitor/`: Daily enterprise-wide attendance monitor.
- `GET /v2/payroll/cycles/`: Payroll cycles overview.
