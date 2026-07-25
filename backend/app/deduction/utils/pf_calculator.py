def calculate_pf(gross: float, hra: float, incentive: float, profile: dict, policy: dict):
    '''
    Business Rule: PF Gross = Gross Salary - HRA - Incentive
    If Ceiling Enabled -> PF Gross = MIN(PF Gross, Configured Ceiling)
    '''
    if not profile.get("pfEnabled", False): return 0, 0, 0
    
    pf_gross = gross - hra - incentive
    if profile.get("pfCeilingEnabled", False):
        pf_gross = min(pf_gross, policy.get("pfCeilingAmount", 15000))
        
    emp_pf = pf_gross * (policy.get("employeePfPct", 12) / 100)
    
    if profile.get("alreadyPensionMember", False):
        emplyr_pf = pf_gross * (policy.get("employerPfPct", 3.67) / 100)
        emplyr_pension = pf_gross * (policy.get("employerPensionPct", 8.33) / 100)
    else:
        emplyr_pf = pf_gross * (policy.get("totalEmployerPfPct", 12) / 100)
        emplyr_pension = 0
        
    return emp_pf, emplyr_pf, emplyr_pension
