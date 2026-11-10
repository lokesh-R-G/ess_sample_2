# Individual Employee Payslip Generation and Email Script

The script `backend/scripts/generate_employee_payslip.py` generates and emails a finalized payslip PDF for an individual employee by employee code. It reuses the core ESS payroll architecture and includes all recent PDF improvements (presentation ordering, whole-rupee Indian formatting, Unicode Rupee symbol ₹, and dynamic leave closing balance calculation).

---

## 1. Syntax and Usage

The script can be executed from the project root or the `backend/` directory.

### Quick Shorthand Syntax
```bash
python backend/scripts/generate_employee_payslip.py --1024
```

### Standard Syntax
```bash
python backend/scripts/generate_employee_payslip.py --employee-code 1024
```

---

## 2. Options and Flags

| Argument | Description | Example |
|---|---|---|
| `--<CODE>` | Shorthand employee code | `--1024` or `--5188` |
| `--employee-code <CODE>` | Standard employee code parameter | `--employee-code 1024` |
| `--period <YYYY-MM>` | Select a specific finalized period | `--period 2026-08` |
| `--output-dir <PATH>` | Custom output directory for PDFs | `--output-dir "D:/ESS_Payslips"` |
| `--no-email` | Generate and save PDF without sending email | `--no-email` |
| `--dry-run` | Show resolved employee, period, recipient without generating or emailing | `--dry-run` |
| `--force` | Overwrite existing payslip PDF if already generated | `--force` |
| `--help` | Display usage and help message | `--help` |

---

## 3. Directory Structure for Generated PDFs

Payslip PDFs are saved in isolated directories per employee and per payroll cycle:

```text
backend/
    generated_payslips/
        1024/
            2026-08/
                payslip_1024_2026-08.pdf
        1025/
            2026-08/
                payslip_1025_2026-08.pdf
```

---

## 4. Execution Workflow

1. **Resolve Employee**: Looks up `employeeCode` to find `employeeId`, full name, company, and registered contact email.
2. **Resolve Payroll Period**: Discovers the latest finalized/published payroll snapshot (or the period requested with `--period`).
3. **Generate PDF**: Invokes `PayslipDataBuilder` and `PayslipPDFCompiler` with the approved presentation rules:
   - `BASIC` is 1st, `HRA` is 2nd, followed by remaining earnings in their original relative sequence.
   - Clean column alignment with fixed percentages (`32%`, `14%`, `14%`, `26%`, `14%`).
   - Whole-rupee formatting with Indian comma grouping (`1,25,000`).
   - Unicode Indian Rupee symbol (`₹`).
   - Dynamic leave calculation: `Closing = Opening - Availed`.
4. **Save in Individual Directory**: Stores the PDF inside `generated_payslips/<employeeCode>/<period>/`.
5. **Email Delivery**: Uses `EmailService` and FastMail SMTP to attach the generated PDF and deliver it directly to the employee's registered email address only.
6. **Execution Summary**: Displays a clean console summary without exposing sensitive credentials.

---

## 5. Automated Tests

Run the test suite:
```bash
python -m pytest backend/tests/test_generate_employee_payslip.py
```

