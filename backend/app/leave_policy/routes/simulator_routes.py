from fastapi import APIRouter
router = APIRouter(prefix="/simulate", tags=["LeaveSimulation"])
@router.post("/")
async def simulate():
    return {"message": "Leave Policy simulated successfully."}
