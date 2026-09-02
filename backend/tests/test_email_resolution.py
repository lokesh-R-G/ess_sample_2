import pytest
from app.employee.services.email_resolver import get_employee_personal_email
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from app.api.routes.admin import invite_employee
from app.api.routes.admin import InviteEmployeeRequest

@pytest.mark.asyncio
async def test_email_resolution_success():
    db = AsyncMock()
    # Employee has personal + work email -> personal email is selected
    db.employee_contacts.find_one.return_value = {
        "employeeId": "E1",
        "personalEmail": "personal@example.com",
        "workEmail": "work@example.com",
        "isCurrent": True
    }
    
    email = await get_employee_personal_email(db, "E1")
    assert email == "personal@example.com"

@pytest.mark.asyncio
async def test_email_resolution_only_work_email():
    db = AsyncMock()
    # Employee has only work email -> rejected, no fallback
    db.employee_contacts.find_one.return_value = {
        "employeeId": "E2",
        "workEmail": "work@example.com",
        "personalEmail": None,
        "isCurrent": True
    }
    
    with pytest.raises(ValueError) as exc:
        await get_employee_personal_email(db, "E2")
    assert "does not have a valid personalEmail" in str(exc.value)

@pytest.mark.asyncio
async def test_email_resolution_no_contact():
    db = AsyncMock()
    db.employee_contacts.find_one.return_value = None
    
    with pytest.raises(ValueError) as exc:
        await get_employee_personal_email(db, "E3")
    assert "No active contact record found" in str(exc.value)

@pytest.mark.asyncio
async def test_email_resolution_email_change():
    db = AsyncMock()
    # Employee changes personal email -> subsequent emails use the new email
    db.employee_contacts.find_one.return_value = {
        "employeeId": "E1",
        "personalEmail": "new@example.com",
        "isCurrent": True
    }
    
    email = await get_employee_personal_email(db, "E1")
    assert email == "new@example.com"

