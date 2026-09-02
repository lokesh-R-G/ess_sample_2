from fastapi import APIRouter, Depends, HTTPException, status
from app.db.mongo import get_database
from app.auth.forgot_password.schemas.forgot_password import (
    ForgotPasswordRequest, VerifyOtpRequest, ResetPasswordRequest,
    GenericSuccessResponse, VerifyOtpResponse
)
from app.auth.forgot_password.services.forgot_password_service import ForgotPasswordService
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter(prefix="/auth", tags=["auth", "forgot-password"])

@router.post("/forgot-password/", response_model=GenericSuccessResponse)
async def forgot_password(payload: ForgotPasswordRequest, db: AsyncIOMotorDatabase = Depends(get_database)):
    service = ForgotPasswordService(db)
    return await service.request_password_reset(payload.employeeCode, payload.email)

@router.post("/verify-reset-otp/", response_model=VerifyOtpResponse)
async def verify_reset_otp(payload: VerifyOtpRequest, db: AsyncIOMotorDatabase = Depends(get_database)):
    service = ForgotPasswordService(db)
    return await service.verify_otp(payload.employeeCode, payload.email, payload.otp)

@router.post("/reset-password/", response_model=GenericSuccessResponse)
async def reset_password(payload: ResetPasswordRequest, db: AsyncIOMotorDatabase = Depends(get_database)):
    service = ForgotPasswordService(db)
    return await service.reset_password(payload.employeeCode, payload.resetToken, payload.newPassword, payload.confirmPassword)
