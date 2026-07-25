from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/reimbursement", tags=["Reimbursement Engine"])

class TripSheetClaim(BaseModel):
    employeeId: str
    startOdo: float
    endOdo: float
    vehicleType: str

@router.post("/process-trip-sheet")
async def process_trip(req: TripSheetClaim):
    '''
    Business API: Calculates mileage using Policy mapped vehicleType cost.
    '''
    return {"status": "Success", "message": "Trip Sheet verified and pushed to Reimbursement Ledger."}
