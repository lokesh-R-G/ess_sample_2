from pydantic import BaseModel
from typing import Optional

class LeaveReservationCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveReservationUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveReservationResponse(LeaveReservationCreate):
    id: str
