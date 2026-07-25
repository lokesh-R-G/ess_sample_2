from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.cash_voucher_claim import CashVoucherClaimModel

class CashVoucherClaimRepository(BaseRepository[CashVoucherClaimModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "cash_voucher_claims", CashVoucherClaimModel)
