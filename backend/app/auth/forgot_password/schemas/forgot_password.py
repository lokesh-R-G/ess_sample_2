from pydantic import BaseModel, EmailStr
from typing import Optional

class ForgotPasswordRequest(BaseModel):
    identifier: str

class VerifyOtpRequest(BaseModel):
    employeeId: str
    otp: str

class VerifyOtpResponse(BaseModel):
    message: str
    resetToken: str

class ResetPasswordRequest(BaseModel):
    resetToken: str
    newPassword: str
    confirmPassword: str

class GenericSuccessResponse(BaseModel):
    message: str
