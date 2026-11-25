import asyncio
from dotenv import load_dotenv
load_dotenv('backend/.env')
from app.db.mongo import get_database

async def main():
    db = get_database()
    emps = await db.employees.find({}).to_list(100)
    for e in emps:
        print(f"emp _id={e.get('_id')} code={e.get('employeeCode')} employeeId={e.get('employeeId')}")

asyncio.run(main())
