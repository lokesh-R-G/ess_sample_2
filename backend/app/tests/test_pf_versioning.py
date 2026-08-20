import pytest
from datetime import datetime
from app.domain_models import PFRule
from app.payroll.repositories.pf_rule_repository import PFRuleRepository
import mongomock_motor

@pytest.fixture
def mock_db():
    client = mongomock_motor.AsyncMongoMockClient()
    return client["test_db"]

@pytest.mark.asyncio
async def test_initial_pf_version_creation(mock_db):
    repo = PFRuleRepository(mock_db)
    
    rule = PFRule(
        effectiveFrom=datetime(2026, 1, 1),
        pfEnabled=True,
        employeePfPercent=12.0
    )
    created = await repo.create_initial_policy(rule)
    
    assert created.version == 1
    assert created.isCurrent is True
    assert created.effectiveTo is None
    assert created.policyCode == "DEFAULT_PF"
    
    # Verify in DB
    from bson import ObjectId
    doc = await mock_db["pf_rules"].find_one({"_id": ObjectId(created.id)})
    assert doc is not None
    assert doc["version"] == 1
    assert doc["isCurrent"] is True

@pytest.mark.asyncio
async def test_pf_version_update_and_resolution(mock_db):
    repo = PFRuleRepository(mock_db)
    
    # Create V1
    rule1 = PFRule(
        effectiveFrom=datetime(2026, 1, 1),
        pfEnabled=True,
        employeePfPercent=10.0
    )
    v1 = await repo.create_initial_policy(rule1)
    
    # Create V2
    rule2 = PFRule(
        effectiveFrom=datetime(2026, 8, 15),
        pfEnabled=True,
        employeePfPercent=12.0
    )
    v2 = await repo.update_policy_version(new_effective_from=datetime(2026, 8, 15), updated_rule=rule2)
    
    assert v2.version == 2
    assert v2.isCurrent is True
    assert v2.effectiveTo is None
    
    # Verify V1 is now archived
    from bson import ObjectId
    v1_doc = await mock_db["pf_rules"].find_one({"_id": ObjectId(v1.id)})
    assert v1_doc["isCurrent"] is False
    assert v1_doc["effectiveTo"] == datetime(2026, 8, 15)
    
    # Test Resolution
    july_res = await repo.resolve_policy_by_date(datetime(2026, 7, 10))
    assert july_res.version == 1
    assert july_res.employeePfPercent == 10.0
    
    aug_14_res = await repo.resolve_policy_by_date(datetime(2026, 8, 14))
    assert aug_14_res.version == 1
    
    aug_15_res = await repo.resolve_policy_by_date(datetime(2026, 8, 15))
    assert aug_15_res.version == 2
    
    dec_res = await repo.resolve_policy_by_date(datetime(2026, 12, 1))
    assert dec_res.version == 2
    
    # Test Missing Policy Domain Error
    missing_res = await repo.resolve_policy_by_date(datetime(2025, 1, 1))
    assert missing_res is None

@pytest.mark.asyncio
async def test_pf_overlapping_rejection(mock_db):
    repo = PFRuleRepository(mock_db)
    rule1 = PFRule(
        effectiveFrom=datetime(2026, 6, 1),
        pfEnabled=True
    )
    await repo.create_initial_policy(rule1)
    
    # Try updating with an older date
    rule2 = PFRule(
        effectiveFrom=datetime(2026, 5, 1),
        pfEnabled=True
    )
    with pytest.raises(ValueError, match="New effectiveFrom must be greater than current"):
        await repo.update_policy_version(datetime(2026, 5, 1), rule2)
