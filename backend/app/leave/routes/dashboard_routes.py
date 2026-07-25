from fastapi import APIRouter
router = APIRouter(prefix="/dashboard", tags=["LeaveDashboard"])
@router.get("/")
async def dashboard():
    return {"message": "Leave Dashboard Metrics."}
