# Phase 1-3 Schema Audit & Implementation Plan

## 1. Current `role_permissions` Document Structure
The existing schema defined in `app/models/rbac.py` (lines 35-49) models the mapping as a single scalar `scope` string per document:
```python
class RolePermission(BaseModel):
    roleId: str
    permissionId: str
    scope: Literal["SELF", "TEAM", "BRANCH", "COMPANY", "GLOBAL"]
```

## 2. Current Indexes
`app/db/mongo.py` currently enforces the following indexes on `role_permissions`:
- Line 36: `await db.role_permissions.create_index([("roleId", 1), ("permissionId", 1), ("scope", 1)], unique=True)`
- Line 37: `await db.role_permissions.create_index([("roleId", 1), ("permissionId", 1)], unique=True)`

**Finding**: Line 37's unique index makes it impossible to insert two documents with the same `roleId` and `permissionId`.

## 3. Multiple Scopes Support
**Finding**: Multiple scopes are NOT currently supported. 
- You cannot insert multiple documents (Model A) because the unique index on `(roleId, permissionId)` prevents it.
- You cannot use an array of scopes (Model B) because `models/rbac.py` specifies a scalar string `scope: Literal[...]`.
- Furthermore, `app/rbac/engine.py` (line 58) evaluates permissions using:
  `perm_entry = next((p for p in perms if p.get("permissionId") == permission_code), None)`
  This means even if multiple rows existed, the engine would only ever evaluate the first one it found.

## 4. How Phase 1-3 Tests Represent Scopes
`tests/test_rbac_phase1.py` inserts mappings with a single `scope` string. For example, it assigns `"SELF"` to one role and `"TEAM"` to another, but it never attempts to assign both to the same role.

## 5. How `seed_roles.py` Inserts Mappings
`seed_roles.py` (lines 87-150) iterates through the canonical roles and permissions, fetching the `default_scope` from the role definition (e.g. `TEAM` for `manager`) and inserting a single document per permission. It explicitly checks for duplicates using `{"roleId": role_id, "permissionId": perm_id}`.

## 6. Safest Schema-Compatible Representation for SELF + TEAM
We cannot use the existing schema to represent `SELF + TEAM`. We must choose between Model A and Model B.
- **Model A (Multiple Documents)**: Requires dropping the unique index on `(roleId, permissionId)` in MongoDB and rewriting `engine.authorize()` to collect all matching documents.
- **Model B (Array of Scopes)**: Requires changing `models/rbac.py` to `scopes: List[Literal[...]]`, migrating existing documents in MongoDB to use arrays, modifying `seed_roles.py`, and updating `engine.authorize()`.

**Recommendation (Model B)**: Model B is cleaner for a NoSQL document database. A single role-permission document should express all valid scopes for that mapping. 
However, **Model A** requires zero schema migration for existing documents; it just requires dropping the index and updating `engine.py` to evaluate all matching rows. 
We will await your direction on which model to proceed with before implementing.

## 7. Migration Impact on Existing History/Versioning
If we adopt Model A (multiple rows), the history collection (`role_permission_history`) naturally supports tracking each row's scope changes individually. 
If we adopt Model B (array of scopes), the history schema (`previousScope`, `newScope`) would also need to be updated to arrays.

## 8. Before/After Matrix (Assuming Model A/B is applied)

**Before:**
| Role | permissionId | Scope |
|---|---|---|
| manager | attendance.read | TEAM |

**After:**
| Role | permissionId | Scope(s) |
|---|---|---|
| manager | attendance.read | SELF, TEAM |

## Open Question for Approval
How would you like to represent multiple scopes? 
1. **Model A**: Multiple documents per `(roleId, permissionId)`. (Requires dropping the unique index and updating engine logic, no data migration needed).
2. **Model B**: Change `scope` to an array of `scopes`. (Requires data migration, schema change, and history schema change).
