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
    def calculateMonthlyGross(gross: float, salary_divisor: float, lop: float, round_off_method: str = "Nearest Rupee") -> float:
        """Calculate Monthly Gross after Loss of Pay (LOP) deduction."""
        if salary_divisor <= 0:
            return 0.0
            
        per_day_salary = gross / salary_divisor
        lop_amount = per_day_salary * lop
        monthly_gross = gross - lop_amount
        
        # Apply configured rounding to the final gross
        import math
        if round_off_method == "Nearest Rupee":
            monthly_gross = round(monthly_gross)
        elif round_off_method == "Nearest 10":
            monthly_gross = round(monthly_gross / 10.0) * 10.0
            
        return max(0.0, float(monthly_gross))

    @staticmethod
    def calculateDistributionRatios(structure_components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculate and append the distributionRatio (0-1) for attendance-dependent components.
        This should be called during Salary Assignment or Revision and the resulting 
        components should be stored as the employee's assigned salary snapshot.
        """
        # Gross contribution is from earning components that are included in gross
        total_gross = sum(
            c.get("monthlyAmount", 0.0)
            for c in structure_components
            if c.get("includeInGross", True)
        )

        # Fixed components are those that are attendanceDependent = False
        fixed_gross = sum(
            c.get("monthlyAmount", 0.0)
            for c in structure_components
            if c.get("includeInGross", True) and not c.get("attendanceDependent", True)
        )

        distributable_gross = total_gross - fixed_gross

        result = []
        for c in structure_components:
            new_c = c.copy()
            if new_c.get("includeInGross", True) and new_c.get("attendanceDependent", True):
                if distributable_gross > 0:
                    new_c["distributionRatio"] = new_c.get("monthlyAmount", 0.0) / distributable_gross
                else:
                    new_c["distributionRatio"] = 0.0
            else:
                new_c["distributionRatio"] = 0.0
            result.append(new_c)

        return result

    @staticmethod
    def splitSalaryComponents(monthly_gross: float, structure_components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Redistribute the monthly gross back into the individual components.
        Fixed components (attendanceDependent = False) retain their full amount and are subtracted from the gross first.
        The remaining gross is then distributed across attendance-dependent components using their stored distributionRatios.
        """
        # First pass: identify fixed components and subtract them from available gross
        remaining_gross = monthly_gross
        result = []
        
        for c in structure_components:
            # Skip non-gross components immediately
            if not c.get("includeInGross", True):
                result.append(c.copy())
                continue
                
            # Handle fixed components
            if not c.get("attendanceDependent", True):
                original_amount = c.get("monthlyAmount", 0.0)
                new_c = c.copy()
                new_c["proratedAmount"] = original_amount
                remaining_gross -= original_amount
                result.append(new_c)
                
        # Prevent negative remaining gross if LOP is extreme and fixed components exceed it
        remaining_gross = max(0.0, remaining_gross)

        # Second pass: distribute remaining gross to attendance-dependent components based on ratios
        for c in structure_components:
            if not c.get("includeInGross", True):
                continue
                
            if c.get("attendanceDependent", True):
                ratio = c.get("distributionRatio", 0.0)
                prorated_amount = remaining_gross * ratio
                
                new_c = c.copy()
                new_c["proratedAmount"] = prorated_amount
                result.append(new_c)

        return result

    @staticmethod
    def calculateGross(components: List[Dict[str, Any]]) -> float:
        """Calculate total gross based on 'includeInGross' flag of components."""
        return sum(
            c.get("proratedAmount", c.get("monthlyAmount", 0.0))
            for c in components
            if c.get("includeInGross", True) and c.get("componentType") == "Earning"
        )

    @staticmethod
    def calculatePfGross(components: List[Dict[str, Any]], pf_rules: Optional[PFRule] = None) -> float:
        """Calculate PF Gross based on components flagged with 'pfApplicable'."""
        if pf_rules and not pf_rules.pfEnabled:
            return 0.0
            
        return sum(
            c.get("proratedAmount", c.get("monthlyAmount", 0.0))
            for c in components
            if c.get("pfApplicable", False) and c.get("componentType") == "Earning"
        )

    @staticmethod
    def calculateEsiGross(components: List[Dict[str, Any]]) -> float:
        """Calculate ESI Gross based on components flagged with 'esiApplicable'."""
        return sum(
            c.get("proratedAmount", c.get("monthlyAmount", 0.0))
            for c in components
            if c.get("esiApplicable", False) and c.get("componentType") == "Earning"
        )

    @staticmethod
    def calculatePf(pf_gross: float, pf_rules: PFRule, employee_choice: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate Employee PF, Employer PF, Pension, EDLI, and Admin Charges based on PF Rules.
        """
        result = {
            "employeePf": 0.0,
            "employerPf": 0.0,
            "employerPension": 0.0,
            "pfAdminCharges": 0.0,
            "edli": 0.0,
        }

        if not pf_rules.pfEnabled:
            return result

        wants_pf = employee_choice.get("wantsPf", True)
        is_fresher = employee_choice.get("isFresher", True)
        is_existing_pension = employee_choice.get("isExistingPensionMember", False)
        use_ceiling = employee_choice.get("useCeiling", False)

        ceiling = pf_rules.pfCeilingAmount
        employee_pf_base = 0.0
        pension_base = 0.0

        if pf_gross <= ceiling:
            if is_fresher or is_existing_pension:
                employee_pf_base = pf_gross
                pension_base = pf_gross
            elif wants_pf:
                # Fallback for someone who is neither (though matrix focuses on fresher/existing)
                employee_pf_base = pf_gross
                pension_base = pf_gross if employee_choice.get("wantsPension", True) else 0.0
        else:
            if wants_pf:
                if is_fresher:
                    employee_pf_base = ceiling if use_ceiling else pf_gross
                    pension_base = 0.0
                elif is_existing_pension:
                    employee_pf_base = ceiling if use_ceiling else pf_gross
                    pension_base = ceiling
                else:
                    # Fallback
                    employee_pf_base = ceiling if use_ceiling else pf_gross
                    pension_base = ceiling if employee_choice.get("wantsPension", True) else 0.0

        if employee_pf_base <= 0:
            return result

        # Calculate Employee PF
        employee_pf = employee_pf_base * (pf_rules.employeePfPercent / 100.0)

        # Calculate Employer Pension
        employer_pension = pension_base * (pf_rules.employerPensionPercent / 100.0)
        if employer_pension > pf_rules.maxPensionAmount:
            employer_pension = pf_rules.maxPensionAmount

        # Employer PF receives the remainder
        employer_pf = employee_pf - employer_pension

        # Admin Charges and EDLI (EDLI defaults to 0.5% if not present in rule)
        edli_percent = getattr(pf_rules, 'edliPercent', 0.5)
        edli = employee_pf_base * (edli_percent / 100.0)
        
        admin_charges = 0.0
        if pf_rules.processingFeeEnabled:
            admin_charges = employee_pf_base * (pf_rules.processingFeePercent / 100.0)

        result["employeePf"] = round(employee_pf)
        result["employerPf"] = round(employer_pf)
        result["employerPension"] = round(employer_pension)
        result["pfAdminCharges"] = round(admin_charges)
        result["edli"] = round(edli)
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
