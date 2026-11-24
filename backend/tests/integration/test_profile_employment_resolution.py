import pytest
import pytest_asyncio
from datetime import datetime, timezone
from bson import ObjectId

from app.db.mongo import get_database
from app.core.security import create_access_token
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest_asyncio.fixture
async def setup_comprehensive_profile_data():
    db = get_database()
    
    # 1. Companies & Branches (using 'companies' and 'branchs')
    comp_res = await db.companies.insert_one({
        "name": "Acme Global Industries",
        "code": "ACME_001",
        "status": "Active"
    })
    comp_id = str(comp_res.inserted_id)

    branch_res = await db.branchs.insert_one({
        "name": "Acme HQ Tech Park",
        "code": "ACME_HQ",
        "companyId": comp_id,
        "status": "Active"
    })
    branch_id = str(branch_res.inserted_id)

    dept_res = await db.departments.insert_one({
        "name": "Platform Engineering",
        "code": "PLAT_ENG",
        "companyId": comp_id,
        "status": "Active"
    })
    dept_id = str(dept_res.inserted_id)

    desig_res = await db.designations.insert_one({
        "name": "Lead Architect",
        "code": "ARCH_01",
        "companyId": comp_id,
        "status": "Active"
    })
    desig_id = str(desig_res.inserted_id)

    # 2. Manager Employee Record
    mgr_res = await db.employees.insert_one({
        "employeeId": "test-mgr-uuid-001",
        "employeeCode": "MGR-001",
        "firstName": "Sarah",
        "lastName": "Connor",
        "status": "Active"
    })
    mgr_obj_id = str(mgr_res.inserted_id)

    await db.employee_personals.insert_one({
        "employeeId": "test-mgr-uuid-001",
        "employeeCode": "MGR-001",
        "firstName": "Sarah",
        "lastName": "Connor"
    })

    # 3. Target Employee 1: Manager referenced by MongoDB ObjectId
    await db.employees.insert_one({
        "employeeId": "test-emp-uuid-001",
        "employeeCode": "EMP-OBJID-001",
        "status": "Active"
    })
    await db.employee_personals.insert_one({
        "employeeId": "test-emp-uuid-001",
        "firstName": "Alex",
        "lastName": "Murphy"
    })
    await db.employee_employment_histories.insert_one({
        "employeeId": "test-emp-uuid-001",
        "companyId": comp_id,
        "branchId": branch_id,
        "departmentId": dept_id,
        "designationId": desig_id,
        "reportingManagerEmployeeId": mgr_obj_id,  # Referencing manager by ObjectId string
        "dateOfJoining": datetime(2023, 1, 15, tzinfo=timezone.utc),
        "employmentType": "Full-Time",
        "status": "Active",
        "isCurrent": True,
        "effectiveFrom": datetime(2023, 1, 15, tzinfo=timezone.utc),
        "deletedAt": None
    })
    await db.users.insert_one({
        "empId": "EMP-OBJID-001",
        "employeeId": "test-emp-uuid-001",
        "employeeCode": "EMP-OBJID-001",
        "role": "Employee",
        "isActive": True
    })

    # 4. Target Employee 2: Manager referenced by employeeId (test-mgr-uuid-001)
    await db.employees.insert_one({
        "employeeId": "test-emp-uuid-002",
        "employeeCode": "EMP-EMPID-002",
        "status": "Active"
    })
    await db.employee_personals.insert_one({
        "employeeId": "test-emp-uuid-002",
        "firstName": "Bruce",
        "lastName": "Wayne"
    })
    await db.employee_employment_histories.insert_one({
        "employeeId": "test-emp-uuid-002",
        "companyId": comp_id,
        "branchId": branch_id,
        "departmentId": dept_id,
        "designationId": desig_id,
        "reportingManagerEmployeeId": "test-mgr-uuid-001",  # Referencing manager by employeeId
        "dateOfJoining": datetime(2024, 2, 1, tzinfo=timezone.utc),
        "employmentType": "Contract",
        "status": "Active",
        "isCurrent": True,
        "effectiveFrom": datetime(2024, 2, 1, tzinfo=timezone.utc),
        "deletedAt": None
    })
    await db.users.insert_one({
        "empId": "EMP-EMPID-002",
        "employeeId": "test-emp-uuid-002",
        "employeeCode": "EMP-EMPID-002",
        "role": "Employee",
        "isActive": True
    })

    # 5. Target Employee 3: Manager referenced by employeeCode (MGR-001)
    await db.employees.insert_one({
        "employeeId": "test-emp-uuid-003",
        "employeeCode": "EMP-CODE-003",
        "status": "Active"
    })
    await db.employee_personals.insert_one({
        "employeeId": "test-emp-uuid-003",
        "firstName": "Diana",
        "lastName": "Prince"
    })
    await db.employee_employment_histories.insert_one({
        "employeeId": "test-emp-uuid-003",
        "companyId": comp_id,
        "branchId": branch_id,
        "departmentId": dept_id,
        "designationId": desig_id,
        "reportingManagerEmployeeId": "MGR-001",  # Referencing manager by employeeCode
        "dateOfJoining": datetime(2025, 5, 10, tzinfo=timezone.utc),
        "employmentType": "Full-Time",
        "status": "Active",
        "isCurrent": True,
        "effectiveFrom": datetime(2025, 5, 10, tzinfo=timezone.utc),
        "deletedAt": None
    })
    await db.users.insert_one({
        "empId": "EMP-CODE-003",
        "employeeId": "test-emp-uuid-003",
        "employeeCode": "EMP-CODE-003",
        "role": "Employee",
        "isActive": True
    })

    # 6. Target Employee 4: Multiple employment history records (History vs Current)
    await db.employees.insert_one({
        "employeeId": "test-emp-uuid-004",
        "employeeCode": "EMP-HIST-004",
        "status": "Active"
    })
    await db.employee_personals.insert_one({
        "employeeId": "test-emp-uuid-004",
        "firstName": "Barry",
        "lastName": "Allen"
    })
    # Older historical promotion
    await db.employee_employment_histories.insert_one({
        "employeeId": "test-emp-uuid-004",
        "companyId": comp_id,
        "branchId": branch_id,
        "departmentId": dept_id,
        "designationId": desig_id,
        "reportingManagerEmployeeId": "MGR-001",
        "dateOfJoining": datetime(2020, 1, 1, tzinfo=timezone.utc),
        "employmentType": "Internship",
        "status": "Active",
        "isCurrent": False,
        "effectiveFrom": datetime(2020, 1, 1, tzinfo=timezone.utc),
        "deletedAt": None
    })
    # Current active promotion
    await db.employee_employment_histories.insert_one({
        "employeeId": "test-emp-uuid-004",
        "companyId": comp_id,
        "branchId": branch_id,
        "departmentId": dept_id,
        "designationId": desig_id,
        "reportingManagerEmployeeId": "MGR-001",
        "dateOfJoining": datetime(2020, 1, 1, tzinfo=timezone.utc),
        "employmentType": "Full-Time",
        "status": "Active",
        "isCurrent": True,
        "effectiveFrom": datetime(2023, 6, 1, tzinfo=timezone.utc),
        "deletedAt": None
    })
    await db.users.insert_one({
        "empId": "EMP-HIST-004",
        "employeeId": "test-emp-uuid-004",
        "employeeCode": "EMP-HIST-004",
        "role": "Employee",
        "isActive": True
    })

    # 7. Target Employee 5: Missing optional employment fields
    await db.employees.insert_one({
        "employeeId": "test-emp-uuid-005",
        "employeeCode": "EMP-OPT-005",
        "status": "Active"
    })
    await db.employee_personals.insert_one({
        "employeeId": "test-emp-uuid-005",
        "firstName": "Clark",
        "lastName": "Kent"
    })
    await db.employee_employment_histories.insert_one({
        "employeeId": "test-emp-uuid-005",
        "companyId": None,
        "branchId": None,
        "departmentId": None,
        "designationId": None,
        "reportingManagerEmployeeId": None,
        "dateOfJoining": None,
        "employmentType": None,
        "status": "Active",
        "isCurrent": True,
        "effectiveFrom": datetime(2024, 1, 1, tzinfo=timezone.utc),
        "deletedAt": None
    })
    await db.users.insert_one({
        "empId": "EMP-OPT-005",
        "employeeId": "test-emp-uuid-005",
        "employeeCode": "EMP-OPT-005",
        "role": "Employee",
        "isActive": True
    })

    yield {
        "comp_id": comp_id,
        "branch_id": branch_id,
        "dept_id": dept_id,
        "desig_id": desig_id,
        "mgr_obj_id": mgr_obj_id
    }

    # Teardown
    all_emp_ids = [
        "test-mgr-uuid-001",
        "test-emp-uuid-001",
        "test-emp-uuid-002",
        "test-emp-uuid-003",
        "test-emp-uuid-004",
        "test-emp-uuid-005"
    ]
    all_user_codes = [
        "MGR-001",
        "EMP-OBJID-001",
        "EMP-EMPID-002",
        "EMP-CODE-003",
        "EMP-HIST-004",
        "EMP-OPT-005"
    ]
    await db.companies.delete_one({"_id": ObjectId(comp_id)})
    await db.branchs.delete_one({"_id": ObjectId(branch_id)})
    await db.departments.delete_one({"_id": ObjectId(dept_id)})
    await db.designations.delete_one({"_id": ObjectId(desig_id)})
    await db.employees.delete_many({"employeeId": {"$in": all_emp_ids}})
    await db.employee_personals.delete_many({"employeeId": {"$in": all_emp_ids}})
    await db.employee_employment_histories.delete_many({"employeeId": {"$in": all_emp_ids}})
    await db.users.delete_many({"empId": {"$in": all_user_codes}})


@pytest.mark.asyncio
async def test_manager_resolution_by_object_id(setup_comprehensive_profile_data):
    token = create_access_token(payload={"sub": "EMP-OBJID-001", "role": "Employee", "employeeId": "test-emp-uuid-001"})
    headers = {"Authorization": f"Bearer {token}"}
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v2/employees/me/profile/", headers=headers)
        assert response.status_code == 200
        emp = response.json()["employment"]
        assert emp["organization"] == "Acme Global Industries"
        assert emp["branch"] == "Acme HQ Tech Park"
        assert emp["department"] == "Platform Engineering"
        assert emp["designation"] == "Lead Architect"
        assert emp["reportingManager"] == "Sarah Connor"
        assert emp["employmentType"] == "Full-Time"


@pytest.mark.asyncio
async def test_manager_resolution_by_employee_id(setup_comprehensive_profile_data):
    token = create_access_token(payload={"sub": "EMP-EMPID-002", "role": "Employee", "employeeId": "test-emp-uuid-002"})
    headers = {"Authorization": f"Bearer {token}"}
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v2/employees/me/profile/", headers=headers)
        assert response.status_code == 200
        emp = response.json()["employment"]
        assert emp["reportingManager"] == "Sarah Connor"
        assert emp["employmentType"] == "Contract"


@pytest.mark.asyncio
async def test_manager_resolution_by_employee_code(setup_comprehensive_profile_data):
    token = create_access_token(payload={"sub": "EMP-CODE-003", "role": "Employee", "employeeId": "test-emp-uuid-003"})
    headers = {"Authorization": f"Bearer {token}"}
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v2/employees/me/profile/", headers=headers)
        assert response.status_code == 200
        emp = response.json()["employment"]
        assert emp["reportingManager"] == "Sarah Connor"
        assert emp["organization"] == "Acme Global Industries"


@pytest.mark.asyncio
async def test_multiple_employment_history_resolves_current(setup_comprehensive_profile_data):
    token = create_access_token(payload={"sub": "EMP-HIST-004", "role": "Employee", "employeeId": "test-emp-uuid-004"})
    headers = {"Authorization": f"Bearer {token}"}
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v2/employees/me/profile/", headers=headers)
        assert response.status_code == 200
        emp = response.json()["employment"]
        # Must resolve the current record (Full-Time) rather than the historical one (Internship)
        assert emp["employmentType"] == "Full-Time"


@pytest.mark.asyncio
async def test_missing_optional_employment_fields(setup_comprehensive_profile_data):
    token = create_access_token(payload={"sub": "EMP-OPT-005", "role": "Employee", "employeeId": "test-emp-uuid-005"})
    headers = {"Authorization": f"Bearer {token}"}
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v2/employees/me/profile/", headers=headers)
        assert response.status_code == 200
        emp = response.json()["employment"]
        assert emp["organization"] == ""
        assert emp["branch"] == ""
        assert emp["reportingManager"] == ""
        assert emp["employmentType"] is None


@pytest.mark.asyncio
async def test_user_to_employee_mapping_without_jwt_employee_id(setup_comprehensive_profile_data):
    # Test token without employeeId on JWT payload (resolving via empId -> users -> employees)
    token = create_access_token(payload={"sub": "EMP-CODE-003", "role": "Employee"})
    headers = {"Authorization": f"Bearer {token}"}
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v2/employees/me/profile/", headers=headers)
        assert response.status_code == 200
        assert response.json()["personal"]["employeeCode"] == "EMP-CODE-003"
        assert response.json()["employment"]["organization"] == "Acme Global Industries"
