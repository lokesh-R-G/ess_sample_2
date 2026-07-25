from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.leave_reservation import LeaveReservationCreate, LeaveReservationUpdate

class LeaveReservationValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["leave_reservations"]
        
    async def validate_create(self, data: LeaveReservationCreate):
        pass
            
    async def validate_update(self, id: str, data: LeaveReservationUpdate):
        pass 
