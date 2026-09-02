import asyncio
from datetime import datetime
from app.attendance_policy.models.leave_policy import LeavePolicy, LeaveTypeConfig
from app.attendance_policy.schemas.leave_policy import LeavePolicyResponse

doc = {
    "_id": "64be1234abcd",
    "policyCode": "TEST_01",
    "version": 1,
    "name": "Test Policy",
    "effectiveFrom": datetime.now(),
    "status": "Active",
    "leaveTypes": []
}

# Emulate repo create
model = LeavePolicy(**doc)
print("Pydantic Model attributes:", model.__dict__)

# Emulate FastAPI response_model validation
try:
    response = LeavePolicyResponse.model_validate(model.model_dump(by_alias=False))
    print("LeavePolicyResponse id:", response.id)
    print("SUCCESS")
except Exception as e:
    print("VALIDATION ERROR:", e)
