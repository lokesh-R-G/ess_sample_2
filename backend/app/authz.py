from typing import List, Optional
from fastapi import Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.dependencies import get_current_user
from app.db.mongo import get_database

class AuthorizationError(HTTPException):
    def __init__(self, detail: str = "Insufficient permissions or out of scope"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

async def _is_manager_of(db: AsyncIOMotorDatabase, manager_id: str, target_employee_id: str) -> bool:
    """Check if target_employee reports to manager_id in employment history/hierarchy."""
    emp = await db.employees.find_one({"employeeId": target_employee_id, "status": "Active"})
    if not emp:
        return False
    return emp.get("managerId") == manager_id

class ScopeValidator:
    def __init__(self, current_user: dict, database: AsyncIOMotorDatabase):
        self.user = current_user
        self.db = database
        self.role = (current_user.get("role") or "").lower()
        self.company_id = str(current_user.get("companyId", ""))
        self.employee_id = str(current_user.get("employeeId", ""))

class AuthorizedScope:
    def __init__(self, user: dict, scope: str, db: AsyncIOMotorDatabase):
        self.user = user
        self.scope = scope
        self.db = db
        self.employee_id = user.get("employeeId")
        self.company_id = user.get("companyId")
        self.branch_id = user.get("branchId")

    async def get_mongo_filter(self, target_employee_field: str = "employeeId") -> dict:
        """
        Returns a MongoDB filter dict based on the resolved permission scope.
        """
        if self.scope == "GLOBAL":
            return {}
            
        if self.scope == "COMPANY":
            if not self.company_id:
                raise AuthorizationError("Company context missing for user.")
            return {"companyId": self.company_id}
            
        if self.scope == "TEAM":
            if not self.employee_id:
                raise AuthorizationError("Employee ID missing for user.")
            # Resolve team (direct reportees)
            reportees = await self.db.employees.find({"managerId": self.employee_id, "status": "Active"}).to_list(None)
            team_ids = [emp.get("employeeId") for emp in reportees if emp.get("employeeId")]
            team_ids.append(self.employee_id)
            return {target_employee_field: {"$in": team_ids}}
            
        if self.scope == "SELF":
            if not self.employee_id:
                raise AuthorizationError("Employee ID missing for user.")
            return {target_employee_field: self.employee_id}
            
        raise AuthorizationError(f"Unknown scope: {self.scope}")

    async def validate_resource_employee(self, target_employee_id: str):
        """
        Validates if the user can access a specific employee ID.
        """
        if self.scope == "GLOBAL":
            return
            
        if self.scope == "COMPANY":
            if not self.company_id:
                raise AuthorizationError("Company context missing.")
            # Verify target employee belongs to this company
            target = await self.db.employees.find_one({"employeeId": target_employee_id, "companyId": self.company_id})
            if not target:
                raise AuthorizationError(f"Employee {target_employee_id} is not in your company or does not exist.")
            return
            
        if self.scope == "TEAM":
            if target_employee_id == self.employee_id:
                return
            target = await self.db.employees.find_one({"employeeId": target_employee_id, "managerId": self.employee_id})
            if not target:
                raise AuthorizationError(f"Employee {target_employee_id} is not in your team.")
            return
            
        if self.scope == "SELF":
            if target_employee_id != self.employee_id:
                raise AuthorizationError("You can only access your own data.")
            return
            
        raise AuthorizationError("Scope validation failed.")

def authorize(permission_code: str):
    """
    Centralized Authorization Dependency.
    Checks if the user has the required permission and injects an AuthorizedScope
    for resource/query validation.
    """
    async def _authorize(token: str = Depends(oauth2_scheme), db: AsyncIOMotorDatabase = Depends(get_database)) -> AuthorizedScope:
        payload = decode_access_token(token)
        if not payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
            
        role_id = payload.get("roleId")
        if not role_id:
            # Fallback for old tokens (temporary migration support)
            legacy_role = payload.get("role")
            role_map = {
                "Employee": "ROLE_EMPLOYEE",
                "Manager": "ROLE_MANAGER",
                "HR": "ROLE_HR",
                "Admin": "ROLE_ADMIN",
                "Accounts": "ROLE_ACCOUNTS",
                "Accounts MD": "ROLE_ACCOUNTS_MD",
                "Super Admin": "ROLE_SUPER_ADMIN"
            }
            role_id = role_map.get(legacy_role)
            if not role_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No valid roleId found in token.")
                
        # Resolve permission from DB (Ideally this should be cached in Redis/memory)
        # We query role_permissions directly to find the assignment and its scope
        perm_assignment = await db.role_permissions.find_one({
            "roleId": role_id,
            "permissionCode": permission_code,
            "isActive": True
        })
        
        if not perm_assignment:
            raise AuthorizationError(f"You do not have permission to perform this action ({permission_code}).")
            
        scope = perm_assignment.get("scope", "SELF")
        
        return AuthorizedScope(user=payload, scope=scope, db=db)

    return _authorize
