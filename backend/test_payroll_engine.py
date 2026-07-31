from datetime import datetime
from app.domain_models import PFRule, ESIRule, ProfessionalTaxSlab
from app.payroll.services.payroll_calculation_service import PayrollCalculationEngine

def run_tests():
    # Setup Rules
    pf_rule = PFRule(
        effectiveFrom=datetime.now(),
        pfEnabled=True,
        mandatoryBelowGross=15000.0,
        pfCeilingAmount=15000.0,
        employeePfPercent=12.0,
        employerPfPercent=3.67,
        employerPensionPercent=8.33,
        maxPensionAmount=1250.0,
        allowExistingPensionMember=True,
        allowFresherLogic=True,
        processingFeeEnabled=False
    )
    
    esi_rule = ESIRule(
        effectiveFrom=datetime.now(),
        esiEnabled=True,
        eligibilityGross=21000.0,
        employeePercent=0.75,
        employerPercent=3.25,
        roundOffRule="Ceil"
    )
    
    pt_slabs = [
        ProfessionalTaxSlab(ptStateId="state1", minGross=0, maxGross=3500, taxAmount=0),
        ProfessionalTaxSlab(ptStateId="state1", minGross=3501, maxGross=5000, taxAmount=25),
        ProfessionalTaxSlab(ptStateId="state1", minGross=5001, maxGross=9999999, taxAmount=100)
    ]
    
    print("--- Scenario 1: PF Gross < Mandatory PF ---")
    res1 = PayrollCalculationEngine.calculatePf(14999.0, pf_rule, {"wantsPf": False})
    print(f"PF Gross 14,999 (wantsPf=False) => Employee PF: {res1['employeePf']} (Expected: 1800.0 approx)")
    assert res1['employeePf'] > 0

    print("\n--- Scenario 2: PF Gross >= Threshold (Prompt for PF option) ---")
    res2 = PayrollCalculationEngine.calculatePf(15000.0, pf_rule, {"wantsPf": False})
    print(f"PF Gross 15,000 (wantsPf=False) => Employee PF: {res2['employeePf']} (Expected: 0.0)")
    assert res2['employeePf'] == 0.0

    print("\n--- Scenario 3 & 4: Actual PF Calculated on PF Gross / Ceiling ---")
    res3 = PayrollCalculationEngine.calculatePf(20000.0, pf_rule, {"wantsPf": True, "useCeiling": True})
    print(f"PF Gross 20,000 (wantsPf=True, useCeiling=True) => Employee PF: {res3['employeePf']} (Expected: 1800.0)")
    assert res3['employeePf'] == 1800.0

    res4 = PayrollCalculationEngine.calculatePf(20000.0, pf_rule, {"wantsPf": True, "useCeiling": False})
    print(f"PF Gross 20,000 (wantsPf=True, useCeiling=False) => Employee PF: {res4['employeePf']} (Expected: 2400.0)")
    assert res4['employeePf'] == 2400.0

    print("\n--- Scenario 5: Existing Pension Member ---")
    res5 = PayrollCalculationEngine.calculatePf(20000.0, pf_rule, {"wantsPf": True, "useCeiling": False, "isExistingPensionMember": True})
    print(f"PF Gross 20,000 (Existing Pension) => Pension: {res5['employerPension']} (Expected: 1250.0 ceiling applied), Employer PF: {res5['employerPf']}")
    assert res5['employerPension'] == 1250.0

    print("\n--- Scenario 6: New Employee (Fresher logic) ---")
    res6 = PayrollCalculationEngine.calculatePf(20000.0, pf_rule, {"wantsPf": True, "useCeiling": False, "isExistingPensionMember": False})
    print(f"PF Gross 20,000 (Fresher > 15k) => Pension: {res6['employerPension']} (Expected: 0.0), Employer PF: {res6['employerPf']} (Expected: 2400.0)")
    assert res6['employerPension'] == 0.0
    assert res6['employerPf'] == 2400.0

    print("\n--- Scenario 7: ESI Eligible ---")
    res7 = PayrollCalculationEngine.calculateEsi(15000.0, esi_rule)
    print(f"ESI Gross 15,000 => Employee ESI: {res7['employeeEsi']} (Expected: 113.0)")
    assert res7['employeeEsi'] > 0

    print("\n--- Scenario 8: ESI Not Eligible ---")
    res8 = PayrollCalculationEngine.calculateEsi(22000.0, esi_rule)
    print(f"ESI Gross 22,000 => Employee ESI: {res8['employeeEsi']} (Expected: 0.0)")
    assert res8['employeeEsi'] == 0.0

    print("\n--- Scenario 9: Professional Tax ---")
    res9_1 = PayrollCalculationEngine.calculateProfessionalTax(4000.0, pt_slabs)
    print(f"Gross 4,000 => PT: {res9_1} (Expected: 25)")
    assert res9_1 == 25

    res9_2 = PayrollCalculationEngine.calculateProfessionalTax(10000.0, pt_slabs)
    print(f"Gross 10,000 => PT: {res9_2} (Expected: 100)")
    assert res9_2 == 100

    print("\nAll Scenarios Passed Successfully!")

if __name__ == "__main__":
    run_tests()
