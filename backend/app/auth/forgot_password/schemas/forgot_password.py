from pydantic import BaseModel, EmailStr
from typing import Optional

class ForgotPasswordRequest(BaseModel):
    employeeCode: str
    email: str

class VerifyOtpRequest(BaseModel):
    employeeCode: str
    email: str
    otp: str

class VerifyOtpResponse(BaseModel):
    message: str
    resetToken: str

class ResetPasswordRequest(BaseModel):
    employeeCode: str
    resetToken: str
    newPassword: str
    confirmPassword: str

class GenericSuccessResponse(BaseModel):
    message: str
