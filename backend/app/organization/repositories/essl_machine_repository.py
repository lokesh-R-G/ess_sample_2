from motor.motor_asyncio import AsyncIOMotorDatabase
from app.organization.repositories.base_repository import BaseRepository
from app.organization.models.essl_machine import ESSLMachineModel

class ESSLMachineRepository(BaseRepository[ESSLMachineModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "essl_machines", ESSLMachineModel)
