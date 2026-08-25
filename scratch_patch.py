import re

with open('backend/app/payroll/routes/admin_payroll_routes.py', 'r') as f:
    content = f.read()

# Add require_permission and company_context
content = content.replace(
    'from app.dependencies import require_roles, get_current_user',
    'from app.dependencies import require_permission, get_current_user\n\nasync def company_context(companyId: str) -> dict:\n    return {"companyId": companyId}'
)

# Replace the Depends(require_roles(...))
content = re.sub(
    r'current_user: AuthUser = Depends\(require_roles\(\["Admin", "Super Admin", "HR"\]\)\)',
    '_admin = Depends(require_permission("payroll.calculate", resource_context_provider=company_context))',
    content
)

# Remove the manual company scope check
content = re.sub(
    r'\s*# Enforce company scope\s*if current_user\.role != "Super Admin" and current_user\.companyId != companyId:\s*raise HTTPException\(status_code=403, detail="Unauthorized company access"\)',
    '',
    content
)

content = re.sub(
    r'\s*if current_user\.role != "Super Admin" and current_user\.companyId != companyId:\s*raise HTTPException\(status_code=403, detail="Unauthorized company access"\)',
    '',
    content
)

with open('backend/app/payroll/routes/admin_payroll_routes.py', 'w') as f:
    f.write(content)
