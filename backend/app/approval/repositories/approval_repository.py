from app.core.repositories.base_repository import BaseRepository
from app.approval.models.approval import ApprovalModel
from typing import List

class ApprovalRepository(BaseRepository[ApprovalModel]):
    def __init__(self, db):
        super().__init__(db, "approvals", ApprovalModel)
        
    async def get_by_manager(self, manager_employee_id: str, status: str = None, allowed_reporting_employee_ids: List[str] = None) -> List[ApprovalModel]:
        from app.services.reporting_hierarchy_service import get_manager_identifiers
        manager_ids = await get_manager_identifiers(self.db, manager_employee_id)
        
        query = {"reportingManagerEmployeeId": {"$in": manager_ids}}
        if allowed_reporting_employee_ids is not None:
            query["employeeId"] = {"$in": allowed_reporting_employee_ids}
        if status:
            query["status"] = status
        cursor = self.collection.find(query).sort([("createdAt", -1)])
        docs = await cursor.to_list(length=None)
        return [self.model_class(**self._prepare_doc(doc)) for doc in docs]
        
    async def get_by_employee(self, emp_id: str, status: str = None) -> List[ApprovalModel]:
        query = {"employeeId": emp_id}
        if status:
            query["status"] = status
        cursor = self.collection.find(query).sort([("createdAt", -1)])
        docs = await cursor.to_list(length=None)
        return [self.model_class(**self._prepare_doc(doc)) for doc in docs]
