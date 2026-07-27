from fastapi import APIRouter, Depends
from app.db.mongo import get_database
from app.dependencies import get_current_user
from app.attendance_policy.schemas.simulator import SimulationRequest, SimulationResponse
from app.attendance_policy.services.simulator_service import SimulationEngine
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter(prefix="/simulate", tags=["Simulator"])

@router.post("/", response_model=SimulationResponse)
async def simulate_policy(req: SimulationRequest, db: AsyncIOMotorDatabase = Depends(get_database), user: dict = Depends(get_current_user)):
    engine = SimulationEngine(db)
    return await engine.simulate(req)
