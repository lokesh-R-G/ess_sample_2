import asyncio
from app.db.mongo import get_database
from app.payroll.services.payroll_export_service import PayrollExportService

async def test_export():
    db = get_database()
    run = await db.payroll_runs.find_one({'status': {'$in': ['CALCULATED', 'ADMIN_REVIEW', 'FINALIZED', 'PUBLISHED', 'EXPORTED']}})
    if not run:
        print('No valid run found')
        return
        
    service = PayrollExportService(db)
    run_id = str(run['_id'])
    print(f'Testing export for run {run_id}...')
    content, filename = await service.generate_payroll_export(run_id, '1')
    
    with open('test_export.xlsx', 'wb') as f:
        f.write(content)
        
    print(f'Export successful: {filename} ({len(content)} bytes)')
    
asyncio.run(test_export())
