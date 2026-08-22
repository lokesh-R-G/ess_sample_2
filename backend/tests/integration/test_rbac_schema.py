# tests for RBAC schema validation

import pytest
from pymongo import MongoClient
from backend.app.core.config import get_settings

@pytest.fixture(scope="module")
def db():
    settings = get_settings()
    client = MongoClient(settings.mongo_uri)
    db = client[settings.mongo_db_name]
    yield db
    client.close()

def test_unique_roleId_index(db):
    indexes = db.roles.index_information()
    # Ensure roleId index exists and is unique
    roleid_idx = next((info for name, info in indexes.items() if any(k == "roleId" for k, _ in info.get("key", []))), None)
    assert roleid_idx is not None, "roleId index missing"
    assert roleid_idx.get("unique", False), "roleId index should be unique"

def test_unique_permissionId_index(db):
    indexes = db.permissions.index_information()
    perm_idx = next((info for name, info in indexes.items() if any(k == "permissionId" for k, _ in info.get("key", []))), None)
    assert perm_idx is not None, "permissionId index missing"
    assert perm_idx.get("unique", False), "permissionId index should be unique"

def test_unique_role_permission_combination(db):
    # Ensure there is a unique compound index on roleId + permissionId in role_permissions collection
    indexes = db.role_permissions.index_information()
    compound_idx = next((info for name, info in indexes.items() if set(k for k, _ in info.get("key", [])) == {"roleId", "permissionId"}), None)
    assert compound_idx is not None, "Compound index on (roleId, permissionId) missing"
    assert compound_idx.get("unique", False), "Compound index should be unique"

def test_valid_scopes(db):
    allowed = {"SELF", "TEAM", "BRANCH", "COMPANY", "GLOBAL"}
    for doc in db.role_permissions.find({}):
        assert doc.get("scope") in allowed, f"Invalid scope {doc.get('scope')} in document {doc['_id']}"

def test_role_permission_history_structure(db):
    # Verify required fields exist in history documents
    required = {"roleId", "permissionId", "changeType", "version", "changedAt"}
    for doc in db.role_permission_history.find({}):
        missing = required - set(doc.keys())
        assert not missing, f"Missing fields {missing} in history doc {doc['_id']}"
