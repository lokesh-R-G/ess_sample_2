from fastapi import APIRouter, Depends
from ....db.mongo import get_database
from ....dependencies import get_current_user
from ..schemas.simulator import SimulationRequest, SimulationResponse
from ..services.simulator_service import SimulationEngine
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter(prefix="/simulate", tags=["Simulator"])

@router.post("/", response_model=SimulationResponse)
async def simulate_policy(req: SimulationRequest, db: AsyncIOMotorDatabase = Depends(get_database), user: dict = Depends(get_current_user)):
    engine = SimulationEngine(db)
    return await engine.simulate(req)
