from typing import List, Dict, Any, Optional
from app.domain_models import PFRule, ESIRule, ProfessionalTaxSlab
from app.payroll.services.payroll_calculation_service import PayrollCalculationEngine

class SalaryCalculationEngine:
    """
    Reusable engine that performs a complete salary calculation based on Basic Salary.
    Returns a structured dictionary representing the full calculation pipeline,
    which is heavily consumed by both the UI Preview and backend Assignment processors.
    """

    @staticmethod
    def calculate_gross_only(basic_salary: float, structure_components: List[dict]) -> dict:
        """
        Calculates earnings, gross, PF gross, ESI gross, and distribution snapshot 
        without running any statutory deductions. 
        Requires no Rule objects.
        """
        earnings = []
        for sc in structure_components:
            if sc.get("componentType") != "Earning":
                continue

            name = sc.get("name", "")
            calc_method = sc.get("calculationMethod", "Flat")
            amount = 0.0
            formula_used = ""

            if name.lower() == "basic":
                amount = basic_salary
                formula_used = "Base Input"
            elif calc_method == "Percentage":
                perc = sc.get("percentageValue", 0.0)
                amount = basic_salary * (perc / 100.0)
                formula_used = f"{perc}% of Basic"
            elif calc_method == "Formula":
                perc = sc.get("percentageValue", 0.0)
                amount = basic_salary * (perc / 100.0)
                formula_used = sc.get("defaultFormula") or f"{perc}% of Basic"
            else:
                amount = sc.get("amount") or sc.get("monthlyAmount") or 0.0
                formula_used = "Flat"

            c_dict = sc.copy()
            c_dict["amount"] = amount
            c_dict["formulaUsed"] = formula_used
            
            c_dict["includeInGross"] = c_dict.get("includeInGross", True)
            c_dict["attendanceDependent"] = c_dict.get("attendanceDependent", True)
            c_dict["pfApplicable"] = c_dict.get("pfApplicable", False)
            c_dict["esiApplicable"] = c_dict.get("esiApplicable", False)
            c_dict["ptApplicable"] = c_dict.get("ptApplicable", False)
            c_dict["componentType"] = c_dict.get("componentType", "Earning")

            earnings.append(c_dict)

        gross_salary = PayrollCalculationEngine.calculateGross(earnings)
        earnings_with_ratios = PayrollCalculationEngine.calculateDistributionRatios(earnings)

        distribution_preview = []
        for e in earnings_with_ratios:
            if e.get("includeInGross", True):
                ratio = e.get("distributionRatio", 0.0)
                distribution_preview.append({
                    "name": e.get("name"),
                    "amount": e.get("amount", 0.0),
                    "distributionRatio": ratio,
                    "distributionPercentage": ratio * 100,
                    "attendanceDependent": e.get("attendanceDependent", True)
                })

        # Calculate base statutory grosses (without ceiling/rules applied)
        pf_gross = PayrollCalculationEngine.calculatePfGross(earnings_with_ratios, None)
        esi_gross = PayrollCalculationEngine.calculateEsiGross(earnings_with_ratios)
        
        return {
            "earnings": [{"name": e["name"], "amount": e["amount"], "formula": e["formulaUsed"]} for e in earnings_with_ratios],
            "distribution": distribution_preview,
            "grossSalary": gross_salary,
            "pfGross": pf_gross,
            "esiGross": esi_gross
        }

    @staticmethod
    def calculate(
        basic_salary: float,
        structure_components: List[Dict[str, Any]],
        pf_option: str,
        esi_option: str,
        pt_state: str,
        pf_rule: PFRule,
        esi_rule: ESIRule,
        pt_slabs: List[ProfessionalTaxSlab]
    ) -> Dict[str, Any]:
        
        # 1. Calculate Earnings
        earnings = []
        for sc in structure_components:
            name = sc.get("name", "Unknown")
            calc_method = sc.get("calculationMethod", "Flat")
            amount = 0.0
            formula_used = ""

            if name.lower() == "basic":
                amount = basic_salary
                formula_used = "Base Input"
            elif calc_method == "Percentage":
                perc = sc.get("percentageValue", 0.0)
                amount = basic_salary * (perc / 100.0)
                formula_used = f"{perc}% of Basic"
            elif calc_method == "Formula":
                # Currently treating 'Formula' as percentage of Basic for simplicity
                # if there is a 'defaultFormula' we could evaluate it, but falling back to basic percentage.
                perc = sc.get("percentageValue", 0.0)
                amount = basic_salary * (perc / 100.0)
                formula_used = sc.get("defaultFormula") or f"{perc}% of Basic"
            else:
                # Flat or otherwise
                amount = sc.get("amount") or sc.get("monthlyAmount") or 0.0
                formula_used = "Flat"

            # Create an instance matching what PayrollCalculationEngine expects
            c_dict = sc.copy()
            c_dict["amount"] = amount
            c_dict["formulaUsed"] = formula_used
            
            # Default missing flags for safety
            c_dict["includeInGross"] = c_dict.get("includeInGross", True)
            c_dict["attendanceDependent"] = c_dict.get("attendanceDependent", True)
            c_dict["pfApplicable"] = c_dict.get("pfApplicable", False)
            c_dict["esiApplicable"] = c_dict.get("esiApplicable", False)
            c_dict["ptApplicable"] = c_dict.get("ptApplicable", False)
            c_dict["componentType"] = c_dict.get("componentType", "Earning")

            earnings.append(c_dict)

        # 2. Calculate Gross
        gross_salary = PayrollCalculationEngine.calculateGross(earnings)

        # 3. Calculate Distribution Snapshot
        earnings_with_ratios = PayrollCalculationEngine.calculateDistributionRatios(earnings)

        # Build detailed distribution list for the preview
        distribution_preview = []
        for e in earnings_with_ratios:
            if e.get("includeInGross", True):
                ratio = e.get("distributionRatio", 0.0)
                distribution_preview.append({
                    "name": e.get("name"),
                    "amount": e.get("amount", 0.0),
                    "distributionRatio": ratio,
                    "distributionPercentage": ratio * 100,
                    "attendanceDependent": e.get("attendanceDependent", True)
                })

        # 4. Statutory: PF Calculations
        pf_gross = PayrollCalculationEngine.calculatePfGross(earnings_with_ratios, pf_rule)
        
        # Determine employee choice based on explicit flags if available
        if preview_request:
            wants_pf = getattr(preview_request, "wantsPf", True)
            wants_pension = getattr(preview_request, "wantsPension", True)
            is_existing_pension = getattr(preview_request, "isExistingPensionMember", False)
            is_fresher = getattr(preview_request, "isFresher", True)
            use_ceiling = getattr(preview_request, "pfCalculationMode", "Default") == "Ceiling"
        else:
            wants_pf = pf_option != 'OptOut'
            use_ceiling = pf_option == 'Ceiling'
            wants_pension = True
            is_existing_pension = False
            is_fresher = True
            
        employee_choice = {
            "wantsPf": wants_pf,
            "wantsPension": wants_pension,
            "isFresher": is_fresher,
            "useCeiling": use_ceiling,
            "isExistingPensionMember": is_existing_pension
        }
        
        pf_result = PayrollCalculationEngine.calculatePf(pf_gross, pf_rule, employee_choice)

        pf_preview = {
            "pfGross": pf_gross,
            "ceilingApplied": pf_rule.defaultMode == "Always Ceiling" or use_ceiling,
            "pfWageUsed": min(pf_gross, pf_rule.pfCeilingAmount) if (pf_rule.defaultMode == "Always Ceiling" or use_ceiling) else pf_gross,
            "employeePf": pf_result["employeePf"],
            "employerPf": pf_result["employerPf"],
            "employerPension": pf_result["employerPension"],
            "adminCharges": pf_result["pfAdminCharges"],
            "totalEmployerPf": pf_result["employerPf"] + pf_result["employerPension"] + pf_result["pfAdminCharges"]
        }

        # 5. Statutory: ESI Calculations
        esi_gross = PayrollCalculationEngine.calculateEsiGross(earnings_with_ratios)
        
        # esiOption: 'Default', 'PhysicalDisability'
        # Check esiEnabled from preview_request if available
        esi_enabled = getattr(preview_request, "esiEnabled", True) if preview_request else (esi_option != 'OptOut')
        esi_result = PayrollCalculationEngine.calculateEsi(esi_gross, esi_rule) if esi_enabled else {"employeeEsi": 0.0, "employerEsi": 0.0}

        esi_preview = {
            "esiGross": esi_gross,
            "employeeEsi": esi_result["employeeEsi"],
            "employerEsi": esi_result["employerEsi"]
        }

        # 6. Statutory: PT Calculation
        # PT state is passed directly. If state == "None", PT is 0.
        pt_amount = 0.0
        if pt_state != "None":
            # Just matching the state to slabs if we had state-specific slabs.
            # Currently calculateProfessionalTax uses 'gender'. We'll assume 'Any'.
            pt_amount = PayrollCalculationEngine.calculateProfessionalTax(gross_salary, pt_slabs, gender="Any")
            
        pt_preview = {
            "ptState": pt_state,
            "professionalTax": pt_amount
        }

        # 7. Deductions
        total_deductions = PayrollCalculationEngine.calculateEmployeeDeduction(pf_result, esi_result, pt_amount, 0.0)
        
        deductions_preview = []
        if pf_result["employeePf"] > 0: deductions_preview.append({"name": "Employee PF", "amount": pf_result["employeePf"]})
        if esi_result["employeeEsi"] > 0: deductions_preview.append({"name": "Employee ESI", "amount": esi_result["employeeEsi"]})
        if pt_amount > 0: deductions_preview.append({"name": "Professional Tax", "amount": pt_amount})

        # 8. Employer Contribution
        employer_contribution = PayrollCalculationEngine.calculateEmployerContribution(pf_result, esi_result)

        employer_preview = []
        if pf_preview["totalEmployerPf"] > 0: employer_preview.append({"name": "Employer PF (incl. Pension & Admin)", "amount": pf_preview["totalEmployerPf"]})
        if esi_result["employerEsi"] > 0: employer_preview.append({"name": "Employer ESI", "amount": esi_result["employerEsi"]})

        # 9. CTC
        take_home = PayrollCalculationEngine.calculateTakeHome(gross_salary, total_deductions)
        monthly_ctc = gross_salary + employer_contribution
        annual_ctc = monthly_ctc * 12

        # 10. Preview Response Formatted to Mirror UI
        return {
            "earnings": [
                {
                    "name": e["name"],
                    "amount": e["amount"],
                    "formula": e["formulaUsed"]
                } for e in earnings_with_ratios
            ],
            "distribution": distribution_preview,
            "statutory": {
                "pf": pf_preview,
                "esi": esi_preview,
                "pt": pt_preview
            },
            "deductions": deductions_preview,
            "employerContributions": employer_preview,
            "summary": {
                "grossSalary": gross_salary,
                "totalDeductions": total_deductions,
                "takeHome": take_home,
                "employerContribution": employer_contribution,
                "monthlyCtc": monthly_ctc,
                "annualCtc": annual_ctc
            },
            # Return raw components for the backend Assignment step
            "_rawComponents": earnings_with_ratios 
        }
