from motor.motor_asyncio import AsyncIOMotorDatabase
from app.compliance.repositories.base_repository import BaseRepository
from app.compliance.models.income_tax_slab import IncomeTaxSlabModel

class IncomeTaxSlabRepository(BaseRepository[IncomeTaxSlabModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'income_tax_slabs', IncomeTaxSlabModel)
