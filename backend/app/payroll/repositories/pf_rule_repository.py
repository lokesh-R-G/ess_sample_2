from typing import Optional, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.domain_models import PFRule
from app.payroll.repositories.base_repository import BaseRepository

class PFRuleRepository(BaseRepository[PFRule]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "pf_rules", PFRule)

    async def get_current_policy(self, policy_code: str = "DEFAULT_PF") -> Optional[PFRule]:
        doc = await self.collection.find_one({"policyCode": policy_code, "isCurrent": True})
        if doc:
            doc["_id"] = str(doc["_id"])
            return PFRule(**doc)
        return None

    async def resolve_policy_by_date(self, target_date: datetime, policy_code: str = "DEFAULT_PF") -> Optional[PFRule]:
        query = {
            "policyCode": policy_code,
            "effectiveFrom": {"$lte": target_date},
            "$or": [
                {"effectiveTo": None},
                {"effectiveTo": {"$gt": target_date}}
            ]
        }
        doc = await self.collection.find_one(query, sort=[("version", -1)])
        if doc:
            doc["_id"] = str(doc["_id"])
            return PFRule(**doc)
        return None

    async def create_initial_policy(self, pf_rule: PFRule) -> PFRule:
        pf_rule.version = 1
        pf_rule.isCurrent = True
        pf_rule.effectiveTo = None
        doc = pf_rule.model_dump(by_alias=True, exclude={"id"})
        result = await self.collection.insert_one(doc)
        pf_rule.id = str(result.inserted_id)
        return pf_rule

    async def update_policy_version(self, new_effective_from: datetime, updated_rule: PFRule, policy_code: str = "DEFAULT_PF") -> PFRule:
        # Find current version
        current_version = await self.get_current_policy(policy_code)
        if not current_version:
            raise ValueError(f"No active policy found for {policy_code}")

        if new_effective_from <= current_version.effectiveFrom:
            raise ValueError("New effectiveFrom must be greater than current effectiveFrom")

        # Expire current version exactly at new_effective_from
        from bson import ObjectId
        await self.collection.update_one(
            {"_id": ObjectId(current_version.id)},
            {"$set": {"isCurrent": False, "effectiveTo": new_effective_from}}
        )

        # Create new version
        updated_rule.version = current_version.version + 1
        updated_rule.effectiveFrom = new_effective_from
        updated_rule.effectiveTo = None
        updated_rule.isCurrent = True
        updated_rule.policyCode = policy_code
        
        doc = updated_rule.model_dump(by_alias=True, exclude={"id"})
        result = await self.collection.insert_one(doc)
        updated_rule.id = str(result.inserted_id)
        return updated_rule
