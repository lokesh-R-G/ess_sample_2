from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from app.attendance_v2.repositories.correction_log_repository import CorrectionLogRepository
from app.attendance_v2.schemas.correction_log import CorrectionLogCreate
from app.employee.repositories.base_repository import BaseRepository
from app.attendance_v2.services.dirty_queue_service import DirtyQueueService
from datetime import datetime, timezone

class CorrectionLogService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = CorrectionLogRepository(db)
        self.dirty_queue = DirtyQueueService(db)

    async def get_all(self, skip: int = 0, limit: int = 100) -> dict:
        return await self.repo.get_all(skip=skip, limit=limit)
        
    async def get_history(self, entity_code: str) -> List[dict]:
        return await self.repo.get_history("entityCode", entity_code)

    async def apply_correction(self, data: CorrectionLogCreate, current_user_id: str) -> dict:
        # 1. We must create a new Version of the policy using the normal BaseRepository logic.
        # But this is a historical correction, so we must insert it in the past.
        # The user requested that the admin cannot change the effectiveFrom/effectiveTo of the historical version.
        # So we create a new Version of the policy that exactly overlaps the historical period, BUT with a higher version number.
        
        collection_mapping = {
            "AttendancePolicy": "attendance_policies",
            "WeeklyOffPolicy": "weekly_off_policies",
            "Shift": "shifts",
            "HolidayCalendar": "holiday_calendars",
            "Holiday": "holiday_dates"
        }
        
        coll_name = collection_mapping.get(data.entityType)
        if not coll_name:
            raise ValueError(f"Unknown entityType: {data.entityType}")
            
        collection = self.db[coll_name]
        
        # Determine code field
        code_field_mapping = {
            "AttendancePolicy": "attendancePolicyCode",
            "WeeklyOffPolicy": "weeklyOffPolicyCode",
            "Shift": "shiftCode",
            "HolidayCalendar": "holidayCalendarCode",
            "Holiday": "holidayCode"
        }
        code_field = code_field_mapping.get(data.entityType)
        
        # 1. Fetch original version
        original_doc = await collection.find_one({
            code_field: data.entityCode,
            "version": data.originalVersion
        })
        
        if not original_doc:
            raise ValueError(f"Original version {data.originalVersion} not found for {data.entityCode}")
            
        # 2. Find highest version to avoid collisions
        highest_doc = await collection.find_one({code_field: data.entityCode}, sort=[("version", -1)])
        new_version = highest_doc["version"] + 1 if highest_doc else data.originalVersion + 1
        
        # 3. Create corrected document. It is NOT isCurrent unless the original was isCurrent.
        # We explicitly preserve effectiveFrom/effectiveTo
        new_doc = {**original_doc, **data.changedFields}
        new_doc.pop("_id", None)
        new_doc["version"] = new_version
        
        # Ensure dates are kept exact
        new_doc["effectiveFrom"] = original_doc.get("effectiveFrom")
        new_doc["effectiveTo"] = original_doc.get("effectiveTo")
        
        # Update audit
        now = datetime.now(timezone.utc)
        new_doc["updatedAt"] = now
        new_doc["updatedBy"] = current_user_id
        
        # If the original was the current version, mark it false, make new one current
        if original_doc.get("isCurrent"):
            await collection.update_one({"_id": original_doc["_id"]}, {"$set": {"isCurrent": False}})
            new_doc["isCurrent"] = True
        else:
            new_doc["isCurrent"] = False
            
        # Save new document
        result = await collection.insert_one(new_doc)
        
        # 4. Save Correction Log
        correction_data = data.model_dump()
        correction_data["correctionVersion"] = new_version
        correction = await self.repo.create_correction(correction_data, created_by=current_user_id)
        
        # 5. Trigger Recalculation by putting all affected employees in Dirty Queue
        # We don't have the explicit list of employees here easily unless we query employment mappings.
        # For simplicity, we queue all active employees for that date range.
        # In a real heavy system we'd filter by shiftCode/policyCode.
        active_employees = await self.db.employees.find({"status": "Active"}).to_list(None)
        
        # If effectiveTo is None, we queue until today
        calc_to = original_doc.get("effectiveTo")
        if not calc_to:
            calc_to = datetime.now()
            
        for emp in active_employees:
            await self.dirty_queue.mark_dirty(
                emp_id=emp["employeeId"],
                from_date=original_doc.get("effectiveFrom"),
                to_date=calc_to,
                source="HISTORICAL_CORRECTION",
                reason=data.reason
            )
            
        return correction.model_dump()
