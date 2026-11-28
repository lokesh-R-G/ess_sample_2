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
        scope_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        query: Dict[str, Any] = {}
        if scope_type:
            query["scopeType"] = scope_type
        if date_val:
            query["date"] = date_val
        if status:
            query["status"] = status

        if company_id:
            # Match if:
            # 1. scopeType is GLOBAL
            # 2. companyId == company_id (SINGLE_COMPANY or legacy)
            # 3. companyIds contains company_id (SELECTED_COMPANIES)
            query["$or"] = [
                {"scopeType": "GLOBAL"},
                {"companyId": company_id},
                {"companyIds": company_id}
            ]

        if branch_id:
            branch_clause = [
                {"applicability": "All Branches"},
                {"selectedBranchIds": branch_id}
            ]
            if "$or" in query:
                query = {"$and": [{"$or": query.pop("$or")}, {"$or": branch_clause}]}
            else:
                query["$or"] = branch_clause

        total = await self.db.special_days.count_documents(query)
        cursor = self.db.special_days.find(query).sort([("date", -1), ("createdAt", -1)]).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)

        # Collect branch and company names
        all_branch_ids = set()
        all_company_ids = set()
        for d in docs:
            for b_id in d.get("selectedBranchIds", []):
                all_branch_ids.add(b_id)
            if d.get("companyId"):
                all_company_ids.add(d["companyId"])
            for c_id in d.get("companyIds", []):
                all_company_ids.add(c_id)

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

        company_map = {}
        if all_company_ids:
            c_oids = []
            for c in all_company_ids:
                try:
                    c_oids.append(ObjectId(c))
                except Exception:
                    c_oids.append(c)
            companies = await self.db.companies.find({"_id": {"$in": c_oids}}).to_list(None)
            for c in companies:
                company_map[str(c["_id"])] = c.get("name") or c.get("code") or str(c["_id"])

        formatted = []
        for d in docs:
            item = self._format_doc(d)
            item["selectedBranchNames"] = [branch_map.get(bid, bid) for bid in item.get("selectedBranchIds", [])]
            item["companyNames"] = [company_map.get(cid, cid) for cid in item.get("companyIds", [])]
            formatted.append(item)

        return {"total": total, "data": formatted}

    async def validate_conflicts(
        self,
        company_id: Optional[str] = None,
        date_str: str = "",
        applicability: str = "All Branches",
        selected_branch_ids: Optional[List[str]] = None,
        scope_type: str = "SINGLE_COMPANY",
        company_ids: Optional[List[str]] = None,
        exclude_id: Optional[str] = None
    ):
        """
        Validate that:
        1. Selected companies exist.
        2. Selected branches belong to the applicable company/companies.
        3. No conflicting active special day exists for the same date with overlapping company & branch scope:
           - Global conflicts with another Global event on the same date.
           - Global conflicts with any event if branch scopes overlap.
           - Selected Companies conflict with Global or any active event sharing at least one company and overlapping branches.
        """
        if selected_branch_ids is None:
            selected_branch_ids = []
        if company_ids is None:
            company_ids = [company_id] if company_id else []

        # Validate company existence
        if scope_type == "SELECTED_COMPANIES":
            if not company_ids:
                raise ValueError("At least one company must be selected for SELECTED_COMPANIES scope.")
            c_oids = [ObjectId(c) if ObjectId.is_valid(c) else c for c in company_ids]
            found_comps = await self.db.companies.find({"_id": {"$in": c_oids}}).to_list(None)
            found_cids = {str(c["_id"]) for c in found_comps}
            for cid in company_ids:
                if cid not in found_cids:
                    raise ValueError(f"Company ID '{cid}' does not exist.")
        elif scope_type == "SINGLE_COMPANY":
            if not company_id:
                raise ValueError("Company ID is required for SINGLE_COMPANY scope.")
            c_oid = ObjectId(company_id) if ObjectId.is_valid(company_id) else company_id
            comp = await self.db.companies.find_one({"_id": c_oid})
            if not comp:
                raise ValueError(f"Company ID '{company_id}' does not exist.")

        # Validate branch ownership
        if applicability == "Selected Branches":
            if not selected_branch_ids:
                raise ValueError("At least one branch must be selected for Selected Branches applicability.")
            
            b_oids = [ObjectId(b) if ObjectId.is_valid(b) else b for b in selected_branch_ids]
            branches = await self.db.branchs.find({"_id": {"$in": b_oids}}).to_list(None)
            found_bids = {str(b["_id"]) for b in branches}
            
            applicable_cids = set(company_ids) if scope_type == "SELECTED_COMPANIES" else ({company_id} if scope_type == "SINGLE_COMPANY" and company_id else None)
            
            for b in branches:
                b_comp = str(b.get("companyId", ""))
                if applicable_cids is not None and b_comp not in applicable_cids:
                    raise ValueError(f"Branch '{b.get('name', b.get('_id'))}' does not belong to authorized company/companies {list(applicable_cids)}.")
            
            for b_id in selected_branch_ids:
                if b_id not in found_bids:
                    raise ValueError(f"Branch ID '{b_id}' does not exist.")

        # Check overlapping conflicts for the same date
        conflict_query: Dict[str, Any] = {
            "date": date_str,
            "status": {"$ne": "Cancelled"}
        }
        if exclude_id:
            try:
                conflict_query["_id"] = {"$ne": ObjectId(exclude_id)}
            except Exception:
                conflict_query["specialDayId"] = {"$ne": exclude_id}

        existing_active = await self.db.special_days.find(conflict_query).to_list(None)

        target_companies = set(company_ids) if scope_type == "SELECTED_COMPANIES" else ({company_id} if company_id else set())
        target_branches = set(selected_branch_ids)

        for existing in existing_active:
            ex_scope = existing.get("scopeType", "SINGLE_COMPANY")
            ex_app = existing.get("applicability", "All Branches")
            ex_branches = set(existing.get("selectedBranchIds", []))
            ex_name = existing.get("eventName", "Existing Configuration")
            ex_type = existing.get("dayType")
            
            ex_companies = set(existing.get("companyIds", []))
            if existing.get("companyId"):
                ex_companies.add(existing["companyId"])

            # 1. Check company overlap
            companies_overlap = False
            if scope_type == "GLOBAL" or ex_scope == "GLOBAL":
                companies_overlap = True
            elif target_companies.intersection(ex_companies):
                companies_overlap = True

            if not companies_overlap:
                continue

            # 2. Check branch overlap within overlapping companies
            branches_overlap = False
            if applicability == "All Branches" or ex_app == "All Branches":
                branches_overlap = True
            elif target_branches.intersection(ex_branches):
                branches_overlap = True

            if branches_overlap:
                common_b = target_branches.intersection(ex_branches) if applicability == "Selected Branches" and ex_app == "Selected Branches" else []
                overlap_desc = f"overlapping branch(es) {list(common_b)}" if common_b else f"scope '{ex_scope} / {ex_app}'"
                raise ValueError(
                    f"Conflict detected on {date_str}: '{ex_name}' ({ex_type}) is already active with "
                    f"{overlap_desc}. Cannot create overlapping configuration."
                )

    async def create(
        self,
        data: SpecialDayCreate,
        current_user_id: str,
        user_role: Optional[str] = None,
        resolved_company_id: Optional[str] = None
    ) -> Dict[str, Any]:
        scope_type = data.scopeType
        company_id = None
        company_ids: List[str] = []

        if scope_type == "GLOBAL":
            company_id = None
            company_ids = []
        elif scope_type == "SELECTED_COMPANIES":
            company_ids = [str(c) for c in (data.companyIds or [])]
            company_id = company_ids[0] if company_ids else None
        elif scope_type == "SINGLE_COMPANY":
            company_id = str(data.companyId or resolved_company_id or "")
            if not company_id:
                raise ValueError("companyId is required for SINGLE_COMPANY scope.")
            company_ids = [company_id]

        await self.validate_conflicts(
            scope_type=scope_type,
            company_id=company_id,
            company_ids=company_ids,
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
            "scopeType": scope_type,
            "companyId": str(company_id) if company_id else None,
            "companyIds": company_ids,
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

        # Write audit log with enhanced scope information
        try:
            await self.db.audit_logs.insert_one({
                "action": "SPECIAL_DAY_CREATED",
                "resource": "special_days",
                "resourceId": special_day_id,
                "scopeType": scope_type,
                "companyId": str(company_id) if company_id else None,
                "companyIds": company_ids,
                "affectedBranchIds": data.selectedBranchIds or [],
                "performedBy": current_user_id,
                "performedByRole": user_role,
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

    async def update(self, config_id: str, data: SpecialDayUpdate, current_user_id: str, user_role: Optional[str] = None) -> Optional[Dict[str, Any]]:
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
                "scopeType": existing.get("scopeType", "SINGLE_COMPANY"),
                "companyId": existing.get("companyId"),
                "companyIds": existing.get("companyIds", []),
                "affectedBranchIds": existing.get("selectedBranchIds", []),
                "performedBy": current_user_id,
                "performedByRole": user_role,
                "timestamp": datetime.now(timezone.utc),
                "previousValues": {k: existing.get(k) for k in update_fields.keys() if k in existing},
                "updatedValues": update_fields
            })
        except Exception:
            pass

        return updated

    async def cancel(self, config_id: str, current_user_id: str, user_role: Optional[str] = None) -> Optional[Dict[str, Any]]:
        return await self.update(config_id, SpecialDayUpdate(status="Cancelled"), current_user_id, user_role=user_role)

    @staticmethod
    def _format_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
        raw_company_id = doc.get("companyId")
        company_ids = [str(c) for c in doc.get("companyIds", [])]
        if raw_company_id and raw_company_id not in company_ids:
            company_ids.append(str(raw_company_id))

        scope_type = doc.get("scopeType")
        if not scope_type:
            scope_type = "GLOBAL" if not raw_company_id and not company_ids else ("SELECTED_COMPANIES" if len(company_ids) > 1 else "SINGLE_COMPANY")

        return {
            "id": str(doc.get("_id", "")),
            "specialDayId": doc.get("specialDayId") or str(doc.get("_id", "")),
            "scopeType": scope_type,
            "companyId": str(raw_company_id) if raw_company_id else None,
            "companyIds": company_ids,
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
