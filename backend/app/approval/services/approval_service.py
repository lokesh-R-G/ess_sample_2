from datetime import datetime, timezone
from fastapi import HTTPException
from app.approval.repositories.approval_repository import ApprovalRepository
from app.approval.models.approval import ApprovalModel
from app.approval.schemas.approval import ApprovalSubmit, ApprovalAction
from app.attendance_v2.services.dirty_queue_service import DirtyQueueService
import uuid

class ApprovalService:
    def __init__(self, db):
        self.db = db
        self.repo = ApprovalRepository(db)

    def _utc_now(self):
        return datetime.now(timezone.utc)

    async def submit_request(self, data: ApprovalSubmit) -> ApprovalModel:
        # Resolve the actual reporting manager securely
        from bson import ObjectId
        
        emp_hist = await self.db.employee_employment_histories.find_one({
            "employeeId": data.employeeId,
            "isCurrent": True,
            "deletedAt": None
        })
        
        if not emp_hist:
            raise HTTPException(status_code=400, detail="Employee employment history not found")
            
        manager_ref = emp_hist.get("reportingManagerEmployeeId") or emp_hist.get("reportingManagerId")
        if not manager_ref:
            raise HTTPException(status_code=400, detail="Reporting manager not mapped for this employee")
            
        manager_uuid = None
        
        # Check if it's an ObjectId (from V1 wizard)
        if isinstance(manager_ref, str) and len(manager_ref) == 24:
            try:
                manager_doc = await self.db.employees.find_one({"_id": ObjectId(manager_ref)})
                if manager_doc:
                    manager_uuid = manager_doc.get("employeeId")
            except Exception:
                pass
        
        # If not resolved via ObjectId, maybe it's already a UUID or we just query by employeeId
        if not manager_uuid:
            manager_doc = await self.db.employees.find_one({"employeeId": manager_ref})
            if manager_doc:
                manager_uuid = manager_doc.get("employeeId")
                
        if not manager_uuid:
            raise HTTPException(status_code=400, detail="Reporting manager identity could not be resolved")

        model = ApprovalModel(
            employeeId=data.employeeId,
            reportingManagerEmployeeId=manager_uuid,
            approvalType=data.approvalType,
            status="PENDING",
            requestData=data.requestData,
            remarks=data.remarks,
            createdAt=self._utc_now()
        )
        return await self.repo.create(model.model_dump(by_alias=True, exclude_none=True))

    async def execute_action(self, approval_id: str, action_data: ApprovalAction) -> ApprovalModel:
        approval = await self.repo.get_by_id(approval_id)
        if not approval:
            raise HTTPException(status_code=404, detail="Approval request not found")
            
        action = action_data.action.upper()
        if action == "APPROVE":
            approval.status = "APPROVED"
            
            # Resolve employeeCode
            employee = await self.db.employees.find_one({"employeeId": approval.employeeId})
            if not employee or not employee.get("employeeCode"):
                raise HTTPException(status_code=400, detail="Employee or employeeCode not found")
            emp_code = employee.get("employeeCode")
            
            # Phase 7: Generate synthetic logs for Miss Punch / Mobile Punch
            if approval.approvalType in ["Miss Punch", "Mobile Punch"]:
                punch_time_str = approval.requestData.get("punchTime", self._utc_now().isoformat())
                punch_time = datetime.fromisoformat(punch_time_str.replace("Z", "+00:00"))
                
                synthetic_log = {
                    "fingerprint": f"APPROVAL_{approval_id}",
                    "empId": emp_code,
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
                
            # Queue for attendance processing
            dirty_queue = DirtyQueueService(self.db)
            
            # Determine processing range based on approval type
            # Leaves/OD might have fromDate and toDate
            target_from = approval.requestData.get("fromDate", approval.requestData.get("date", approval.requestData.get("punchTime", self._utc_now().isoformat())))
            target_to = approval.requestData.get("toDate", target_from)
            
            await dirty_queue.push(
                employee_id=approval.employeeId,
                employee_code=emp_code,
                from_date=target_from,
                to_date=target_to,
                reason=f"Approval {approval.approvalType} APPROVED",
                trigger="APPROVAL"
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
            
        updated = await self.repo.update(approval_id, approval.model_dump(by_alias=True, exclude={"id"}))
        if updated:
            enriched = await self._enrich_approvals_with_employee_info([updated])
            return enriched[0]
        return updated

    async def _enrich_approvals_with_employee_info(self, approvals):
        if not approvals:
            return approvals
            
        emp_ids = list(set(a.employeeId for a in approvals))
        employees_cursor = self.db.employees.find({"employeeId": {"$in": emp_ids}})
        employees = await employees_cursor.to_list(None)
        emp_map = {e.get("employeeId"): e for e in employees}
        
        personals_cursor = self.db.employee_personals.find({"employeeId": {"$in": emp_ids}, "isCurrent": True})
        personals = await personals_cursor.to_list(None)
        personal_map = {p.get("employeeId"): p for p in personals}
        
        for a in approvals:
            emp = emp_map.get(a.employeeId)
            if emp:
                a.employeeCode = emp.get("employeeCode")
            
            personal = personal_map.get(a.employeeId)
            if personal and (personal.get("firstName") or personal.get("lastName")):
                first = personal.get("firstName", "")
                last = personal.get("lastName", "")
                a.employeeName = f"{first} {last}".strip()
            elif a.employeeCode:
                a.employeeName = a.employeeCode
                
        return approvals

    async def get_manager_inbox(self, manager_employee_id: str, status: str = None):
        approvals = await self.repo.get_by_manager(manager_employee_id, status)
        return await self._enrich_approvals_with_employee_info(approvals)
        
    async def get_employee_requests(self, emp_id: str, status: str = None):
        approvals = await self.repo.get_by_employee(emp_id, status)
        return await self._enrich_approvals_with_employee_info(approvals)
