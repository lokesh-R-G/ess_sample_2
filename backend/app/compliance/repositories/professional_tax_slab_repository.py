from motor.motor_asyncio import AsyncIOMotorDatabase
from app.compliance.repositories.base_repository import BaseRepository
from app.compliance.models.professional_tax_slab import ProfessionalTaxSlabModel

class ProfessionalTaxSlabRepository(BaseRepository[ProfessionalTaxSlabModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'professional_tax_slabs', ProfessionalTaxSlabModel)
