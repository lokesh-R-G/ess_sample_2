#!/usr/bin/env python3
"""
Individual Employee Payslip Generation and Email Script.

Usage:
    python backend/scripts/generate_employee_payslip.py --1024
    python backend/scripts/generate_employee_payslip.py --employee-code 1024
    python backend/scripts/generate_employee_payslip.py --1024 --period 2026-08 --dry-run
    python backend/scripts/generate_employee_payslip.py --1024 --no-email
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
import argparse
import asyncio
from bson import ObjectId

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Ensure root dir is also on sys.path if needed
root_dir = backend_dir.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Load .env
from dotenv import load_dotenv
env_path = backend_dir / ".env"
if env_path.exists():
    load_dotenv(str(env_path))
else:
    root_env = root_dir / ".env"
    if root_env.exists():
        load_dotenv(str(root_env))

from app.db.mongo import get_database
from app.payroll.services.payslip_data_builder import PayslipDataBuilder
from app.payroll.services.payslip_pdf_compiler import PayslipPDFCompiler
from app.employee.services.email_resolver import get_employee_personal_email
from app.email_service.services.email_service import EmailService
from app.email_service.schemas.email_log import EmailLogCreate


def parse_arguments(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments supporting:
      --<code_digits> (e.g. --1024)
      --employee-code 1024
      --period YYYY-MM
      --output-dir PATH
      --no-email
      --force
      --dry-run
    """
    raw_args = list(sys.argv[1:] if argv is None else argv)
    cleaned_args = []
    shorthand_code = None

    for arg in raw_args:
        # Check for shorthand syntax like --1024 or --5188
        if arg.startswith("--") and len(arg) > 2 and arg[2:].isdigit():
            if shorthand_code is None:
                shorthand_code = arg[2:]
            else:
                print(f"[Error] Multiple employee codes specified: {shorthand_code} and {arg[2:]}", file=sys.stderr)
                sys.exit(1)
        else:
            cleaned_args.append(arg)

    parser = argparse.ArgumentParser(
        description="Generate and email an individual employee payslip PDF using existing ESS payroll architecture.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python backend/scripts/generate_employee_payslip.py --1024
  python backend/scripts/generate_employee_payslip.py --employee-code 1024
  python backend/scripts/generate_employee_payslip.py --employee-code 1024 --period 2026-08
  python backend/scripts/generate_employee_payslip.py --1024 --no-email
  python backend/scripts/generate_employee_payslip.py --1024 --dry-run
        """
    )

    parser.add_argument(
        "--employee-code",
        dest="employee_code",
        type=str,
        default=shorthand_code,
        help="Employee code (e.g. 1024 or 5188)"
    )
    parser.add_argument(
        "--period",
        dest="period",
        type=str,
        default=None,
        help="Specific payroll period formatted as YYYY-MM (e.g. 2026-08)"
    )
    parser.add_argument(
        "--output-dir",
        dest="output_dir",
        type=str,
        default=None,
        help="Custom output root directory for generated payslips (defaults to backend/generated_payslips)"
    )
    parser.add_argument(
        "--no-email",
        dest="no_email",
        action="store_true",
        help="Generate and save the PDF without sending an email"
    )
    parser.add_argument(
        "--force",
        dest="force",
        action="store_true",
        help="Allow regenerating and overwriting an existing PDF file"
    )
    parser.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        help="Display resolved employee, payroll period, and recipient without generating or emailing"
    )

    parsed = parser.parse_args(cleaned_args)

    if not parsed.employee_code:
        parser.print_help(file=sys.stderr)
        print("\n[Error] Employee code is required (e.g., --1024 or --employee-code 1024)", file=sys.stderr)
        sys.exit(1)

    return parsed


async def resolve_employee(db, employee_code: str) -> Dict[str, Any]:
    """
    Step 1: Resolve employee using employeeCode.
    Returns dictionary with employee details or exits with error.
    """
    # Find employee by employeeCode
    emp = await db.employees.find_one({"employeeCode": employee_code, "isCurrent": True})
    if not emp:
        # Fallback to any current/active match
        emp = await db.employees.find_one({"employeeCode": employee_code})
    
    if not emp:
        print(f"[Error] Employee with code '{employee_code}' does not exist.", file=sys.stderr)
        sys.exit(1)

    emp_id = str(emp.get("employeeId"))
    if not emp_id:
        print(f"[Error] Employee record for code '{employee_code}' lacks an internal employeeId.", file=sys.stderr)
        sys.exit(1)

    # Resolve name from employee_personals or emp document
    emp_personal = await db.employee_personals.find_one({"employeeId": emp_id, "isCurrent": True})
    first_name = (emp_personal.get("firstName") if emp_personal else None) or emp.get("firstName", "")
    last_name = (emp_personal.get("lastName") if emp_personal else None) or emp.get("lastName", "")
    full_name = f"{first_name} {last_name}".strip() or emp.get("employeeName", f"Employee {employee_code}")

    # Resolve company name
    company_name = "Enterprise Organisation"
    hist = await db.employee_employment_histories.find_one({"employeeId": emp_id, "isCurrent": True})
    company_id = hist.get("companyId") if hist else emp.get("companyId")
    if company_id:
        comp = await db.companies.find_one({"_id": ObjectId(company_id)}) if len(str(company_id)) == 24 else await db.companies.find_one({"_id": company_id})
        if comp and comp.get("name"):
            company_name = comp.get("name")

    # Resolve registered official/personal email
    email = None
    try:
        email = await get_employee_personal_email(db, emp_id)
    except Exception:
        # Fallback to email on emp document
        email = emp.get("email") or (emp_personal.get("email") if emp_personal else None)

    return {
        "employeeCode": employee_code,
        "employeeId": emp_id,
        "fullName": full_name,
        "companyName": company_name,
        "companyId": str(company_id) if company_id else None,
        "email": email,
        "status": emp.get("status", "Active")
    }


def extract_period_key(cycle_doc: Dict[str, Any]) -> Tuple[str, str]:
    """
    Extract (YYYY-MM, Pretty Name) from a cycle document.
    """
    dt = cycle_doc.get("startDate") or cycle_doc.get("periodStart")
    if isinstance(dt, datetime):
        period_key = dt.strftime("%Y-%m")
        pretty_name = dt.strftime("%B %Y")
        return period_key, pretty_name
    
    # Fallback to name
    name = str(cycle_doc.get("name", "Unknown Period"))
    return name.replace(" ", "_"), name


async def resolve_payroll_period(
    db, 
    emp_info: Dict[str, Any], 
    requested_period: Optional[str] = None
) -> Tuple[Dict[str, Any], Dict[str, Any], str, str]:
    """
    Step 2: Resolve the appropriate finalized payroll record and cycle.
    Returns (payroll_doc, cycle_doc, period_key, pretty_period_name).
    """
    emp_code = emp_info["employeeCode"]
    emp_id = emp_info["employeeId"]

    # Query all payroll records for this employee
    payroll_cursor = db.payrolls.find({
        "$or": [{"employeeCode": emp_code}, {"employeeId": emp_id}]
    })
    payrolls = await payroll_cursor.to_list(100)

    if not payrolls:
        print(f"[Error] No payroll records found for employee code '{emp_code}' (ID: {emp_id}).", file=sys.stderr)
        sys.exit(1)

    # Allowed finalized statuses in ESS payroll
    FINALIZED_STATUSES = {"FINALIZED", "PUBLISHED", "EXPORTED"}

    eligible_options = []

    for p in payrolls:
        c_id = p.get("cycleId")
        if not c_id:
            continue
        cycle = await db.payroll_cycles.find_one({"_id": ObjectId(c_id)}) if len(str(c_id)) == 24 else await db.payroll_cycles.find_one({"_id": c_id})
        if not cycle:
            continue

        # Check payroll run status for this cycle
        run = await db.payroll_runs.find_one({"cycleId": str(c_id)})
        run_status = (run.get("status") if run else "").upper()
        p_status = (p.get("status") or "").upper()

        is_eligible = (
            run_status in FINALIZED_STATUSES or
            p_status in {"FINALIZED", "PUBLISHED", "GENERATED"}
        )

        if not is_eligible:
            continue

        period_key, pretty_name = extract_period_key(cycle)
        dt = cycle.get("startDate") or cycle.get("periodStart") or datetime.min

        eligible_options.append({
            "payroll": p,
            "cycle": cycle,
            "period_key": period_key,
            "pretty_name": pretty_name,
            "start_dt": dt if isinstance(dt, datetime) else datetime.min
        })

    if not eligible_options:
        print(f"[Error] No finalized or eligible payroll cycle found for employee '{emp_code}'.", file=sys.stderr)
        sys.exit(1)

    # Sort descending by period start date
    eligible_options.sort(key=lambda x: x["start_dt"], reverse=True)

    # If requested_period is specified, match against period_key or cycle name
    if requested_period:
        clean_req = requested_period.strip().lower()
        matched = [
            opt for opt in eligible_options
            if opt["period_key"].lower() == clean_req or clean_req in opt["pretty_name"].lower()
        ]
        if not matched:
            print(f"[Error] Requested period '{requested_period}' not found among eligible cycles for employee '{emp_code}'.", file=sys.stderr)
            print("Available periods:", file=sys.stderr)
            for opt in eligible_options:
                print(f"  - {opt['period_key']} ({opt['pretty_name']})", file=sys.stderr)
            sys.exit(1)
        selected = matched[0]
    else:
        # Pick latest eligible cycle safely
        selected = eligible_options[0]

    return (
        selected["payroll"],
        selected["cycle"],
        selected["period_key"],
        selected["pretty_name"]
    )


def build_payslip_pdf(
    payslip_data, 
    output_path: Path
) -> bytes:
    """
    Step 3: Generate PDF using PayslipPDFCompiler with all registered fonts and formatters.
    """
    compiler = PayslipPDFCompiler()
    pdf_bytes = compiler.compile(payslip_data)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(pdf_bytes)
    return pdf_bytes


async def send_payslip_email(
    db, 
    emp_info: Dict[str, Any], 
    period_name: str, 
    pdf_path: Path
) -> bool:
    """
    Step 5: Send PDF attachment to the employee's registered email using EmailService.
    """
    recipient = emp_info.get("email")
    if not recipient or "@" not in recipient:
        raise ValueError(f"Employee {emp_info['employeeCode']} has no valid registered email address ({recipient})")

    email_service = EmailService(db)
    subject = f"Your Payslip for {period_name}"
    
    context = {
        "payroll_month": period_name,
        "salary_period": period_name,
        "employee_name": emp_info["fullName"]
    }
    
    filename = pdf_path.name
    attachments = [{
        "file": str(pdf_path),
        "headers": {"Content-Disposition": f'attachment; filename="{filename}"'},
        "mime_type": "application/pdf"
    }]

    # Send directly using FastMail in EmailService
    from fastapi_mail import MessageSchema, MessageType
    message = MessageSchema(
        subject=subject,
        recipients=[recipient],
        template_body=context,
        subtype=MessageType.html,
        attachments=attachments
    )
    
    try:
        await email_service.fm.send_message(message, template_name="payslip_email.html")
        
        # Log success in email logs
        log_entry = EmailLogCreate(
            recipient=recipient,
            subject=subject,
            template="payslip_email.html",
            status="Sent",
            sent_time=datetime.now(timezone.utc),
            attachment=filename
        )
        await email_service._log_email(log_entry)
        return True
    except Exception as e:
        log_entry = EmailLogCreate(
            recipient=recipient,
            subject=subject,
            template="payslip_email.html",
            status="Failed",
            failure_reason=str(e),
            attachment=filename
        )
        await email_service._log_email(log_entry)
        raise RuntimeError(f"SMTP delivery failed: {e}")


def print_summary(
    emp_info: Dict[str, Any],
    period_name: str,
    pdf_location: Optional[str],
    email_status: str,
    dry_run: bool = False
):
    """Step 6: Display execution summary cleanly."""
    status_title = "DRY RUN COMPLETED (NO ACTIONS PERFORMED)" if dry_run else "PROCESS COMPLETED"
    print("\n" + "=" * 48)
    print("          ESS INDIVIDUAL PAYSLIP")
    print("=" * 48)
    print(f"Employee Code : {emp_info['employeeCode']}")
    print(f"Employee ID   : {emp_info['employeeId']}")
    print(f"Employee Name : {emp_info['fullName']}")
    print(f"Company       : {emp_info['companyName']}")
    print(f"Payroll Period: {period_name}")
    print("-" * 48)
    if dry_run:
        print("Mode          : DRY-RUN")
        print(f"Target PDF    : {pdf_location}")
        print(f"Recipient     : {emp_info.get('email') or 'NOT REGISTERED'}")
    else:
        print(f"PDF Generation: SUCCESS")
        print(f"PDF Location  : {pdf_location}")
        print(f"Email Recipient: {emp_info.get('email')}")
        print(f"Email Status   : {email_status}")
    print("=" * 48)
    print(f"          {status_title}")
    print("=" * 48 + "\n")


async def main_async(args: argparse.Namespace):
    db = get_database()
    
    # 1. Resolve Employee
    emp_info = await resolve_employee(db, args.employee_code)

    # 2. Resolve Payroll Period
    payroll_doc, cycle_doc, period_key, period_name = await resolve_payroll_period(
        db, emp_info, args.period
    )

    # Determine destination path
    if args.output_dir:
        base_out = Path(args.output_dir).resolve()
    else:
        base_out = (backend_dir / "generated_payslips").resolve()

    employee_dir = base_out / args.employee_code / period_key
    pdf_filename = f"payslip_{args.employee_code}_{period_key}.pdf"
    pdf_path = employee_dir / pdf_filename

    # If dry-run, stop after printing resolved plan
    if args.dry_run:
        print_summary(emp_info, period_name, str(pdf_path), "DRY-RUN", dry_run=True)
        return

    # Check if PDF already exists
    if pdf_path.exists() and not args.force:
        print(f"[Warning] PDF already exists at '{pdf_path}'.", file=sys.stderr)
        print("Use --force to regenerate and overwrite this payslip.", file=sys.stderr)
        sys.exit(1)

    # 3. Generate Payslip PDF Data & Compile
    builder = PayslipDataBuilder(db)
    payslip_data = await builder.build(payroll_doc, cycle_doc)
    
    # Build and write PDF
    build_payslip_pdf(payslip_data, pdf_path)

    # 5. Send Email if requested
    email_status = "SKIPPED (--no-email)"
    if not args.no_email:
        if not emp_info.get("email"):
            print(f"[Error] Employee has no registered email. PDF was generated, but email could not be sent.", file=sys.stderr)
            email_status = "FAILED (Missing Email)"
        else:
            try:
                await send_payslip_email(db, emp_info, period_name, pdf_path)
                email_status = "SENT"
            except Exception as e:
                email_status = f"FAILED ({e})"
                print(f"[Error] Email transmission failed: {e}", file=sys.stderr)
                sys.exit(1)

    # 6. Display Summary
    print_summary(emp_info, period_name, str(pdf_path), email_status)


def main():
    args = parse_arguments()
    try:
        asyncio.run(main_async(args))
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    main()

