import uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.reimbursement.schemas import TripSheetRequest
from app.reimbursement_policy.models.trip_allowance_policy import TripAllowancePolicyModel

class ReimbursementService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def get_active_trip_allowance(self, company_id: str, date_str: str) -> TripAllowancePolicyModel:
        print(f"DEBUG: get_active_trip_allowance called with company_id={company_id}, date_str={date_str}")
        cursor = self.db.trip_allowance_policies.find({
            "companyId": company_id,
            "policyCode": "TRIP_ALL_DEFAULT",
            "effectiveFrom": {"$lte": date_str},
            "$or": [{"effectiveTo": None}, {"effectiveTo": {"$gt": date_str}}]
        }).sort("version", -1)
        
        docs = await cursor.to_list(length=1)
        if not docs:
            raise ValueError("No active Trip Allowance Policy found for the company on this date.")
        docs[0]["_id"] = str(docs[0]["_id"])
        return TripAllowancePolicyModel(**docs[0])

    async def create_trip_sheet_claim(self, employee_id: str, company_id: str, branch_id: str, req: TripSheetRequest) -> dict:
        policy = await self.get_active_trip_allowance(company_id, req.tripDate)
        
        if req.tripType not in policy.allowedTripTypes:
            raise ValueError(f"Trip type {req.tripType} is not allowed under current policy.")
            
        calculated_distance = req.endOdometer - req.startOdometer
        if calculated_distance <= 0:
            raise ValueError("End odometer must be strictly greater than start odometer.")
            
        calculated_amount = calculated_distance * policy.ratePerKm
        
        claim_id = str(uuid.uuid4())
        
        trip_doc = {
            "claimId": claim_id,
            "tripDate": req.tripDate,
            "fromLocation": req.fromLocation,
            "toLocation": req.toLocation,
            "tripType": req.tripType,
            "startOdometer": req.startOdometer,
            "endOdometer": req.endOdometer,
            "claimedDistance": req.claimedDistance,
            "calculatedDistance": calculated_distance,
            "ratePerKm": policy.ratePerKm,
            "calculatedAmount": calculated_amount
        }
        
        reimbursement_doc = {
            "id": claim_id,
            "employeeId": employee_id,
            "companyId": company_id,
            "claimType": "TRIP_SHEET",
            "description": req.description,
            "status": "SUBMITTED",
            "calculatedAmount": calculated_amount,
            "approvedAmount": 0.0,
            "hodStatus": None,
            "accountsStatus": None,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "tripSheet": trip_doc,
            "attachments": []
        }
        
        await self.db.reimbursement_claims.insert_one(reimbursement_doc)
        
        return {
            "claimId": claim_id,
            "status": "SUBMITTED",
            "calculatedAmount": calculated_amount
        }

    async def get_my_claims(self, employee_id: str) -> list:
        cursor = self.db.reimbursement_claims.find({"employeeId": employee_id})
        return await self.format_claims(cursor)

    async def get_hod_pending_claims(self, company_id: str, hod_employee_id: str) -> list:
        # Just return SUBMITTED claims for simplicity. 
        cursor = self.db.reimbursement_claims.find({"companyId": company_id, "status": "SUBMITTED"})
        return await self.format_claims(cursor)

    async def process_hod_action(self, claim_id: str, hod_id: str, action: str, reason: str = None) -> dict:
        claim = await self.db.reimbursement_claims.find_one({"id": claim_id})
        if not claim:
            raise ValueError("Claim not found.")
            
        employee = await self.db.employees.find_one({"employeeId": claim["employeeId"], "reportingManager": hod_id})
        if not employee:
            raise ValueError("Unauthorized: You are not the reporting manager for this employee.")
            
        status = "HOD_APPROVED" if action == "APPROVE" else "HOD_REJECTED"
        await self.db.reimbursement_claims.update_one(
            {"id": claim_id},
            {"$set": {"hodStatus": action, "status": status, "hodRejectionReason": reason}}
        )
        return {"status": "Success", "claimId": claim_id}

    async def get_accounts_pending_claims(self, company_id: str) -> list:
        cursor = self.db.reimbursement_claims.find({"companyId": company_id, "status": "HOD_APPROVED"})
        return await self.format_claims(cursor)

    async def process_accounts_action(self, claim_id: str, accounts_id: str, action: str, reason: str = None) -> dict:
        status = "APPROVED" if action == "APPROVE" else "REJECTED"
        await self.db.reimbursement_claims.update_one(
            {"id": claim_id},
            {"$set": {"accountsStatus": action, "status": status, "accountsRejectionReason": reason}}
        )
        return {"status": "Success", "claimId": claim_id}
        
    async def format_claims(self, cursor) -> list:
        docs = await cursor.to_list(length=100)
        for doc in docs:
            doc.pop("_id", None)
        return docs
