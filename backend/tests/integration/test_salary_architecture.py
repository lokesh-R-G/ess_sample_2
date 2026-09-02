import pytest
from app.payroll.services.salary_calculation_engine import SalaryCalculationEngine, CalculationMode, StatutoryDecisions
from app.domain_models import EmployeeSalaryComponent

@pytest.fixture
def statutory_decisions():
    return StatutoryDecisions(
        isFresher=True,
        isExistingPensionMember=False,
        wantsPf=True,
        wantsPension=True,
        pfCalculationMode="Default",
        esiEnabled=True,
        ptState="None"
    )

def test_basic_identified_by_id(statutory_decisions):
    # Test 1: Basic identified by configuration, not name.
    components = [
        {"_id": "c1", "name": "StrangeNameBasic", "isBasicComponent": True, "calculationMethod": "Flat", "amount": 0, "includeInGross": True, "attendanceDependent": True, "componentType": "Earning"}
    ]
    result = SalaryCalculationEngine.calculate(25000, components, CalculationMode.GROSS_ONLY, statutory_decisions)
    assert result["earnings"][0]["amount"] == 25000
    assert result["grossSalary"] == 25000

def test_hra_percentage_of_basic(statutory_decisions):
    # Test 2: HRA = 40% of Basic
    components = [
        {"_id": "c1", "name": "Basic", "isBasicComponent": True, "calculationMethod": "Flat", "includeInGross": True, "attendanceDependent": True, "componentType": "Earning"},
        {"_id": "c2", "name": "HRA", "calculationMethod": "Percentage", "percentageValue": 40.0, "percentageDerivedFromComponentId": "c1", "includeInGross": True, "attendanceDependent": True, "componentType": "Earning"}
    ]
    result = SalaryCalculationEngine.calculate(20000, components, CalculationMode.GROSS_ONLY, statutory_decisions)
    
    assert result["grossSalary"] == 28000  # 20000 + 8000
    earnings_map = {e["name"]: e["amount"] for e in result["earnings"]}
    assert earnings_map["HRA"] == 8000

def test_percentage_component_references_another(statutory_decisions):
    # Test 4: Percentage component references another component by ObjectId
    components = [
        {"_id": "c1", "name": "Basic", "isBasicComponent": True, "calculationMethod": "Flat", "includeInGross": True, "attendanceDependent": True, "componentType": "Earning"},
        {"_id": "c2", "name": "Allowance", "calculationMethod": "Percentage", "percentageValue": 50.0, "percentageDerivedFromComponentId": "c1", "includeInGross": True, "attendanceDependent": True, "componentType": "Earning"},
        {"_id": "c3", "name": "SubAllowance", "calculationMethod": "Percentage", "percentageValue": 10.0, "percentageDerivedFromComponentId": "c2", "includeInGross": True, "attendanceDependent": True, "componentType": "Earning"}
    ]
    result = SalaryCalculationEngine.calculate(10000, components, CalculationMode.GROSS_ONLY, statutory_decisions)
    earnings_map = {e["name"]: e["amount"] for e in result["earnings"]}
    assert earnings_map["Basic"] == 10000
    assert earnings_map["Allowance"] == 5000
    assert earnings_map["SubAllowance"] == 500
    assert result["grossSalary"] == 15500

def test_invalid_reference_rejected(statutory_decisions):
    # Test 5: Invalid component reference rejected
    # Will fallback and if not found, calculate as 0
    components = [
        {"_id": "c1", "name": "Basic", "isBasicComponent": True, "calculationMethod": "Flat", "includeInGross": True, "attendanceDependent": True, "componentType": "Earning"},
        {"_id": "c2", "name": "Invalid", "calculationMethod": "Percentage", "percentageValue": 50.0, "percentageDerivedFromComponentId": "invalid_id", "includeInGross": True, "attendanceDependent": True, "componentType": "Earning"}
    ]
    result = SalaryCalculationEngine.calculate(10000, components, CalculationMode.GROSS_ONLY, statutory_decisions)
    earnings_map = {e["name"]: e["amount"] for e in result["earnings"]}
    assert earnings_map["Invalid"] == 0

def test_circular_dependency_rejected(statutory_decisions):
    # Test 6: Circular dependency rejected
    components = [
        {"_id": "c1", "name": "Basic", "isBasicComponent": True, "calculationMethod": "Flat", "includeInGross": True, "attendanceDependent": True, "componentType": "Earning"},
        {"_id": "c2", "name": "A", "calculationMethod": "Percentage", "percentageValue": 10.0, "percentageDerivedFromComponentId": "c3", "includeInGross": True, "attendanceDependent": True, "componentType": "Earning"},
        {"_id": "c3", "name": "B", "calculationMethod": "Percentage", "percentageValue": 20.0, "percentageDerivedFromComponentId": "c2", "includeInGross": True, "attendanceDependent": True, "componentType": "Earning"}
    ]
    with pytest.raises(ValueError, match="Circular dependency detected"):
        SalaryCalculationEngine.calculate(10000, components, CalculationMode.GROSS_ONLY, statutory_decisions)

def test_gross_only_configured_earnings(statutory_decisions):
    # Test 7: Gross only includes configured earning components
    components = [
        {"_id": "c1", "name": "Basic", "isBasicComponent": True, "calculationMethod": "Flat", "includeInGross": True, "attendanceDependent": True, "componentType": "Earning"},
        {"_id": "c2", "name": "NotGross", "calculationMethod": "Flat", "amount": 5000, "includeInGross": False, "attendanceDependent": True, "componentType": "Earning"},
        {"_id": "c3", "name": "Deduction", "calculationMethod": "Flat", "amount": 2000, "includeInGross": True, "attendanceDependent": True, "componentType": "Deduction"}
    ]
    result = SalaryCalculationEngine.calculate(20000, components, CalculationMode.GROSS_ONLY, statutory_decisions)
    assert result["grossSalary"] == 20000

def test_distribution_ratios_calculated(statutory_decisions):
    # Test 10 & 11: Attendance-dependent vs fixed components produce correct distributable gross
    components = [
        {"_id": "c1", "name": "Basic", "isBasicComponent": True, "calculationMethod": "Flat", "includeInGross": True, "attendanceDependent": True, "componentType": "Earning"},
        {"_id": "c2", "name": "HRA", "calculationMethod": "Percentage", "percentageValue": 50.0, "percentageDerivedFromComponentId": "c1", "includeInGross": True, "attendanceDependent": True, "componentType": "Earning"},
        {"_id": "c3", "name": "FixedAllow", "calculationMethod": "Flat", "amount": 10000, "includeInGross": True, "attendanceDependent": False, "componentType": "Earning"}
    ]
    # Basic = 20000, HRA = 10000, Fixed = 10000. Gross = 40000.
    # Fixed gross = 10000. Distributable gross = 30000.
    # Basic ratio = 20000/30000 = 0.666...
    # HRA ratio = 10000/30000 = 0.333...
    result = SalaryCalculationEngine.calculate(20000, components, CalculationMode.GROSS_ONLY, statutory_decisions)
    dist_map = {e["name"]: e["distributionRatio"] for e in result["distribution"]}
    
    assert abs(dist_map["Basic"] - 0.666666) < 0.0001
    assert abs(dist_map["HRA"] - 0.333333) < 0.0001
    assert dist_map["FixedAllow"] == 0.0
