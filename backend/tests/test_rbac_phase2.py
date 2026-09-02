import os
import asyncio
from datetime import datetime
import pytest

from motor.motor_asyncio import AsyncIOMotorClient

# Import seed function and catalog
from app.permission.engine.seed_permissions import seed_permissions, CANONICAL_PERMISSIONS

# Load environment variables for DB connection
from backend.tests.mock_db import _MockClient
client = _MockClient()
db = client['ess_test']

@pytest.fixture(scope="module")
async def setup_db():
    await db.permissions.delete_many({})
    yield
    await db.permissions.delete_many({})

@pytest.mark.asyncio
async def test_seed_permissions_first_run(setup_db):
    result = await seed_permissions(db)
    assert result["conflicts"] == []
    assert result["created"] == len(CANONICAL_PERMISSIONS)
    for perm in CANONICAL_PERMISSIONS:
        doc = await db.permissions.find_one({"permissionId": perm["permissionId"]})
        assert doc is not None
        for field in ["permissionId", "name", "description", "module", "action", "isActive", "version", "createdAt", "updatedAt"]:
            assert field in doc
        assert "scope" not in doc

@pytest.mark.asyncio
async def test_seed_permissions_idempotent(setup_db):
    await seed_permissions(db)
    count_before = await db.permissions.count_documents({})
    result = await seed_permissions(db)
    assert result["created"] == 0
    assert result["conflicts"] == []
    count_after = await db.permissions.count_documents({})
    assert count_before == count_after
    # Ensure uniqueness of permissionId
    ids = []
    async for doc in db.permissions.find({}):
        ids.append(doc["permissionId"])
    assert len(ids) == len(set(ids))
