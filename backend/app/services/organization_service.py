from datetime import datetime, timezone
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Any, List
from app.models import Company, Branch, Department, Designation

def prepare_org_doc(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    return doc

async def get_companies(db: AsyncIOMotorDatabase) -> List[Company]:
    cursor = db.companies.find()
    docs = await cursor.to_list(length=None)
    return [Company(**prepare_org_doc(doc)) for doc in docs]

async def create_company(db: AsyncIOMotorDatabase, company: Company) -> Company:
    doc = company.model_dump(exclude={"id"}, exclude_unset=True)
    doc["createdAt"] = datetime.now(timezone.utc)
    doc["updatedAt"] = doc["createdAt"]
    result = await db.companies.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return Company(**doc)

async def get_branches(db: AsyncIOMotorDatabase, company_id: str = None) -> List[Branch]:
    query = {"companyId": company_id} if company_id else {}
    cursor = db.branches.find(query)
    docs = await cursor.to_list(length=None)
    return [Branch(**prepare_org_doc(doc)) for doc in docs]

async def create_branch(db: AsyncIOMotorDatabase, branch: Branch) -> Branch:
    doc = branch.model_dump(exclude={"id"}, exclude_unset=True)
    doc["createdAt"] = datetime.now(timezone.utc)
    doc["updatedAt"] = doc["createdAt"]
    result = await db.branches.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return Branch(**doc)

async def get_departments(db: AsyncIOMotorDatabase, company_id: str = None) -> List[Department]:
    query = {"companyId": company_id} if company_id else {}
    cursor = db.departments.find(query)
    docs = await cursor.to_list(length=None)
    return [Department(**prepare_org_doc(doc)) for doc in docs]

async def create_department(db: AsyncIOMotorDatabase, dept: Department) -> Department:
    doc = dept.model_dump(exclude={"id"}, exclude_unset=True)
    doc["createdAt"] = datetime.now(timezone.utc)
    doc["updatedAt"] = doc["createdAt"]
    result = await db.departments.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return Department(**doc)

async def get_designations(db: AsyncIOMotorDatabase, company_id: str = None, department_id: str = None) -> List[Designation]:
    query = {}
    if company_id:
        query["companyId"] = company_id
    if department_id:
        query["departmentId"] = department_id
    cursor = db.designations.find(query)
    docs = await cursor.to_list(length=None)
    return [Designation(**prepare_org_doc(doc)) for doc in docs]

async def create_designation(db: AsyncIOMotorDatabase, desig: Designation) -> Designation:
    doc = desig.model_dump(exclude={"id"}, exclude_unset=True)
    doc["createdAt"] = datetime.now(timezone.utc)
    doc["updatedAt"] = doc["createdAt"]
    result = await db.designations.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return Designation(**doc)
