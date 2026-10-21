import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.payroll.services.payroll_calculation_service import PayrollCalculationEngine
from app.payroll.services.payroll_input_builder import PayrollInputBuilder

async def run_tests():
    db = AsyncIOMotorClient('mongodb://lokeshca2004_db_user:q7mutTirXPPe8AzC@ac-uj8llxh-shard-00-00.e5z9cjy.mongodb.net:27017,ac-uj8llxh-shard-00-01.e5z9cjy.mongodb.net:27017,ac-uj8llxh-shard-00-02.e5z9cjy.mongodb.net:27017/?ssl=true&authSource=admin&replicaSet=atlas-dztgx9-shard-0')['essl_production']
    builder = PayrollInputBuilder(db)

    employee_id = "1001"
    cases = [
        # 1. 31-day month, Fixed 30 Days setting, 1 LOP
        {
            "name": "August 31 Days, 1 LOP",
            "start": datetime(2026, 8, 1),
            "end": datetime(2026, 8, 31),
            "lop": 1.0,
            "salary": 12000.0,
        },
        # 2. 28-day month, 0 LOP
        {
            "name": "Feb 28 Days, 0 LOP",
            "start": datetime(2026, 2, 1),
            "end": datetime(2026, 2, 28),
            "lop": 0.0,
            "salary": 12000.0,
        },
        # 3. 30-day month, multiple LOP
        {
            "name": "Sep 30 Days, 2.5 LOP",
            "start": datetime(2026, 9, 1),
            "end": datetime(2026, 9, 30),
            "lop": 2.5,
            "salary": 12000.0,
        }
    ]

    for case in cases:
        print(f"\n--- TEST: {case['name']} ---")
        # We will mock ui_components to skip db lookup for components
        input_data = await builder.build(
            employee_id=employee_id,
            start_date=case["start"],
            end_date=case["end"],
            ui_components=[{"componentName": "Basic", "monthlyAmount": case["salary"], "includeInGross": True, "componentType": "Earning", "attendanceDependent": True}]
        )
        # Override lopDays manually for test
        input_data.lopDays = case["lop"]
        
        print(f"Calendar Days: {(case['end'] - case['start']).days + 1}")
        print(f"Working Days (from Input): {input_data.workingDays}")
        print(f"Salary Calculation Method: {input_data.salaryCalculationMethod}")
        print(f"Salary Divisor: {input_data.salaryDivisor}")
        print(f"LOP Days: {input_data.lopDays}")
        
        gross = PayrollCalculationEngine.calculateMonthlyGross(
            gross=case["salary"],
            salary_divisor=input_data.salaryDivisor,
            lop=input_data.lopDays,
            round_off_method=input_data.roundOffMethod
        )
        per_day = case["salary"] / input_data.salaryDivisor
        lop_amount = per_day * input_data.lopDays
        
        print(f"Per Day Salary: {per_day:.2f}")
        print(f"LOP Amount: {lop_amount:.2f}")
        print(f"Gross: {gross}")

if __name__ == "__main__":
    asyncio.run(run_tests())
