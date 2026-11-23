# Technical Architecture Audit: ESS/HRMS Forgot Password Reset Token Issue

> **Audit Type:** Technical Root Cause & Architecture Analysis  
> **Status:** Completed (Audit-Only — No Code/Database Alterations)  
> **Scope:** Frontend (React/TypeScript), Backend API (FastAPI/Python), Database Layer (MongoDB via Motor/PyMongo)  
> **Date:** November 2026  

---

## Executive Summary

During the ESS/HRMS Forgot Password flow, users are able to request an OTP, receive it via email, and successfully pass OTP verification to obtain a JWT password reset token. However, upon submitting the new password alongside the reset token, the backend consistently rejects the request with HTTP 400:

```json
{
  "detail": "Reset token has already been used or is invalid"
}
```

A comprehensive audit of the end-to-end flow revealed that **the root cause is a BSON `ObjectId` vs. string type mismatch in MongoDB document queries and updates**:

1. **Storage Format:** When an OTP record is inserted into MongoDB collection `password_reset_otps`, MongoDB automatically generates a native BSON `ObjectId` for `_id` (e.g. `ObjectId("6b0420b5a94ea18c2ee8b181")`).
2. **PyMongo Query Semantic:** In PyMongo/Motor, querying `{"_id": "6b0420b5a94ea18c2ee8b181"}` (where the selector value is a Python `str`) **never matches** a BSON `ObjectId`. Motor requires `{"_id": ObjectId(otp_id)}`.
3. **Double Failure Point:**
   - In `OtpRepository.mark_verified(otp_id: str)`: PyMongo executes `update_one({"_id": otp_id}, {"$set": {"verified": True}})`. Because `otp_id` is passed as a string, **0 documents match**, so the database document's `verified` field **remains `False`**.
   - In `ForgotPasswordService.reset_password(...)`: The service attempts to locate the record using `self.db.password_reset_otps.find_one({"_id": otp_id, "used": False, "verified": True})`. Again, querying with a `str` produces `None`. Even if `verified` were somehow true, matching against `_id: str` yields `None`.
4. **Why Unit Tests Failed to Catch This:** The existing unit tests (`backend/tests/test_forgot_password_v2.py` and `backend/tests/test_forgot_password_e2e.py`) used `AsyncMock` to mock `db.password_reset_otps.find_one` and `otp_repo.mark_verified`. The mocks accepted string keys without exercising PyMongo's BSON serialization rules.

---

## 1. Complete Forgot Password Architecture & Flow Trace

The table below traces the entire 14-step lifecycle across frontend components, API services, backend routes, services, repositories, and database collections:

| Step # | Flow Step | Component / Layer | File / Location | Implementation Details |
|---|---|---|---|---|
| **1** | Forgot Password Modal | Frontend Component | `src/components/auth/ForgotPasswordModal.tsx` | User clicks "Forgot Password?" from LoginModal; Modal opens in Step 1. |
| **2** | Employee & Email Identification | Frontend Input | `ForgotPasswordModal.tsx` (`handleRequestOtp`) | Collects `employeeCode` (e.g. "202102") and `email`. |
| **3** | Request OTP API Call | Frontend Service | `src/services/authService.ts` (`authApi.forgotPassword`) | Calls `POST /api/v1/auth/forgot-password/` with payload `{"employeeCode": "...", "email": "..."}`. |
| **4** | Route Handling | Backend Router | `backend/app/auth/forgot_password/routes/router.py` (`forgot_password`) | Validates payload against `ForgotPasswordRequest`. Delegates to `ForgotPasswordService.request_password_reset`. |
| **5** | Identity & Email Verification | Backend Service | `backend/app/auth/forgot_password/services/forgot_password_service.py` | Finds user in `db.users` by `employeeCode`/`empId`/`employeeId`. Resolves canonical email via `get_employee_personal_email(db, emp_id)`. Checks case-insensitive email match. |
| **6** | Rate Limiting & Previous Invalidation | Backend Service & Repo | `forgot_password_service.py` & `OtpRepository` | Verifies $\le 5$ requests/hour via `otp_repo.count_recent_otps`. Invalidates older unused tokens via `otp_repo.invalidate_previous_otps`. |
| **7** | OTP Generation & Hash Storage | Backend Service & Repo | `forgot_password_service.py` (`request_password_reset`) | Uses `secrets.randbelow(10)` to generate 6-digit cryptographic OTP. Hashes via PBKDF2-SHA256 (`hash_password(otp)`). Inserts into `password_reset_otps` collection with `expiresAt = now + 5 min`. |
| **8** | OTP Delivery via Email | Email Service | `backend/app/email_service/services/email_service.py` | Asynchronously dispatches template `forgot_password_otp.html` to recipient. |
| **9** | OTP Verification Submission | Frontend Component & Service | `ForgotPasswordModal.tsx` (`handleVerifyOtp`) & `authService.ts` (`verifyResetOtp`) | Submits `POST /api/v1/auth/verify-reset-otp/` with `{"employeeCode": "...", "email": "...", "otp": "..."}`. |
| **10** | OTP Verification & Token Minting | Backend Service & Security | `forgot_password_service.py` (`verify_otp`) & `app/core/security.py` | Finds active OTP by `emp_id`. Validates attempt limits ($\le 3$). Verifies OTP hash using `verify_password`. Calls `otp_repo.mark_verified(str(otp_doc.id))`. Creates 15-minute signed JWT token containing `{"empId": emp_id, "purpose": "password_reset", "otpId": str(otp_doc.id)}`. |
| **11** | Reset Token Transmission to Frontend | Frontend State | `ForgotPasswordModal.tsx` | Receives `{"message": "...", "resetToken": "..."}` and stores `resetToken` in React component state; advances to Step 3. |
| **12** | New Password Submission | Frontend Component & Service | `ForgotPasswordModal.tsx` (`handleResetPassword`) & `authService.ts` (`resetPassword`) | Submits `POST /api/v1/auth/reset-password/` with payload `{"employeeCode": "...", "resetToken": "...", "newPassword": "...", "confirmPassword": "..."}`. |
| **13** | Token Validation & Record Lookup | Backend Service | `forgot_password_service.py` (`reset_password`) | Decodes JWT, verifies signature, expiry, and `purpose == "password_reset"`. Matches employee ownership. Looks up OTP record in MongoDB: `db.password_reset_otps.find_one({"_id": otp_id, "used": False, "verified": True})`. |
| **14** | Password Update & Token Invalidation | Backend Service | `forgot_password_service.py` (`reset_password`) | Hashes new password with PBKDF2-SHA256, updates `db.users`, invalidates OTP via `otp_repo.mark_used(otp_id)`, logs audit entry, sends confirmation email. |

---

## 2. Root Cause Analysis of the Reset Token Error

### Exact Code Under Investigation

In `backend/app/auth/forgot_password/services/forgot_password_service.py`:

```python
# Lines 128-131: In verify_otp
# Generate a temporary reset token valid for 15 minutes
token = create_access_token(
    {"empId": emp_id, "purpose": "password_reset", "otpId": str(otp_doc.id)},
    expires_delta=timedelta(minutes=15)
)

# Line 125: In verify_otp
await self.otp_repo.mark_verified(str(otp_doc.id))
```

And in `backend/app/auth/forgot_password/repositories/otp_repository.py`:

```python
# Lines 35-39:
async def mark_verified(self, otp_id: str):
    await self.collection.update_one(
        {"_id": otp_id},
        {"$set": {"verified": True, "updatedAt": datetime.now(timezone.utc)}}
    )

# Lines 41-45:
async def mark_used(self, otp_id: str):
    await self.collection.update_one(
        {"_id": otp_id},
        {"$set": {"used": True, "updatedAt": datetime.now(timezone.utc)}}
    )
```

And in `backend/app/auth/forgot_password/services/forgot_password_service.py`:

```python
# Lines 158-161: In reset_password
# Check if OTP was already used
otp_doc = await self.db.password_reset_otps.find_one({"_id": otp_id, "used": False, "verified": True})
if not otp_doc:
    raise HTTPException(status_code=400, detail="Reset token has already been used or is invalid")
```

### Empirical Verification Against MongoDB Driver Behaviour

An isolated test against MongoDB with the identical driver environment executed:

```python
# In MongoDB, doc._id is BSON ObjectId('6b0420b5a94ea18c2ee8b181')
# Test 1: mark_verified with string otp_id
res_verify = await db.password_reset_otps.update_one({'_id': otp_id}, {'$set': {'verified': True}})
# Result: matched_count = 0, modified_count = 0

# Test 2: find_one in reset_password with string otp_id
found_with_str = await db.password_reset_otps.find_one({'_id': otp_id, 'used': False, 'verified': True})
# Result: None

# Test 3: mark_verified and find_one with ObjectId(otp_id)
res_verify_oid = await db.password_reset_otps.update_one({'_id': ObjectId(otp_id)}, {'$set': {'verified': True}})
# Result: matched_count = 1, modified_count = 1
found_with_oid = await db.password_reset_otps.find_one({'_id': ObjectId(otp_id), 'used': False, 'verified': True})
# Result: Document matched successfully
```

### Investigation of Hypotheses (A through F)

| Hypothesis Area | Question / Possibility | Finding | Status |
|---|---|---|---|
| **A. Token Lifecycle** | Is the token being consumed during OTP verification? | No. OTP verification calls `mark_verified`, setting `verified=True`. It does not set `used=True`. | Ruled out |
| | Is the token marked as used before password reset? | No. But because `mark_verified` used a string query, `verified` was **never set to `True`** in MongoDB. | **Contributing Cause** |
| | Is the token invalidated by another operation? | No. Only `invalidate_previous_otps` updates older records. | Ruled out |
| **B. Token Mismatch** | Is the frontend sending the same token backend generated? | Yes. `setResetToken(response.resetToken)` in `ForgotPasswordModal.tsx` stores the exact JWT string returned by `/v1/auth/verify-reset-otp/`, and sends `resetToken` in the payload. | Ruled out |
| | Is the token being truncated or modified? | No. Inspection of `ForgotPasswordModal.tsx` and `authService.ts` confirms the string is passed intact. | Ruled out |
| | Is the wrong field name used in the request payload? | No. Frontend sends `{ employeeCode, resetToken, newPassword, confirmPassword }`. Backend `ResetPasswordRequest` expects `employeeCode`, `resetToken`, `newPassword`, `confirmPassword`. Field names match verbatim. | Ruled out |
| **C. Token Storage** | Is the reset token stored correctly? | The reset token is a stateless signed JWT containing `otpId`. The state tracking occurs in `password_reset_otps` keyed by `_id`. | Validated |
| | Is the database query comparing the correct token representation? | **No.** `otp_id` in the JWT is a 24-character hexadecimal string, but MongoDB stores `_id` as BSON `ObjectId`. Motor/PyMongo treats `_id: str` and `_id: ObjectId` as distinct types. | **PRIMARY ROOT CAUSE** |
| **D. Expiration** | Is the token expiring immediately? | No. Expiry is set to 15 minutes (`expires_delta=timedelta(minutes=15)`). Token verification does not fail on expiration during normal test submission. | Ruled out |
| | Timezone discrepancies? | Both `createdAt` and `expiresAt` use `datetime.now(timezone.utc)` uniformly. | Ruled out |
| **E. Duplicate Requests**| Is React StrictMode or retry sending duplicate requests? | The modal disables buttons during loading (`loading={isLoading}`). No retry interceptor exists in `lib/api.ts`. | Ruled out |
| **F. Database & Deployment**| Separate databases or workers? | Backend and repository use a single MongoDB database configured via `MONGO_DB_NAME`. | Ruled out |

---

## 3. Frontend and Backend API Contracts Analysis

### Contract Comparison Matrix

#### Stage 1: Request OTP
- **Frontend Call:** `POST /api/v1/auth/forgot-password/`
- **Frontend Payload:** `{ "employeeCode": string, "email": string }`
- **Backend Schema:** `ForgotPasswordRequest(employeeCode: str, email: str)`
- **Backend Response:** `GenericSuccessResponse(message: str)`
- **Match Status:** **Exact Match**

#### Stage 2: Verify OTP
- **Frontend Call:** `POST /api/v1/auth/verify-reset-otp/`
- **Frontend Payload:** `{ "employeeCode": string, "email": string, "otp": string }`
- **Backend Schema:** `VerifyOtpRequest(employeeCode: str, email: str, otp: str)`
- **Backend Response:** `VerifyOtpResponse(message: str, resetToken: str)`
- **Match Status:** **Exact Match**

#### Stage 3: Reset Password
- **Frontend Call:** `POST /api/v1/auth/reset-password/`
- **Frontend Payload:** `{ "employeeCode": string, "resetToken": string, "newPassword": string, "confirmPassword": string }`
- **Backend Schema:** `ResetPasswordRequest(employeeCode: str, resetToken: str, newPassword: str, confirmPassword: str)`
- **Backend Response:** `GenericSuccessResponse(message: str)`
- **Match Status:** **Exact Match**

Both schemas and field naming conventions (`camelCase`) are identical across frontend and backend.

---

## 4. Token Consumption and Transaction Safety

### Current Execution Sequence in `reset_password`

```python
# 1. Decode JWT reset_token
payload = decode_access_token(reset_token)
otp_id = payload.get("otpId")

# 2. Check OTP status in MongoDB (FAILS HERE)
otp_doc = await self.db.password_reset_otps.find_one({"_id": otp_id, "used": False, "verified": True})
if not otp_doc:
    raise HTTPException(status_code=400, detail="Reset token has already been used or is invalid")

# 3. Hash password
new_hash = hash_password(new_password)

# 4. Update user record
await self.db.users.update_one({"employeeId": emp_id}, {"$set": {"passwordHash": new_hash, ...}})

# 5. Invalidate OTP (Also uses string otp_id!)
await self.otp_repo.mark_used(otp_id)
```

### Critical Observations:
1. **Pre-condition Check Failure:** Step 2 fails because `{"_id": otp_id}` queries MongoDB for a string `_id` against a collection where `_id` is an `ObjectId`. Consequently, Step 2 always evaluates to `None` and raises HTTP 400.
2. **Defective Invalidation (`mark_used`):** In Step 5, `self.otp_repo.mark_used(otp_id)` calls `self.collection.update_one({"_id": otp_id}, {"$set": {"used": True}})`. Because it queries with `otp_id: str` without `ObjectId(otp_id)`, **it would also fail to update the record in MongoDB**, leaving `used: False`.
3. **Transaction Safety / Atomicity:** Currently, MongoDB operations are executed as individual queries without an atomic transaction session or a conditional state transition. If an error occurs between user password update and OTP invalidation, the token state could remain inconsistent.

---

## 5. Security Audit Findings

| Security Check | Evaluation | Details |
|---|---|---|
| **Plaintext OTP Storage** | **PASSED** | OTP is hashed using PBKDF2-SHA256 before storage in `password_reset_otps`. Plaintext OTP is never stored in DB. |
| **Reset Token Generation** | **PASSED** | Token is an HMAC-SHA256 signed JWT with 15-minute expiration, containing `empId`, `purpose: "password_reset"`, and `otpId`. |
| **Token Expiry** | **PASSED** | JWT token has explicit `exp` claim set to 15 minutes. OTP expires in 5 minutes. |
| **User Identity Association** | **PASSED** | Service validates that the `employeeCode` provided matches the `empId` bound to the signed JWT. Cross-account token submission is blocked. |
| **Brute Force Protection** | **PASSED** | Maximum 3 attempts per OTP (`attemptCount >= maxAttempts`). Maximum 5 OTP requests per hour per employee. |
| **Account Enumeration Protection** | **PASSED** | Non-existent employee code or mismatched email returns a generic success/acknowledgment message in `request_password_reset`. |
| **Post-Reset Invalidation** | **DEFECTIVE (BSON Issue)** | The design specifies marking `used: True`, but `mark_used(otp_id)` passes a string, failing to update the database record. |

---

## 6. Exact Files Requiring Modification

Only two files in the backend require adjustments to resolve this issue and prevent recurrence:

### 1. `backend/app/auth/forgot_password/repositories/otp_repository.py`
Functions requiring modification:
- `increment_attempts(self, otp_id: str)`: Convert `otp_id` to `ObjectId` before querying `_id`.
- `mark_verified(self, otp_id: str)`: Convert `otp_id` to `ObjectId` before querying `_id`.
- `mark_used(self, otp_id: str)`: Convert `otp_id` to `ObjectId` before querying `_id`.

### 2. `backend/app/auth/forgot_password/services/forgot_password_service.py`
Functions requiring modification:
- `reset_password(...)`: Convert `otp_id` to `ObjectId` when querying `self.db.password_reset_otps.find_one({"_id": ObjectId(otp_id), "used": False, "verified": True})`.

---

## 7. Recommended Minimal Fix (For Approval)

### Proposed Changes

#### A. In `backend/app/auth/forgot_password/repositories/otp_repository.py`
Import `ObjectId` from `bson`:
```python
from bson import ObjectId
```
Update ID matching helpers in `OtpRepository`:
```python
    def _to_object_id(self, otp_id: str | ObjectId) -> ObjectId:
        if isinstance(otp_id, ObjectId):
            return otp_id
        try:
            return ObjectId(otp_id)
        except Exception:
            return None

    async def increment_attempts(self, otp_id: str):
        oid = self._to_object_id(otp_id)
        if not oid:
            return
        await self.collection.update_one(
            {"_id": oid},
            {"$inc": {"attemptCount": 1}, "$set": {"updatedAt": datetime.now(timezone.utc)}}
        )

    async def mark_verified(self, otp_id: str):
        oid = self._to_object_id(otp_id)
        if not oid:
            return
        await self.collection.update_one(
            {"_id": oid},
            {"$set": {"verified": True, "updatedAt": datetime.now(timezone.utc)}}
        )

    async def mark_used(self, otp_id: str):
        oid = self._to_object_id(otp_id)
        if not oid:
            return
        await self.collection.update_one(
            {"_id": oid},
            {"$set": {"used": True, "updatedAt": datetime.now(timezone.utc)}}
        )
```

#### B. In `backend/app/auth/forgot_password/services/forgot_password_service.py`
Import `ObjectId` and safely query `password_reset_otps`:
```python
from bson import ObjectId

# In reset_password:
try:
    oid = ObjectId(otp_id)
except Exception:
    raise HTTPException(status_code=400, detail="Reset token has already been used or is invalid")

otp_doc = await self.db.password_reset_otps.find_one({"_id": oid, "used": False, "verified": True})
if not otp_doc:
    raise HTTPException(status_code=400, detail="Reset token has already been used or is invalid")
```

---

## 8. Test Scenarios & Regression Verification Plan

The following test suite should be executed to validate the fix:

| # | Test Scenario | Input / Precondition | Expected Behavior |
|---|---|---|---|
| 1 | **Correct OTP & Valid Reset Token (Happy Path)** | Valid OTP verified $\to$ token passed to reset endpoint with valid matching passwords. | Password updated in `db.users`, OTP marked `used: True`, returns 200 OK. |
| 2 | **Incorrect OTP** | User enters wrong 6-digit OTP during verification. | Rejects with 400 "Invalid OTP", increments `attemptCount`. |
| 3 | **Max OTP Attempts Exceeded** | 3 incorrect attempts. | Fourth attempt returns 400 "Maximum OTP attempts exceeded", marks record `used: True`. |
| 4 | **Expired OTP** | OTP submitted after 5 minutes. | `find_active_otp` ignores expired record; returns 400 "Invalid or expired OTP". |
| 5 | **Reused OTP** | Attempting to verify an OTP that was already verified. | `find_active_otp` queries `verified: False`, ignores previously verified OTP. |
| 6 | **Reset Token Used Twice** | Submitting the same reset token for a second password reset. | Fails at `find_one` because `used: True`. Returns 400 "Reset token has already been used or is invalid". |
| 7 | **Expired Reset Token** | Submitting reset token after 15 minutes. | `decode_access_token` raises `jwt.ExpiredSignatureError`, returns 401 "Invalid or expired reset token". |
| 8 | **Tampered Reset Token** | Altered JWT signature or payload claims. | Returns 401 "Invalid or expired reset token". |
| 9 | **Reset Token Belonging to Another Employee** | Token minted for Emp A submitted with `employeeCode` for Emp B. | Returns 400 "Invalid employee code for this reset transaction". |
| 10| **Password Complexity Validation Failure** | Password fails uppercase/number/special char requirement. | `PasswordValidator.validate` raises 400 with specific requirement message before any DB update. |
| 11| **Password Mismatch** | `newPassword != confirmPassword`. | Returns 400 "Passwords do not match". |
| 12| **Unit Test Coverage Update** | Replace mocks with realistic BSON `ObjectId` fixtures in `test_forgot_password_v2.py`. | Confirms both string and `ObjectId` types pass without regressions. |
