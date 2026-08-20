from typing import Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.domain_models import ESIRule
from app.payroll.repositories.base_repository import BaseRepository

class ESIRuleRepository(BaseRepository[ESIRule]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "esi_rules", ESIRule)
        
    async def get_current_policy(self, policy_code: str = "DEFAULT_ESI") -> Optional[ESIRule]:
        doc = await self.collection.find_one({
            "policyCode": policy_code,
            "isCurrent": True
        })
        if not doc: return None
        doc["_id"] = str(doc["_id"])
        return ESIRule(**doc)

    async def resolve_policy_by_date(self, target_date: datetime, policy_code: str = "DEFAULT_ESI") -> Optional[ESIRule]:
        query = {
            "policyCode": policy_code,
            "effectiveFrom": {"$lte": target_date},
            "$or": [
                {"effectiveTo": None},
                {"effectiveTo": {"$gt": target_date}}
            ]
        }
        
        doc = await self.collection.find_one(query, sort=[("version", -1)])
        if not doc:
            return None
        doc["_id"] = str(doc["_id"])
        return ESIRule(**doc)
        
    async def create_initial_policy(self, rule: ESIRule) -> ESIRule:
        rule.version = 1
        rule.isCurrent = True
        rule.effectiveTo = None
        if not rule.policyCode:
            rule.policyCode = "DEFAULT_ESI"
            
        doc = rule.dict(by_alias=True, exclude={"id"}, exclude_none=True)
        result = await self.collection.insert_one(doc)
        rule.id = str(result.inserted_id)
        return rule

    async def update_policy_version(self, new_effective_from: datetime, updated_rule: ESIRule) -> ESIRule:
        current_version = await self.get_current_policy(updated_rule.policyCode or "DEFAULT_ESI")
        if not current_version:
            raise ValueError("No current policy found to update")
            
        if current_version.effectiveFrom >= new_effective_from:
            raise ValueError("New effectiveFrom must be greater than current effectiveFrom")

        # Expire current version exactly at new_effective_from
        from bson import ObjectId
        await self.collection.update_one(
            {"_id": ObjectId(current_version.id)},
            {"$set": {"isCurrent": False, "effectiveTo": new_effective_from}}
        )

        # Insert new version
        updated_rule.version = current_version.version + 1
        updated_rule.isCurrent = True
        updated_rule.effectiveFrom = new_effective_from
        updated_rule.effectiveTo = None
        if not updated_rule.policyCode:
            updated_rule.policyCode = "DEFAULT_ESI"
            
        doc = updated_rule.dict(by_alias=True, exclude={"id"}, exclude_none=True)
        result = await self.collection.insert_one(doc)
        updated_rule.id = str(result.inserted_id)
        return updated_rule
