import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import traceback

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import EmailStr

from app.core.config import get_settings
from app.email_service.schemas.email_log import EmailLogCreate
from app.email_service.repositories.email_log_repository import EmailLogRepository

settings = get_settings()

template_folder = Path(__file__).parent.parent / "templates"

conf = ConnectionConfig(
    MAIL_USERNAME=settings.smtp_username,
    MAIL_PASSWORD=settings.smtp_password,
    MAIL_FROM=settings.smtp_from_email,
    MAIL_PORT=settings.smtp_port,
    MAIL_SERVER=settings.smtp_host,
    MAIL_FROM_NAME=settings.smtp_from_name,
    MAIL_STARTTLS=settings.smtp_tls,
    MAIL_SSL_TLS=settings.smtp_ssl,
    USE_CREDENTIALS=bool(settings.smtp_username),
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=template_folder
)

class EmailService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.email_log_repo = EmailLogRepository(db)
        self.fm = FastMail(conf)

    async def _log_email(self, log_data: EmailLogCreate):
        await self.email_log_repo.create(log_data.model_dump())

    async def _send_email_task(
        self, 
        recipients: List[EmailStr], 
        subject: str, 
        template_name: str, 
        template_body: Dict[str, Any],
        attachments: Optional[List[Any]] = None
    ):
        try:
            message = MessageSchema(
                subject=subject,
                recipients=recipients,
                template_body=template_body,
                subtype=MessageType.html,
                attachments=attachments or []
            )
            
            await self.fm.send_message(message, template_name=template_name)
            
            # Log success
            log_entry = EmailLogCreate(
                recipient=", ".join(recipients),
                subject=subject,
                template=template_name,
                status="Sent",
                sent_time=datetime.now(timezone.utc),
                attachment=str(attachments) if attachments else None
            )
            await self._log_email(log_entry)
            
        except Exception as e:
            # Log failure
            log_entry = EmailLogCreate(
                recipient=", ".join(recipients),
                subject=subject,
                template=template_name,
                status="Failed",
                failure_reason=str(e),
                attachment=str(attachments) if attachments else None
            )
            await self._log_email(log_entry)
            print(f"[EmailService Error] Failed to send email to {recipients}: {e}")
            traceback.print_exc()

    async def send_welcome_email(self, recipient: str, context: dict):
        subject = "Welcome to Enterprise HRMS"
        await self._send_email_task([recipient], subject, "welcome.html", context)

    async def send_password_reset_otp(self, recipient: str, context: dict):
        subject = "Password Reset OTP"
        await self._send_email_task([recipient], subject, "forgot_password_otp.html", context)

    async def send_password_changed_notification(self, recipient: str, context: dict):
        subject = "Your Password Has Been Changed"
        await self._send_email_task([recipient], subject, "password_changed.html", context)

    async def send_account_created_email(self, recipient: str, context: dict):
        subject = "Account Created"
        await self._send_email_task([recipient], subject, "account_created.html", context)

    async def send_account_locked_email(self, recipient: str, context: dict):
        subject = "Security Alert: Account Locked"
        await self._send_email_task([recipient], subject, "account_locked.html", context)

    async def send_leave_status_email(self, recipient: str, status: str, context: dict):
        subject = f"Leave Request {status.capitalize()}"
        template = "leave_approved.html" if status.lower() == "approved" else "leave_rejected.html"
        await self._send_email_task([recipient], subject, template, context)

    async def send_workflow_notification(self, recipient: str, context: dict):
        subject = "Workflow Notification"
        await self._send_email_task([recipient], subject, "workflow_notification.html", context)

    async def send_payslip_email(self, recipient: str, context: dict, attachments: list):
        subject = f"Payslip for {context.get('payrollMonth', 'this month')}"
        await self._send_email_task([recipient], subject, "payslip_email.html", context, attachments)

    async def send_custom_email(self, recipient: str, subject: str, context: dict):
        await self._send_email_task([recipient], subject, "general_notification.html", context)

