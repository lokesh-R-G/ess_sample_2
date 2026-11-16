from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta, timezone
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase


class AttendanceReportBuilder:
    """
    Builds structured, read-only data for the Master and Individual Attendance PDF Reports.
    Strictly queries existing records; does not alter, recalculate, or create any DB documents.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    def _clean_leave_type(self, leave_type: Optional[str]) -> str:
        if not leave_type:
            return ""
        # Remove internal suffixes such as _TEST
        cleaned = leave_type.replace("_TEST", "").replace("_test", "").strip()
        return cleaned

    def _format_time(self, time_val: Any) -> Optional[str]:
        if not time_val:
            return None
        if isinstance(time_val, datetime):
            return time_val.strftime("%H:%M:%S")
        if isinstance(time_val, str):
            val = time_val.strip()
            if "T" in val:
                try:
                    dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
                    return dt.strftime("%H:%M:%S")
                except Exception:
                    pass
            if len(val) >= 8 and ":" in val:
                return val[:8]
            return val
        return None

    async def build_report_data(
        self,
        employees: List[Dict[str, Any]],
        dt_from: datetime,
        dt_to: datetime,
        export_type: str = "Master Export",
        user_info: Optional[Dict[str, Any]] = None,
        company_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Gathers attendance, approvals, ledgers, and profile metadata for all provided employees
        across the date range [dt_from, dt_to] and structures it for the PDF compiler.
        """
        if not employees:
            return {
                "companyName": company_name or "HRMS ENTERPRISE",
                "periodLabel": f"{dt_from.strftime('%B %Y')}",
                "exportType": export_type,
                "generatedAt": datetime.now(timezone.utc).strftime("%d-%b-%Y %H:%M UTC"),
                "generatedBy": user_info.get("name") or user_info.get("empId") if user_info else "System",
                "scopeRole": user_info.get("role") or user_info.get("roleId") if user_info else "Admin",
                "employees": []
            }

        emp_ids = [str(e.get("employeeId")) for e in employees if e.get("employeeId")]
        emp_codes = [str(e.get("employeeCode")) for e in employees if e.get("employeeCode")]

        # 1. Resolve Personal Names
        personals_cursor = self.db.employee_personals.find(
            {"employeeId": {"$in": emp_ids}, "isCurrent": True, "deletedAt": None}
        )
        personal_map = {}
        async for p in personals_cursor:
            first = (p.get("firstName") or "").strip()
            last = (p.get("lastName") or "").strip()
            full = f"{first} {last}".strip()
            if full:
                personal_map[str(p.get("employeeId"))] = full

        # 2. Resolve Employment Histories for Branch, Department, Designation & Shift
        hist_cursor = self.db.employee_employment_histories.find(
            {"employeeId": {"$in": emp_ids}, "isCurrent": True, "deletedAt": None}
        )
        hist_map = {}
        branch_ids = set()
        dept_ids = set()
        desig_ids = set()

        async for h in hist_cursor:
            e_id = str(h.get("employeeId"))
            hist_map[e_id] = h
            if h.get("branchId"):
                branch_ids.add(h["branchId"])
            if h.get("departmentId"):
                dept_ids.add(h["departmentId"])
            if h.get("designationId"):
                desig_ids.add(h["designationId"])

        # Fetch lookup entities
        async def fetch_lookup_map(collection_name: str, id_set: set) -> Dict[str, str]:
            lookup = {}
            if not id_set:
                return lookup
            obj_ids = []
            str_ids = []
            for item in id_set:
                str_ids.append(str(item))
                if len(str(item)) == 24:
                    try:
                        obj_ids.append(ObjectId(str(item)))
                    except Exception:
                        pass
            cursor = self.db[collection_name].find({
                "$or": [
                    {"_id": {"$in": obj_ids}},
                    {"_id": {"$in": str_ids}},
                    {"id": {"$in": str_ids}}
                ]
            })
            async for doc in cursor:
                doc_name = doc.get("name") or doc.get("title") or ""
                lookup[str(doc.get("_id"))] = doc_name
                if doc.get("id"):
                    lookup[str(doc.get("id"))] = doc_name
            return lookup

        branch_map = await fetch_lookup_map("branchs", branch_ids)
        dept_map = await fetch_lookup_map("departments", dept_ids)
        desig_map = await fetch_lookup_map("designations", desig_ids)

        # 3. Resolve Company Name if not given
        if not company_name and employees:
            c_id = employees[0].get("companyId")
            if c_id:
                try:
                    c_doc = await self.db.companys.find_one({
                        "$or": [
                            {"_id": ObjectId(str(c_id)) if len(str(c_id)) == 24 else c_id},
                            {"_id": str(c_id)},
                            {"id": str(c_id)}
                        ]
                    })
                    if c_doc:
                        company_name = c_doc.get("companyName") or c_doc.get("name")
                except Exception:
                    pass

        # 4. Fetch Attendance Records for the Date Range
        from_str = dt_from.strftime("%Y-%m-%d")
        to_str = dt_to.strftime("%Y-%m-%d")
        att_cursor = self.db.attendance.find({
            "$or": [
                {"empId": {"$in": emp_codes}},
                {"employeeCode": {"$in": emp_codes}},
                {"employeeId": {"$in": emp_ids}}
            ],
            "date": {"$gte": from_str, "$lte": to_str}
        })
        
        # Group attendance by employeeId and date
        # Map employeeCode to employeeId
        code_to_empid = {}
        for emp in employees:
            e_id = str(emp.get("employeeId"))
            e_code = str(emp.get("employeeCode"))
            code_to_empid[e_code] = e_id
            code_to_empid[e_id] = e_id

        att_by_emp_date: Dict[str, Dict[str, Dict[str, Any]]] = {e_id: {} for e_id in emp_ids}

        async for att in att_cursor:
            a_empid = str(att.get("employeeId") or "")
            a_empcode = str(att.get("employeeCode") or att.get("empId") or "")
            matched_id = a_empid if a_empid in att_by_emp_date else code_to_empid.get(a_empcode)
            if matched_id and matched_id in att_by_emp_date:
                att_by_emp_date[matched_id][att.get("date")] = att

        # 5. Fetch Leave Approvals
        # Approvals in the system are keyed by employeeId
        approvals_cursor = self.db.approvals.find({
            "employeeId": {"$in": emp_ids},
            "approvalType": "Leave"
        })
        
        # Also build a cache of approver names for human-readable display
        approver_ids = set()
        leave_approvals: List[Dict[str, Any]] = []
        async for app in approvals_cursor:
            leave_approvals.append(app)
            if app.get("approvedBy"):
                approver_ids.add(str(app["approvedBy"]))

        approver_name_map = {}
        if approver_ids:
            appr_personals = self.db.employee_personals.find({
                "employeeId": {"$in": list(approver_ids)},
                "isCurrent": True,
                "deletedAt": None
            })
            async for p in appr_personals:
                full = f"{(p.get('firstName') or '').strip()} {(p.get('lastName') or '').strip()}".strip()
                if full:
                    approver_name_map[str(p.get("employeeId"))] = full

            # Also check employees collection if not found in personals
            missing_apprs = [aid for aid in approver_ids if aid not in approver_name_map]
            if missing_apprs:
                m_cursor = self.db.employees.find({
                    "$or": [
                        {"employeeId": {"$in": missing_apprs}},
                        {"employeeCode": {"$in": missing_apprs}}
                    ]
                })
                async for e in m_cursor:
                    full = f"{(e.get('firstName') or '').strip()} {(e.get('lastName') or '').strip()}".strip()
                    if full:
                        approver_name_map[str(e.get("employeeId"))] = full
                        if e.get("employeeCode"):
                            approver_name_map[str(e.get("employeeCode"))] = full

        # 6. Fetch Leave Ledgers for the relevant calendar year(s)
        calendar_years = list({dt_from.year, dt_to.year})
        ledgers_cursor = self.db.leave_ledgers.find({
            "$or": [
                {"employeeId": {"$in": emp_ids}},
                {"employeeCode": {"$in": emp_codes}}
            ],
            "calendarYear": {"$in": calendar_years}
        })

        # Index ledger allocations: ledger_alloc_index[(employeeId, date, approvalId)] = alloc
        # and ledger_alloc_by_date[(employeeId, date)] = list of allocs
        ledger_alloc_index = {}
        async for led in ledgers_cursor:
            l_empid = str(led.get("employeeId") or "")
            l_code = str(led.get("employeeCode") or "")
            resolved_eid = l_empid if l_empid in att_by_emp_date else code_to_empid.get(l_code)
            if not resolved_eid:
                continue

            for alloc in led.get("allocations", []):
                a_date = alloc.get("date")
                a_id = str(alloc.get("approvalId") or "")
                if a_date:
                    key = (resolved_eid, a_date, a_id)
                    ledger_alloc_index[key] = {
                        "allocated": alloc.get("allocated", 0.0),
                        "lop": alloc.get("lop", 0.0),
                        "type": alloc.get("type"),
                        "penaltyDays": alloc.get("penaltyDays", 0.0),
                        "leaveType": self._clean_leave_type(led.get("leaveType"))
                    }

        # 7. Generate day range for the reporting period
        current_dt = dt_from.date() if isinstance(dt_from, datetime) else dt_from
        end_dt = dt_to.date() if isinstance(dt_to, datetime) else dt_to
        all_dates = []
        while current_dt <= end_dt:
            all_dates.append(current_dt)
            current_dt += timedelta(days=1)

        # 8. Compile per-employee report structures
        compiled_employees = []

        for emp in employees:
            e_id = str(emp.get("employeeId"))
            e_code = str(emp.get("employeeCode") or "")
            emp_name = personal_map.get(e_id)
            if not emp_name:
                emp_name = f"{(emp.get('firstName') or '').strip()} {(emp.get('lastName') or '').strip()}".strip()
            if not emp_name:
                emp_name = e_code or e_id

            hist = hist_map.get(e_id, {})
            b_name = branch_map.get(str(hist.get("branchId")), "")
            d_name = dept_map.get(str(hist.get("departmentId")), "")
            des_name = desig_map.get(str(hist.get("designationId")), "")
            default_shift = hist.get("shiftCode") or "GEN"

            emp_atts = att_by_emp_date.get(e_id, {})

            # Summary counters
            summary = {
                "present": 0,
                "absent": 0,
                "leave": 0,
                "weekOff": 0,
                "holiday": 0,
                "lopDays": 0.0,
                "lopHours": 0.0,
                "lateCount": 0
            }

            daily_rows = []

            for d in all_dates:
                d_str = d.strftime("%Y-%m-%d")
                d_name_abbr = d.strftime("%a")

                att = emp_atts.get(d_str)

                # Initialize row defaults
                row = {
                    "date": d_str,
                    "day": d_name_abbr,
                    "shiftCode": default_shift,
                    "inTime": None,
                    "outTime": None,
                    "workHours": 0.0,
                    "status": "No Record",
                    "statusDisplay": "No Record",
                    "isLate": False,
                    "lateMinutes": 0,
                    "leaveType": None,
                    "leaveDuration": None,
                    "approvalStatus": None,
                    "approvedBy": None,
                    "approvalTimestamp": None,
                    "ledgerDeducted": None,
                    "ledgerAllocated": 0.0,
                    "lopDays": 0.0,
                    "lopReason": None
                }

                if att:
                    raw_status = att.get("status") or "Unknown"
                    row["status"] = raw_status
                    row["statusDisplay"] = raw_status
                    row["shiftCode"] = att.get("shiftCode") or default_shift
                    row["inTime"] = self._format_time(att.get("inTime"))
                    row["outTime"] = self._format_time(att.get("outTime"))
                    row["workHours"] = float(att.get("workHours") or 0.0)

                    late_m = att.get("lateMinutes", 0)
                    if late_m > 0:
                        row["isLate"] = True
                        row["lateMinutes"] = late_m
                        summary["lateCount"] += 1

                    # Read authoritative LOP metrics directly from attendance
                    att_leave_lop = float(att.get("leaveLopDays") or 0.0)
                    att_rej_lop = float(att.get("rejectedLeaveLopDays") or 0.0)
                    att_lop_hours = float(att.get("lopHours") or 0.0)
                    att_lop_reason = att.get("lopReason")

                    # Calculate total LOP days for this date
                    total_date_lop_days = att_leave_lop + att_rej_lop
                    if total_date_lop_days == 0.0 and raw_status.upper() == "LOP":
                        # If status is manual LOP or hourly LOP
                        exp_hours = float(att.get("expectedWorkingHours") or 8.0)
                        if exp_hours <= 0:
                            exp_hours = 8.0
                        total_date_lop_days = att_lop_hours / exp_hours if att_lop_hours > 0 else 1.0

                    row["lopDays"] = total_date_lop_days
                    row["lopReason"] = att_lop_reason

                    summary["lopDays"] += total_date_lop_days
                    summary["lopHours"] += att_lop_hours

                    # Track summary counts
                    status_upper = raw_status.upper()
                    if status_upper in ["PRESENT", "MP"]:
                        summary["present"] += 1
                    elif status_upper in ["ABSENT", "MA"]:
                        summary["absent"] += 1
                    elif status_upper == "LEAVE":
                        summary["leave"] += 1
                    elif status_upper in ["WEEK OFF", "WEEKOFF", "WEEK OFF WORKED"]:
                        summary["weekOff"] += 1
                    elif status_upper == "HOLIDAY":
                        summary["holiday"] += 1
                    elif status_upper == "LOP":
                        # Manual LOP is counted as absence/LOP
                        summary["absent"] += 1

                    # Check approvalSnapshot embedded in attendance doc
                    for snap in att.get("approvalSnapshot", []):
                        stype = (snap.get("type") or snap.get("approvalType") or "").upper()
                        if stype == "LEAVE":
                            if snap.get("leaveType"):
                                row["leaveType"] = self._clean_leave_type(snap.get("leaveType"))

                else:
                    # Genuinely missing attendance record: Check weekend
                    if d.weekday() == 6:  # Sunday
                        row["status"] = "Week Off"
                        row["statusDisplay"] = "Week Off"
                        summary["weekOff"] += 1

                # Match with authoritative approvals for this employee on this date
                matching_approval = None
                for app in leave_approvals:
                    if str(app.get("employeeId")) != e_id:
                        continue
                    rd = app.get("requestData", {})
                    f_d = rd.get("fromDate", rd.get("date", ""))
                    t_d = rd.get("toDate", f_d)
                    if f_d and t_d and f_d <= d_str <= t_d:
                        matching_approval = app
                        break

                if matching_approval:
                    app_id = str(matching_approval["_id"])
                    app_status = matching_approval.get("status", "PENDING")
                    row["approvalStatus"] = app_status

                    rd = matching_approval.get("requestData", {})
                    l_type = self._clean_leave_type(rd.get("leaveType") or row["leaveType"])
                    row["leaveType"] = l_type

                    is_half = rd.get("isHalfDay", False)
                    half_type = rd.get("half", "Full Day") if is_half else "Full Day"
                    row["leaveDuration"] = half_type

                    # Approver info
                    raw_approver = matching_approval.get("approvedBy")
                    if raw_approver:
                        row["approvedBy"] = approver_name_map.get(str(raw_approver), str(raw_approver))

                    if matching_approval.get("approvedAt"):
                        row["approvalTimestamp"] = self._format_time(matching_approval.get("approvedAt"))

                    # Authoritative Leave Ledger Consumption Verification:
                    # Search ledger_alloc_index for (e_id, d_str, app_id)
                    alloc_entry = ledger_alloc_index.get((e_id, d_str, app_id))
                    if alloc_entry:
                        allocated_qty = alloc_entry.get("allocated", 0.0)
                        row["ledgerAllocated"] = allocated_qty
                        if allocated_qty > 0:
                            row["ledgerDeducted"] = "YES"
                        else:
                            row["ledgerDeducted"] = "NO"

                        # If ledger recorded LOP days
                        if alloc_entry.get("lop", 0.0) > 0 and row["lopDays"] == 0.0:
                            row["lopDays"] = alloc_entry["lop"]
                            summary["lopDays"] += alloc_entry["lop"]
                            if not row["lopReason"]:
                                row["lopReason"] = "Insufficient Leave Balance"
                    else:
                        # No allocation found in ledger
                        if app_status == "APPROVED":
                            row["ledgerDeducted"] = "NO"
                        elif app_status == "PENDING":
                            row["ledgerDeducted"] = "-"
                        elif app_status == "REJECTED":
                            row["ledgerDeducted"] = "NO"
                            if not row["lopReason"] and row["lopDays"] > 0:
                                row["lopReason"] = "Rejected Leave + Absent"

                daily_rows.append(row)

            compiled_employees.append({
                "employeeId": e_id,
                "employeeCode": e_code,
                "name": emp_name,
                "branchName": b_name,
                "departmentName": d_name,
                "designationName": des_name,
                "summary": summary,
                "rows": daily_rows
            })

        return {
            "companyName": company_name or "HRMS ENTERPRISE",
            "periodLabel": f"{dt_from.strftime('%B %Y')}",
            "exportType": export_type,
            "generatedAt": datetime.now(timezone.utc).strftime("%d-%b-%Y %H:%M UTC"),
            "generatedBy": (user_info.get("name") or user_info.get("empId") if user_info else "System"),
            "scopeRole": (user_info.get("role") or user_info.get("roleId") or "Admin" if user_info else "Admin").title(),
            "employees": compiled_employees
        }
