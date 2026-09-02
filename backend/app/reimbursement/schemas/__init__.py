from pydantic import BaseModel, Field
from typing import Optional, List

class TripSheetRequest(BaseModel):
    tripDate: str
    fromLocation: str
    toLocation: str
    tripType: str
    startOdometer: float
    endOdometer: float
    claimedDistance: float
    description: str
    attachmentIds: List[str] = Field(default_factory=list)

class CashVoucherRequest(BaseModel):
    voucherDate: str
    expenseCategory: str
    vendorName: Optional[str] = None
    billNumber: Optional[str] = None
    claimedAmount: float
    description: str

class AttachmentResponse(BaseModel):
    id: str
    fileName: str
    mimeType: str
    uploadedBy: str

class AttachmentUploadRequest(BaseModel):
    fileName: str
    mimeType: str
    dataBase64: str


class TripSheetResponse(BaseModel):
    id: str
    claimId: str
    tripDate: str
    fromLocation: str
    toLocation: str
    tripType: str
    startOdometer: float
    endOdometer: float
    claimedDistance: float
    calculatedDistance: float
    ratePerKm: float
    calculatedAmount: float

class ReimbursementClaimResponse(BaseModel):
    id: str
    employeeId: str
    companyId: str
    claimType: str
    description: str
    status: str
    calculatedAmount: float
    approvedAmount: float
    hodStatus: Optional[str]
    hodRejectionReason: Optional[str]
    accountsStatus: Optional[str]
    accountsRejectionReason: Optional[str]
    createdAt: str
    
    tripSheet: Optional[TripSheetResponse] = None
    attachments: List[AttachmentResponse] = []
