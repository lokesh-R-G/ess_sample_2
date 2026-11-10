from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.employee.repositories.base_repository import BaseRepository
from app.employee.models.employee import EmployeeModel
import math

class EmployeeRepository(BaseRepository[EmployeeModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "employees", EmployeeModel)

    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, sort_by: str = "createdAt", sort_order: int = -1, search: str = None, search_fields: List[str] = None) -> dict:
        if query is None:
            query = {}
            
        if "deletedAt" not in query:
            query["deletedAt"] = None
            
        if "isCurrent" not in query:
            query["isCurrent"] = True
            
        match_stage = query.copy()

        if search and search_fields:
            search_query = [{"$regex": search, "$options": "i"}]
            match_stage["$or"] = [{field: search_query[0]} for field in search_fields]

        pipeline = [
            {"$match": match_stage},
            {"$lookup": {
                "from": "employee_personals",
                "let": {"empId": "$employeeId"},
                "pipeline": [
                    {"$match": {"$expr": {"$and": [{"$eq": ["$employeeId", "$$empId"]}, {"$eq": ["$isCurrent", True]}]}}}
                ],
                "as": "personal"
            }},
            {"$lookup": {
                "from": "employee_contacts",
                "let": {"empId": "$employeeId"},
                "pipeline": [
                    {"$match": {"$expr": {"$and": [{"$eq": ["$employeeId", "$$empId"]}, {"$eq": ["$isCurrent", True]}]}}}
                ],
                "as": "contact"
            }},
            {"$lookup": {
                "from": "employee_employment_histories",
                "let": {"empId": "$employeeId"},
                "pipeline": [
                    {"$match": {"$expr": {"$and": [{"$eq": ["$employeeId", "$$empId"]}, {"$eq": ["$isCurrent", True]}]}}}
                ],
                "as": "employment"
            }},
            {"$unwind": {"path": "$personal", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$contact", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$employment", "preserveNullAndEmptyArrays": True}},
            {"$addFields": {
                "compObjId": {
                    "$cond": {
                        "if": {"$and": [{"$ne": ["$employment.companyId", None]}, {"$ne": ["$employment.companyId", ""]}]},
                        "then": {"$toObjectId": "$employment.companyId"},
                        "else": None
                    }
                },
                "brObjId": {
                    "$cond": {
                        "if": {"$and": [{"$ne": ["$employment.branchId", None]}, {"$ne": ["$employment.branchId", ""]}]},
                        "then": {"$toObjectId": "$employment.branchId"},
                        "else": None
                    }
                },
                "deptObjId": {
                    "$cond": {
                        "if": {"$and": [{"$ne": ["$employment.departmentId", None]}, {"$ne": ["$employment.departmentId", ""]}]},
                        "then": {"$toObjectId": "$employment.departmentId"},
                        "else": None
                    }
                },
                "desgObjId": {
                    "$cond": {
                        "if": {"$and": [{"$ne": ["$employment.designationId", None]}, {"$ne": ["$employment.designationId", ""]}]},
                        "then": {"$toObjectId": "$employment.designationId"},
                        "else": None
                    }
                }
            }},
            {"$lookup": {
                "from": "companies",
                "localField": "compObjId",
                "foreignField": "_id",
                "as": "companyDoc"
            }},
            {"$lookup": {
                "from": "branchs",
                "localField": "brObjId",
                "foreignField": "_id",
                "as": "branchDoc"
            }},
            {"$lookup": {
                "from": "departments",
                "localField": "deptObjId",
                "foreignField": "_id",
                "as": "deptDoc"
            }},
            {"$lookup": {
                "from": "designations",
                "localField": "desgObjId",
                "foreignField": "_id",
                "as": "desgDoc"
            }},
            {"$unwind": {"path": "$companyDoc", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$branchDoc", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$deptDoc", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$desgDoc", "preserveNullAndEmptyArrays": True}},
            {"$project": {
                "_id": 0,
                "id": {"$toString": "$_id"},
                "employeeId": {"$toString": "$employeeId"},
                "employeeCode": 1,
                "systemAccessEnabled": 1,
                "essStatus": 1,
                "authUserId": 1,
                "status": 1,
                "firstName": "$personal.firstName",
                "lastName": "$personal.lastName",
                "email": "$contact.personalEmail",
                "companyId": "$employment.companyId",
                "companyName": "$companyDoc.name",
                "branchId": "$employment.branchId",
                "branchName": "$branchDoc.name",
                "departmentId": "$employment.departmentId",
                "departmentName": "$deptDoc.name",
                "designationId": "$employment.designationId",
                "designationName": "$desgDoc.name"
            }}
        ]
        
        if sort_by:
            pipeline.append({"$sort": {sort_by: sort_order}})
            
        pipeline.append({"$skip": skip})
        pipeline.append({"$limit": limit})
        
        total = await self.collection.count_documents(match_stage)
        
        cursor = self.collection.aggregate(pipeline)
        docs = await cursor.to_list(length=None)

        return {
            "data": docs,
            "total": total,
            "page": (skip // limit) + 1 if limit > 0 else 1,
            "pageSize": limit,
            "totalPages": math.ceil(total / limit) if limit > 0 else 1
        }

    async def get_directory(self, skip: int = 0, limit: int = 100) -> dict:
        pipeline = [
            {"$match": {"deletedAt": None, "isCurrent": True}},
            {"$lookup": {
                "from": "employee_personals",
                "let": {"empId": "$employeeId"},
                "pipeline": [
                    {"$match": {"$expr": {"$and": [{"$eq": ["$employeeId", "$$empId"]}, {"$eq": ["$isCurrent", True]}]}}}
                ],
                "as": "personal"
            }},
            {"$lookup": {
                "from": "employee_contacts",
                "let": {"empId": "$employeeId"},
                "pipeline": [
                    {"$match": {"$expr": {"$and": [{"$eq": ["$employeeId", "$$empId"]}, {"$eq": ["$isCurrent", True]}]}}}
                ],
                "as": "contact"
            }},
            {"$lookup": {
                "from": "employee_employment_histories",
                "let": {"empId": "$employeeId"},
                "pipeline": [
                    {"$match": {"$expr": {"$and": [{"$eq": ["$employeeId", "$$empId"]}, {"$eq": ["$isCurrent", True]}]}}}
                ],
                "as": "employment"
            }},
            {"$unwind": {"path": "$personal", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$contact", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$employment", "preserveNullAndEmptyArrays": True}},
            {"$addFields": {
                "compObjId": {
                    "$cond": {
                        "if": {"$and": [{"$ne": ["$employment.companyId", None]}, {"$ne": ["$employment.companyId", ""]}]},
                        "then": {"$toObjectId": "$employment.companyId"},
                        "else": None
                    }
                },
                "deptObjId": {
                    "$cond": {
                        "if": {"$and": [{"$ne": ["$employment.departmentId", None]}, {"$ne": ["$employment.departmentId", ""]}]},
                        "then": {"$toObjectId": "$employment.departmentId"},
                        "else": None
                    }
                },
                "desgObjId": {
                    "$cond": {
                        "if": {"$and": [{"$ne": ["$employment.designationId", None]}, {"$ne": ["$employment.designationId", ""]}]},
                        "then": {"$toObjectId": "$employment.designationId"},
                        "else": None
                    }
                }
            }},
            {"$lookup": {
                "from": "companies",
                "localField": "compObjId",
                "foreignField": "_id",
                "as": "companyDoc"
            }},
            {"$lookup": {
                "from": "departments",
                "localField": "deptObjId",
                "foreignField": "_id",
                "as": "deptDoc"
            }},
            {"$lookup": {
                "from": "designations",
                "localField": "desgObjId",
                "foreignField": "_id",
                "as": "desgDoc"
            }},
            {"$unwind": {"path": "$companyDoc", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$deptDoc", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$desgDoc", "preserveNullAndEmptyArrays": True}},
            {"$project": {
                "_id": 0,
                "employeeId": {"$toString": "$employeeId"},
                "employeeCode": 1,
                "systemAccessEnabled": 1,
                "essStatus": 1,
                "authUserId": 1,
                "status": 1,
                "firstName": "$personal.firstName",
                "lastName": "$personal.lastName",
                "personalEmail": "$contact.personalEmail",
                "companyId": "$employment.companyId",
                "companyName": "$companyDoc.name",
                "departmentId": "$employment.departmentId",
                "departmentName": "$deptDoc.name",
                "designationId": "$employment.designationId",
                "designationName": "$desgDoc.name"
            }},
            {"$skip": skip},
            {"$limit": limit}
        ]

        cursor = self.collection.aggregate(pipeline)
        docs = await cursor.to_list(length=None)

        total = await self.collection.count_documents({"deletedAt": None, "isCurrent": True})

        return {
            "data": docs,
            "total": total
        }

    async def get_company_employees(self, company_id: str, branch_id: Optional[str] = None, cycle_start: Optional[datetime] = None, cycle_end: Optional[datetime] = None) -> List[dict]:
        match_stage = {"employment.companyId": company_id, "deletedAt": None}
        if branch_id:
            match_stage["employment.branchId"] = branch_id

        if cycle_end:
            emp_pipeline = [
                {"$match": {
                    "$expr": {"$and": [
                        {"$eq": ["$employeeId", "$$empId"]},
                        {"$lte": ["$effectiveFrom", cycle_end]}
                    ]},
                    "deletedAt": None
                }},
                {"$sort": {"effectiveFrom": -1}},
                {"$limit": 1}
            ]
        else:
            emp_pipeline = [
                {"$match": {
                    "$expr": {"$and": [
                        {"$eq": ["$employeeId", "$$empId"]},
                        {"$eq": ["$isCurrent", True]}
                    ]},
                    "deletedAt": None
                }}
            ]

        pipeline = [
            {"$match": {"deletedAt": None}},
            {"$lookup": {
                "from": "employee_employment_histories",
                "let": {"empId": "$employeeId"},
                "pipeline": emp_pipeline,
                "as": "employment"
            }},
            {"$unwind": {"path": "$employment", "preserveNullAndEmptyArrays": False}},
            {"$match": match_stage},
            {"$lookup": {
                "from": "employee_personals",
                "let": {"empId": "$employeeId"},
                "pipeline": [
                    {"$match": {"$expr": {"$and": [{"$eq": ["$employeeId", "$$empId"]}, {"$eq": ["$isCurrent", True]}]}}}
                ],
                "as": "personal"
            }},
            {"$unwind": {"path": "$personal", "preserveNullAndEmptyArrays": True}},
            {"$project": {
                "_id": 0,
                "employeeId": {"$toString": "$employeeId"},
                "employeeCode": 1,
                "firstName": "$personal.firstName",
                "lastName": "$personal.lastName",
                "companyId": "$employment.companyId",
                "branchId": "$employment.branchId",
                "status": 1
            }}
        ]
        
        cursor = self.collection.aggregate(pipeline)
        docs = await cursor.to_list(length=10000)
        return docs

    async def get_by_employee_id(self, employee_id: str) -> Optional[EmployeeModel]:
        doc = await self.collection.find_one({
            "employeeId": employee_id,
            "deletedAt": None,
            "isCurrent": True
        })
        if doc:
            return self.model_class(**self._prepare_doc(doc))
        return None

    async def get_by_employee_code(self, employee_code: str) -> Optional[EmployeeModel]:
        doc = await self.collection.find_one({
            "employeeCode": employee_code,
            "deletedAt": None,
            "isCurrent": True
        })
        if doc:
            return self.model_class(**self._prepare_doc(doc))
        return None

    async def assign_employee_code(self, employee_id: str, employee_code: str) -> None:
        """
        Atomically assign an Employee Code to an Employee record.
        Used exclusively during the ESS invitation flow.
        Once an ESS account is created (essStatus != 'Not Invited'),
        the Employee Code is locked and cannot be changed via this method.
        """
        now = datetime.now(timezone.utc)
        await self.collection.update_one(
            {"employeeId": employee_id, "isCurrent": True, "deletedAt": None},
            {"$set": {"employeeCode": employee_code, "updatedAt": now}}
        )

    async def update_ess_status(
        self,
        employee_id: str,
        ess_status: str,
        auth_user_id: str,
        system_access_enabled: bool = True,
    ) -> None:
        """Write-back ESS provisioning state into the Employee V2 record."""
        now = datetime.now(timezone.utc)
        await self.collection.update_one(
            {"employeeId": employee_id, "isCurrent": True, "deletedAt": None},
            {"$set": {
                "essStatus": ess_status,
                "systemAccessEnabled": system_access_enabled,
                "authUserId": auth_user_id,
                "updatedAt": now,
            }}
        )
