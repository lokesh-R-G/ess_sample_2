def prorate_salary(base_ctc: float, total_working_days: int, lop_days: float):
    '''
    Business Rule: Prorates salary based on LOP (Loss of Pay) days sent from Leave Engine.
    '''
    if lop_days >= total_working_days: return 0
    per_day = base_ctc / total_working_days
    return base_ctc - (per_day * lop_days)
