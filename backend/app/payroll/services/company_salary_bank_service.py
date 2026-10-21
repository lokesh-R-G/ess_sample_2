from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.payroll.schemas.company_salary_bank import (
    CompanySalaryBankAccountModel,
    CompanySalaryBankAccountCreate,
    CompanySalaryBankAccountUpdate
)

class CompanySalaryBankService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = self.db.company_salary_banks

    async def _enforce_single_primary(self, company_code: str, exclude_id: Optional[str] = None):
        """Ensures that only one bank account per company is primary at a time."""
        query = {"companyCode": company_code, "isPrimary": True}
        if exclude_id:
            query["_id"] = {"$ne": ObjectId(exclude_id)}
            
        await self.collection.update_many(
            query,
            {"$set": {"isPrimary": False, "updatedAt": datetime.utcnow()}}
        )

    async def create(self, data: CompanySalaryBankAccountCreate, created_by: str) -> CompanySalaryBankAccountModel:
        if data.isPrimary:
            await self._enforce_single_primary(data.companyCode)
            
        doc = data.model_dump()
        doc["createdAt"] = datetime.utcnow()
        doc["updatedAt"] = datetime.utcnow()
        doc["createdBy"] = created_by
        doc["updatedBy"] = created_by
        
        result = await self.collection.insert_one(doc)
        doc["_id"] = str(result.inserted_id)
        return CompanySalaryBankAccountModel(**doc)

    async def get_by_company(self, company_code: str) -> List[CompanySalaryBankAccountModel]:
        cursor = self.collection.find({"companyCode": company_code})
        results = []
        async for doc in cursor:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            results.append(CompanySalaryBankAccountModel(**doc))
        return results

    async def get_all(self, company_code: Optional[str] = None) -> List[CompanySalaryBankAccountModel]:
        query = {}
        if company_code:
            query["companyCode"] = company_code
            
        cursor = self.collection.find(query)
        results = []
        async for doc in cursor:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            results.append(CompanySalaryBankAccountModel(**doc))
        return results

    async def get_by_id(self, id: str) -> Optional[CompanySalaryBankAccountModel]:
        doc = await self.collection.find_one({"_id": ObjectId(id)})
        if doc:
            doc["_id"] = str(doc["_id"])
            return CompanySalaryBankAccountModel(**doc)
        return None

    async def update(self, id: str, data: CompanySalaryBankAccountUpdate, updated_by: str) -> Optional[CompanySalaryBankAccountModel]:
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_id(id)

        update_data["updatedAt"] = datetime.utcnow()
        update_data["updatedBy"] = updated_by

        doc = await self.collection.find_one({"_id": ObjectId(id)})
        if not doc:
            raise ValueError("Bank account not found")

        company_code = doc["companyCode"]

        if update_data.get("isPrimary") is True:
            await self._enforce_single_primary(company_code, exclude_id=id)
        elif update_data.get("isPrimary") is False:
            # Optionally prevent unsetting primary if it's the only one, but we'll allow it for now.
            pass

        await self.collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": update_data}
        )
        return await self.get_by_id(id)

    async def set_primary(self, id: str, updated_by: str) -> Optional[CompanySalaryBankAccountModel]:
        return await self.update(id, CompanySalaryBankAccountUpdate(isPrimary=True), updated_by)
