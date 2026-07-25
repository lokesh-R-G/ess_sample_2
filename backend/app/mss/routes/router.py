from fastapi import APIRouter
router = APIRouter(prefix="/mss", tags=["Manager Self Service Engine"])

@router.get("/dashboard")
async def mss_dashboard():
    return {"status": "Success", "message": "MSS Dashboard aggregated."}

@router.get("/approvals")
async def mss_approvals():
    return {"status": "Success", "message": "Pending approvals fetched via Workflow Engine."}
