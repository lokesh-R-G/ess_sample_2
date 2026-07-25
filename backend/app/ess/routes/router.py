from fastapi import APIRouter
router = APIRouter(prefix="/ess", tags=["Employee Self Service Engine"])

@router.get("/dashboard")
async def ess_dashboard():
    return {"status": "Success", "message": "ESS Dashboard data aggregated."}

@router.get("/payslips")
async def ess_payslips():
    return {"status": "Success", "message": "ESS Payslips fetched from Payslip Engine."}
