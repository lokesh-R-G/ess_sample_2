from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class EmployeeBankModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    employeeId: str
    bankName: Optional[str] = None
    branchName: Optional[str] = None
    accountNumber: Optional[str] = None
    ifscCode: Optional[str] = None
    accountType: Optional[str] = None
    nameAsPerBank: Optional[str] = None
    status: str = "Active"
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    deletedAt: Optional[datetime] = None
    deletedBy: Optional[str] = None
