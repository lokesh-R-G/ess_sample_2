from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class DailyAttendanceModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    name: Optional[str] = None
    status: str = "Active"
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    deletedAt: Optional[datetime] = None
    deletedBy: Optional[str] = None
    
    # Audit and Tracing (Phases K, L, M)
    calculationTrace: List[str] = Field(default_factory=list)
    policySnapshot: Dict[str, Any] = Field(default_factory=dict)
    engineVersion: str = "1.0.0"
    replayCount: int = 0
