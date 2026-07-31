from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Override the auth dependency to return a mock user
from app.auth.dependencies import get_current_user

def override_get_current_user():
    return {"id": "mock_user"}

app.dependency_overrides[get_current_user] = override_get_current_user

response = client.post(
    "/api/v2/employee/employees/",
    json={"employeeCode": "EMP1234", "systemAccessEnabled": False, "essStatus": "Not Invited"}
)

print(response.status_code)
print(response.json())
