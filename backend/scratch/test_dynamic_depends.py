import asyncio
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

app = FastAPI()

def get_current_user():
    return {"companyId": "123"}

def my_provider(user: dict = Depends(get_current_user)):
    return {"provided_company": user["companyId"]}

def require_permission(perm: str, provider=None):
    if provider is None:
        async def guard(user=Depends(get_current_user)):
            return user
        return guard
    else:
        async def guard(user=Depends(get_current_user), rc=Depends(provider)):
            return rc
        return guard

@app.get("/test")
async def test_route(data=Depends(require_permission("test", provider=my_provider))):
    return data

client = TestClient(app)
print(client.get("/test").json())
