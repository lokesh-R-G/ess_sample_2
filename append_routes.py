import codecs
from textwrap import dedent

path = r'c:\ess\ess_sample_2\backend\app\payroll\routes\admin_payroll_routes.py'
content = codecs.open(path, 'r', 'utf-8').read()

new_routes = dedent("""
from app.payroll.services.statutory_export_service import StatutoryExportService
from fastapi import Response

@router.get("/export/pf/{payroll_run_id}")
async def export_pf(
    payroll_run_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user),
    _admin = Depends(require_permission("payroll.calculate")) 
):
    try:
        service = StatutoryExportService(db)
        content_bytes, filename = await service.export_pf(payroll_run_id, current_user.get("empId"))
        
        return Response(
            content=content_bytes,
            media_type="text/plain",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/esi/{payroll_run_id}")
async def export_esi(
    payroll_run_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user),
    _admin = Depends(require_permission("payroll.calculate"))
):
    raise HTTPException(status_code=501, detail="ESIC format specification is missing. Expected precise column structure from Revenue Manual cannot be verified.")
""")

if "StatutoryExportService" not in content:
    content += "\n" + new_routes
    codecs.open(path, 'w', 'utf-8').write(content)
    print("Routes appended")
