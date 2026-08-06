from datetime import datetime, timezone
from fastapi import HTTPException
from app.approval.repositories.approval_repository import ApprovalRepository
from app.approval.models.approval import ApprovalModel
from app.approval.schemas.approval import ApprovalSubmit, ApprovalAction
import uuid

class ApprovalService:
    def __init__(self, db):
        self.db = db
        self.repo = ApprovalRepository(db)

    def _utc_now(self):
        return datetime.now(timezone.utc)

    async def submit_request(self, data: ApprovalSubmit) -> ApprovalModel:
        model = ApprovalModel(
            employeeId=data.employeeId,
            reportingManagerEmployeeId=data.reportingManagerEmployeeId,
            approvalType=data.approvalType,
            status="PENDING",
            requestData=data.requestData,
            remarks=data.remarks,
            createdAt=self._utc_now()
        )
        return await self.repo.create(model)

    async def execute_action(self, approval_id: str, action_data: ApprovalAction) -> ApprovalModel:
        approval = await self.repo.get_by_id(approval_id)
        if not approval:
            raise HTTPException(status_code=404, detail="Approval request not found")
            
        action = action_data.action.upper()
        if action == "APPROVE":
            approval.status = "APPROVED"
            
            # Phase 7: Generate synthetic logs for Miss Punch / Mobile Punch / Remote Attendance
            if approval.approvalType in ["Miss Punch", "Mobile Punch", "Remote Attendance"]:
                # The requestData must contain the punch time. Example: {"punchTime": "2026-08-01T09:00:00Z"}
                # For demo safety, we parse it or default to now.
                punch_time_str = approval.requestData.get("punchTime", self._utc_now().isoformat())
                punch_time = datetime.fromisoformat(punch_time_str.replace("Z", "+00:00"))
                
                synthetic_log = {
                    "fingerprint": f"APPROVAL_{approval_id}",
                    "empId": approval.employeeId,
                    "timestamp": punch_time,
                    "source": "approval",
                    "deviceSn": "APPROVAL_ENGINE",
                    "approvalId": approval_id,
                    "createdAt": self._utc_now()
                }
                await self.db.attendance_logs.update_one(
                    {"fingerprint": synthetic_log["fingerprint"]},
                    {"$set": synthetic_log},
                    upsert=True
                )
                
        elif action == "REJECT":
            approval.status = "REJECTED"
        elif action == "WITHDRAW":
            approval.status = "WITHDRAWN"
        elif action == "CANCEL":
            approval.status = "CANCELLED"
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
            
        approval.approvedAt = self._utc_now()
        approval.approvedBy = action_data.actedBy
        if action_data.remarks:
            approval.remarks = action_data.remarks
            
        updated = await self.repo.update(approval_id, approval)
        return updated

    async def get_manager_inbox(self, manager_emp_id: str, status: str = None):
        return await self.repo.get_by_manager(manager_emp_id, status)
        
    async def get_employee_requests(self, emp_id: str, status: str = None):
        return await self.repo.get_by_employee(emp_id, status)
