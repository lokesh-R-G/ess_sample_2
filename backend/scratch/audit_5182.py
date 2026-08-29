import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

async def audit():
    from dotenv import load_dotenv
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI", "mongodb+srv://lokeshca2004_db_user:maYiWdAooh5Qw7QM@cluster0.aehbv6j.mongodb.net/7")
    db_name = os.getenv("MONGO_DB_NAME", "essl_production")
    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]

    async def get_emp(emp_code):
        emp = await db.employees.find_one({"employeeCode": emp_code})
        if emp:
            print(f"Employee {emp_code} found. ID: {emp['_id']}, employeeId: {emp.get('employeeId')}, empId: {emp.get('empId')}")
            return emp
        print(f"Employee {emp_code} NOT FOUND in employees collection")
        return None

    emp_5188 = await get_emp("5188")
    emp_5182 = await get_emp("5182")
    
    async def get_components(emp_code, emp_obj):
        # We don't know exactly which ID was used to save components. Let's try employeeCode and ObjectId
        ids_to_try = [emp_code]
        if emp_obj:
            ids_to_try.append(str(emp_obj["_id"]))
            if emp_obj.get("employeeId"): ids_to_try.append(emp_obj["employeeId"])
            if emp_obj.get("empId"): ids_to_try.append(emp_obj["empId"])
            
        for ident in set(ids_to_try):
            cursor = db.employee_salary_components.find({"employeeId": ident})
            docs = await cursor.to_list(length=None)
            if docs:
                print(f"\nFound {len(docs)} components for {emp_code} using employeeId='{ident}'")
                for d in docs[:1]: # Print first doc to see structure
                    print(f"Sample: effectiveFrom={d.get('effectiveFrom')}, isCurrent={d.get('isCurrent')}, status={d.get('status')}")
                return docs
        print(f"\nFound NO components for {emp_code} using any known identifier.")
        return []

    docs_5188 = await get_components("5188", emp_5188)
    docs_5182 = await get_components("5182", emp_5182)

if __name__ == "__main__":
    asyncio.run(audit())
