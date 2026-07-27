from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class PasswordResetOtpModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    employeeId: str
    email: str
    otpHash: str
    purpose: str = "password_reset"
    createdAt: datetime
    expiresAt: datetime
    verified: bool = False
    attemptCount: int = 0
    maxAttempts: int = 3
    used: bool = False
    createdBy: Optional[str] = None
    updatedAt: Optional[datetime] = None
