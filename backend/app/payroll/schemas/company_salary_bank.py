from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class CompanySalaryBankAccountModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    companyCode: str
    accountHolderName: str
    bankName: str
    accountNumber: str
    ifscCode: str
    branchName: Optional[str] = None
    accountType: Optional[str] = None
    status: str = "Active"
    isPrimary: bool = False
    branchIds: List[str] = Field(default_factory=list)
    createdAt: datetime
    updatedAt: datetime
    createdBy: str
    updatedBy: str

class CompanySalaryBankAccountCreate(BaseModel):
    companyCode: str
    accountHolderName: str
    bankName: str
    accountNumber: str
    ifscCode: str
    branchName: Optional[str] = None
    accountType: Optional[str] = None
    status: str = "Active"
    isPrimary: bool = False
    branchIds: List[str] = Field(default_factory=list)

class CompanySalaryBankAccountUpdate(BaseModel):
    accountHolderName: Optional[str] = None
    bankName: Optional[str] = None
    accountNumber: Optional[str] = None
    ifscCode: Optional[str] = None
    branchName: Optional[str] = None
    accountType: Optional[str] = None
    status: Optional[str] = None
    isPrimary: Optional[bool] = None
    branchIds: Optional[List[str]] = None

class CompanySalaryBankAccountResponse(CompanySalaryBankAccountModel):
    pass
