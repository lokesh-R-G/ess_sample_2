import pytest
from app.payroll.services.payroll_calculation_service import PayrollCalculationEngine
from app.domain_models import PFRule

@pytest.fixture
def pf_rules():
    return PFRule(
        pfEnabled=True,
        pfCeilingAmount=15000.0,
        employeePfPercent=12.0,
        employerPensionPercent=8.33,
        maxPensionAmount=1250.0,
        edliPercent=0.5,
        processingFeeEnabled=True,
        processingFeePercent=0.5,
        effectiveFrom=datetime.utcnow() if 'datetime' in globals() else "2023-04-01T00:00:00Z"
    )

# Case 1: Fresher <= Ceiling
def test_case_1_fresher_below_ceiling(pf_rules):
    result = PayrollCalculationEngine.calculatePf(
        pf_gross=10000.0,
        pf_rules=pf_rules,
        employee_choice={"isFresher": True} # WantsPF shouldn't matter
    )
    # Employee PF = 10000 * 12% = 1200
    # Pension = 10000 * 8.33% = 833
    # Employer PF = 1200 - 833 = 367
    assert result["employeePf"] == 1200
    assert result["employerPension"] == 833
    assert result["employerPf"] == 367

# Case 2: Fresher > Ceiling + PF No
def test_case_2_fresher_above_ceiling_pf_no(pf_rules):
    result = PayrollCalculationEngine.calculatePf(
        pf_gross=30000.0,
        pf_rules=pf_rules,
        employee_choice={"isFresher": True, "wantsPf": False}
    )
    assert result["employeePf"] == 0
    assert result["employerPension"] == 0
    assert result["employerPf"] == 0

# Case 3: Fresher > Ceiling + PF Yes + Actual
def test_case_3_fresher_above_ceiling_pf_yes_actual(pf_rules):
    result = PayrollCalculationEngine.calculatePf(
        pf_gross=30000.0,
        pf_rules=pf_rules,
        employee_choice={"isFresher": True, "wantsPf": True, "useCeiling": False}
    )
    # Employee PF = 30000 * 12% = 3600
    # Pension = 0
    # Employer PF = 3600 - 0 = 3600
    assert result["employeePf"] == 3600
    assert result["employerPension"] == 0
    assert result["employerPf"] == 3600

# Case 4: Fresher > Ceiling + PF Yes + Ceiling
def test_case_4_fresher_above_ceiling_pf_yes_ceiling(pf_rules):
    result = PayrollCalculationEngine.calculatePf(
        pf_gross=30000.0,
        pf_rules=pf_rules,
        employee_choice={"isFresher": True, "wantsPf": True, "useCeiling": True}
    )
    # Employee PF = 15000 * 12% = 1800
    # Pension = 0
    # Employer PF = 1800 - 0 = 1800
    assert result["employeePf"] == 1800
    assert result["employerPension"] == 0
    assert result["employerPf"] == 1800

# Case 5: Existing Pension Member <= Ceiling
def test_case_5_existing_pension_member_below_ceiling(pf_rules):
    result = PayrollCalculationEngine.calculatePf(
        pf_gross=12000.0,
        pf_rules=pf_rules,
        employee_choice={"isFresher": False, "isExistingPensionMember": True}
    )
    # Employee PF = 12000 * 12% = 1440
    # Pension = 12000 * 8.33% = 999.6 -> 1000
    # Employer PF = 1440 - 1000 = 440
    assert result["employeePf"] == 1440
    assert result["employerPension"] == 1000
    assert result["employerPf"] == 440

# Case 6: Existing Pension Member > Ceiling + PF No
def test_case_6_existing_pension_member_above_ceiling_pf_no(pf_rules):
    result = PayrollCalculationEngine.calculatePf(
        pf_gross=30000.0,
        pf_rules=pf_rules,
        employee_choice={"isFresher": False, "isExistingPensionMember": True, "wantsPf": False}
    )
    assert result["employeePf"] == 0
    assert result["employerPension"] == 0
    assert result["employerPf"] == 0

# Case 7: Existing Pension Member > Ceiling + PF Yes + Actual
def test_case_7_existing_pension_member_above_ceiling_pf_yes_actual(pf_rules):
    result = PayrollCalculationEngine.calculatePf(
        pf_gross=30000.0,
        pf_rules=pf_rules,
        employee_choice={"isFresher": False, "isExistingPensionMember": True, "wantsPf": True, "useCeiling": False}
    )
    # Employee PF Base = 30000 -> Employee PF = 3600
    # Pension Base = 15000 -> Pension = 1250 (max)
    # Employer PF = 3600 - 1250 = 2350
    assert result["employeePf"] == 3600
    assert result["employerPension"] == 1250
    assert result["employerPf"] == 2350

# Case 8: Existing Pension Member > Ceiling + PF Yes + Ceiling
def test_case_8_existing_pension_member_above_ceiling_pf_yes_ceiling(pf_rules):
    result = PayrollCalculationEngine.calculatePf(
        pf_gross=30000.0,
        pf_rules=pf_rules,
        employee_choice={"isFresher": False, "isExistingPensionMember": True, "wantsPf": True, "useCeiling": True}
    )
    # Employee PF Base = 15000 -> Employee PF = 1800
    # Pension Base = 15000 -> Pension = 1250 (max)
    # Employer PF = 1800 - 1250 = 550
    assert result["employeePf"] == 1800
    assert result["employerPension"] == 1250
    assert result["employerPf"] == 550

# Test backend protection: Fresher > Ceiling + wantsPf=True + wantsPension=True (invalid frontend input)
def test_fresher_above_ceiling_invalid_pension_request(pf_rules):
    result = PayrollCalculationEngine.calculatePf(
        pf_gross=30000.0,
        pf_rules=pf_rules,
        employee_choice={"isFresher": True, "wantsPf": True, "wantsPension": True, "useCeiling": False}
    )
    # Backend must override wantsPension=True and give 0 pension
    assert result["employeePf"] == 3600
    assert result["employerPension"] == 0
    assert result["employerPf"] == 3600

# Test backend protection: Fresher > Ceiling + wantsPf=False + wantsPension=True
def test_fresher_above_ceiling_wants_pf_false_but_pension_true(pf_rules):
    result = PayrollCalculationEngine.calculatePf(
        pf_gross=30000.0,
        pf_rules=pf_rules,
        employee_choice={"isFresher": True, "wantsPf": False, "wantsPension": True}
    )
    assert result["employeePf"] == 0
    assert result["employerPension"] == 0
    assert result["employerPf"] == 0
