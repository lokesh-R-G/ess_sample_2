import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from app.auth.forgot_password.services.forgot_password_service import ForgotPasswordService
from app.auth.forgot_password.models.otp import PasswordResetOtpModel
from app.core.security import hash_password, create_access_token

@pytest.fixture
def mock_db():
    db = AsyncMock()
    return db

@pytest.fixture
def service(mock_db):
    svc = ForgotPasswordService(mock_db)
    # mock email_service to avoid real sending
    svc.email_service.send_password_reset_otp = AsyncMock()
    # mock otp_repo methods
    svc.otp_repo.count_recent_otps = AsyncMock(return_value=0)
    svc.otp_repo.invalidate_previous_otps = AsyncMock()
    svc.otp_repo.create = AsyncMock()
    svc.otp_repo.find_active_otp = AsyncMock()
    svc.otp_repo.mark_used = AsyncMock()
    svc.otp_repo.increment_attempts = AsyncMock()
    svc.otp_repo.mark_verified = AsyncMock()
    return svc

@pytest.mark.asyncio
async def test_request_reset_success(service, mock_db):
    mock_db.users.find_one.return_value = {"employeeId": "E1", "empId": "202102"}
    mock_db.employees.find_one.return_value = {"employeeId": "E1"}
    # canonical email setup
    with patch("app.employee.services.email_resolver.get_employee_personal_email", new_callable=AsyncMock) as mock_resolve:
        mock_resolve.return_value = "ramesh@gmail.com"
        
        # Act
        res = await service.request_password_reset("202102", "ramesh@gmail.com")
        
        # Assert
        assert res["message"] == "If an account exists, a password reset link has been sent."
        mock_resolve.assert_called_once_with(mock_db, "E1")
        # OTP creation check
        assert service.otp_repo.create.called

@pytest.mark.asyncio
async def test_request_reset_wrong_email(service, mock_db):
    mock_db.users.find_one.return_value = {"employeeId": "E1", "empId": "202102"}
    mock_db.employees.find_one.return_value = {"employeeId": "E1"}
    # canonical email setup
    with patch("app.employee.services.email_resolver.get_employee_personal_email", new_callable=AsyncMock) as mock_resolve:
        mock_resolve.return_value = "ramesh@gmail.com"
        
        # Act
        res = await service.request_password_reset("202102", "wrong@gmail.com")
        
        # Assert - generic message returned but OTP NOT created
        assert res["message"] == "The employee code or email is invalid."
        assert not service.otp_repo.create.called

@pytest.mark.asyncio
async def test_request_reset_wrong_code(service, mock_db):
    mock_db.users.find_one.return_value = None
    
    res = await service.request_password_reset("WRONG", "ramesh@gmail.com")
    assert res["message"] == "The employee code or email is invalid."
    assert not service.otp_repo.create.called

@pytest.mark.asyncio
async def test_verify_otp_success(service, mock_db):
    mock_db.users.find_one.return_value = {"employeeId": "E1", "empId": "202102"}
    mock_db.employees.find_one.return_value = {"employeeId": "E1"}
    
    otp = "123456"
    otp_doc = PasswordResetOtpModel(
        employeeId="E1",
        email="ramesh@gmail.com",
        otpHash=hash_password(otp),
        createdAt=datetime.now(timezone.utc),
        expiresAt=datetime.now(timezone.utc) + timedelta(minutes=5)
    )
    service.otp_repo.find_active_otp.return_value = otp_doc
    
    with patch("app.employee.services.email_resolver.get_employee_personal_email", new_callable=AsyncMock) as mock_resolve:
        mock_resolve.return_value = "ramesh@gmail.com"
        
        res = await service.verify_otp("202102", "ramesh@gmail.com", otp)
        assert res["message"] == "OTP verified successfully"
        assert "resetToken" in res

@pytest.mark.asyncio
async def test_verify_otp_incorrect_otp(service, mock_db):
    mock_db.users.find_one.return_value = {"employeeId": "E1", "empId": "202102"}
    mock_db.employees.find_one.return_value = {"employeeId": "E1"}
    
    otp_doc = PasswordResetOtpModel(
        employeeId="E1",
        email="ramesh@gmail.com",
        otpHash=hash_password("123456"),
        createdAt=datetime.now(timezone.utc),
        expiresAt=datetime.now(timezone.utc) + timedelta(minutes=5)
    )
    service.otp_repo.find_active_otp.return_value = otp_doc
    
    with patch("app.employee.services.email_resolver.get_employee_personal_email", new_callable=AsyncMock) as mock_resolve:
        mock_resolve.return_value = "ramesh@gmail.com"
        
        with pytest.raises(HTTPException) as exc:
            await service.verify_otp("202102", "ramesh@gmail.com", "999999")
        assert exc.value.status_code == 400
        assert "Invalid OTP" in str(exc.value.detail)

@pytest.mark.asyncio
async def test_reset_password_success(service, mock_db):
    # Setup token
    token = create_access_token(
        {"empId": "E1", "purpose": "password_reset", "otpId": "otp_123"},
        expires_delta=timedelta(minutes=15)
    )
    
    mock_db.users.find_one.return_value = {"employeeId": "E1", "empId": "202102"}
    mock_db.employees.find_one.return_value = {"employeeId": "E1"}
    
    mock_db.password_reset_otps.find_one.return_value = {"_id": "otp_123", "used": False, "verified": True}
    
    res = await service.reset_password("202102", token, "NewPass123!", "NewPass123!")
    
    assert res["message"] == "Password reset successfully"
    mock_db.users.update_one.assert_called_once()
