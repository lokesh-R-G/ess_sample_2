from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class PermissionLedgerModel(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)
    
    id: Optional[str] = Field(default=None, alias="_id")
    employeeId: str
    employeeCode: Optional[str] = None
    month: str # Format: "YYYY-MM"
    
    # Allowances
    freeAllowanceMinutes: float = 0.0
    
    # Consumed
    consumedMinutes: float = 0.0
    
    # Excess Calculations
    currentExcessMinutes: float = 0.0
    previousCarriedMinutes: float = 0.0
    accumulatedExcessMinutes: float = 0.0
    
    # LOP Application
    lopGenerated: float = 0.0
    remainingCarriedMinutes: float = 0.0
    
    # Audit fields
    updatedAt: Optional[datetime] = None
