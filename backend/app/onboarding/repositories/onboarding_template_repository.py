from motor.motor_asyncio import AsyncIOMotorDatabase
from app.onboarding.repositories.base_repository import BaseRepository
from app.onboarding.models.onboarding_template import OnboardingTemplateModel

class OnboardingTemplateRepository(BaseRepository[OnboardingTemplateModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'onboarding_templates', OnboardingTemplateModel)
