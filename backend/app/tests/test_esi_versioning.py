import pytest
from datetime import datetime
from app.domain_models import ESIRule
from app.payroll.repositories.esi_rule_repository import ESIRuleRepository
import mongomock_motor
from bson import ObjectId

@pytest.fixture
def mock_db():
    client = mongomock_motor.AsyncMongoMockClient()
    return client["test_db"]

@pytest.mark.asyncio
async def test_initial_esi_version_creation(mock_db):
    repo = ESIRuleRepository(mock_db)
    
    rule = ESIRule(
        effectiveFrom=datetime(2026, 1, 1),
        esiEnabled=True
    )
    created = await repo.create_initial_policy(rule)
    
    assert created.version == 1
    assert created.isCurrent is True
    assert created.effectiveTo is None
    assert created.policyCode == "DEFAULT_ESI"
    
    doc = await mock_db["esi_rules"].find_one({"_id": ObjectId(created.id)})
    assert doc is not None
    assert doc["version"] == 1
    assert doc["isCurrent"] is True

@pytest.mark.asyncio
async def test_esi_version_update_and_resolution(mock_db):
    repo = ESIRuleRepository(mock_db)
    
    # Create V1
    rule1 = ESIRule(
        effectiveFrom=datetime(2026, 1, 1),
        esiEnabled=True,
        employeePercent=0.75
    )
    v1 = await repo.create_initial_policy(rule1)
    
    # Create V2
    rule2 = ESIRule(
        effectiveFrom=datetime(2026, 9, 1),
        esiEnabled=True,
        employeePercent=1.0
    )
    v2 = await repo.update_policy_version(new_effective_from=datetime(2026, 9, 1), updated_rule=rule2)
    
    assert v2.version == 2
    assert v2.isCurrent is True
    assert v2.effectiveTo is None
    
    # Verify V1 is archived exactly at V2.effectiveFrom
    v1_doc = await mock_db["esi_rules"].find_one({"_id": ObjectId(v1.id)})
    assert v1_doc["isCurrent"] is False
    assert v1_doc["effectiveTo"] == datetime(2026, 9, 1)
    
    # 5. August date resolves V1
    aug_res = await repo.resolve_policy_by_date(datetime(2026, 8, 15))
    assert aug_res.version == 1
    assert aug_res.employeePercent == 0.75
    
    # 6. September boundary resolves V2
    sep_res = await repo.resolve_policy_by_date(datetime(2026, 9, 1))
    assert sep_res.version == 2
    assert sep_res.employeePercent == 1.0
    
    # 7. Historical calculation resolves correct version
    dec_res = await repo.resolve_policy_by_date(datetime(2026, 12, 1))
    assert dec_res.version == 2
    
    # 8. Missing policy produces clean domain error logic (handled in processor)
    missing_res = await repo.resolve_policy_by_date(datetime(2025, 1, 1))
    assert missing_res is None

@pytest.mark.asyncio
async def test_esi_overlapping_rejection(mock_db):
    repo = ESIRuleRepository(mock_db)
    rule1 = ESIRule(effectiveFrom=datetime(2026, 6, 1))
    await repo.create_initial_policy(rule1)
    
    # Try updating with older date
    rule2 = ESIRule(effectiveFrom=datetime(2026, 5, 1))
    with pytest.raises(ValueError, match="New effectiveFrom must be greater than current"):
        await repo.update_policy_version(datetime(2026, 5, 1), rule2)
