from motor.motor_asyncio import AsyncIOMotorDatabase
from app.workflow.repositories.base_repository import BaseRepository
from app.workflow.models.workflow_history import WorkflowHistoryModel

class WorkflowHistoryRepository(BaseRepository[WorkflowHistoryModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'workflow_history', WorkflowHistoryModel)
