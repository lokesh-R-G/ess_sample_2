from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClientSession
from fastapi import HTTPException
from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError

class IdentifierRegistryService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["employee_identifier_registry"]

    async def reserve_machine_id(
        self,
        machine_id: str,
        master_employee_id: str,
        session: Optional[AsyncIOMotorClientSession] = None
    ) -> None:
        """
        Atomically reserve a machineId for a given master_employee_id.
        Fails with HTTP 409 if machineId is already reserved by another employee.
        """
        raw_mid = str(machine_id).strip()
        if not raw_mid:
            return

        now = datetime.now(timezone.utc)

        # 1. Check if token is already in registry
        existing = await self.collection.find_one({"identifier": raw_mid}, session=session)
        if existing:
            if existing.get("masterEmployeeId") != master_employee_id:
                raise HTTPException(
                    status_code=409,
                    detail=f"Machine ID '{raw_mid}' is already reserved by another employee."
                )
            # Already owned by same employee
            await self.collection.update_one(
                {"_id": existing["_id"]},
                {"$set": {"updatedAt": now}},
                session=session
            )
            return

        # 2. Insert new reservation
        try:
            await self.collection.insert_one({
                "identifier": raw_mid,
                "masterEmployeeId": master_employee_id,
                "fieldType": "machineId",
                "createdAt": now,
                "updatedAt": now
            }, session=session)
        except DuplicateKeyError:
            # Race condition caught by unique index
            check = await self.collection.find_one({"identifier": raw_mid}, session=session)
            if check and check.get("masterEmployeeId") != master_employee_id:
                raise HTTPException(
                    status_code=409,
                    detail=f"Machine ID '{raw_mid}' was concurrently reserved by another employee."
                )

    async def release_machine_id(
        self,
        machine_id: str,
        master_employee_id: str,
        session: Optional[AsyncIOMotorClientSession] = None
    ) -> None:
        """
        Release a machineId reservation when an employee changes or removes it.
        """
        raw_mid = str(machine_id).strip()
        if not raw_mid:
            return
        await self.collection.delete_one({
            "identifier": raw_mid,
            "masterEmployeeId": master_employee_id
        }, session=session)

