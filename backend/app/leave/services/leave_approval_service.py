from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.leave.repositories.leave_approval_repository import LeaveApprovalRepository
from app.leave.validators.leave_approval_validator import LeaveApprovalValidator
from app.leave.schemas.leave_approval import LeaveApprovalCreate, LeaveApprovalUpdate
from app.leave.models.leave_approval import LeaveApprovalModel
import asyncio
from app.email_service.services.email_service import EmailService

class LeaveApprovalService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = LeaveApprovalRepository(db)
        self.validator = LeaveApprovalValidator(db)
        self.email_service = EmailService(db)
        
    async def create(self, data: LeaveApprovalCreate, user_id: str = None) -> LeaveApprovalModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[LeaveApprovalModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: LeaveApprovalUpdate, user_id: str = None) -> Optional[LeaveApprovalModel]:
        await self.validator.validate_update(id, data)
        updated_approval = await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
        # Email Integration
        if updated_approval:
            status = getattr(updated_approval, "status", None)
            if status in ["Approved", "Rejected"]:
                # Fetch employee email based on employee_id
                emp_id = getattr(updated_approval, "employeeId", "unknown")
                from app.employee.services.email_resolver import get_employee_personal_email
                try:
                    contact_email = await get_employee_personal_email(self.db, emp_id)
                    context = {
                        "leave_type": "Leave Request",
                        "start_date": "N/A", # Needs real start_date from LeaveApplication
                        "end_date": "N/A",
                        "remarks": getattr(updated_approval, "remarks", "None"),
                        "reason": getattr(updated_approval, "remarks", "Please contact your manager.")
                    }
                    asyncio.create_task(
                        self.email_service.send_leave_status_email(
                            recipient=contact_email, 
                            status=status, 
                            context=context
                        )
                    )
                except ValueError as e:
                    print(f"[LeaveApprovalService] Cannot send leave status email: {e}")
                
        return updated_approval
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
