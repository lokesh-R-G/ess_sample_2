from typing import List, Dict, Any, Optional
from app.domain_models import (
    PFRule, ESIRule, ProfessionalTaxSlab, SalaryComponent
)

class PayrollCalculationEngine:
    """
    Payroll Calculation Engine.
    Stateless engine for all statutory and payroll-related calculations.
    Consumes configurations from Payroll Rules.
    """

    @staticmethod
    def calculateMonthlyGross(gross: float, working_days: float, lop: float) -> float:
        """Calculate Monthly Gross after Loss of Pay (LOP) deduction."""
        if working_days <= 0:
            return 0.0
        per_day_salary = gross / working_days
        monthly_gross = gross - (per_day_salary * lop)
        return max(0.0, monthly_gross)

    @staticmethod
    def splitSalaryComponents(monthly_gross: float, structure_components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Redistribute the monthly gross back into the individual components based on their percentage share
        of the total original gross.
        
        Args:
            monthly_gross: The prorated gross for the month (after LOP).
            structure_components: List of dicts representing the assigned components with their original amounts.
                                  Must include 'amount' and 'includeInGross' flag.
        """
        total_original_gross = sum(
            c.get("amount", 0.0) 
            for c in structure_components 
            if c.get("includeInGross", True)
        )

        result = []
        for c in structure_components:
            # We don't prorate non-gross components like employer PF
            if not c.get("includeInGross", True):
                result.append(c.copy())
                continue

            original_amount = c.get("amount", 0.0)
            if total_original_gross > 0:
                share_percentage = original_amount / total_original_gross
                prorated_amount = monthly_gross * share_percentage
            else:
                prorated_amount = 0.0

            new_c = c.copy()
            new_c["proratedAmount"] = prorated_amount
            result.append(new_c)

        return result

    @staticmethod
    def calculateGross(components: List[Dict[str, Any]]) -> float:
        """Calculate total gross based on 'includeInGross' flag of components."""
        return sum(
            c.get("proratedAmount", c.get("amount", 0.0))
            for c in components
            if c.get("includeInGross", True) and c.get("componentType") == "Earning"
        )

    @staticmethod
    def calculatePfGross(components: List[Dict[str, Any]], pf_rules: PFRule) -> float:
        """Calculate PF Gross based on components flagged with 'pfApplicable'."""
        if not pf_rules.pfEnabled:
            return 0.0
            
        return sum(
            c.get("proratedAmount", c.get("amount", 0.0))
            for c in components
            if c.get("pfApplicable", False) and c.get("componentType") == "Earning"
        )

    @staticmethod
    def calculateEsiGross(components: List[Dict[str, Any]]) -> float:
        """Calculate ESI Gross based on components flagged with 'esiApplicable'."""
        return sum(
            c.get("proratedAmount", c.get("amount", 0.0))
            for c in components
            if c.get("esiApplicable", False) and c.get("componentType") == "Earning"
        )

    @staticmethod
    def calculatePf(pf_gross: float, pf_rules: PFRule, employee_choice: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate Employee PF, Employer PF, and Pension based on PF Rules.
        
        Args:
            pf_gross: The calculated PF Gross for the month.
            pf_rules: The PFRule object.
            employee_choice: Dict containing:
                             - wantsPf: bool
                             - useCeiling: bool
                             - isExistingPensionMember: bool
        """
        result = {
            "employeePf": 0.0,
            "employerPf": 0.0,
            "employerPension": 0.0,
            "pfAdminCharges": 0.0,
        }

        if not pf_rules.pfEnabled:
            return result

        is_mandatory = pf_gross < pf_rules.mandatoryBelowGross
        wants_pf = employee_choice.get("wantsPf", True)

        if not is_mandatory and not wants_pf:
            return result

        # Determine calculation base
        calc_base = pf_gross
        if pf_rules.defaultMode == "Always Ceiling" or employee_choice.get("useCeiling", False):
            calc_base = min(pf_gross, pf_rules.pfCeilingAmount)

        # Calculate Employee PF
        employee_pf = calc_base * (pf_rules.employeePfPercent / 100.0)

        # Calculate Employer splits
        is_existing_pension = employee_choice.get("isExistingPensionMember", False)
        if pf_rules.allowExistingPensionMember and is_existing_pension:
            pension_base = min(calc_base, pf_rules.pfCeilingAmount)
            employer_pension = pension_base * (pf_rules.employerPensionPercent / 100.0)
            # Cap pension
            employer_pension = min(employer_pension, pf_rules.maxPensionAmount)
            employer_pf = (calc_base * (pf_rules.employeePfPercent / 100.0)) - employer_pension
        elif pf_rules.allowFresherLogic and not is_existing_pension:
            if calc_base > pf_rules.pfCeilingAmount:
                # Fresher with salary > 15000 -> No pension, all goes to Employer PF
                employer_pension = 0.0
                employer_pf = calc_base * (pf_rules.employeePfPercent / 100.0)
            else:
                employer_pension = calc_base * (pf_rules.employerPensionPercent / 100.0)
                employer_pf = (calc_base * (pf_rules.employeePfPercent / 100.0)) - employer_pension
        else:
            # Fallback
            employer_pension = calc_base * (pf_rules.employerPensionPercent / 100.0)
            employer_pf = (calc_base * (pf_rules.employeePfPercent / 100.0)) - employer_pension

        # Processing fees
        admin_charges = 0.0
        if pf_rules.processingFeeEnabled:
            admin_charges = calc_base * (pf_rules.processingFeePercent / 100.0)

        result["employeePf"] = round(employee_pf)
        result["employerPf"] = round(employer_pf)
        result["employerPension"] = round(employer_pension)
        result["pfAdminCharges"] = round(admin_charges)
        return result

    @staticmethod
    def calculateEsi(esi_gross: float, esi_rules: ESIRule) -> Dict[str, float]:
        """Calculate Employee and Employer ESI."""
        result = {
            "employeeEsi": 0.0,
            "employerEsi": 0.0
        }

        if not esi_rules.esiEnabled or esi_gross <= 0:
            return result

        if esi_gross > esi_rules.eligibilityGross:
            return result

        emp_esi = esi_gross * (esi_rules.employeePercent / 100.0)
        empr_esi = esi_gross * (esi_rules.employerPercent / 100.0)

        import math
        if esi_rules.roundOffRule == "Ceil":
            result["employeeEsi"] = float(math.ceil(emp_esi))
            result["employerEsi"] = float(math.ceil(empr_esi))
        elif esi_rules.roundOffRule == "Nearest Rupee":
            result["employeeEsi"] = float(round(emp_esi))
            result["employerEsi"] = float(round(empr_esi))
        else:
            result["employeeEsi"] = round(emp_esi, 2)
            result["employerEsi"] = round(empr_esi, 2)

        return result

    @staticmethod
    def calculateProfessionalTax(gross: float, pt_slabs: List[ProfessionalTaxSlab], gender: str = "Any") -> float:
        """Calculate Professional Tax based on state slabs and gross salary."""
        if not pt_slabs:
            return 0.0
            
        applicable_slabs = [
            slab for slab in pt_slabs 
            if slab.gender == "Any" or slab.gender == gender
        ]
        
        # Sort by minGross just in case
        applicable_slabs.sort(key=lambda x: x.minGross)

        for slab in applicable_slabs:
            if slab.minGross <= gross <= slab.maxGross:
                return slab.taxAmount
            
            # Handling the case where maxGross is very large (e.g., infinity equivalent)
            if gross >= slab.minGross and slab.maxGross == -1: # or some high value
                return slab.taxAmount
                
        return 0.0

    @staticmethod
    def calculateEmployeeDeduction(pf_result: Dict[str, float], esi_result: Dict[str, float], pt: float, other_deductions: float = 0.0) -> float:
        """Calculate total deductions for the employee."""
        return pf_result["employeePf"] + esi_result["employeeEsi"] + pt + other_deductions
        
    @staticmethod
    def calculateEmployerContribution(pf_result: Dict[str, float], esi_result: Dict[str, float]) -> float:
        """Calculate total employer contributions."""
        return pf_result["employerPf"] + pf_result["employerPension"] + pf_result["pfAdminCharges"] + esi_result["employerEsi"]

    @staticmethod
    def calculateTakeHome(monthly_gross: float, total_deductions: float) -> float:
        """Calculate final take-home salary."""
        return max(0.0, monthly_gross - total_deductions)
