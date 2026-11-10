import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import pypdf
from io import BytesIO

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from scripts.generate_employee_payslip import (
    parse_arguments,
    resolve_employee,
    resolve_payroll_period,
    extract_period_key,
    build_payslip_pdf,
    send_payslip_email
)
from app.payroll.models.payslip_data import PayslipData


def test_cli_argument_parsing():
    # 1. Shorthand syntax --1024
    args = parse_arguments(["--1024"])
    assert args.employee_code == "1024"
    assert args.no_email is False
    assert args.dry_run is False

    # 2. Standard syntax --employee-code 1024
    args2 = parse_arguments(["--employee-code", "1024", "--period", "2026-10", "--no-email", "--force"])
    assert args2.employee_code == "1024"
    assert args2.period == "2026-10"
    assert args2.no_email is True
    assert args2.force is True

    # 3. Dry-run option
    args3 = parse_arguments(["--5188", "--dry-run"])
    assert args3.employee_code == "5188"
    assert args3.dry_run is True


@pytest.mark.asyncio
async def test_resolve_employee_not_found():
    mock_db = MagicMock()
    mock_db.employees.find_one = AsyncMock(return_value=None)
    with pytest.raises(SystemExit):
        await resolve_employee(mock_db, "999999")


@pytest.mark.asyncio
async def test_resolve_employee_valid():
    mock_db = MagicMock()
    mock_db.employees.find_one = AsyncMock(return_value={
        "employeeCode": "1024",
        "employeeId": "emp_1024",
        "firstName": "Ushanandhini",
        "lastName": "S",
        "status": "Active"
    })
    mock_db.employee_personals.find_one = AsyncMock(return_value={
        "firstName": "Ushanandhini",
        "lastName": "S",
        "email": "usha@example.com"
    })
    mock_db.employee_employment_histories.find_one = AsyncMock(return_value={
        "companyId": "comp_1"
    })
    mock_db.companies.find_one = AsyncMock(return_value={
        "name": "IDS Logistics"
    })

    emp = await resolve_employee(mock_db, "1024")
    assert emp["employeeCode"] == "1024"
    assert emp["employeeId"] == "emp_1024"
    assert "Ushanandhini" in emp["fullName"]
    assert emp["companyName"] == "IDS Logistics"
    assert emp["email"] == "usha@example.com"


@pytest.mark.asyncio
async def test_resolve_payroll_period():
    from datetime import datetime
    mock_db = MagicMock()
    
    mock_payroll_cursor = MagicMock()
    mock_payroll_cursor.to_list = AsyncMock(return_value=[
        {"cycleId": "cycle_aug", "status": "Generated"},
        {"cycleId": "cycle_jul", "status": "Generated"},
    ])
    mock_db.payrolls.find = MagicMock(return_value=mock_payroll_cursor)

    async def mock_cycle_find(query):
        cid = query.get("_id")
        if cid == "cycle_aug":
            return {"_id": "cycle_aug", "name": "August 2026", "startDate": datetime(2026, 8, 1)}
        elif cid == "cycle_jul":
            return {"_id": "cycle_jul", "name": "July 2026", "startDate": datetime(2026, 7, 1)}
        return None

    mock_db.payroll_cycles.find_one = AsyncMock(side_effect=mock_cycle_find)
    mock_db.payroll_runs.find_one = AsyncMock(return_value={"status": "PUBLISHED"})

    emp_info = {"employeeCode": "1024", "employeeId": "emp_1024"}

    # Default latest
    payroll_doc, cycle_doc, p_key, p_name = await resolve_payroll_period(mock_db, emp_info, None)
    assert p_key == "2026-08"
    assert p_name == "August 2026"

    # Specific period
    payroll_doc2, cycle_doc2, p_key2, p_name2 = await resolve_payroll_period(mock_db, emp_info, "2026-07")
    assert p_key2 == "2026-07"
    assert p_name2 == "July 2026"


def test_build_payslip_pdf(tmp_path):
    out_pdf = tmp_path / "test_slip.pdf"
    data = PayslipData(
        companyName="TEST CORP",
        branchName="HQ",
        payrollMonth="Aug-26",
        periodStart="2026-08-01",
        periodEnd="2026-08-31",
        employeeId="emp1",
        employeeCode="1024",
        employeeName="TEST EMPLOYEE",
        department="TECH",
        designation="DEV",
        workingDays=30,
        payableDays=30,
        lopDays=0,
        earnings=[{"name": "BASIC", "scale": 10000, "amount": 10000}],
        grossEarnings=10000,
        deductions=[],
        grossDeductions=0,
        netPay=10000,
        netPayWords="Rupees Ten Thousand Only"
    )
    pdf_bytes = build_payslip_pdf(data, out_pdf)
    assert out_pdf.exists()
    assert len(pdf_bytes) > 0
    
    r = pypdf.PdfReader(BytesIO(pdf_bytes))
    txt = r.pages[0].extract_text()
    assert "₹" in txt
    assert "10,000" in txt


@pytest.mark.asyncio
async def test_send_payslip_email_missing_email(tmp_path):
    mock_db = MagicMock()
    emp_info = {"employeeCode": "1024", "fullName": "Test", "email": None}
    dummy_file = tmp_path / "dummy.pdf"
    dummy_file.write_bytes(b"%PDF")
    with pytest.raises(ValueError, match="no valid registered email"):
        await send_payslip_email(mock_db, emp_info, "August 2026", dummy_file)


@pytest.mark.asyncio
async def test_send_payslip_email_mocked_success(tmp_path):
    mock_db = MagicMock()
    emp_info = {"employeeCode": "1024", "fullName": "Test", "email": "employee@example.com"}
    dummy_file = tmp_path / "dummy.pdf"
    dummy_file.write_bytes(b"%PDF")

    with patch("scripts.generate_employee_payslip.EmailService") as MockEmailService:
        instance = MockEmailService.return_value
        instance.fm.send_message = AsyncMock(return_value=None)
        instance._log_email = AsyncMock(return_value=None)
        
        ok = await send_payslip_email(mock_db, emp_info, "August 2026", dummy_file)
        assert ok is True
        assert instance.fm.send_message.called


@pytest.mark.asyncio
async def test_send_payslip_email_smtp_failure(tmp_path):
    mock_db = MagicMock()
    emp_info = {"employeeCode": "1024", "fullName": "Test", "email": "employee@example.com"}
    dummy_file = tmp_path / "dummy.pdf"
    dummy_file.write_bytes(b"%PDF")

    with patch("scripts.generate_employee_payslip.EmailService") as MockEmailService:
        instance = MockEmailService.return_value
        instance.fm.send_message = AsyncMock(side_effect=Exception("Connection refused"))
        instance._log_email = AsyncMock(return_value=None)
        
        with pytest.raises(RuntimeError, match="SMTP delivery failed"):
            await send_payslip_email(mock_db, emp_info, "August 2026", dummy_file)

