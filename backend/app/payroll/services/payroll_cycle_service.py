from datetime import datetime
from typing import Optional, List, Dict, Any
from app.domain_models import PayrollCycle, PayrollSettings
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

class PayrollCycleService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def create_cycle(self, name: str, start_date: datetime, end_date: datetime) -> PayrollCycle:
        # Check for duplicate cycle overlapping dates
        # Payroll cycles are global periods. Company scope belongs to PayrollRun.
        query = {
            "$or": [
                {"startDate": {"$lte": end_date}, "endDate": {"$gte": start_date}}
            ]
        }
        existing = await self.db.payroll_cycles.find_one(query)
        if existing:
            raise ValueError("A payroll cycle already exists for this date range.")

        cycle = PayrollCycle(
            name=name,
            startDate=start_date,
            endDate=end_date
        )
        doc = cycle.model_dump(by_alias=True, exclude_none=True)
        result = await self.db.payroll_cycles.insert_one(doc)
        cycle.id = str(result.inserted_id)
        return cycle

    async def get_cycle(self, cycle_id: str) -> Optional[PayrollCycle]:
        doc = await self.db.payroll_cycles.find_one({"_id": ObjectId(cycle_id)})
        if not doc:
            return None
        doc["_id"] = str(doc["_id"])
        return PayrollCycle(**doc)

    async def list_cycles(self) -> List[PayrollCycle]:
        cursor = self.db.payroll_cycles.find({}).sort("startDate", -1)
        cycles = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            cycles.append(PayrollCycle(**doc))
        return cycles
