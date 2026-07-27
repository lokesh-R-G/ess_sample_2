from motor.motor_asyncio import AsyncIOMotorDatabase
from app.recruitment.repositories.base_repository import BaseRepository
from app.recruitment.models.offer_letter import OfferLetterModel

class OfferLetterRepository(BaseRepository[OfferLetterModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'offer_letters', OfferLetterModel)
