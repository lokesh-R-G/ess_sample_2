from fastapi import APIRouter
router = APIRouter(prefix="/compliance", tags=["Compliance Engine"])

@router.post("/pf/register")
async def register_pf():
    return {"status": "Success", "message": "PF Register generated for the month."}

@router.post("/pt/register")
async def register_pt():
    return {"status": "Success", "message": "PT Register recorded from manual inputs."}
