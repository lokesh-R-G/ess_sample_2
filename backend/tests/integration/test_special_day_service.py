import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from app.holiday_calendar.services.special_day_service import SpecialDayService
from app.holiday_calendar.schemas.special_day import SpecialDayCreate, SpecialDayUpdate

@pytest.fixture
def mock_db():
    db = MagicMock()
    db.special_days = MagicMock()
    db.branchs = MagicMock()
    db.companies = MagicMock()
    db.companies.find_one = AsyncMock(return_value={"_id": "MY_COMPANY", "name": "My Company"})
    db.audit_logs = MagicMock()
    return db

@pytest.mark.asyncio
async def test_validate_branch_cross_tenant_conflict(mock_db):
    service = SpecialDayService(mock_db)
    
    # Mock branch returning different companyId
    mock_db.branchs.find.return_value.to_list = AsyncMock(return_value=[
        {"_id": "branch_1", "name": "Branch 1", "companyId": "OTHER_COMPANY"}
    ])

    with pytest.raises(ValueError, match="does not belong to authorized company"):
        await service.validate_conflicts(
            company_id="MY_COMPANY",
            date_str="2026-08-15",
            applicability="Selected Branches",
            selected_branch_ids=["branch_1"]
        )

@pytest.mark.asyncio
async def test_validate_all_branches_overlap_conflict(mock_db):
    service = SpecialDayService(mock_db)
    
    mock_db.branchs.find.return_value.to_list = AsyncMock(return_value=[])
    # Mock existing active configuration for the date
    mock_db.special_days.find.return_value.to_list = AsyncMock(return_value=[
        {
            "_id": "sd_existing",
            "eventName": "Existing Holiday",
            "dayType": "Sudden Holiday",
            "applicability": "All Branches",
            "date": "2026-08-15",
            "companyId": "MY_COMPANY",
            "status": "Active"
        }
    ])

    with pytest.raises(ValueError, match="Conflict detected on 2026-08-15"):
        await service.validate_conflicts(
            company_id="MY_COMPANY",
            date_str="2026-08-15",
            applicability="All Branches",
            selected_branch_ids=[]
        )

@pytest.mark.asyncio
async def test_validate_overlapping_selected_branches_conflict(mock_db):
    service = SpecialDayService(mock_db)
    
    mock_db.branchs.find.return_value.to_list = AsyncMock(return_value=[
        {"_id": "b1", "name": "Branch 1", "companyId": "MY_COMPANY"},
        {"_id": "b2", "name": "Branch 2", "companyId": "MY_COMPANY"}
    ])
    mock_db.special_days.find.return_value.to_list = AsyncMock(return_value=[
        {
            "_id": "sd_existing",
            "eventName": "Existing Special Day",
            "dayType": "Sudden Cutoff",
            "applicability": "Selected Branches",
            "selectedBranchIds": ["b1"],
            "date": "2026-08-15",
            "companyId": "MY_COMPANY",
            "status": "Active"
        }
    ])

    # Trying to add b1 and b2 conflicts on b1
    with pytest.raises(ValueError, match="Conflict detected on 2026-08-15"):
        await service.validate_conflicts(
            company_id="MY_COMPANY",
            date_str="2026-08-15",
            applicability="Selected Branches",
            selected_branch_ids=["b1", "b2"]
        )

@pytest.mark.asyncio
async def test_validate_disjoint_selected_branches_allowed(mock_db):
    service = SpecialDayService(mock_db)
    
    mock_db.branchs.find.return_value.to_list = AsyncMock(return_value=[
        {"_id": "b2", "name": "Branch 2", "companyId": "MY_COMPANY"}
    ])
    mock_db.special_days.find.return_value.to_list = AsyncMock(return_value=[
        {
            "_id": "sd_existing",
            "eventName": "Existing Special Day",
            "dayType": "Sudden Cutoff",
            "applicability": "Selected Branches",
            "selectedBranchIds": ["b1"],
            "date": "2026-08-15",
            "companyId": "MY_COMPANY",
            "status": "Active"
        }
    ])

    # b2 does not overlap with b1 -> should not raise
    await service.validate_conflicts(
        company_id="MY_COMPANY",
        date_str="2026-08-15",
        applicability="Selected Branches",
        selected_branch_ids=["b2"]
    )
