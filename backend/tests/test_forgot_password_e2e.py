import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from app.auth.forgot_password.services.forgot_password_service import ForgotPasswordService
from app.auth.forgot_password.models.otp import PasswordResetOtpModel
from app.core.security import hash_password, verify_password, create_access_token

@pytest.mark.asyncio
async def test_forgot_password_flow():
    # Setup mock db
    mock_db = AsyncMock()
    mock_db.users.find_one.return_value = {"employeeId": "E1", "empId": "202102"}
    mock_db.employees.find_one.return_value = {"employeeId": "E1"}
    
    # Store OTP manually in memory to simulate DB
    memory_db = {}
    
    async def mock_create(data):
        doc = data.copy()
        doc["_id"] = "mock_otp_id"
        memory_db["active_otp"] = doc
        return PasswordResetOtpModel(**doc)
        
    async def mock_find_active(emp_id):
        doc = memory_db.get("active_otp")
        if not doc:
            return None
        # Check expiry
        if doc["expiresAt"] > datetime.now(timezone.utc):
            # Normalize for Pydantic like repo does
            doc["_id"] = str(doc.get("_id", "mock_otp_id"))
            return PasswordResetOtpModel(**doc)
        return None

    service = ForgotPasswordService(mock_db)
    service.email_service.send_password_reset_otp = AsyncMock()
    
    service.otp_repo.count_recent_otps = AsyncMock(return_value=0)
    service.otp_repo.invalidate_previous_otps = AsyncMock()
    service.otp_repo.create = mock_create
    service.otp_repo.find_active_otp = mock_find_active
    service.otp_repo.mark_used = AsyncMock()
    service.otp_repo.increment_attempts = AsyncMock()
    service.otp_repo.mark_verified = AsyncMock()
    
    with patch("app.employee.services.email_resolver.get_employee_personal_email", new_callable=AsyncMock) as mock_resolve:
        mock_resolve.return_value = "ramesh@gmail.com"
        
        # 1. Forgot Password
        res1 = await service.request_password_reset("202102", "ramesh@gmail.com")
        assert res1["message"] == "If an account exists, a password reset link has been sent."
        
        # Capture generated OTP by inspecting the email service call
        call_args = service.email_service.send_password_reset_otp.call_args
        assert call_args is not None, "Email service was not called"
        kwargs = call_args.kwargs
        context = kwargs.get("context")
        plaintext_otp = context.get("otp")
        
        assert plaintext_otp is not None
        
        # 2. Verify OTP
        res2 = await service.verify_otp("202102", "ramesh@gmail.com", plaintext_otp)
        assert res2["message"] == "OTP verified successfully"
        reset_token = res2["resetToken"]
        assert reset_token is not None
        
        # 3. Reset Password
        mock_db.password_reset_otps.find_one.return_value = {"_id": "mock_otp_id", "used": False, "verified": True}
        res3 = await service.reset_password("202102", reset_token, "NewPass123!", "NewPass123!")
        assert res3["message"] == "Password reset successfully"
