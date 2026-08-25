from datetime import datetime


class PayrollRunService:
    """Company-specific processing state for one global payroll cycle."""

    def __init__(self, db):
        self.db = db

    async def get_or_create(self, cycle_id: str, company_id: str) -> dict:
        run = await self.db.payroll_runs.find_one({"cycleId": cycle_id, "companyId": company_id})
        if run:
            run["_id"] = str(run["_id"])
            return run
        now = datetime.utcnow()
        document = {"cycleId": cycle_id, "companyId": company_id, "status": "DRAFT", "attendanceSummary": {}, "calculationSummary": {}, "createdAt": now, "updatedAt": now}
        result = await self.db.payroll_runs.insert_one(document)
        document["_id"] = str(result.inserted_id)
        return document

    async def get(self, cycle_id: str, company_id: str) -> dict | None:
        run = await self.db.payroll_runs.find_one({"cycleId": cycle_id, "companyId": company_id})
        if run:
            run["_id"] = str(run["_id"])
        return run

    async def update(self, cycle_id: str, company_id: str, **changes) -> dict:
        changes["updatedAt"] = datetime.utcnow()
        await self.db.payroll_runs.update_one({"cycleId": cycle_id, "companyId": company_id}, {"$set": changes})
        return await self.get(cycle_id, company_id)
