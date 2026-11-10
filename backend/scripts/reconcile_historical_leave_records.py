"""
Historical Leave Reconciliation Script
======================================
Reconciles employee leave balances from Excel, reopens previously approved leave requests,
reverses associated leave-ledger deductions and LOP, and routes requests to the existing manager approval workflow.

Confirmed Excel Structure & Exact Database Mapping:
--------------------------------------------------
- Worksheet: 'Leave Details' (or active sheet)
- CL:
    - Excel CL Elig  -> CL ledger `credited`
    - Excel CL Avail -> CL ledger `consumed`
- SL:
    - Excel SL Elig  -> SL ledger `credited`
    - Excel SL Avail -> SL ledger `consumed`
- EL:
    - Excel EL Elig  -> EL ledger `credited`
    - Excel EL Avail -> EL ledger `consumed`
- Calculation:
    `availableBalance = credited - consumed` (preserving valid carriedForward if present: `(credited + carriedForward) - consumed`)
- Opening Balance:
    Preserve existing ledger `openingBalance` according to existing ledger architecture. Do NOT overwrite with credited or consumed.
- Rollback & Idempotency:
    Reopening approvals reverses allocations via LeaveLedgerService.rollback_approval(), and the final Excel consumed total takes precedence without double-counting.

Usage:
    python scripts/reconcile_historical_leave_records.py --input "29-10-2026 leave details(1).xlsx" [--dry-run] [--apply] [--report path] [--company "Name"] [--employee-name "Name"] [--limit N]
"""

from __future__ import annotations

import argparse
import asyncio
import copy
from datetime import date, datetime, timezone
import json
import logging
import os
import re
import sys
import uuid
from typing import Any, Dict, List, Optional, Set, Tuple

# Ensure backend root is on Python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(BACKEND_ROOT, ".env"))

import openpyxl
from bson import ObjectId

from app.core.config import get_settings
from app.db.mongo import get_database
from app.attendance_v2.services.leave_ledger_service import LeaveLedgerService
from app.attendance_v2.services.attendance_processor import AttendanceProcessor

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("leave_reconciliation")


def norm_str(s: Any) -> str:
    """Normalize string by stripping, removing punctuation, and lowercasing."""
    if s is None:
        return ""
    return re.sub(r"[^a-zA-Z0-9]", "", str(s)).lower()


def extract_tokens(text: Any) -> Set[str]:
    """Tokenize string into non-empty alphanumeric tokens."""
    if not text:
        return set()
    cleaned = re.sub(r"[^a-zA-Z0-9]", " ", str(text)).lower()
    return set(t for t in cleaned.split() if t)


def names_match(n1: str, n2: str) -> bool:
    """Fuzzy name matching handling spacing, initials, and common spelling differences."""
    t1 = extract_tokens(n1)
    t2 = extract_tokens(n2)
    if not t1 or not t2:
        return False

    norm1 = norm_str(n1)
    norm2 = norm_str(n2)

    # Exact normalized match
    if norm1 == norm2:
        return True

    # Substring match if sufficiently long
    if (norm1 in norm2 or norm2 in norm1) and (len(norm1) >= 4 and len(norm2) >= 4):
        return True

    # Token match for multi-character words
    words1 = [t for t in t1 if len(t) >= 2]
    words2 = [t for t in t2 if len(t) >= 2]

    common_words = set(words1).intersection(set(words2))
    if common_words:
        return True

    # Phonetic/transliteration substitutions (e.g. th vs d, ck vs k)
    for w1 in words1:
        for w2 in words2:
            if w1 == w2:
                return True
            if w1.replace("th", "d") == w2.replace("th", "d"):
                return True
            if w1.replace("ck", "k") == w2.replace("ck", "k"):
                return True

    return False


def dates_match(d1: Any, d2: Any) -> bool:
    """Compare two dates (handling string YYYY-MM-DD or datetime objects)."""
    if not d1 or not d2:
        return False
    s1 = d1.strftime("%Y-%m-%d") if isinstance(d1, (date, datetime)) else str(d1).split()[0]
    s2 = d2.strftime("%Y-%m-%d") if isinstance(d2, (date, datetime)) else str(d2).split()[0]
    return s1 == s2


class HistoricalLeaveReconciler:
    def __init__(self, db: Any, input_path: str, is_apply: bool, report_path: Optional[str] = None):
        self.db = db
        self.input_path = input_path
        self.is_apply = is_apply
        self.report_path = report_path
        self.batch_id = f"RECON_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        self.ledger_service = LeaveLedgerService(db)
        self.attendance_processor = AttendanceProcessor(db)

        # Cached DB entities
        self.companies: Dict[str, Dict[str, Any]] = {}
        self.db_employees: List[Dict[str, Any]] = []
        self.active_policies: List[Dict[str, Any]] = []
        self.payroll_cycles: List[Dict[str, Any]] = []
        self.payroll_runs: List[Dict[str, Any]] = []

        # Audit/reporting structures
        self.matching_records: List[Dict[str, Any]] = []
        self.balance_records: List[Dict[str, Any]] = []
        self.approval_records: List[Dict[str, Any]] = []
        self.attendance_records: List[Dict[str, Any]] = []
        self.payroll_impact_records: List[Dict[str, Any]] = []
        self.exceptions_records: List[Dict[str, Any]] = []

    async def initialize(self):
        """Preload lookup collections from MongoDB."""
        # 1. Companies
        company_docs = await self.db.companies.find().to_list(length=None)
        for c in company_docs:
            c_id = str(c["_id"])
            c_name = c.get("companyName") or c.get("name") or ""
            self.companies[c_id] = {
                "id": c_id,
                "name": c_name.strip(),
                "code": c.get("companyCode") or c.get("code") or ""
            }

        # 2. Leave Policies
        self.active_policies = await self.db.leave_policies.find({"deletedAt": None}).sort([("version", -1)]).to_list(length=None)

        # 3. Payroll Cycles & Runs
        self.payroll_cycles = await self.db.payroll_cycles.find().to_list(length=None)
        self.payroll_runs = await self.db.payroll_runs.find().to_list(length=None)

        # 4. Employees with employment history and personal details
        emp_docs = await self.db.employees.find().to_list(length=None)
        for emp in emp_docs:
            eid = str(emp.get("employeeId"))
            ecode = str(emp.get("employeeCode") or "")

            ehs = await self.db.employee_employment_histories.find({"employeeId": eid}).to_list(length=None)
            personals = await self.db.employee_personals.find({"employeeId": eid}).to_list(length=None)

            # Resolve Logistics vs General identity for overlapping IDs
            if ecode in ["423001", "424002", "425001", "425002", "426001", "426002"]:
                # Match logistics company
                eh = next((h for h in ehs if str(h.get("companyId")) == "6ac4cc1529e34be07e20f5bc"), None)
                pers = next((p for p in personals if p.get("firstName") in ["WAHEEDA", "JANARDHANAN ", "SATHIYAPRIYA", "KARTHIK", "VAIRAMANI", "USHA NANDHINI "]), None)
            else:
                eh = next((h for h in ehs if h.get("isCurrent")), ehs[0] if ehs else None)
                pers = personals[0] if personals else None

            first = emp.get("firstName") or ""
            last = emp.get("lastName") or ""
            full_name = f"{first} {last}".strip()
            if not full_name and pers:
                p_first = pers.get("firstName") or ""
                p_last = pers.get("lastName") or ""
                full_name = f"{p_first} {p_last}".strip() or pers.get("displayName") or ""

            comp_id = str(eh.get("companyId")) if eh else ""
            comp_name = self.companies.get(comp_id, {}).get("name", "")
            doj = eh.get("dateOfJoining") if eh else None

            self.db_employees.append({
                "employeeId": eid,
                "employeeCode": ecode,
                "name": full_name,
                "companyId": comp_id,
                "companyName": comp_name,
                "branchId": str(eh.get("branchId")) if eh else "",
                "doj": doj,
                "doj_str": doj.strftime("%Y-%m-%d") if doj else "",
                "reportingManagerEmployeeId": eh.get("reportingManagerEmployeeId") if eh else None,
                "raw_emp": emp,
                "raw_eh": eh,
                "raw_pers": pers
            })

        logger.info(f"Initialized reconciler with {len(self.companies)} companies and {len(self.db_employees)} DB employees.")

    def parse_excel(self) -> List[Dict[str, Any]]:
        """Parse Excel workbook into structured employee records supporting both worksheet layouts."""
        if not os.path.exists(self.input_path):
            raise FileNotFoundError(f"Excel workbook not found at {self.input_path}")

        wb = openpyxl.load_workbook(self.input_path)
        ws = wb["Leave Details"] if "Leave Details" in wb.sheetnames else wb.active

        current_company = ""
        records: List[Dict[str, Any]] = []

        def to_float(val: Any) -> Optional[float]:
            if val is None or val == "":
                return None
            try:
                return float(val)
            except ValueError:
                return None

        # Determine column layout by inspecting row 2 / row 3
        is_clean_layout = False
        for check_r in [2, 3]:
            # If col 4 is 'CL' and col 6 is 'SL', or col 4 is 'Elig' and col 5 is 'Avail'
            v4 = str(ws.cell(check_r, 4).value or "").strip()
            v5 = str(ws.cell(check_r, 5).value or "").strip()
            if v4 in ["CL", "Elig"] and v5 in ["Avail"]:
                is_clean_layout = True
                break

        for r in range(1, ws.max_row + 1):
            c1 = str(ws.cell(r, 1).value or "").strip()
            c2 = str(ws.cell(r, 2).value or "").strip()

            # Detect company header rows
            for sec in ["IDS Financial Services", "IDS e Solutions", "IDS Logistics", "IDS INDUSTRIES", "Contract"]:
                if sec.lower() in c1.lower() and not c1.isdigit():
                    current_company = c1
                    break

            # Filter non-employee rows
            if not c2 or c2 in ["Name", "total", "None"] or c2.startswith("S.no"):
                continue

            if is_clean_layout:
                # Layout in '29-10-2026 leave details(1).xlsx':
                # Col 1: S.no, Col 2: Name, Col 3: DOJ
                # Col 4: CL Elig, Col 5: CL Avail
                # Col 6: SL Elig, Col 7: SL Avail
                # Col 8: EL Elig, Col 9: EL Avail
                doj_val = ws.cell(r, 3).value
                cl_elig = to_float(ws.cell(r, 4).value)
                cl_avail = to_float(ws.cell(r, 5).value)
                sl_elig = to_float(ws.cell(r, 6).value)
                sl_avail = to_float(ws.cell(r, 7).value)
                el_elig = to_float(ws.cell(r, 8).value)
                el_avail = to_float(ws.cell(r, 9).value)
            else:
                # Layout in original workbook (with Right side cols 24-29):
                # Col 22: DOJ
                # Col 24: CL Elig, Col 25: CL Avail
                # Col 26: SL Elig, Col 27: SL Avail
                # Col 28: EL Elig, Col 29: EL Avail
                doj_val = ws.cell(r, 22).value
                cl_elig = to_float(ws.cell(r, 24).value)
                cl_avail = to_float(ws.cell(r, 25).value)
                sl_elig = to_float(ws.cell(r, 26).value)
                sl_avail = to_float(ws.cell(r, 27).value)
                el_elig = to_float(ws.cell(r, 28).value)
                el_avail = to_float(ws.cell(r, 29).value)

            if isinstance(doj_val, (date, datetime)):
                doj_str = doj_val.strftime("%Y-%m-%d")
            elif doj_val:
                tokens = str(doj_val).split()
                doj_str = tokens[0] if tokens else ""
            else:
                doj_str = ""

            records.append({
                "row": r,
                "s_no": ws.cell(r, 1).value,
                "company": current_company,
                "name": c2,
                "doj": doj_val,
                "doj_str": doj_str,
                "cl_elig": cl_elig,
                "cl_avail": cl_avail,
                "sl_elig": sl_elig,
                "sl_avail": sl_avail,
                "el_elig": el_elig,
                "el_avail": el_avail
            })

        logger.info(f"Parsed {len(records)} employee records from {self.input_path} (Layout mode: {'Clean 9-column' if is_clean_layout else 'Wide 32-column'})")
        return records

    def match_employee(self, rec: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], str, List[Any]]:
        """
        Composite matching strategy:
        1. Company
        2. Employee name
        3. Date of joining (DOJ)
        """
        c_norm = norm_str(rec["company"])
        n_excel = rec["name"]
        doj_excel = rec["doj_str"]

        candidates = []
        for d in self.db_employees:
            d_c_norm = norm_str(d["companyName"])

            # Company verification
            comp_match = False
            if ("esolution" in c_norm and "esolution" in d_c_norm) or \
               ("financial" in c_norm and "financial" in d_c_norm) or \
               ("logistics" in c_norm and "logistics" in d_c_norm) or \
               ("industries" in c_norm and "industries" in d_c_norm):
                comp_match = True

            n_match = names_match(n_excel, d["name"])
            doj_match = dates_match(doj_excel, d["doj_str"]) if doj_excel and d["doj_str"] else False

            if comp_match and n_match:
                candidates.append({
                    "db_emp": d,
                    "comp_match": comp_match,
                    "name_match": n_match,
                    "doj_match": doj_match
                })

        if len(candidates) == 1:
            matched = candidates[0]
            status = "MATCHED_EXACT_DOJ" if matched["doj_match"] else "MATCHED_NAME_COMPANY"
            return matched["db_emp"], status, candidates
        elif len(candidates) > 1:
            # Check if exactly one candidate has matching DOJ
            doj_candidates = [c for c in candidates if c["doj_match"]]
            if len(doj_candidates) == 1:
                return doj_candidates[0]["db_emp"], "MATCHED_DOJ_DISAMBIGUATED", candidates
            return None, "AMBIGUOUS_MULTIPLE_MATCHES", candidates
        else:
            return None, "UNMATCHED_NOT_FOUND", []

    def resolve_policy_and_types(self, db_emp: Dict[str, Any], year: int) -> Tuple[Optional[Dict[str, Any]], Dict[str, str]]:
        """
        Resolve employee's active leave policy and map CL, SL, EL to actual codes in DB.
        """
        target_date = datetime(year, 10, 1, tzinfo=timezone.utc)

        # Policy lookup
        policy = None
        for p in self.active_policies:
            if p.get("isCurrent"):
                policy = p
                break
        if not policy and self.active_policies:
            policy = self.active_policies[0]

        if not policy:
            return None, {}

        # Resolve CL, SL, EL codes
        type_map = {}
        for lt in policy.get("leaveTypes", []):
            code = lt.get("code", "")
            name = lt.get("name", "").upper()
            code_upper = code.upper()

            if "CASUAL" in name or code_upper.startswith("CL"):
                type_map["CL"] = code
            elif "SICK" in name or code_upper.startswith("SL"):
                type_map["SL"] = code
            elif "EARN" in name or code_upper.startswith("EL"):
                type_map["EL"] = code

        return policy, type_map

    async def get_or_prep_ledger(
        self,
        db_emp: Dict[str, Any],
        leave_type_code: str,
        year: int,
        policy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fetch existing ledger or prepare a new ledger document skeleton."""
        eid = db_emp["employeeId"]
        ecode = db_emp["employeeCode"]

        ledger = await self.db.leave_ledgers.find_one({
            "employeeId": eid,
            "leaveType": leave_type_code,
            "calendarYear": year
        })

        if ledger:
            return ledger

        # Find entitlement from policy
        type_conf = next((t for t in policy.get("leaveTypes", []) if t.get("code") == leave_type_code), {})
        entitlement = float(type_conf.get("annualEntitlement", 12.0))

        now = datetime.now(timezone.utc)
        return {
            "_id": None,  # Indicates new
            "employeeId": eid,
            "employeeCode": ecode,
            "calendarYear": year,
            "leaveType": leave_type_code,
            "policyCode": policy.get("policyCode"),
            "policyVersion": policy.get("version", 1),
            "openingBalance": entitlement,
            "annualEntitlement": entitlement,
            "anniversaryEntitlement": 0.0,
            "carriedForward": 0.0,
            "credited": entitlement,
            "consumed": 0.0,
            "availableBalance": entitlement,
            "expired": 0.0,
            "lopDays": 0.0,
            "version": 1,
            "allocations": [],
            "createdAt": now,
            "updatedAt": now
        }

    async def find_reconciliation_approvals(self, db_emp: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify approved leave requests for the employee that should be reopened."""
        eid = db_emp["employeeId"]
        approvals = await self.db.approvals.find({
            "employeeId": eid,
            "approvalType": "Leave",
            "status": "APPROVED"
        }).to_list(length=None)
        return approvals

    async def rollback_and_reopen_approval(
        self,
        approval: Dict[str, Any],
        db_emp: Dict[str, Any]
    ) -> Tuple[float, float]:
        """
        Use LeaveLedgerService.rollback_approval() to reverse allocations & LOP,
        then reset approval to PENDING routed to reporting manager.
        """
        app_id_str = str(approval["_id"])
        now = datetime.now(timezone.utc)

        # 1. Rollback leave ledger allocations and LOP
        restored_leave = 0.0
        reversed_lop = 0.0

        if self.is_apply:
            await self.ledger_service.rollback_approval(app_id_str)
        else:
            # In dry-run, calculate what would be rolled back
            ledgers = await self.db.leave_ledgers.find({"allocations.approvalId": app_id_str}).to_list(length=None)
            for l in ledgers:
                for alloc in l.get("allocations", []):
                    if alloc.get("approvalId") == app_id_str:
                        restored_leave += alloc.get("allocated", 0.0)
                        reversed_lop += alloc.get("lop", 0.0)

        # 2. Reset approval status to PENDING
        manager_id = db_emp.get("reportingManagerEmployeeId")
        if self.is_apply:
            history_entry = {
                "action": "REOPENED_FOR_HISTORICAL_RECONCILIATION",
                "batchId": self.batch_id,
                "reopenedAt": now,
                "previousStatus": "APPROVED",
                "reason": "Historical leave reconciliation from Excel workbook"
            }
            await self.db.approvals.update_one(
                {"_id": approval["_id"]},
                {
                    "$set": {
                        "status": "PENDING",
                        "approverEmployeeId": manager_id,
                        "approvedAt": None,
                        "approvedBy": None,
                        "updatedAt": now
                    },
                    "$push": {
                        "workflowHistory": history_entry
                    }
                }
            )

        return restored_leave, reversed_lop

    async def check_payroll_overlap(self, employee_id: str, dates: List[date]) -> List[Dict[str, Any]]:
        """Identify finalized payroll periods overlapping given attendance dates."""
        if not dates:
            return []

        min_date = min(dates)
        max_date = max(dates)
        overlapping = []

        for pr in self.payroll_runs:
            status = pr.get("status")
            cycle_id = pr.get("cycleId")
            cycle = next((c for c in self.payroll_cycles if str(c.get("_id")) == str(cycle_id)), None)
            if not cycle:
                continue

            c_start = cycle.get("startDate")
            c_end = cycle.get("endDate")
            if isinstance(c_start, datetime):
                c_start = c_start.date()
            if isinstance(c_end, datetime):
                c_end = c_end.date()

            if c_start and c_end and not (max_date < c_start or min_date > c_end):
                overlapping.append({
                    "cycleId": str(cycle_id),
                    "cycleName": cycle.get("name"),
                    "period": f"{c_start} to {c_end}",
                    "status": status,
                    "action": "ALLOW_RECALCULATION" if status != "FINALIZED" else "FLAGGED_FINALIZED_PAYROLL"
                })

        return overlapping

    async def reconcile_all(self, company_filter: Optional[str] = None, emp_filter: Optional[str] = None, limit: Optional[int] = None):
        """Main reconciliation controller."""
        excel_records = self.parse_excel()

        # Apply CLI filters
        filtered_records = []
        for r in excel_records:
            if company_filter and company_filter.lower() not in r["company"].lower():
                continue
            if emp_filter and emp_filter.lower() not in r["name"].lower():
                continue
            filtered_records.append(r)

        if limit and limit > 0:
            filtered_records = filtered_records[:limit]

        logger.info(f"Processing {len(filtered_records)} records after filtering...")

        reopened_approvals_total = 0
        reversed_leave_total = 0.0
        reversed_lop_total = 0.0
        ledgers_updated_total = 0

        current_year = 2026

        for rec in filtered_records:
            db_emp, match_status, candidates = self.match_employee(rec)

            self.matching_records.append({
                "company": rec["company"],
                "excel_name": rec["name"],
                "excel_doj": rec["doj_str"],
                "matched_emp_id": db_emp["employeeId"] if db_emp else None,
                "matched_emp_code": db_emp["employeeCode"] if db_emp else None,
                "match_status": match_status
            })

            if not db_emp:
                self.exceptions_records.append({
                    "type": "EMPLOYEE_NOT_MATCHED",
                    "company": rec["company"],
                    "excel_name": rec["name"],
                    "details": f"Status: {match_status}, Candidates count: {len(candidates)}"
                })
                continue

            # 1. Resolve Policy & Leave Types
            policy, type_map = self.resolve_policy_and_types(db_emp, current_year)
            if not policy:
                self.exceptions_records.append({
                    "type": "POLICY_NOT_FOUND",
                    "employee": f"{db_emp['employeeId']} ({db_emp['name']})",
                    "details": "No active leave policy found in database."
                })
                continue

            # 2. Reopen Approved Requests
            approvals_to_reopen = await self.find_reconciliation_approvals(db_emp)
            affected_dates: List[date] = []

            for app in approvals_to_reopen:
                req_data = app.get("requestData", {})
                f_date_str = req_data.get("fromDate")
                t_date_str = req_data.get("toDate")
                lt_code = req_data.get("leaveType")

                if f_date_str and t_date_str:
                    try:
                        d_from = datetime.strptime(f_date_str, "%Y-%m-%d").date()
                        d_to = datetime.strptime(t_date_str, "%Y-%m-%d").date()
                        cur = d_from
                        while cur <= d_to:
                            affected_dates.append(cur)
                            cur = cur.fromordinal(cur.toordinal() + 1)
                    except Exception:
                        pass

                restored_leave, reversed_lop = await self.rollback_and_reopen_approval(app, db_emp)
                reopened_approvals_total += 1
                reversed_leave_total += restored_leave
                reversed_lop_total += reversed_lop

                self.approval_records.append({
                    "employee": f"{db_emp['employeeId']} ({db_emp['name']})",
                    "approval_id": str(app["_id"]),
                    "leave_type": lt_code,
                    "dates": f"{f_date_str} to {t_date_str}",
                    "current_status": "APPROVED",
                    "allocated_leave": restored_leave,
                    "associated_lop": reversed_lop,
                    "proposed_status": "PENDING"
                })

            # Check payroll overlap
            if affected_dates:
                payroll_overlaps = await self.check_payroll_overlap(db_emp["employeeId"], affected_dates)
                for po in payroll_overlaps:
                    self.payroll_impact_records.append({
                        "employee": f"{db_emp['employeeId']} ({db_emp['name']})",
                        "period": po["period"],
                        "payroll_status": po["status"],
                        "affected_attendance": f"{min(affected_dates)} to {max(affected_dates)}",
                        "action": po["action"]
                    })

                # Trigger Attendance Recalculation
                if self.is_apply:
                    try:
                        await self.attendance_processor.process_range(
                            from_date=min(affected_dates),
                            to_date=max(affected_dates),
                            force=True,
                            employee_ids=[db_emp["employeeId"]]
                        )
                        att_recalc_status = "SUCCESSFULLY_RECALCULATED"
                    except Exception as e:
                        att_recalc_status = f"FAILED: {str(e)}"
                        self.exceptions_records.append({
                            "type": "ATTENDANCE_PROCESSING_FAILURE",
                            "employee": f"{db_emp['employeeId']} ({db_emp['name']})",
                            "details": str(e)
                        })
                else:
                    att_recalc_status = "PENDING_APPLY"

                self.attendance_records.append({
                    "employee": f"{db_emp['employeeId']} ({db_emp['name']})",
                    "date_range": f"{min(affected_dates)} to {max(affected_dates)}",
                    "current_status": "Leave",
                    "expected_recalculation": "Absent/Biometric punches (Reopened request)",
                    "impact": att_recalc_status
                })

            # 3. Exact Database Mapping:
            # Excel CL/SL/EL Elig  -> credited
            # Excel CL/SL/EL Avail -> consumed
            # availableBalance     = (credited + carriedForward) - consumed
            # Preserve openingBalance intact
            leave_types_data = {
                "CL": {"elig": rec["cl_elig"], "avail": rec["cl_avail"]},
                "SL": {"elig": rec["sl_elig"], "avail": rec["sl_avail"]},
                "EL": {"elig": rec["el_elig"], "avail": rec["el_avail"]}
            }

            for lt_generic, lt_data in leave_types_data.items():
                excel_elig = lt_data["elig"]
                excel_avail = lt_data["avail"]

                # If the row has no data for this leave type, skip
                if excel_elig is None and excel_avail is None:
                    continue

                # If only one of (elig, avail) is provided in Excel, default the missing one to 0.0
                if excel_elig is None and excel_avail is not None:
                    excel_elig = 0.0
                elif excel_avail is None and excel_elig is not None:
                    excel_avail = 0.0

                actual_code = type_map.get(lt_generic)
                if not actual_code:
                    self.exceptions_records.append({
                        "type": "MISSING_LEAVE_TYPE",
                        "employee": f"{db_emp['employeeId']} ({db_emp['name']})",
                        "details": f"Leave type {lt_generic} not found in policy {policy.get('policyCode')}"
                    })
                    continue

                ledger = await self.get_or_prep_ledger(db_emp, actual_code, current_year, policy)

                # Capture existing ledger state
                exist_credited = float(ledger.get("credited", 0.0))
                exist_consumed = float(ledger.get("consumed", 0.0))
                exist_cf = float(ledger.get("carriedForward", 0.0))
                exist_avail = float(ledger.get("availableBalance", 0.0))
                exist_op_bal = float(ledger.get("openingBalance", 0.0))

                # Exact mapping:
                # 1. Proposed Credited = Excel Elig
                proposed_credited = float(excel_elig) if excel_elig is not None else exist_credited

                # 2. Proposed Consumed = Excel Avail
                proposed_consumed = float(excel_avail) if excel_avail is not None else exist_consumed

                # 3. Preserve Carried Forward
                proposed_cf = exist_cf

                # 4. Opening Balance is preserved according to existing ledger architecture
                proposed_op_bal = exist_op_bal

                # 5. Proposed Available Balance = (credited + carriedForward) - consumed
                proposed_avail = (proposed_credited + proposed_cf) - proposed_consumed

                # Validations:
                # Proposed Credited = Excel Elig
                val_cred = (excel_elig is None) or (proposed_credited == float(excel_elig))
                # Proposed Consumed = Excel Avail
                val_cons = (excel_avail is None) or (proposed_consumed == float(excel_avail))
                # Proposed Available = Excel Elig - Excel Avail (when CF is 0)
                expected_simple_avail = (float(excel_elig or 0.0) - float(excel_avail or 0.0))
                val_avail = (proposed_cf != 0.0) or (round(proposed_avail, 2) == round(expected_simple_avail, 2))

                is_valid = val_cred and val_cons and val_avail

                # Flag negative balance if any
                is_negative = proposed_avail < 0.0
                if is_negative:
                    self.exceptions_records.append({
                        "type": "NEGATIVE_AVAILABLE_BALANCE",
                        "employee": f"{db_emp['employeeId']} ({db_emp['name']})",
                        "details": f"{actual_code}: Proposed Available is negative ({proposed_avail:.1f}). Clamping avoided."
                    })

                self.balance_records.append({
                    "employee": f"{db_emp['employeeId']} ({db_emp['name']})",
                    "leave_type": actual_code,
                    "excel_elig": excel_elig,
                    "excel_avail": excel_avail,
                    "exist_credited": exist_credited,
                    "exist_consumed": exist_consumed,
                    "exist_avail": exist_avail,
                    "exist_op_bal": exist_op_bal,
                    "exist_cf": exist_cf,
                    "proposed_credited": proposed_credited,
                    "proposed_consumed": proposed_consumed,
                    "proposed_avail": proposed_avail,
                    "proposed_op_bal": proposed_op_bal,
                    "proposed_cf": proposed_cf,
                    "is_valid": is_valid,
                    "is_negative": is_negative
                })

                if not is_valid:
                    self.exceptions_records.append({
                        "type": "BALANCE_RECONCILIATION_MISMATCH",
                        "employee": f"{db_emp['employeeId']} ({db_emp['name']})",
                        "details": f"{actual_code}: Proposed values do not match Excel Elig/Avail."
                    })

                # Check if ledger needs update
                has_changes = (
                    exist_credited != proposed_credited or
                    exist_consumed != proposed_consumed or
                    exist_avail != proposed_avail
                )

                if has_changes:
                    ledgers_updated_total += 1

                if self.is_apply and has_changes:
                    now = datetime.now(timezone.utc)
                    audit_entry = {
                        "type": "HISTORICAL_RECONCILIATION_EXCEL_MAPPING",
                        "batchId": self.batch_id,
                        "date": now.strftime("%Y-%m-%d"),
                        "previous": {
                            "credited": exist_credited,
                            "consumed": exist_consumed,
                            "availableBalance": exist_avail,
                            "openingBalance": exist_op_bal
                        },
                        "adjusted": {
                            "credited": proposed_credited,
                            "consumed": proposed_consumed,
                            "availableBalance": proposed_avail,
                            "openingBalance": proposed_op_bal
                        },
                        "createdAt": now
                    }

                    if ledger.get("_id"):
                        # Update existing document without modifying openingBalance
                        await self.db.leave_ledgers.update_one(
                            {"_id": ledger["_id"]},
                            {
                                "$set": {
                                    "credited": proposed_credited,
                                    "consumed": proposed_consumed,
                                    "availableBalance": proposed_avail,
                                    "updatedAt": now
                                },
                                "$inc": {"version": 1},
                                "$push": {"allocations": audit_entry}
                            }
                        )
                    else:
                        # Insert newly prepared ledger
                        ledger["credited"] = proposed_credited
                        ledger["consumed"] = proposed_consumed
                        ledger["availableBalance"] = proposed_avail
                        ledger["openingBalance"] = proposed_op_bal
                        ledger["allocations"] = [audit_entry]
                        await self.db.leave_ledgers.insert_one(ledger)

        logger.info(f"Reconciliation run finished.")
        logger.info(f"Summary: Reopened Approvals: {reopened_approvals_total}, Reversed Leave: {reversed_leave_total}, Reversed LOP: {reversed_lop_total}, Ledgers Updated: {ledgers_updated_total}")

        # Generate Report
        return self.generate_report(
            reopened_approvals_total,
            reversed_leave_total,
            reversed_lop_total,
            ledgers_updated_total
        )

    def generate_report(
        self,
        reopened_approvals: int,
        reversed_leave: float,
        reversed_lop: float,
        ledgers_updated: int
    ) -> str:
        """Construct comprehensive markdown report matching prompt specifications."""
        settings = get_settings()
        env_name = getattr(settings, "mongo_db_name", "essl_production")

        matched_count = len([m for m in self.matching_records if m["match_status"].startswith("MATCHED")])
        unmatched_count = len([m for m in self.matching_records if m["match_status"] == "UNMATCHED_NOT_FOUND"])
        ambiguous_count = len([m for m in self.matching_records if m["match_status"] == "AMBIGUOUS_MULTIPLE_MATCHES"])

        lines = []
        lines.append(f"# Historical Leave Reconciliation Report")
        lines.append("")
        lines.append(f"**Execution Timestamp:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}  ")
        lines.append(f"**Reconciliation Batch ID:** `{self.batch_id}`  ")
        lines.append(f"**Database Environment:** `{env_name}`  ")
        lines.append(f"**Mode:** `{'APPLY (Database Writes Enabled)' if self.is_apply else 'DRY-RUN (Read-Only Preview)'}`  ")
        lines.append(f"**Input Workbook:** `{os.path.basename(self.input_path)}`  ")
        lines.append("")
        lines.append("## Executive Summary")
        lines.append("")
        lines.append(f"- **Total Excel Employee Rows Processed:** {len(self.matching_records)}")
        lines.append(f"- **Successfully Matched Employees:** {matched_count}")
        lines.append(f"- **Unmatched Employees (Not in DB):** {unmatched_count}")
        lines.append(f"- **Ambiguous Matches:** {ambiguous_count}")
        lines.append(f"- **Approved Leave Requests Reopened:** {reopened_approvals}")
        lines.append(f"- **Reversed Leave Deductions:** {reversed_leave} days")
        lines.append(f"- **Reversed Leave-Related LOP:** {reversed_lop} days")
        lines.append(f"- **Leave Ledgers Proposed for Update:** {ledgers_updated}")
        lines.append(f"- **Attendance Recalculation Ranges:** {len(self.attendance_records)}")
        lines.append(f"- **Overlapping Payroll Periods Flagged:** {len(self.payroll_impact_records)}")
        lines.append("")

        # 1. Employee matching report
        lines.append("## 1. Employee Matching Report")
        lines.append("")
        lines.append("| Company | Excel Employee Name | Excel DOJ | Matched Employee ID | Matched Code | Match Status |")
        lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for m in self.matching_records:
            lines.append(f"| {m['company']} | {m['excel_name']} | {m['excel_doj']} | {m['matched_emp_id'] or '-'} | {m['matched_emp_code'] or '-'} | {m['match_status']} |")
        lines.append("")

        # 2. Leave balance report: Employee | Leave Type | Excel Elig | Excel Avail | Proposed Credited | Proposed Consumed | Proposed Available
        lines.append("## 2. Leave Balance Report")
        lines.append("")
        lines.append("| Employee | Leave Type | Excel Elig | Excel Avail | Proposed Credited | Proposed Consumed | Proposed Available | Validation |")
        lines.append("| :--- | :--- | ---: | ---: | ---: | ---: | ---: | :--- |")
        for b in self.balance_records:
            e_elig = f"{b['excel_elig']:.1f}" if b['excel_elig'] is not None else "-"
            e_avail = f"{b['excel_avail']:.1f}" if b['excel_avail'] is not None else "-"
            valid_tag = "OK" if b['is_valid'] else "MISMATCH"
            if b.get("is_negative"):
                valid_tag += " (NEGATIVE)"
            lines.append(
                f"| {b['employee']} | {b['leave_type']} | {e_elig} | {e_avail} | "
                f"{b['proposed_credited']:.1f} | {b['proposed_consumed']:.1f} | "
                f"{b['proposed_avail']:.1f} | {valid_tag} |"
            )
        lines.append("")

        # 3. Approval reconciliation report
        lines.append("## 3. Approval Reconciliation Report")
        lines.append("")
        lines.append("| Employee | Approval ID | Leave Type | Leave Dates | Current Status | Allocated Leave | Associated LOP | Proposed Status |")
        lines.append("| :--- | :--- | :--- | :--- | :--- | ---: | ---: | :--- |")
        if self.approval_records:
            for a in self.approval_records:
                lines.append(f"| {a['employee']} | `{a['approval_id']}` | {a['leave_type']} | {a['dates']} | {a['current_status']} | {a['allocated_leave']:.1f} | {a['associated_lop']:.1f} | {a['proposed_status']} |")
        else:
            lines.append("| *None* | - | - | - | - | - | - | - |")
        lines.append("")

        # 4. Attendance impact report
        lines.append("## 4. Attendance Impact Report")
        lines.append("")
        lines.append("| Employee | Date Range | Current Status | Expected Recalculation | Impact |")
        lines.append("| :--- | :--- | :--- | :--- | :--- |")
        if self.attendance_records:
            for att in self.attendance_records:
                lines.append(f"| {att['employee']} | {att['date_range']} | {att['current_status']} | {att['expected_recalculation']} | {att['impact']} |")
        else:
            lines.append("| *None* | - | - | - | - |")
        lines.append("")

        # 5. Payroll impact report
        lines.append("## 5. Payroll Impact Report")
        lines.append("")
        lines.append("| Employee | Payroll Period | Payroll Status | Affected Attendance | Action |")
        lines.append("| :--- | :--- | :--- | :--- | :--- |")
        if self.payroll_impact_records:
            for p in self.payroll_impact_records:
                lines.append(f"| {p['employee']} | {p['period']} | {p['payroll_status']} | {p['affected_attendance']} | {p['action']} |")
        else:
            lines.append("| *None* | - | - | - | - |")
        lines.append("")

        # 6. Exceptions report
        lines.append("## 6. Exceptions Report")
        lines.append("")
        lines.append("| Exception Type | Subject / Employee | Details |")
        lines.append("| :--- | :--- | :--- |")
        for exc in self.exceptions_records:
            subj = exc.get("employee") or exc.get("excel_name") or "-"
            lines.append(f"| `{exc['type']}` | {subj} | {exc['details']} |")
        lines.append("")

        report_content = "\n".join(lines)
        if self.report_path:
            os.makedirs(os.path.dirname(os.path.abspath(self.report_path)), exist_ok=True)
            with open(self.report_path, "w", encoding="utf-8") as f:
                f.write(report_content)
            logger.info(f"Report written to {self.report_path}")

        return report_content


def parse_args():
    parser = argparse.ArgumentParser(description="Reconcile historical employee leave records from Excel workbook.")
    parser.add_argument("--input", default="29-10-2026 leave details(1).xlsx", help="Path to input Excel workbook")
    parser.add_argument("--dry-run", action="store_true", default=False, help="Preview all proposed changes without database writes (Default)")
    parser.add_argument("--apply", action="store_true", default=False, help="Execute reconciliation and apply changes to database")
    parser.add_argument("--report", default="docs/architecture-audit/historical-leave-reconciliation-dry-run-report.md", help="Path to output markdown report")
    parser.add_argument("--company", help="Optional company filter")
    parser.add_argument("--employee-name", help="Optional employee name filter for testing")
    parser.add_argument("--limit", type=int, help="Optional maximum employee count for testing")
    return parser.parse_args()


async def main():
    args = parse_args()

    if args.dry_run and args.apply:
        logger.error("Cannot specify both --dry-run and --apply simultaneously.")
        sys.exit(1)

    is_apply = bool(args.apply)
    mode_label = "APPLY (WRITES ENABLED)" if is_apply else "DRY-RUN (READ-ONLY PREVIEW)"

    settings = get_settings()
    logger.info("==================================================")
    logger.info("  ESS HISTORICAL LEAVE RECONCILIATION SCRIPT      ")
    logger.info("==================================================")
    logger.info(f"Target Database: {settings.mongo_db_name}")
    logger.info(f"Execution Mode:  {mode_label}")
    logger.info(f"Input Workbook:  {args.input}")
    logger.info("==================================================")

    db = get_database()
    reconciler = HistoricalLeaveReconciler(
        db=db,
        input_path=args.input,
        is_apply=is_apply,
        report_path=args.report
    )

    await reconciler.initialize()
    report = await reconciler.reconcile_all(
        company_filter=args.company,
        emp_filter=args.employee_name,
        limit=args.limit
    )

    print("\n" + "="*80)
    print("RECONCILIATION SUMMARY")
    print("="*80)
    print("\n".join(report.splitlines()[:45]))
    print(f"\n[Full report saved to {args.report}]")


if __name__ == "__main__":
    asyncio.run(main())
