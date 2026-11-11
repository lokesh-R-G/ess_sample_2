from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from bson import ObjectId
from app.employee.repositories.employee_repository import EmployeeRepository
from app.employee.validators.employee_validator import EmployeeValidator
from app.employee.services.identifier_registry_service import IdentifierRegistryService
from app.employee.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.employee.models.employee import EmployeeModel
import asyncio
from app.email_service.services.email_service import EmailService

class EmployeeService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = EmployeeRepository(db)
        self.validator = EmployeeValidator(db)
        self.registry = IdentifierRegistryService(db)
        self.email_service = EmailService(db)
        
    async def create(self, data: EmployeeCreate, user_id: str = None) -> EmployeeModel:
        # Pre-generate masterEmployeeId for atomic reservation
        gen_master_id = str(ObjectId())

        # Normalize machineId if present
        norm_machine_id = str(data.machineId).strip() if data.machineId is not None else None
        if norm_machine_id == "":
            norm_machine_id = None

        payload = data.model_dump(exclude_unset=True)
        if norm_machine_id is not None:
            payload["machineId"] = norm_machine_id

        payload["_id"] = ObjectId(gen_master_id)
        payload["masterEmployeeId"] = gen_master_id

        async with await self.db.client.start_session() as session:
            async with session.start_transaction():
                # 1. Cross-field validation against other employees
                await self.validator.validate_create(data, master_employee_id=gen_master_id, session=session)

                # 2. Atomic reservation in registry if machineId provided
                if norm_machine_id:
                    await self.registry.reserve_machine_id(
                        machine_id=norm_machine_id,
                        master_employee_id=gen_master_id,
                        session=session
                    )

                # 3. Phase 8: Atomic generation of Employee ID sequence
                counter = await self.db.identity_counters.find_one_and_update(
                    {"_id": "employeeId"},
                    {"$inc": {"sequence_value": 1}},
                    upsert=True,
                    return_document=True,
                    session=session
                )
                payload["employeeId"] = str(counter["sequence_value"])
                payload["employeeCode"] = data.employeeCode
                payload["systemAccessEnabled"] = False
                payload["essStatus"] = "Not Invited"

                employee = await self.repo.create(payload, user_id, session=session)
                return employee
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["employeeId"])
        
    async def get_by_id(self, id: str) -> Optional[EmployeeModel]:
        doc = await self.repo.get_by_id(id)
        if not doc:
            doc = await self.repo.get_by_employee_id(id)
        return doc
        
    async def update(self, id: str, data: EmployeeUpdate, user_id: str = None) -> Optional[EmployeeModel]:
        # 1. Resolve authoritative target employee document
        emp_doc = await self.repo.get_by_id(id)
        if not emp_doc:
            emp_doc = await self.repo.get_by_employee_id(id)
        if not emp_doc:
            return None

        target_obj_id = emp_doc.id
        master_emp_id = getattr(emp_doc, "masterEmployeeId", None) or str(target_obj_id)
        old_machine_id = getattr(emp_doc, "machineId", None)

        update_dict = data.model_dump(exclude_unset=True)
        norm_machine_id = None
        if "machineId" in update_dict:
            if update_dict["machineId"] is not None:
                norm_machine_id = str(update_dict["machineId"]).strip()
                if norm_machine_id == "":
                    norm_machine_id = None
            update_dict["machineId"] = norm_machine_id

        async with await self.db.client.start_session() as session:
            async with session.start_transaction():
                # 2. Validate update
                await self.validator.validate_update(
                    id=target_obj_id,
                    data=data,
                    master_employee_id=master_emp_id,
                    session=session
                )

                # 3. Registry changes if machineId changed
                if "machineId" in update_dict and norm_machine_id != old_machine_id:
                    if old_machine_id:
                        await self.registry.release_machine_id(
                            machine_id=old_machine_id,
                            master_employee_id=master_emp_id,
                            session=session
                        )
                    if norm_machine_id:
                        await self.registry.reserve_machine_id(
                            machine_id=norm_machine_id,
                            master_employee_id=master_emp_id,
                            session=session
                        )

                # 4. Perform temporal version update
                doc = await self.repo.update(target_obj_id, update_dict, user_id, session=session)

        if doc and getattr(doc, "employeeId", None):
            try:
                from app.services.user_sync_service import sync_user_name_from_employee
                await sync_user_name_from_employee(self.db, employee_id=doc.employeeId)
            except Exception as e:
                print(f"[EmployeeService] User name sync failed: {e}")
        return doc
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
