from app.core.repositories.base_repository import BaseRepository
from app.approval.models.approval import ApprovalModel
from typing import List

class ApprovalRepository(BaseRepository[ApprovalModel]):
    def __init__(self, db):
        super().__init__(db, "approvals", ApprovalModel)
        
    async def get_by_manager(self, manager_emp_id: str, status: str = None) -> List[ApprovalModel]:
        query = {"reportingManagerEmployeeId": manager_emp_id}
        if status:
            query["status"] = status
        cursor = self.collection.find(query).sort([("createdAt", -1)])
        docs = await cursor.to_list(length=None)
        return [self.model_class(**doc) for doc in docs]
        
    async def get_by_employee(self, emp_id: str, status: str = None) -> List[ApprovalModel]:
        query = {"employeeId": emp_id}
        if status:
            query["status"] = status
        cursor = self.collection.find(query).sort([("createdAt", -1)])
        docs = await cursor.to_list(length=None)
        return [self.model_class(**doc) for doc in docs]
