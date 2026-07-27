from motor.motor_asyncio import AsyncIOMotorDatabase
from app.onboarding.repositories.base_repository import BaseRepository
from app.onboarding.models.onboarding_task import OnboardingTaskModel

class OnboardingTaskRepository(BaseRepository[OnboardingTaskModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'onboarding_tasks', OnboardingTaskModel)
