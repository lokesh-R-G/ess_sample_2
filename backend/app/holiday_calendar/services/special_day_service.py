from datetime import datetime, timezone
import uuid
from typing import List, Optional, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.holiday_calendar.models.special_day import SpecialDayModel
from app.holiday_calendar.schemas.special_day import SpecialDayCreate, SpecialDayUpdate

class SpecialDayService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def get_by_id(self, config_id: str) -> Optional[Dict[str, Any]]:
        query = {"$or": [{"specialDayId": config_id}]}
        try:
            query["$or"].append({"_id": ObjectId(config_id)})
        except Exception:
            pass
        doc = await self.db.special_days.find_one(query)
        if not doc:
            return None
        return self._format_doc(doc)

    async def list_configurations(
        self,
        company_id: Optional[str] = None,
        date_val: Optional[str] = None,
        branch_id: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        query: Dict[str, Any] = {}
        if company_id:
            query["companyId"] = company_id
        if date_val:
            query["date"] = date_val
        if status:
            query["status"] = status
        if branch_id:
            query["$or"] = [
                {"applicability": "All Branches"},
                {"selectedBranchIds": branch_id}
            ]

        total = await self.db.special_days.count_documents(query)
        cursor = self.db.special_days.find(query).sort([("date", -1), ("createdAt", -1)]).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)

        # Collect branch names
        all_branch_ids = set()
        for d in docs:
            for b_id in d.get("selectedBranchIds", []):
                all_branch_ids.add(b_id)

        branch_map = {}
        if all_branch_ids:
            b_oids = []
            for b in all_branch_ids:
                try:
                    b_oids.append(ObjectId(b))
                except Exception:
                    b_oids.append(b)
            branches = await self.db.branchs.find({"_id": {"$in": b_oids}}).to_list(None)
            for b in branches:
                branch_map[str(b["_id"])] = b.get("name") or b.get("code") or str(b["_id"])

        formatted = []
        for d in docs:
            item = self._format_doc(d)
            item["selectedBranchNames"] = [branch_map.get(bid, bid) for bid in item.get("selectedBranchIds", [])]
            formatted.append(item)

        return {"total": total, "data": formatted}

    async def validate_conflicts(
        self,
        company_id: str,
        date_str: str,
        applicability: str,
        selected_branch_ids: List[str],
        exclude_id: Optional[str] = None
    ):
        """
        Validate that:
        1. Selected branches belong to the company/tenant.
        2. No conflicting active special day exists for the same date and overlapping branch scope.
        """
        if applicability == "Selected Branches":
            if not selected_branch_ids:
                raise ValueError("At least one branch must be selected.")
            
            b_oids = []
            for b in selected_branch_ids:
                try:
                    b_oids.append(ObjectId(b))
                except Exception:
                    b_oids.append(b)
            
            branches = await self.db.branchs.find({"_id": {"$in": b_oids}}).to_list(None)
            found_ids = {str(b["_id"]) for b in branches}
            for b in branches:
                if str(b.get("companyId")) != str(company_id):
                    raise ValueError(f"Branch '{b.get('name', b.get('_id'))}' does not belong to authorized company '{company_id}'.")
            
            for b_id in selected_branch_ids:
                if b_id not in found_ids:
                    raise ValueError(f"Branch ID '{b_id}' does not exist.")

        conflict_query: Dict[str, Any] = {
            "companyId": company_id,
            "date": date_str,
            "status": "Active"
        }
        if exclude_id:
            try:
                conflict_query["_id"] = {"$ne": ObjectId(exclude_id)}
            except Exception:
                conflict_query["specialDayId"] = {"$ne": exclude_id}

        existing_active = await self.db.special_days.find(conflict_query).to_list(None)

        for existing in existing_active:
            ex_app = existing.get("applicability")
            ex_branches = set(existing.get("selectedBranchIds", []))
            ex_name = existing.get("eventName", "Existing Configuration")
            ex_type = existing.get("dayType")

            if applicability == "All Branches" or ex_app == "All Branches":
                raise ValueError(
                    f"Conflict detected on {date_str}: '{ex_name}' ({ex_type}) is already active with "
                    f"scope '{ex_app}'. Cannot create overlapping configuration."
                )

            common_branches = set(selected_branch_ids).intersection(ex_branches)
            if common_branches:
                raise ValueError(
                    f"Conflict detected on {date_str}: '{ex_name}' ({ex_type}) already applies to "
                    f"overlapping branch(es) {list(common_branches)}."
                )

    async def create(self, data: SpecialDayCreate, company_id: str, current_user_id: str) -> Dict[str, Any]:
        await self.validate_conflicts(
            company_id=company_id,
            date_str=data.date,
            applicability=data.applicability,
            selected_branch_ids=data.selectedBranchIds or []
        )

        now = datetime.now(timezone.utc)
        special_day_id = f"SD-{uuid.uuid4().hex[:8].upper()}"

        # Resolve shift details if shiftId was selected
        start_time = data.startTime
        end_time = data.endTime
        expected_working_hours = data.expectedWorkingHours
        is_cross_midnight = data.isCrossMidnight
        break_start = data.breakStartTime
        break_end = data.breakEndTime
        shift_code = data.shiftCode

        if data.dayType == "Sudden Shift Change":
            if data.shiftId:
                try:
                    s_query = {"$or": [{"_id": ObjectId(data.shiftId)}, {"_id": data.shiftId}, {"shiftCode": data.shiftId}]}
                except Exception:
                    s_query = {"$or": [{"_id": data.shiftId}, {"shiftCode": data.shiftId}]}
                shift_doc = await self.db.shifts.find_one(s_query)
                if shift_doc:
                    shift_code = shift_doc.get("shiftCode")
                    start_time = start_time or shift_doc.get("startTime")
                    end_time = end_time or shift_doc.get("endTime")
                    is_cross_midnight = shift_doc.get("isCrossMidnight", False)
                    break_start = break_start or shift_doc.get("breakStartTime")
                    break_end = break_end or shift_doc.get("breakEndTime")

            # Validate start/end times exist for Sudden Shift Change
            if not start_time or not end_time:
                raise ValueError("Expected IN Time (startTime) and Expected OUT Time (endTime) are required for Sudden Shift Change.")

            # Calculate expected working hours if not explicitly provided
            if expected_working_hours is None:
                try:
                    t_in = datetime.strptime(start_time[:5], "%H:%M")
                    t_out = datetime.strptime(end_time[:5], "%H:%M")
                    diff_seconds = (t_out - t_in).total_seconds()
                    if diff_seconds < 0 or is_cross_midnight:
                        diff_seconds += 24 * 3600
                    expected_working_hours = round(diff_seconds / 3600.0, 2)
                except Exception:
                    expected_working_hours = 8.0

        elif data.dayType == "Sudden Cutoff":
            if expected_working_hours is None or expected_working_hours <= 0:
                raise ValueError("expectedWorkingHours is required for Sudden Cutoff.")

        doc = {
            "specialDayId": special_day_id,
            "companyId": str(company_id),
            "eventName": data.eventName.strip(),
            "date": data.date,
            "dayType": data.dayType,
            "applicability": data.applicability,
            "selectedBranchIds": data.selectedBranchIds or [],
            "shiftId": data.shiftId,
            "shiftCode": shift_code,
            "startTime": start_time,
            "endTime": end_time,
            "expectedWorkingHours": expected_working_hours if data.dayType in ["Sudden Cutoff", "Sudden Shift Change"] else None,
            "isCrossMidnight": is_cross_midnight,
            "breakStartTime": break_start,
            "breakEndTime": break_end,
            "reason": (data.reason or "").strip() or None,
            "status": "Active",
            "createdBy": current_user_id,
            "createdAt": now,
            "updatedBy": current_user_id,
            "updatedAt": now
        }

        result = await self.db.special_days.insert_one(doc)
        doc["_id"] = result.inserted_id

        # Write audit log
        try:
            await self.db.audit_logs.insert_one({
                "action": "SPECIAL_DAY_CREATED",
                "resource": "special_days",
                "resourceId": special_day_id,
                "companyId": str(company_id),
                "performedBy": current_user_id,
                "timestamp": now,
                "details": {
                    "eventName": data.eventName,
                    "date": data.date,
                    "dayType": data.dayType,
                    "applicability": data.applicability,
                    "startTime": start_time,
                    "endTime": end_time
                }
            })
        except Exception:
            pass

        return self._format_doc(doc)

    async def update(self, config_id: str, data: SpecialDayUpdate, current_user_id: str) -> Optional[Dict[str, Any]]:
        existing = await self.get_by_id(config_id)
        if not existing:
            return None

        update_fields: Dict[str, Any] = {
            "updatedBy": current_user_id,
            "updatedAt": datetime.now(timezone.utc)
        }

        if data.eventName is not None:
            update_fields["eventName"] = data.eventName.strip()
        if data.reason is not None:
            update_fields["reason"] = data.reason.strip()
        if data.startTime is not None:
            update_fields["startTime"] = data.startTime
        if data.endTime is not None:
            update_fields["endTime"] = data.endTime
        if data.isCrossMidnight is not None:
            update_fields["isCrossMidnight"] = data.isCrossMidnight
        if data.breakStartTime is not None:
            update_fields["breakStartTime"] = data.breakStartTime
        if data.breakEndTime is not None:
            update_fields["breakEndTime"] = data.breakEndTime
        if data.expectedWorkingHours is not None:
            update_fields["expectedWorkingHours"] = data.expectedWorkingHours
        if data.status in ["Active", "Cancelled"]:
            update_fields["status"] = data.status
            if data.status == "Cancelled":
                update_fields["cancelledBy"] = current_user_id
                update_fields["cancelledAt"] = datetime.now(timezone.utc)

        target_id = existing["id"]
        try:
            q = {"_id": ObjectId(target_id)}
        except Exception:
            q = {"specialDayId": target_id}

        await self.db.special_days.update_one(q, {"$set": update_fields})
        updated = await self.get_by_id(target_id)

        try:
            await self.db.audit_logs.insert_one({
                "action": "SPECIAL_DAY_UPDATED",
                "resource": "special_days",
                "resourceId": config_id,
                "performedBy": current_user_id,
                "timestamp": datetime.now(timezone.utc),
                "details": update_fields
            })
        except Exception:
            pass

        return updated

    async def cancel(self, config_id: str, current_user_id: str) -> Optional[Dict[str, Any]]:
        return await self.update(config_id, SpecialDayUpdate(status="Cancelled"), current_user_id)

    @staticmethod
    def _format_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": str(doc.get("_id", "")),
            "specialDayId": doc.get("specialDayId") or str(doc.get("_id", "")),
            "companyId": str(doc.get("companyId", "")),
            "eventName": doc.get("eventName", ""),
            "date": doc.get("date", ""),
            "dayType": doc.get("dayType", ""),
            "applicability": doc.get("applicability", "All Branches"),
            "selectedBranchIds": [str(b) for b in doc.get("selectedBranchIds", [])],
            "shiftId": doc.get("shiftId"),
            "shiftCode": doc.get("shiftCode"),
            "startTime": doc.get("startTime"),
            "endTime": doc.get("endTime"),
            "expectedWorkingHours": doc.get("expectedWorkingHours"),
            "isCrossMidnight": doc.get("isCrossMidnight", False),
            "breakStartTime": doc.get("breakStartTime"),
            "breakEndTime": doc.get("breakEndTime"),
            "reason": doc.get("reason"),
            "status": doc.get("status", "Active"),
            "createdBy": doc.get("createdBy"),
            "createdAt": doc.get("createdAt").isoformat() if isinstance(doc.get("createdAt"), datetime) else str(doc.get("createdAt", "")) if doc.get("createdAt") else None,
            "updatedBy": doc.get("updatedBy"),
            "updatedAt": doc.get("updatedAt").isoformat() if isinstance(doc.get("updatedAt"), datetime) else str(doc.get("updatedAt", "")) if doc.get("updatedAt") else None,
            "cancelledBy": doc.get("cancelledBy"),
            "cancelledAt": doc.get("cancelledAt").isoformat() if isinstance(doc.get("cancelledAt"), datetime) else str(doc.get("cancelledAt", "")) if doc.get("cancelledAt") else None,
        }
