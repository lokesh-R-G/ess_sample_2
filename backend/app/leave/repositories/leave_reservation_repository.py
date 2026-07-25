from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.leave_reservation import LeaveReservationModel

class LeaveReservationRepository(BaseRepository[LeaveReservationModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_reservations", LeaveReservationModel)
