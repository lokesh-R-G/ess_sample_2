def calculate_mileage(start_odo: float, end_odo: float, cost_per_km: float):
    '''
    Business Rule: End Odometer > Start Odometer.
    Mileage = Distance * Configured Cost Per KM.
    '''
    if end_odo <= start_odo:
        raise ValueError("End odometer must be greater than start odometer.")
    distance = end_odo - start_odo
    return distance * cost_per_km
