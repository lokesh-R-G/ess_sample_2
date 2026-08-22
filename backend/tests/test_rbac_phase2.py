import os
import asyncio
from datetime import datetime
import pytest

from motor.motor_asyncio import AsyncIOMotorClient

# Import seed function and catalog
from app.permission.engine.seed_permissions import seed_permissions, CANONICAL_PERMISSIONS

# Load environment variables for DB connection
MONGO_URI = os.getenv('MONGODB_URI') or ''
DB_NAME = os.getenv('MONGODB_DB_NAME') or 'ess_test'

if MONGO_URI:
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
else:
    # Simple async in‑memory mock collections
    class _InMemoryCollection:
        def __init__(self):
            self.store = {}
            self._id_counter = 0
        async def insert_one(self, doc):
            self._id_counter += 1
            _id = str(self._id_counter)
            doc_copy = doc.copy()
            doc_copy["_id"] = _id
            self.store[_id] = doc_copy
            return type("Result", (), {"inserted_id": _id})
        async def delete_many(self, _):
            self.store.clear()
        async def find_one(self, filter):
            for doc in self.store.values():
                if all(doc.get(k) == v for k, v in filter.items()):
                    return doc
            return None
        async def find(self, filter=None):
            filter = filter or {}
            for doc in self.store.values():
                if all(doc.get(k) == v for k, v in filter.items()):
                    yield doc
        async def count_documents(self, filter=None):
            filter = filter or {}
            return sum(1 for doc in self.store.values() if all(doc.get(k) == v for k, v in filter.items()))
    class _MockDatabase:
        def __init__(self):
            self._collections = {}
        def __getitem__(self, name):
            if name not in self._collections:
                self._collections[name] = _InMemoryCollection()
            return self._collections[name]
        __getattr__ = __getitem__
    class _MockClient:
        def __getitem__(self, name):
            return _MockDatabase()
    client = _MockClient()
    db = client[DB_NAME]

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
