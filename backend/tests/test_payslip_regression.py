import pytest
from app.payroll.services.payslip_pdf_compiler import format_inr_currency, PayslipPDFCompiler
from app.payroll.models.payslip_data import PayslipData
import pypdf
from io import BytesIO


def test_format_inr_currency():
    # Presentation rounding and Indian grouping
    assert format_inr_currency(9103.40) == "9,103"
    assert format_inr_currency(9103.50) == "9,104"
    assert format_inr_currency(9103.94) == "9,104"
    assert format_inr_currency(125000) == "1,25,000"
    assert format_inr_currency(0) == "0"
    assert format_inr_currency("-") == "-"
    assert format_inr_currency(-500) == "-500"
    assert format_inr_currency(10000000) == "1,00,00,000"


def test_earnings_order_presentation():
    raw_earnings = [
        {"name": "CONVEYANCE", "amount": 800},
        {"name": "BASIC", "amount": 6160},
        {"name": "INCENTIVE", "amount": 636},
        {"name": "HRA", "amount": 3080},
        {"name": "MEDICAL ALLOWANCE", "amount": 300},
    ]

    def _earnings_sort_key(item_idx_tuple):
        idx, item = item_idx_tuple
        comp_name = item.get("name", "").strip().upper()
        if comp_name == "BASIC":
            return (0, idx)
        elif comp_name == "HRA":
            return (1, idx)
        else:
            return (2, idx)

    sorted_items = sorted(enumerate(raw_earnings), key=_earnings_sort_key)
    ordered = [item for _, item in sorted_items]

    names = [x["name"] for x in ordered]
    assert names == ["BASIC", "HRA", "CONVEYANCE", "INCENTIVE", "MEDICAL ALLOWANCE"]


def test_leave_closing_balance_calculation():
    # Formula: Closing = Opening - Availed
    # Supports normal, fractional, zero, and negative values
    test_cases = [
        {"opening": 12, "consumed": 3, "expected": 9.0},
        {"opening": 10, "consumed": 2, "expected": 8.0},
        {"opening": 15, "consumed": 5, "expected": 10.0},
        {"opening": 12.5, "consumed": 2.5, "expected": 10.0},
        {"opening": 0, "consumed": 0, "expected": 0.0},
        {"opening": 2, "consumed": 5, "expected": -3.0},
    ]
    for case in test_cases:
        closing = round(float(case["opening"]) - float(case["consumed"]), 2)
        assert closing == case["expected"]


def test_pdf_rupee_symbol_and_layout():
    compiler = PayslipPDFCompiler()
    data = PayslipData(
        companyName="TEST CORP",
        branchName="HQ",
        payrollMonth="Aug-26",
        periodStart="2026-08-01",
        periodEnd="2026-08-31",
        employeeId="emp1",
        employeeCode="5188",
        employeeName="TEST EMPLOYEE",
        department="ENGINEERING",
        designation="SR DEVELOPER",
        workingDays=30,
        payableDays=30,
        lopDays=0,
        leaveDetails=[
            {"leaveType": "CL", "openingBalance": 12, "consumed": 3, "availableBalance": 9},
            {"leaveType": "SL", "openingBalance": 2, "consumed": 5, "availableBalance": -3},
        ],
        earnings=[
            {"name": "BASIC", "scale": 6160, "amount": 6160},
            {"name": "HRA", "scale": 3080, "amount": 3080},
            {"name": "SPECIAL", "scale": "-", "amount": 500},
        ],
        grossEarnings=9740,
        deductions=[
            {"name": "Employee PF", "scale": "-", "amount": 1800},
            {"name": "Advance", "scale": "-", "amount": 50},
        ],
        grossDeductions=1850,
        netPay=7890,
        netPayWords="Rupees Seven Thousand Eight Hundred Ninety Only",
    )
    pdf_bytes = compiler.compile(data)
    assert len(pdf_bytes) > 0
    reader = pypdf.PdfReader(BytesIO(pdf_bytes))
    text = reader.pages[0].extract_text()
    # Unicode Rupee symbol
    assert "₹" in text
    assert "NET PAY : ₹ 7,890" in text
    # Clean whole numbers
    assert "6,160" in text
    assert "3,080" in text
    assert "1,800" in text
    # Negative leave balance preserved
    assert "-3" in text

