import pytest
import pytest_asyncio
import asyncio
from datetime import datetime, timezone

from app.db.mongo import get_database

@pytest_asyncio.fixture
async def setup_v2_profile_data():
    db = get_database()
    
    # 1. Employee
    await db.employees.insert_one({
        "employeeId": "test-profile-emp-001",
        "employeeCode": "EMP-001",
        "status": "Active"
    })
    
    # 2. Personal
    await db.employee_personals.insert_one({
        "employeeId": "test-profile-emp-001",
        "firstName": "John",
        "lastName": "Doe",
        "gender": "Male",
        "bloodGroup": "O+"
    })
    
    # 3. Contact
    await db.employee_contacts.insert_one({
        "employeeId": "test-profile-emp-001",
        "mobilePhone": "+123456789",
        "emergencyContactName": "Jane Doe",
        "emergencyContactRelation": "Spouse"
    })
    
    # 4. Bank
    await db.employee_banks.insert_one({
        "employeeId": "test-profile-emp-001",
        "bankName": "Test Bank",
        "accountNumber": "000123456"
    })
    
    # 5. Organization refs
    org_id = await db.organizations.insert_one({"name": "Test Org"})
    dept_id = await db.departments.insert_one({"name": "Engineering"})
    
    # 6. Employment History
    await db.employee_employment_histories.insert_one({
        "employeeId": "test-profile-emp-001",
        "companyId": str(org_id.inserted_id),
        "departmentId": str(dept_id.inserted_id),
        "status": "Active",
        "effectiveFrom": datetime.now(timezone.utc)
    })
    
    # 7. Mock user for dependency
    await db.users.insert_one({
        "empId": "EMP-001",
        "employeeId": "test-profile-emp-001",
        "role": "Employee"
    })
    
    yield "EMP-001"
    
    # Teardown
    await db.employees.delete_many({"employeeId": "test-profile-emp-001"})
    await db.employee_personals.delete_many({"employeeId": "test-profile-emp-001"})
    await db.employee_contacts.delete_many({"employeeId": "test-profile-emp-001"})
    await db.employee_banks.delete_many({"employeeId": "test-profile-emp-001"})
    await db.employee_addresses.delete_many({"employeeId": "test-profile-emp-001"})
    await db.employee_employment_histories.delete_many({"employeeId": "test-profile-emp-001"})
    await db.organizations.delete_many({"_id": org_id.inserted_id})
    await db.departments.delete_many({"_id": dept_id.inserted_id})
    await db.users.delete_many({"empId": "EMP-001"})


@pytest.mark.asyncio
async def test_profile_v2_flow(setup_v2_profile_data):
    from app.core.security import create_access_token
    token = create_access_token(payload={"sub": "EMP-001", "role": "Employee", "employeeId": "test-profile-emp-001"})
    headers = {"Authorization": f"Bearer {token}"}
    
    from httpx import ASGITransport, AsyncClient
    from app.main import app
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Test GET Profile
        response = await ac.get("/api/v2/employees/me/profile/", headers=headers)
            
        assert response.status_code == 200
        data = response.json()
        
        # Assert personal
        assert data["personal"]["firstName"] == "John"
        # Assert contact
        assert data["contact"]["mobilePhone"] == "+123456789"
        # Assert bank
        assert data["bank"]["bankName"] == "Test Bank"
        # Assert employment references resolved
        assert data["employment"]["organization"] == "Test Org"
        assert data["employment"]["department"] == "Engineering"

        # 2. Test UPDATE Profile Success (Allowed Fields)
        payload = {
            "mobilePhone": "+987654321",
            "currentCity": "Test City"
        }
        
        response = await ac.patch("/api/v2/employees/me/profile/", json=payload, headers=headers)
            
        assert response.status_code == 200
        data = response.json()
        
        # Assert contact updated
        assert data["contact"]["mobilePhone"] == "+987654321"
        # Assert address updated
        assert data["address"]["currentCity"] == "Test City"

        # 3. Test UPDATE Profile Security Boundary (Forbidden Fields)
        payload_forbidden = {
            "mobilePhone": "+987654321",
            "bankName": "Hacker Bank",
            "emergencyContactName": "Hacker",
            "departmentId": "some-id"
        }
        
        response = await ac.patch("/api/v2/employees/me/profile/", json=payload_forbidden, headers=headers)
        
        # Pydantic forbid extra fields should reject this with 422
        assert response.status_code == 422
        
        # Verify in DB that it didn't change
        db = get_database()
        bank = await db.employee_banks.find_one({"employeeId": "test-profile-emp-001"})
        assert bank["bankName"] == "Test Bank"
