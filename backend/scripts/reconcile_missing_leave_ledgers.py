"""
Reconcile Missing Leave Ledgers Script
Usage:
    python scripts/reconcile_missing_leave_ledgers.py [--dry-run] [--apply] [--employee-id EMP_ID] [--limit N] [--report PATH]
"""
import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone

# Ensure backend root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from app.db.mongo import get_database
from app.attendance_v2.services.leave_ledger_service import LeaveLedgerService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("reconcile_leave_ledgers")

async def run_reconciliation(args):
    db = get_database()
    ledger_svc = LeaveLedgerService(db)
    
    is_apply = bool(args.apply)
    mode_str = "APPLY (writes enabled)" if is_apply else "DRY-RUN (read-only)"
    logger.info(f"Starting Leave Ledger Reconciliation in {mode_str} mode")
    
    now = datetime.now(timezone.utc)
    
    # 1. Resolve active policy for reference
    query = {
        "deletedAt": None,
        "effectiveFrom": {"$lte": now},
        "$or": [
            {"effectiveTo": None},
            {"effectiveTo": {"$gt": now}}
        ]
    }
    docs = await db.leave_policies.find(query).sort([("version", -1)]).to_list(length=1)
    if not docs:
        docs = await db.leave_policies.find({"deletedAt": None, "isCurrent": True}).sort([("version", -1)]).to_list(length=1)
        
    if not docs:
        logger.error("No active leave policy found. Aborting reconciliation.")
        return 1
        
    policy = docs[0]
    policy_code = policy.get("policyCode")
    policy_version = policy.get("version")
    enabled_types = [t for t in policy.get("leaveTypes", []) if t.get("enabled", True)]
    type_codes = [t.get("code") for t in enabled_types]
    
    logger.info(f"Active Leave Policy: {policy_code} (v{policy_version}), Enabled types: {type_codes}")
    
    # 2. Build Employee Query
    emp_query = {"deletedAt": None}
    if args.employee_id:
        emp_query["employeeId"] = args.employee_id
        
    cursor = db.employees.find(emp_query).sort([("employeeId", 1)])
    if args.limit:
        cursor = cursor.limit(args.limit)
        
    employees = await cursor.to_list(length=None)
    
    # Deduplicate employees by employeeId if corrupt duplicates exist
    seen_ids = set()
    unique_employees = []
    duplicate_review = []
    
    for emp in employees:
        eid = emp.get("employeeId")
        if not eid:
            duplicate_review.append({"doc_id": str(emp.get("_id")), "reason": "Missing employeeId field"})
            continue
        if eid in seen_ids:
            duplicate_review.append({"doc_id": str(emp.get("_id")), "employeeId": eid, "reason": "Duplicate employeeId in employees collection"})
            continue
        seen_ids.add(eid)
        unique_employees.append(emp)
        
    total_scanned = len(unique_employees)
    eligible_count = 0
    existing_ledgers_found = 0
    missing_ledgers_count = 0
    proposed_creations = 0
    skipped_count = 0
    manual_review_count = len(duplicate_review)
    errors_count = 0
    
    candidate_reports = []
    
    for emp in unique_employees:
        emp_id = emp.get("employeeId")
        emp_code = emp.get("employeeCode", "UNKNOWN")
        status = emp.get("status", "Active")
        
        # Check active employment history
        hists = await db.employee_employment_histories.find({
            "employeeId": emp_id,
            "deletedAt": None
        }).sort([("effectiveFrom", -1), ("createdAt", -1)]).to_list(length=10)
        
        current_hists = [h for h in hists if h.get("isCurrent") is True]
        
        if len(current_hists) > 1:
            manual_review_count += 1
            candidate_reports.append({
                "employeeId": emp_id,
                "employeeCode": emp_code,
                "status": "MANUAL_REVIEW",
                "reason": f"Multiple isCurrent=True employment histories ({len(current_hists)})"
            })
            continue
            
        selected_hist = current_hists[0] if current_hists else (hists[0] if hists else None)
        
        if not selected_hist:
            skipped_count += 1
            candidate_reports.append({
                "employeeId": emp_id,
                "employeeCode": emp_code,
                "status": "SKIPPED",
                "reason": "No employment history record found"
            })
            continue
            
        doj = await ledger_svc._get_employee_doj(emp_id)
        if not doj:
            skipped_count += 1
            candidate_reports.append({
                "employeeId": emp_id,
                "employeeCode": emp_code,
                "status": "SKIPPED",
                "reason": "Date of Joining could not be resolved"
            })
            continue
            
        # Check plausible DOJ year
        if doj.year > 2100 or doj.year < 1950:
            manual_review_count += 1
            candidate_reports.append({
                "employeeId": emp_id,
                "employeeCode": emp_code,
                "status": "MANUAL_REVIEW",
                "reason": f"Anomalous Date of Joining: {doj.isoformat()}"
            })
            continue
            
        eligible_count += 1
        
        # Determine cycle year
        cycle_year = now.year
        if policy.get("leaveCycleStartType") == "DATE_OF_JOINING" and doj:
            try:
                cycle_start_this_year = datetime(now.year, doj.month, doj.day, tzinfo=timezone.utc)
            except ValueError:
                cycle_start_this_year = datetime(now.year, doj.month, doj.day - 1, tzinfo=timezone.utc)
            if now < cycle_start_this_year:
                cycle_year = now.year - 1
                
        emp_existing = []
        emp_missing = []
        emp_created = []
        
        for t in enabled_types:
            lt_code = t.get("code")
            existing = await db.leave_ledgers.find_one({
                "employeeId": emp_id,
                "calendarYear": cycle_year,
                "leaveType": lt_code
            })
            if existing:
                existing_ledgers_found += 1
                emp_existing.append({
                    "leaveType": lt_code,
                    "calendarYear": cycle_year,
                    "availableBalance": existing.get("availableBalance", 0.0),
                    "openingBalance": existing.get("openingBalance", 0.0)
                })
            else:
                missing_ledgers_count += 1
                proposed_creations += 1
                
                # In dry run mode, compute proposed ledger without writing
                if not is_apply:
                    virtual_doc = await ledger_svc.get_or_create_ledger(
                        emp_id, emp_code, now, lt_code, create_if_missing=False
                    )
                    emp_missing.append({
                        "leaveType": lt_code,
                        "calendarYear": cycle_year,
                        "proposedEntitlement": virtual_doc.get("annualEntitlement", 0.0) if virtual_doc else t.get("annualEntitlement", 0.0)
                    })
                else:
                    # Apply mode
                    try:
                        res_doc = await ledger_svc.get_or_create_ledger(
                            emp_id, emp_code, now, lt_code, create_if_missing=True
                        )
                        if res_doc:
                            emp_created.append({
                                "leaveType": lt_code,
                                "calendarYear": cycle_year,
                                "availableBalance": res_doc.get("availableBalance", 0.0),
                                "openingBalance": res_doc.get("openingBalance", 0.0)
                            })
                    except Exception as err:
                        errors_count += 1
                        logger.error(f"Failed to create ledger for emp {emp_id}, {lt_code}: {err}")
                        
        candidate_reports.append({
            "employeeId": emp_id,
            "employeeCode": emp_code,
            "status": "PROCESSED",
            "doj": doj.isoformat(),
            "cycleYear": cycle_year,
            "existingLedgers": emp_existing,
            "missingLedgers": emp_missing,
            "createdLedgers": emp_created
        })

    report_summary = {
        "mode": "APPLY" if is_apply else "DRY_RUN",
        "timestamp": now.isoformat(),
        "totalEmployeesScanned": total_scanned,
        "eligibleEmployees": eligible_count,
        "existingLedgerRecordsFound": existing_ledgers_found,
        "missingLedgerRecords": missing_ledgers_count,
        "recordsProposedForCreation": proposed_creations,
        "recordsSkipped": skipped_count,
        "recordsRequiringManualReview": manual_review_count,
        "errors": errors_count,
        "manualReviewDetails": duplicate_review,
        "candidates": candidate_reports
    }
    
    print("\n" + "="*60)
    print("LEAVE LEDGER RECONCILIATION SUMMARY")
    print("="*60)
    print(f"Mode:                            {report_summary['mode']}")
    print(f"Total employees scanned:         {report_summary['totalEmployeesScanned']}")
    print(f"Eligible employees:              {report_summary['eligibleEmployees']}")
    print(f"Existing ledger records found:   {report_summary['existingLedgerRecordsFound']}")
    print(f"Missing ledger records:          {report_summary['missingLedgerRecords']}")
    print(f"Records proposed for creation:   {report_summary['recordsProposedForCreation']}")
    print(f"Records skipped:                 {report_summary['recordsSkipped']}")
    print(f"Records requiring manual review: {report_summary['recordsRequiringManualReview']}")
    print(f"Errors encountered:              {report_summary['errors']}")
    print("="*60 + "\n")
    
    if args.report:
        try:
            with open(args.report, 'w', encoding='utf-8') as f:
                json.dump(report_summary, f, indent=2, default=str)
            logger.info(f"Detailed reconciliation report saved to: {args.report}")
        except Exception as e:
            logger.error(f"Failed to save report to {args.report}: {e}")
            
    return 0

def main():
    parser = argparse.ArgumentParser(description="Reconcile missing leave ledgers for eligible employees.")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Default dry-run mode (no writes).")
    parser.add_argument("--apply", action="store_true", default=False, help="Explicitly enable writes to persist missing ledgers.")
    parser.add_argument("--employee-id", type=str, default=None, help="Restrict to a single employeeId.")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of employees processed.")
    parser.add_argument("--report", type=str, default=None, help="Path to output JSON summary report.")
    
    args = parser.parse_args()
    if args.apply:
        args.dry_run = False
        
    return asyncio.run(run_reconciliation(args))

if __name__ == "__main__":
    sys.exit(main())

