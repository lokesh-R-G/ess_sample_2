# Organization Module – Request Contract Audit

> [!NOTE]
> Backend DTOs are the source of truth. All comparisons are made against the actual schema files.

---

## Part 1: Entity-by-Entity Request Matrix

### How the Base Repository Handles Responses
`BaseRepository.create()` returns `self.model_class(**data)` where `data` still has the key `"_id"`. The Model classes all declare `id: Optional[str] = Field(default=None, alias="_id")`. This means the model hydrates correctly using `_id`. However, the Response DTOs (schemas) all declare `id: str = Field(alias="_id")`, meaning FastAPI must serialize using the alias `_id`. Whether this works depends on whether `response_model_by_alias=True` is in effect.

---

### 1. Organization

| Dimension | Detail |
|:---|:---|
| **Endpoint** | `POST /v2/organization/organizations/` |
| **Backend Required** | `name: str` |
| **Backend Optional** | — |
| **Frontend Sends** | `{ name }` |
| **Missing Fields** | None |
| **Response DTO** | `OrganizationResponse` → `id: str = Field(alias="_id")` |
| **Response Issue** | ⚠️ FastAPI will serialize as `"id"` by default, not `"_id"`, unless `by_alias=True` is configured globally |
| **Status** | ✅ CREATE works · ⚠️ Response field name inconsistency |

---

### 2. Company

| Dimension | Detail |
|:---|:---|
| **Endpoint** | `POST /v2/organization/companys/` |
| **Backend Required** | `name: str` |
| **Backend Optional** | — |
| **Frontend Sends** | `{ name }` |
| **Missing Fields** | None |
| **Response DTO** | `CompanyResponse` → `id: str = Field(alias="_id")` |
| **Response Issue** | ⚠️ Same alias serialization inconsistency as Organization |
| **Status** | ✅ CREATE works · ⚠️ Response field name inconsistency |

---

### 3. Branch

| Dimension | Detail |
|:---|:---|
| **Endpoint** | `POST /v2/organization/branchs/` |
| **Backend Required** | `companyId: str`, `name: str` |
| **Backend Optional** | `code`, `location`, `address`, `city`, `state`, `country`, `pincode`, `contactDetails`, `attendanceEnabled` (default: `True`), `esslMachineId`, `timezone` (default: `"Asia/Kolkata"`) |
| **Frontend Sends** | `{ companyId, name, address, city, state, country, pincode, esslMachineId, attendanceEnabled }` |
| **Missing Fields** | None – all required fields are covered |
| **Response DTO** | `BranchResponse` – uses `ConfigDict(populate_by_name=True)` and `Field(validation_alias="id", serialization_alias="_id")` |
| **Response Issue** | ⚠️ The model hydrates from `BranchModel.id` (which is populated from `_id`). `validation_alias="id"` will fail to hydrate because the dict coming from the model has key `"id"` (correct), but `serialization_alias="_id"` means FastAPI outputs `"_id"`. This branch of the DTO is **more correct than others** but still needs verification that `id` is populated before serialization. |
| **Status** | ✅ CREATE likely works · ⚠️ Verify response serialization |

---

### 4. Department

| Dimension | Detail |
|:---|:---|
| **Endpoint** | `POST /v2/organization/departments/` |
| **Backend Required** | `name: str` |
| **Backend Optional** | — |
| **Frontend Sends** | `{ companyId, name }` |
| **Missing Fields** | None |
| **Backend DTO Gap** | 🚨 `DepartmentCreate` only requires `name`. The schema does **NOT** declare `companyId` as a field at all. The frontend sends it, but the backend silently ignores it because `DepartmentCreate` has no `companyId` field. The data IS stored (because `model_dump(exclude_unset=True)` produces `{"name": ...}` – `companyId` is excluded). |
| **MongoDB Storage** | `companyId` is **NOT** stored in the department document. |
| **Impact** | Department records are not linked to a Company in the database. Cross-entity filtering by `companyId` will return no results. |
| **Response DTO** | `DepartmentResponse` → `id: str = Field(alias="_id")` |
| **Response Issue** | ⚠️ Same alias issue as Company |
| **Status** | 🚨 CRITICAL – `companyId` not declared in DTO, not stored in DB |

---

### 5. Designation

| Dimension | Detail |
|:---|:---|
| **Endpoint** | `POST /v2/organization/designations/` |
| **Backend Required** | `name: str` |
| **Backend Optional** | — |
| **Frontend Sends** | `{ companyId, departmentId, name }` |
| **Missing Fields** | None sent |
| **Backend DTO Gap** | 🚨 `DesignationCreate` only requires `name`. Neither `companyId` nor `departmentId` is declared in the DTO. Both are silently dropped. |
| **MongoDB Storage** | Neither `companyId` nor `departmentId` stored. |
| **Impact** | Designations cannot be filtered by company or department. The department-designation relationship is broken. |
| **Response DTO** | `DesignationResponse` → `id: str = Field(alias="_id")` |
| **Status** | 🚨 CRITICAL – Both `companyId` and `departmentId` missing from DTO |

---

### 6. Shift

| Dimension | Detail |
|:---|:---|
| **Endpoint** | `POST /v2/organization/shifts/` |
| **Backend Required** | `name: str` |
| **Backend Optional** | — |
| **Frontend Sends** | `{ companyId, name, startTime, endTime }` |
| **Backend DTO Gap** | 🚨 `ShiftCreate` only requires `name`. `companyId`, `startTime`, `endTime` are not declared. All three are dropped on arrival. |
| **MongoDB Storage** | `startTime` and `endTime` are **NOT** stored. Shifts are useless without time ranges. |
| **Response DTO** | `ShiftResponse` → `id: str = Field(alias="_id")` |
| **Status** | 🚨 CRITICAL – `companyId`, `startTime`, `endTime` missing from DTO |

---

### 7. Holiday

| Dimension | Detail |
|:---|:---|
| **Endpoint** | `POST /v2/organization/holidays/` |
| **Backend Required** | `name: str` |
| **Backend Optional** | — |
| **Frontend Sends** | `{ companyId, name, date }` |
| **Backend DTO Gap** | 🚨 `HolidayCreate` only requires `name`. `companyId` and `date` are not declared. Both are dropped. |
| **MongoDB Storage** | The date of the holiday is **NOT** stored. |
| **Response DTO** | `HolidayResponse` → `id: str = Field(alias="_id")` |
| **Status** | 🚨 CRITICAL – `companyId` and `date` missing from DTO |

---

### 8. eSSL Machine

| Dimension | Detail |
|:---|:---|
| **Endpoint** | `POST /v2/organization/essl-machines/` |
| **Backend Required** | `serialNumber: str`, `status: Literal["Active","Offline","Maintenance"]` (default: `"Active"`) |
| **Backend Optional** | `vendor`, `model`, `firmwareVersion`, `ipAddress`, `port`, `communicationType`, `location`, `remarks` |
| **Frontend Sends** | `{ serialNumber, ipAddress, status }` |
| **Missing Fields** | None – required fields are covered |
| **Response DTO** | `ESSLMachineResponse` → `id: str = Field(alias="_id")` |
| **Response Issue** | ⚠️ Same alias serialization issue |
| **Status** | ✅ CREATE works · ⚠️ Response field name inconsistency |

---

### 9. Salary Component

| Dimension | Detail |
|:---|:---|
| **Endpoint** | `POST /v2/organization/salary-components/` |
| **Backend Required** | `companyId: str`, `name: str`, `componentType: Literal["Earning","Deduction"]` |
| **Backend Optional** | `code`, `calculationMethod` (default: `"Flat"`), `defaultFormula`, `isTaxable` (default: `True`), `pfApplicability` (default: `False`), `esiApplicability` (default: `False`), `displayOrder` (default: `1`), `isActive` (default: `True`) |
| **Frontend Sends** | `{ companyId, name, componentType, calculationMethod, isTaxable, pfApplicability, esiApplicability }` |
| **Missing Fields** | None – all required fields covered |
| **Response DTO** | `SalaryComponentResponse` → `id: str = Field(alias="_id")` |
| **GET Failure Root Cause** | 🚨 The `SalaryComponentResponse` schema inherits from `SalaryComponentCreate`, which declares `companyId: str` and `componentType: Literal[...]` as **required non-optional fields**. If **any legacy MongoDB document** is missing `companyId` or `componentType`, the Pydantic model will raise a `ValidationError` when trying to hydrate it via `SalaryComponentResponse`. |
| **Status** | 🚨 GET fails on legacy documents missing `companyId`/`componentType` |

---

### 10. Salary Structure

| Dimension | Detail |
|:---|:---|
| **Endpoint** | `POST /v2/organization/salary-structures/` |
| **Backend Required** | `companyId: str`, `name: str` |
| **Backend Optional** | `description` |
| **Frontend Sends** | `{ companyId, name, description }` |
| **Missing Fields** | None |
| **Response DTO** | `SalaryStructureResponse` → `id: str = Field(alias="_id")` |
| **Status** | ✅ CREATE works · ⚠️ Response field name inconsistency |

---

## Part 2: Response Model Audit – `id` vs `_id`

The `BaseRepository._prepare_doc()` converts `ObjectId` to a string and stores it as `doc["_id"]`. The `Model` classes (e.g., `CompanyModel`) declare `id: Optional[str] = Field(default=None, alias="_id")`, so `model_class(**doc)` hydrates `id` correctly from the `_id` key.

The `Response` schemas (e.g., `CompanyResponse`) declare `id: str = Field(alias="_id")`. FastAPI serializes using **Python attribute names by default** (i.e., `"id"`), **not the alias**, unless `response_model_by_alias=True` is set on the route or globally.

| Entity | Response DTO Field | Alias | Likely Serialized As | Fix Needed |
|:---|:---|:---|:---|:---|
| Organization | `id = Field(alias="_id")` | `_id` | `"id"` | ✅ Add `by_alias=True` |
| Company | `id = Field(alias="_id")` | `_id` | `"id"` | ✅ Add `by_alias=True` |
| Branch | `id = Field(serialization_alias="_id")` | `_id` | `"_id"` | Already correct |
| Department | `id = Field(alias="_id")` | `_id` | `"id"` | ✅ Add `by_alias=True` |
| Designation | `id = Field(alias="_id")` | `_id` | `"id"` | ✅ Add `by_alias=True` |
| Shift | `id = Field(alias="_id")` | `_id` | `"id"` | ✅ Add `by_alias=True` |
| Holiday | `id = Field(alias="_id")` | `_id` | `"id"` | ✅ Add `by_alias=True` |
| eSSL Machine | `id = Field(alias="_id")` | `_id` | `"id"` | ✅ Add `by_alias=True` |
| Salary Component | `id = Field(alias="_id")` | `_id` | `"id"` | ✅ Add `by_alias=True` |
| Salary Structure | `id = Field(alias="_id")` | `_id` | `"id"` | ✅ Add `by_alias=True` |

---

## Part 3: Generic CRUD Coverage – Missing Form Fields vs Backend DTO

| Entity | Backend Required Fields | Frontend Form Has | Gap |
|:---|:---|:---|:---|
| Organization | `name` | `name` | ✅ None |
| Company | `name` | `name` | ✅ None |
| Branch | `companyId`, `name` | `companyId`, `name`, address fields, `esslMachineId`, `attendanceEnabled` | ✅ None |
| Department | `name` (but should be `name + companyId`) | `companyId`, `name` | 🚨 `companyId` missing from backend DTO |
| Designation | `name` (but should be `name + companyId + departmentId`) | `companyId`, `departmentId`, `name` | 🚨 Both FKs missing from backend DTO |
| Shift | `name` (but should be `name + companyId + startTime + endTime`) | `companyId`, `name`, `startTime`, `endTime` | 🚨 `companyId`, `startTime`, `endTime` missing from backend DTO |
| Holiday | `name` (but should be `name + companyId + date`) | `companyId`, `name`, `date` | 🚨 `companyId` and `date` missing from backend DTO |
| eSSL Machine | `serialNumber`, `status` (default) | `serialNumber`, `ipAddress`, `status` | ✅ None |
| Salary Component | `companyId`, `name`, `componentType` | `companyId`, `name`, `componentType`, `calculationMethod`, booleans | ✅ None |
| Salary Structure | `companyId`, `name` | `companyId`, `name`, `description` | ✅ None |

---

## Part 4: Root Cause Summary

| Entity | Root Cause Category | Specific Issue |
|:---|:---|:---|
| Organization | ⚠️ Response DTO mismatch | `id` serialized instead of `_id` |
| Company | ⚠️ Response DTO mismatch | `id` serialized instead of `_id` |
| Branch | ✅ Working | Minor: verify serialization alias path |
| Department | 🚨 Backend DTO missing fields | `companyId` not in `DepartmentCreate` → not stored in DB |
| Designation | 🚨 Backend DTO missing fields | `companyId` + `departmentId` not in `DesignationCreate` → not stored |
| Shift | 🚨 Backend DTO missing fields | `companyId`, `startTime`, `endTime` not in `ShiftCreate` → not stored |
| Holiday | 🚨 Backend DTO missing fields | `companyId` + `date` not in `HolidayCreate` → date not stored |
| eSSL Machine | ⚠️ Response DTO mismatch | `id` serialized instead of `_id` |
| Salary Component | 🚨 Legacy MongoDB documents | Documents missing `companyId`/`componentType` fail model validation on GET |
| Salary Structure | ⚠️ Response DTO mismatch | `id` serialized instead of `_id` |

---

## Recommended Fix Order

1. **Critical (Broken Functionality):**
   - Fix `DepartmentCreate`, `DesignationCreate`, `ShiftCreate`, `HolidayCreate` – add missing FK + business fields.
   - Fix `SalaryComponentResponse` / GET route – handle legacy documents missing required fields.

2. **High (Response Contract):**
   - Add `model_config = ConfigDict(populate_by_name=True)` and change `alias` to `serialization_alias="_id"` on all Response DTOs, OR set `response_model_by_alias=True` globally in FastAPI.

3. **Low (Schema Cleanup):**
   - Remove inherited required fields from `SalaryComponentResponse` and `SalaryStructureResponse` – response models should not inherit strict Create constraints.
