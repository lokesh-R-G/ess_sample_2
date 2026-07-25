def calculate_esi(gross: float, policy: dict):
    '''
    Business Rule: Gross Salary <= Configured ESI Ceiling
    '''
    ceiling = policy.get("esiCeiling", 21000)
    if gross > ceiling:
        return 0, 0
        
    emp_esi = gross * (policy.get("employeeEsiPct", 0.75) / 100)
    emplyr_esi = gross * (policy.get("employerEsiPct", 3.25) / 100)
    return emp_esi, emplyr_esi
