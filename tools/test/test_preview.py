import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from app.payroll.services.payroll_processor import PayrollProcessor

async def test_preview():
    client = AsyncIOMotorClient("mongodb+srv://lokeshca2004_db_user:maYiWdAooh5Qw7QM@cluster0.aehbv6j.mongodb.net/")
    db = client.essl_production
    
    processor = PayrollProcessor(db)
    emp_id = "ccb45a55-14e4-4544-96c6-75a4d131e812"
    
    dt_from = datetime.fromisoformat("2026-08-01")
    dt_to = datetime.fromisoformat("2026-08-19")
    
    res = await processor.calculate_employee_preview(emp_id, dt_from, dt_to)
    
    import pprint
    pprint.pprint(res)

if __name__ == "__main__":
    asyncio.run(test_preview())
